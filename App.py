#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, font, messagebox, ttk
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
        self.current_unit_type = None
        self.buttons_frame = None

        if not self._load_config(config_path):
            self.withdraw()
            sys.exit(1)
        
        if not self._validate_config():
            self.withdraw()
            sys.exit(1)

        self.title("Port Control Interface")
        self.geometry("1200x800")

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
        # Top frame for unit type selection
        top_frame = tk.Frame(self, padx=10, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        # Unit type selection
        tk.Label(top_frame, text="Unit Type:", font=("Helvetica", 11, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.unit_type_var = tk.StringVar()
        unit_types = list(self.config.get('unit_types', {}).keys())
        if unit_types:
            self.unit_type_var.set(unit_types[0])  # Set default
            self.current_unit_type = unit_types[0]
        
        self.unit_dropdown = ttk.Combobox(top_frame, textvariable=self.unit_type_var, 
                                         values=unit_types, state="readonly", width=20)
        self.unit_dropdown.pack(side=tk.LEFT, padx=(0, 20))
        self.unit_dropdown.bind('<<ComboboxSelected>>', self._on_unit_type_change)

        # Unit description
        self.unit_description = tk.Label(top_frame, text="", fg="gray", font=("Helvetica", 10))
        self.unit_description.pack(side=tk.LEFT, padx=(0, 20))

        # Main container for buttons (above logs)
        self.buttons_container = tk.Frame(self, padx=10, pady=10)
        self.buttons_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create initial buttons
        self._create_buttons()

        # Logs window at the bottom (taking 1/5 of screen height)
        logs_frame = tk.Frame(self, padx=10, pady=10)
        logs_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(logs_frame, text="Command Output Logs:", font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(logs_frame, wrap=tk.WORD, height=8, width=80)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.tag_config("ERROR", foreground="red")
        self.output_text.tag_config("SUCCESS", foreground="green")
        self.output_text.tag_config("WARNING", foreground="orange")

        # Add a status bar at the very bottom
        self.status_bar = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Update unit description
        self._update_unit_description()

    def _on_unit_type_change(self, event=None):
        """Handle unit type change from dropdown"""
        new_unit_type = self.unit_type_var.get()
        if new_unit_type != self.current_unit_type:
            self.current_unit_type = new_unit_type
            self._recreate_buttons()
            self._update_unit_description()
            self.log(f"Switched to unit type: {new_unit_type}", "SUCCESS")

    def _update_unit_description(self):
        """Update the unit description label"""
        if self.current_unit_type:
            unit_config = self.config['unit_types'].get(self.current_unit_type, {})
            description = unit_config.get('description', '')
            self.unit_description.config(text=description)

    def _create_buttons(self):
        """Create buttons for the current unit type"""
        if not self.current_unit_type:
            return

        # Clear existing buttons
        for widget in self.buttons_container.winfo_children():
            widget.destroy()

        unit_config = self.config['unit_types'].get(self.current_unit_type, {})
        button_groups = unit_config.get('button_groups', [])

        # Create a frame for all button groups
        self.buttons_frame = tk.Frame(self.buttons_container)
        self.buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Create button groups in a grid layout (3 columns)
        for i, group in enumerate(button_groups):
            row = i // 3
            col = i % 3
            
            group_frame = tk.LabelFrame(self.buttons_frame, text=group['title'], padx=10, pady=10)
            group_frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)

            if 'description' in group:
                tk.Label(group_frame, text=group['description'], wraplength=250, justify='left', fg='gray').pack(fill=tk.X, pady=(0,5))

            # Create buttons for this group
            for j, btn_config in enumerate(group['buttons']):
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

                style = btn_config.get('style', {})
                if callback:
                    btn = tk.Button(group_frame, text=btn_config['text'], command=callback, **style)
                    btn.pack(fill=tk.X, pady=2)

        # Configure grid weights for even distribution
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        self.buttons_frame.grid_columnconfigure(2, weight=1)

    def _recreate_buttons(self):
        """Recreate buttons when unit type changes"""
        self._create_buttons()
    
    def _format_command(self, command_template):
        return command_template.format(**self.config['settings'])

    def log(self, message, level="INFO"):
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n", level.upper())
        self.output_text.see(tk.END)
        
        # Update status bar with the last message
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=f"Last: {message[:50]}{'...' if len(message) > 50 else ''}")

    def update_status(self, message):
        """Update the status bar with a custom message"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)

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
        # Unbind mouse wheel to prevent memory leaks
        self.unbind_all("<MouseWheel>")
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()