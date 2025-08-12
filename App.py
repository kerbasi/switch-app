#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, font, messagebox, ttk, simpledialog, colorchooser
import subprocess
import threading
import json
import sys
import os
import time
import glob

class AddCommandDialog:
    def __init__(self, parent, unit_type, group_title, group_type):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Add New Command - {group_title}")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.unit_type = unit_type
        self.group_title = group_title
        self.group_type = group_type  # 'serial' or 'local'
        self.result = None
        
        self._create_widgets()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"500x450+{x}+{y}")
        
    def _create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Button text
        tk.Label(main_frame, text="Button Text:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.button_text = tk.Entry(main_frame, width=50)
        self.button_text.pack(fill=tk.X, pady=(0, 15))
        
        # Command type info (read-only)
        action_text = "Send to Serial" if self.group_type == 'serial' else "Run Local Command"
        tk.Label(main_frame, text=f"Action Type: {action_text}", 
                font=("Helvetica", 9), fg="gray").pack(anchor="w", pady=(0, 15))
        
        # Command
        tk.Label(main_frame, text="Command:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.command_text = tk.Text(main_frame, height=4, width=50)
        self.command_text.pack(fill=tk.X, pady=(0, 15))
        
        # Style options with visual color picker
        style_frame = tk.LabelFrame(main_frame, text="Button Style (Optional)", padx=10, pady=10)
        style_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Background color with color picker
        bg_frame = tk.Frame(style_frame)
        bg_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(bg_frame, text="Background Color:").pack(side=tk.LEFT)
        self.bg_color = tk.Entry(bg_frame, width=15)
        self.bg_color.pack(side=tk.LEFT, padx=(10, 5))
        self.bg_color.insert(0, "#f0f0f0")
        self.bg_preview = tk.Frame(bg_frame, width=30, height=20, bg="#f0f0f0", relief=tk.RAISED, bd=2)
        self.bg_preview.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(bg_frame, text="Pick Color", command=self._pick_bg_color, 
                 width=10, bg="#e0e0e0").pack(side=tk.LEFT)
        
        # Text color with color picker
        fg_frame = tk.Frame(style_frame)
        fg_frame.pack(fill=tk.X, pady=(0, 5))
        tk.Label(fg_frame, text="Text Color:    ").pack(side=tk.LEFT)
        self.fg_color = tk.Entry(fg_frame, width=15)
        self.fg_color.pack(side=tk.LEFT, padx=(10, 5))
        self.fg_color.insert(0, "black")
        self.fg_preview = tk.Frame(fg_frame, width=30, height=20, bg="black", relief=tk.RAISED, bd=2)
        self.fg_preview.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(fg_frame, text="Pick Color", command=self._pick_fg_color, 
                 width=10, bg="#e0e0e0").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="Add Command", command=self._add_command, 
                 bg="green", fg="white", width=15).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Button(button_frame, text="Cancel", command=self._cancel, 
                 bg="red", fg="white", width=15).pack(side=tk.RIGHT)
        
    def _pick_bg_color(self):
        """Open color picker for background color"""
        color = colorchooser.askcolor(self.bg_color.get(), title="Choose Background Color")
        if color[1]:  # color[1] contains the hex value
            self.bg_color.delete(0, tk.END)
            self.bg_color.insert(0, color[1])
            self.bg_preview.config(bg=color[1])
    
    def _pick_fg_color(self):
        """Open color picker for text color"""
        color = colorchooser.askcolor(self.fg_color.get(), title="Choose Text Color")
        if color[1]:  # color[1] contains the hex value
            self.fg_color.delete(0, tk.END)
            self.fg_color.insert(0, color[1])
            self.fg_preview.config(bg=color[1])
        
    def _add_command(self):
        button_text = self.button_text.get().strip()
        command = self.command_text.get("1.0", tk.END).strip()
        
        if not button_text or not command:
            messagebox.showerror("Error", "Button text and command are required!")
            return
            
        # Create style dict if colors are specified
        style = {}
        if self.bg_color.get() and self.bg_color.get() != "#f0f0f0":
            style["bg"] = self.bg_color.get()
        if self.fg_color.get() and self.fg_color.get() != "black":
            style["fg"] = self.fg_color.get()
            
        self.result = {
            "text": button_text,
            "action": "send_to_serial" if self.group_type == 'serial' else "run_local_command",
            "command": command
        }
        
        if style:
            self.result["style"] = style
            
        self.dialog.destroy()
        
    def _cancel(self):
        self.dialog.destroy()

class AddGroupDialog:
    def __init__(self, parent, unit_type):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Add New Button Group - {unit_type}")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.unit_type = unit_type
        self.result = None
        
        self._create_widgets()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
    def _create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Group title
        tk.Label(main_frame, text="Group Title:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.group_title = tk.Entry(main_frame, width=40)
        self.group_title.pack(fill=tk.X, pady=(0, 15))
        
        # Group description
        tk.Label(main_frame, text="Group Description:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.group_description = tk.Text(main_frame, height=4, width=40)
        self.group_description.pack(fill=tk.X, pady=(0, 15))
        
        # Group type selection
        tk.Label(main_frame, text="Group Type:", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.group_type_var = tk.StringVar(value="serial")
        type_frame = tk.Frame(main_frame)
        type_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Radiobutton(type_frame, text="Serial Commands", variable=self.group_type_var, 
                      value="serial").pack(side=tk.LEFT, padx=(0, 20))
        tk.Radiobutton(type_frame, text="Local Commands", variable=self.group_type_var, 
                      value="local").pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="Add Group", command=self._add_group, 
                 bg="green", fg="white", width=15).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Button(button_frame, text="Cancel", command=self._cancel, 
                 bg="red", fg="white", width=15).pack(side=tk.RIGHT)
        
    def _add_group(self):
        title = self.group_title.get().strip()
        description = self.group_description.get("1.0", tk.END).strip()
        group_type = self.group_type_var.get()
        
        if not title:
            messagebox.showerror("Error", "Group title is required!")
            return
            
        self.result = {
            "title": title,
            "description": description,
            "group_type": group_type,
            "buttons": []
        }
        
        self.dialog.destroy()
        
    def _cancel(self):
        self.dialog.destroy()

class App(tk.Tk):
    def __init__(self, config_path='config.json'):
        super().__init__()
        
        # Переменная для хранения процесса xterm/screen
        self.screen_process = None
        self.current_unit_type = None
        self.buttons_frame = None
        self.config_path = config_path

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

    def _save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save config file: {e}")
            return False

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

        # Add command button
        tk.Button(top_frame, text="+ Add Command", command=self._add_command_dialog,
                 bg="#4CAF50", fg="white", font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=(0, 10))
        
        # Add group button
        tk.Button(top_frame, text="+ Add Group", command=self._add_group_dialog,
                 bg="#2196F3", fg="white", font=("Helvetica", 9)).pack(side=tk.RIGHT, padx=(0, 10))

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

    def _add_command_dialog(self):
        """Open dialog to add a new command button"""
        if not self.current_unit_type:
            messagebox.showwarning("Warning", "Please select a unit type first!")
            return
            
        # Get available groups for the current unit type
        unit_config = self.config['unit_types'].get(self.current_unit_type, {})
        button_groups = unit_config.get('button_groups', [])
        
        if not button_groups:
            messagebox.showwarning("Warning", "No button groups available. Please add a group first!")
            return
            
        # Create a simple dialog to select group and add command
        group_dialog = tk.Toplevel(self)
        group_dialog.title("Select Button Group")
        group_dialog.geometry("300x200")
        group_dialog.transient(self)
        group_dialog.grab_set()
        
        # Center the dialog
        group_dialog.update_idletasks()
        x = (group_dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (group_dialog.winfo_screenheight() // 2) - (200 // 2)
        group_dialog.geometry(f"300x200+{x}+{y}")
        
        main_frame = tk.Frame(group_dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Select group to add command:", font=("Helvetica", 10, "bold")).pack(pady=(0, 15))
        
        group_var = tk.StringVar(value=button_groups[0]['title'])
        for group in button_groups:
            tk.Radiobutton(main_frame, text=group['title'], variable=group_var, 
                          value=group['title']).pack(anchor="w", pady=2)
        
        def open_add_command():
            selected_group = group_var.get()
            group_dialog.destroy()
            
            # Find the group index and determine its type
            group_index = next((i for i, g in enumerate(button_groups) if g['title'] == selected_group), 0)
            selected_group_data = button_groups[group_index]
            
            # Determine group type based on existing buttons or group title
            group_type = self._determine_group_type(selected_group_data)
            
            # Open the add command dialog
            dialog = AddCommandDialog(self, self.current_unit_type, selected_group, group_type)
            self.wait_window(dialog.dialog)
            
            if dialog.result:
                self._add_command_to_group(group_index, dialog.result)
        
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(button_frame, text="Continue", command=open_add_command,
                 bg="green", fg="white", width=15).pack(side=tk.RIGHT, padx=(10, 0))
        tk.Button(button_frame, text="Cancel", command=group_dialog.destroy,
                 bg="red", fg="white", width=15).pack(side=tk.RIGHT, padx=(0, 0))

    def _determine_group_type(self, group_data):
        """Determine if a group is for serial or local commands"""
        # Check if group has a type specified
        if 'group_type' in group_data:
            return group_data['group_type']
        
        # Check existing buttons to determine type
        buttons = group_data.get('buttons', [])
        if buttons:
            # If any button has send_to_serial action, it's a serial group
            if any(btn.get('action') == 'send_to_serial' for btn in buttons):
                return 'serial'
            # If any button has run_local_command action, it's a local group
            elif any(btn.get('action') == 'run_local_command' for btn in buttons):
                return 'local'
        
        # Default based on group title
        title_lower = group_data['title'].lower()
        if 'serial' in title_lower or 'command' in title_lower:
            return 'serial'
        elif 'local' in title_lower or 'bash' in title_lower or 'terminal' in title_lower:
            return 'local'
        else:
            # Default to serial for unknown groups
            return 'serial'

    def _add_group_dialog(self):
        """Open dialog to add a new button group"""
        if not self.current_unit_type:
            messagebox.showwarning("Warning", "Please select a unit type first!")
            return
            
        dialog = AddGroupDialog(self, self.current_unit_type)
        self.wait_window(dialog.dialog)
        
        if dialog.result:
            self._add_button_group(dialog.result)

    def _add_command_to_group(self, group_index, command_data):
        """Add a new command to an existing button group"""
        try:
            # Add the command to the config
            self.config['unit_types'][self.current_unit_type]['button_groups'][group_index]['buttons'].append(command_data)
            
            # Save the config
            if self._save_config():
                # Recreate buttons to show the new command
                self._recreate_buttons()
                self.log(f"Added new command '{command_data['text']}' to group '{self.config['unit_types'][self.current_unit_type]['button_groups'][group_index]['title']}'", "SUCCESS")
            else:
                messagebox.showerror("Error", "Failed to save configuration!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add command: {e}")

    def _add_button_group(self, group_data):
        """Add a new button group to the current unit type"""
        try:
            # Add the new group to the config
            self.config['unit_types'][self.current_unit_type]['button_groups'].append(group_data)
            
            # Save the config
            if self._save_config():
                # Recreate buttons to show the new group
                self._recreate_buttons()
                self.log(f"Added new button group '{group_data['title']}'", "SUCCESS")
            else:
                messagebox.showerror("Error", "Failed to save configuration!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add button group: {e}")

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