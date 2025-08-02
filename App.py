#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, font, messagebox
import subprocess
import threading
import json
import sys

class App(tk.Tk):
    def __init__(self, config_path='config.json'):
        super().__init__()
        
        # Переменная для хранения процесса xterm/screen
        self.screen_process = None

        if not self._load_config(config_path):
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

    def _create_widgets(self):
        controls_frame = tk.Frame(self, padx=10, pady=10)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, anchor='n')

        output_frame = tk.Frame(self, padx=10, pady=10)
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(output_frame, text="Local Command Output:").pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10, width=60)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.tag_config("ERROR", foreground="red")
        
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

                style = btn_config.get('style', {})
                if callback:
                    tk.Button(group_frame, text=btn_config['text'], command=callback, **style).pack(fill=tk.X, pady=2)
    
    def _format_command(self, command_template):
        return command_template.format(**self.config['settings'])

    def log(self, message, level="INFO"):
        self.output_text.insert(tk.END, f"{message}\n", level.upper())
        self.output_text.see(tk.END)

    def run_in_thread(self, target_func, *args):
        thread = threading.Thread(target=target_func, args=args)
        thread.daemon = True
        thread.start()

    def _send_to_serial(self, text_command):
        device = self.config['settings']['serial_device']
        command_to_run = f"echo '{text_command}' > {device}"
        try:
            subprocess.run(command_to_run, shell=True, check=True)
        except Exception as e:
            # Вывод ошибки в основное окно будет затруднен из потока,
            # можно использовать self.after для безопасного обновления GUI
            self.after(0, self.log, f"Error sending to serial: {e}", "ERROR")

    def _execute_local_command(self, command):
        self.after(0, self.log, f"▶ Executing: {command}")
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True, text=True)
            if result.stdout:
                self.after(0, self.log, result.stdout)
            if result.stderr:
                self.after(0, self.log, result.stderr, "ERROR")
        except subprocess.CalledProcessError as e:
            self.after(0, self.log, f"Error executing command:\n{e.stderr}", "ERROR")

    def open_screen(self):
        if self.screen_process and self.screen_process.poll() is None:
            messagebox.showwarning("Warning", "Screen is already running.")
            return
        
        settings = self.config['settings']
        command = ["xterm", "-bg", "black", "-fg", "white", "-e", "screen", settings['serial_device'], settings['serial_baudrate']]
        try:
            self.screen_process = subprocess.Popen(command)
            self.log("Screen process started.")
        except FileNotFoundError:
            messagebox.showerror("Error", "'xterm' or 'screen' not found.")
    
    def close_screen(self):
        if self.screen_process and self.screen_process.poll() is None:
            self.screen_process.terminate()
            try:
                self.screen_process.wait(timeout=2)
                self.log("Screen process terminated.")
            except subprocess.TimeoutExpired:
                self.screen_process.kill()
                self.log("Screen process forcefully killed.")
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