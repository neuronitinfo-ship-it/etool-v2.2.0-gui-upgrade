# v2master Android Servicing Toolkit

A combined ADB and EDL-based Android servicing platform.

## What this repo contains

- `unlock_tool/`: Main portable tool scaffold with GUI/CLI support for ADB-based unlocking, FRP bypass, bootloader unlock, screen lock removal, and firmware operations.
- `Tools/`: Copied EDL helper scripts from the original `edl-master` project for Qualcomm and MediaTek service modes.
- `Drivers/`: Linux udev rules and driver configuration files required for USB/EDL device access.

## Getting started

1. Create a Python virtual environment in `unlock_tool`:
   ```bash
   cd /home/tjms/Downloads/v2master/unlock_tool
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

2. Install Linux rules:
   ```bash
   sudo cp ../Drivers/*.rules /etc/udev/rules.d/
   sudo cp ../Drivers/blacklist-qcserial.conf /etc/modprobe.d/
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

3. Run the unlock tool (portable version):
   ```bash
   cd unlock_tool
   # On Linux/macOS
   ./setup.sh  # One-time setup
   ./run.sh --gui
   
   # On Windows
   setup.bat
   run.bat --gui
   ```

## Windows Summary

This repository includes a portable Windows-ready unlock tool with a self-contained GUI and optional standalone build package.

- **Portable execution**: Run from an extracted folder without installation
- **System requirements**: Windows 10/11 64-bit, administrator privileges recommended
- **Main executable**: `unlock_tool.exe` in the Windows portable package
- **Quick start**:
  1. Extract the Windows ZIP package
  2. Run `unlock_tool.exe`
  3. Connect the device and use the Auto Exploit or device-specific tabs
- **Driver support**: Includes Windows driver guidance and EDL-ready USB driver packages
- **Key Windows features**: FRP bypass, bootloader unlock, IMEI repair, screen lock bypass, and device recovery utilities
- **Build files included**: `build_windows.ps1`, `build_windows.bat`, and PyInstaller spec files for creating a standalone Windows app

For full Windows instructions, see `unlock_tool/README_Windows.md`.

## Notes

- `unlock_tool` is the active service framework for this repo.
- `Tools/` retains legacy EDL scripts and loader utilities for integration with Qualcomm low-level flashing.
- The portable version includes bundled Python interpreters for true plug-and-play usage.
- Use `unlock_tool/INSTALLATION.md` for detailed setup guidance.
