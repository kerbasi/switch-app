# Switch Control App

A Python GUI application for controlling network switches and devices via RS-232 serial communication. This app provides an intuitive interface for sending commands to devices through serial ports, with support for interactive terminal sessions and local command execution.

## Features

- **Serial Communication**: Direct RS-232 port control without pyserial dependency
- **Interactive Terminal**: Screen-based terminal sessions for real-time device interaction
- **GUI Interface**: User-friendly Tkinter-based interface with organized button groups
- **Configuration-Driven**: JSON-based configuration for easy customization
- **Multi-Platform**: Support for Linux and Windows systems
- **Threading**: Non-blocking GUI with threaded command execution
- **Error Handling**: Comprehensive error handling and user feedback

## Prerequisites

### Linux

- Python 3.6+
- `screen` command-line tool
- `xterm` terminal emulator
- Appropriate permissions for serial port access

### Windows

- Python 3.6+
- PuTTY or similar terminal emulator
- COM port access permissions

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed
3. Install required dependencies:
   ```bash
   pip install tkinter
   ```
   Note: tkinter is usually included with Python installations

## Configuration

The app uses `config.json` for configuration. Here's the structure:

```json
{
  "settings": {
    "serial_device": "/dev/ttyS0",
    "serial_baudrate": "115200",
    "default_ip_address": "192.168.10.20",
    "power_on_script_path": "/usr/flexfs/TechNvidia/",
    "power_on_script_name": "powerOnMoose.py"
  },
  "button_groups": [
    {
      "title": "Screen Control",
      "buttons": [
        {
          "text": "Open Screen",
          "action": "open_screen",
          "style": { "bg": "green", "fg": "white" }
        },
        {
          "text": "Close Screen",
          "action": "close_screen",
          "style": { "bg": "red", "fg": "white" }
        }
      ]
    }
  ]
}
```

### Configuration Options

- **serial_device**: Path to serial port (Linux: `/dev/ttyS0`, Windows: `COM1`)
- **serial_baudrate**: Baud rate for serial communication
- **default_ip_address**: Default IP address for network configuration
- **power_on_script_path**: Path to power management scripts
- **power_on_script_name**: Name of the power management script

## Usage

### Running the Application

```bash
python App.py
```

### Main Interface

The application provides three main sections:

1. **Screen Control**: Open/close interactive terminal sessions
2. **Serial Commands**: Send commands directly to the serial port
3. **Local Commands**: Execute commands on the local machine

### Button Actions

- **open_screen**: Opens an interactive terminal session using screen
- **close_screen**: Closes the active terminal session
- **send_to_serial**: Sends commands directly to the serial port
- **run_local_command**: Executes commands on the local system

### Example Commands

The app comes pre-configured with common switch management commands:

- Login as root
- Kill DHCP client
- Configure network interfaces
- Show network configuration
- Power management operations

## Serial Communication

The app uses direct file I/O for serial communication, avoiding pyserial for better BIOS-level control:

```python
# Commands are sent using:
echo 'command' > /dev/ttyS0
```

This approach provides:

- Direct device access
- Better control for BIOS menu navigation
- Reduced dependency overhead
- Faster command execution

## Platform Support

### Linux

- Serial ports: `/dev/ttyS0`, `/dev/ttyS1`, etc.
- Terminal: xterm + screen
- File permissions may be required for serial port access

### Windows

- Serial ports: `COM1`, `COM2`, etc.
- Terminal: PuTTY or Windows Terminal
- May require administrator privileges

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure you have access to the serial port

   ```bash
   sudo usermod -a -G dialout $USER
   ```

2. **Device Not Found**: Check if the serial port exists

   ```bash
   ls /dev/ttyS*
   ```

3. **Screen Not Starting**: Ensure screen is installed

   ```bash
   sudo apt-get install screen
   ```

4. **Commands Not Working**: Verify baud rate and device settings

### Debug Mode

Enable debug logging by checking the output window in the application. All commands and errors are logged there.

## Customization

### Adding New Commands

1. Edit `config.json`
2. Add new button configurations to appropriate groups
3. Use available actions: `send_to_serial`, `run_local_command`, `open_screen`, `close_screen`

### Styling Buttons

Use the `style` property to customize button appearance:

```json
{
  "text": "Custom Button",
  "action": "send_to_serial",
  "command": "custom_command",
  "style": { "bg": "blue", "fg": "white", "font": "Arial 12 bold" }
}
```

## Security Considerations

- The app executes commands with the same privileges as the user running it
- Serial port access may require elevated permissions
- Be cautious with commands that modify system settings
- Consider network security when configuring IP addresses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the configuration examples
3. Check system permissions and dependencies
4. Create an issue in the repository

---

**Note**: This application is designed for network administrators and technicians who need reliable RS-232 communication with network devices. Always ensure proper authorization before accessing network equipment.
