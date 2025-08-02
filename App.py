#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, font, messagebox
import subprocess
import threading
import json
import sys
import os
import time
import glob

class App(tk.Tk):
    def __init__(self, config_path='config.json'):
        super().__init__()
        
        # Переменная для хранения процесса xterm/screen
        self.screen_process = None

        if not self._load_config(config_path):
            self.withdraw()
            sys.exit(1)
        
        if not self._validate_config():
            self.withdraw()
            sys.exit(1)

        self.title("Port Control Interface")
        self.geometry("800x600")

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Helvetica", size=10)
        
        self._create_widgets()

    def _load_config(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Config Error", f"Failed to load config file: {e}")
            return False

    def _validate_config(self):
        """Validate configuration settings"""
        required_settings = ['serial_device', 'serial_baudrate']
        for setting in required_settings:
            if setting not in self.config.get('settings', {}):
                messagebox.showerror("Config Error", f"Missing required setting: {setting}")
                return False
        return True

    def detect_serial_ports(self):
        """Detect available serial ports"""
        if sys.platform.startswith('win'):
            # Windows - check common COM ports
            ports = [f"COM{i}" for i in range(1, 10)]
            available_ports = []
            for port in ports:
                try:
                    # Try to open the port to see if it exists
                    import serial
                    ser = serial.Serial(port, timeout=1)
                    ser.close()
                    available_ports.append(port)
                except:
                    continue
            return available_ports
        else:
            # Linux/Unix
            ports = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
            return ports

    def _create_widgets(self):
        controls_frame = tk.Frame(self, padx=10, pady=10)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, anchor='n')

        output_frame = tk.Frame(self, padx=10, pady=10)
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(output_frame, text="Local Command Output:").pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10, width=60)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.tag_config("ERROR", foreground="red")
        self.output_text.tag_config("SUCCESS", foreground="green")
        self.output_text.tag_config("WARNING", foreground="orange")
        
        for group in self.config.get('button_groups', []):
            group_frame = tk.LabelFrame(controls_frame, text=group['title'], padx=10, pady=10)
            group_frame.pack(fill=tk.X, pady=5)

            if 'description' in group:
                tk.Label(group_frame, text=group['description'], wraplength=200, justify='left', fg='gray').pack(fill=tk.X, pady=(0,5))

            for btn_config in group['buttons']:
                action = btn_config.get('action')
                callback = None
                
                if action == 'open_screen':
                    callback = self.open_screen
                elif action == 'close_screen':
                    callback = self.close_screen
                elif action == 'send_to_serial':
                    cmd = self._format_command(btn_config.get('command', ''))
                    callback = lambda c=cmd: self.run_in_thread(self._send_to_serial, c)
                elif action == 'run_local_command':
                    cmd = self._format_command(btn_config.get('command', ''))
                    callback = lambda c=cmd: self.run_in_thread(self._execute_local_command, c)
                elif action == 'send_bios_key':
                    key = btn_config.get('key', '')
                    callback = lambda k=key: self.run_in_thread(self.send_bios_key, k)

                style = btn_config.get('style', {})
                if callback:
                    tk.Button(group_frame, text=btn_config['text'], command=callback, **style).pack(fill=tk.X, pady=2)
    
    def _format_command(self, command_template):
        return command_template.format(**self.config['settings'])

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n", level.upper())
        self.output_text.see(tk.END)

    def run_in_thread(self, target_func, *args):
        thread = threading.Thread(target=target_func, args=args)
        thread.daemon = True
        thread.start()

    def _send_to_serial(self, text_command):
        device = self.config['settings']['serial_device']
        
        # Add line ending and proper formatting
        formatted_command = f"{text_command}\r\n"
        
        try:
            with open(device, 'w') as serial_port:
                serial_port.write(formatted_command)
                serial_port.flush()  # Ensure data is sent immediately
            self.after(0, self.log, f"Sent: {text_command}", "SUCCESS")
        except Exception as e:
            self.after(0, self.log, f"Error sending to serial: {e}", "ERROR")

    def send_bios_key(self, key):
        """Send BIOS navigation keys with proper timing"""
        device = self.config['settings']['serial_device']
        try:
            with open(device, 'w') as serial_port:
                serial_port.write(key)
                serial_port.flush()
                time.sleep(0.1)  # Small delay for BIOS processing
            self.after(0, self.log, f"Sent BIOS key: {key}", "SUCCESS")
        except Exception as e:
            self.after(0, self.log, f"Error sending BIOS key: {e}", "ERROR")

    def _execute_local_command(self, command):
        self.after(0, self.log, f"▶ Executing: {command}")
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True, text=True)
            if result.stdout:
                self.after(0, self.log, result.stdout)
            if result.stderr:
                self.after(0, self.log, result.stderr, "WARNING")
        except subprocess.CalledProcessError as e:
            self.after(0, self.log, f"Error executing command:\n{e.stderr}", "ERROR")

    def open_screen(self):
        if self.screen_process and self.screen_process.poll() is None:
            messagebox.showwarning("Warning", "Screen is already running.")
            return
        
        settings = self.config['settings']
        
        if sys.platform.startswith('win'):
            # Windows - use PuTTY or similar
            try:
                # Try to use PuTTY if available
                command = ["putty", "-serial", settings['serial_device'], "-sercfg", f"{settings['serial_baudrate']},8,n,1,N"]
                self.screen_process = subprocess.Popen(command)
                self.log("PuTTY process started.", "SUCCESS")
            except FileNotFoundError:
                messagebox.showerror("Error", "PuTTY not found. Please install PuTTY or configure a different terminal.")
        else:
            # Linux/Unix - use xterm + screen
            command = ["xterm", "-bg", "black", "-fg", "white", "-e", "screen", settings['serial_device'], settings['serial_baudrate']]
            try:
                self.screen_process = subprocess.Popen(command)
                self.log("Screen process started.", "SUCCESS")
            except FileNotFoundError:
                messagebox.showerror("Error", "'xterm' or 'screen' not found.")
    
    def close_screen(self):
        if self.screen_process and self.screen_process.poll() is None:
            self.screen_process.terminate()
            try:
                self.screen_process.wait(timeout=2)
                self.log("Screen process terminated.", "SUCCESS")
            except subprocess.TimeoutExpired:
                self.screen_process.kill()
                self.log("Screen process forcefully killed.", "WARNING")
            self.screen_process = None
        else:
            messagebox.showinfo("Info", "No active screen session to close.")

    def on_closing(self):
        if self.screen_process and self.screen_process.poll() is None:
            if messagebox.askyesno("Exit", "An active screen session is running. Close it before exiting?"):
                self.close_screen()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()