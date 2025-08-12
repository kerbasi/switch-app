# 🚀 Port Control Interface

A professional, dynamic network equipment management interface built with Python and Tkinter. This application provides an intuitive way to manage network switches, routers, and servers through serial connections and local command execution.

## ✨ Features

### 🎯 **Dynamic Unit Management**

- **Multiple Unit Types**: Support for Switch, Router, and Server configurations
- **Smart Button Loading**: Interface automatically adapts based on selected unit type
- **Real-time Updates**: Changes reflect immediately in the interface

### 🎨 **Visual Customization**

- **Visual Color Picker**: Built-in color chooser with preview squares
- **Button Styling**: Customize background and text colors for any button
- **Professional Interface**: Clean, organized layout with visual feedback

### ⚙️ **Dynamic Configuration**

- **Add Commands**: Create new command buttons on-the-fly
- **Add Groups**: Organize commands into logical button groups
- **Persistent Storage**: All changes automatically saved to configuration
- **No Manual Editing**: Full customization through the user interface

### 🔧 **Command Execution**

- **Serial Communication**: Send commands to network equipment via serial port
- **Local Commands**: Execute commands on the local machine
- **Screen Management**: Open/close interactive terminal sessions
- **Real-time Logging**: Comprehensive command output logging

### 📱 **User Experience**

- **Intuitive Interface**: Easy-to-use dialogs and controls
- **Responsive Design**: Adapts to different screen sizes
- **Status Updates**: Real-time feedback on all operations
- **Error Handling**: Graceful error handling with user notifications

## 🏗️ Architecture

```
Port Control Interface
├── Unit Type Selection (Switch/Router/Server)
├── Dynamic Button Groups
│   ├── Screen Control
│   ├── Serial Commands
│   ├── Local Commands
│   └── Custom Groups
├── Visual Color Picker
├── Configuration Management
└── Real-time Logging
```

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- Tkinter (usually included with Python)
- Serial port access (for network equipment communication)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd switch-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python App.py
```

### Dependencies

```bash
pip install pyserial  # For serial communication
```

## 📖 Usage

### 1. **Select Unit Type**

- Choose from the dropdown: Switch, Router, or Server
- Interface automatically loads appropriate button configurations

### 2. **Add New Commands**

- Click **"+ Add Command"** button
- Select target button group
- Fill in button details:
  - Button text
  - Command to execute
  - Custom colors (optional)
- Command type automatically determined by group context

### 3. **Add New Groups**

- Click **"+ Add Group"** button
- Enter group title and description
- Choose group type (Serial or Local Commands)
- Organize commands logically

### 4. **Customize Appearance**

- Use the visual color picker for button styling
- Preview colors before applying
- System color chooser integration

### 5. **Execute Commands**

- Click any button to execute its associated command
- Monitor output in the real-time log window
- View status updates in the status bar

## ⚙️ Configuration

### Settings File (`config.json`)

```json
{
  "settings": {
    "serial_device": "/dev/ttyS0",
    "serial_baudrate": "115200",
    "default_ip_address": "192.168.10.20"
  },
  "unit_types": {
    "Switch": {
      "description": "Network Switch Configuration",
      "button_groups": [...]
    }
  }
}
```

### Configuration Structure

- **Settings**: Serial port configuration and default values
- **Unit Types**: Equipment-specific button configurations
- **Button Groups**: Organized command categories
- **Buttons**: Individual command definitions with styling

## 🔌 Serial Communication

### Supported Platforms

- **Windows**: COM ports (COM1, COM2, etc.)
- **Linux/Unix**: `/dev/ttyS*`, `/dev/ttyUSB*`
- **macOS**: `/dev/tty.*` devices

### Terminal Applications

- **Windows**: PuTTY (automatic detection)
- **Linux/Unix**: xterm + screen
- **Fallback**: System default terminal

## 🎨 Customization Examples

### Adding a Custom Command

```python
# Example: Add a network diagnostic command
{
  "text": "Ping Gateway",
  "action": "send_to_serial",
  "command": "ping -c 4 192.168.1.1",
  "style": {
    "bg": "#4CAF50",
    "fg": "white"
  }
}
```

### Creating a Custom Group

```python
# Example: Network Diagnostics group
{
  "title": "Network Diagnostics",
  "description": "Network troubleshooting commands",
  "group_type": "serial",
  "buttons": [...]
}
```

## 🚨 Troubleshooting

### Common Issues

#### Serial Port Not Found

- Check device permissions
- Verify port exists in device manager
- Ensure no other application is using the port

#### PuTTY Not Found (Windows)

- Install PuTTY from official website
- Add PuTTY to system PATH
- Restart the application

#### Permission Denied (Linux)

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Debug Mode

- Check the log window for detailed error messages
- Verify configuration file syntax
- Ensure all required dependencies are installed

## 🔧 Development

### Project Structure

```
switch-app/
├── App.py              # Main application
├── config.json         # Configuration file
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Key Classes

- **App**: Main application window and logic
- **AddCommandDialog**: Command creation interface
- **AddGroupDialog**: Group creation interface

### Extending Functionality

- Add new unit types in `config.json`
- Implement new action types in button handlers
- Customize dialog layouts and styling

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the configuration examples

## 🎯 Roadmap

- [ ] Network device auto-discovery
- [ ] Command templates and presets
- [ ] Multi-language support
- [ ] Plugin system for custom actions
- [ ] Cloud configuration sync
- [ ] Mobile-responsive web interface

---

**Built with ❤️ for network administrators and technicians**

_Simplify your network management workflow with this powerful, customizable interface._
