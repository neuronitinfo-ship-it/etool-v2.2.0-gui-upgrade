#!/usr/bin/env python3
"""
eTool v2.2.0 - Mobile Device Unlock Tool
Command-line tool for device servicing operations.

This is a functional CLI tool with optional web UI for interactive use.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.device_detector import DeviceDetector
from core.logger import setup_logger
from core.adb_interface import ADBInterface
from core.fastboot_interface import FastbootInterface

# Setup logging
logger = setup_logger("etool")

def detect_devices():
    """Detect connected devices"""
    logger.info("Scanning for devices...")
    detector = DeviceDetector(logger)
    device = detector.detect_device()
    
    if device:
        logger.info(f"✓ Device detected: {device['platform']} ({device['mode']})")
        if 'model' in device:
            logger.info(f"  Model: {device['model']}")
        if 'serial' in device:
            logger.info(f"  Serial: {device['serial']}")
        return device
    else:
        logger.warning("✗ No device detected")
        return None

def list_devices():
    """List all connected devices"""
    logger.info("Listing connected devices...")
    detector = DeviceDetector(logger)
    
    adb_interface = ADBInterface(logger)
    if adb_interface.adb_path:
        adb_devices = adb_interface.get_devices()
        if adb_devices:
            logger.info("ADB Devices:")
            for device in adb_devices:
                logger.info(f"  - {device['serial']} ({device['state']})")
    
    fastboot_interface = FastbootInterface(logger)
    if fastboot_interface.fastboot_path:
        fastboot_devices = fastboot_interface.get_devices()
        if fastboot_devices:
            logger.info("Fastboot Devices:")
            for device in fastboot_devices:
                logger.info(f"  - {device['serial']} ({device['state']})")

def get_device_info(serial):
    """Get detailed device information"""
    logger.info(f"Getting device info for {serial}...")
    adb = ADBInterface(logger)
    result = adb.run_command(['shell', 'getprop'], device=serial, timeout=10)
    
    if result[0] == 0:
        logger.info("Device Properties:")
        for line in result[1].splitlines()[:10]:  # Show first 10 properties
            if ': [' in line:
                logger.info(f"  {line}")
    else:
        logger.error(f"Failed to get device info: {result[1]}")

def start_web_ui():
    """Start the web UI server"""
    logger.info("Starting eTool v2.2.0 web interface...")
    logger.info("Frontend: http://localhost:5173 (dev) or http://localhost:3000 (prod)")
    
    try:
        import subprocess
        
        # Install dependencies if needed
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"
        ], check=False)
        
        # Install Node dependencies if needed
        if not os.path.exists("node_modules"):
            logger.info("Installing Node dependencies...")
            subprocess.run(["npm", "install"], check=False)
        
        # Start Vite dev server
        logger.info("Starting Vite development server...")
        subprocess.run(["npm", "run", "dev"], check=False)
    except KeyboardInterrupt:
        logger.info("Web UI stopped by user")
    except Exception as e:
        logger.error(f"Failed to start web UI: {e}")
        sys.exit(1)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="eTool v2.2.0 - Mobile Device Unlock Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Device Operations:
  %(prog)s detect              # Detect connected devices
  %(prog)s list                # List all devices
  %(prog)s info <serial>       # Get device information
  
Web Interface:
  %(prog)s ui                  # Start web UI server
  
Examples:
  %(prog)s detect              # Auto-detect device
  %(prog)s list                # Show connected devices
  %(prog)s info emulator-5554  # Get device details
  %(prog)s ui                  # Launch web interface
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Device detection
    detect_parser = subparsers.add_parser('detect', help='Detect connected devices')
    
    # List devices
    list_parser = subparsers.add_parser('list', help='List all connected devices')
    
    # Device info
    info_parser = subparsers.add_parser('info', help='Get device information')
    info_parser.add_argument('serial', help='Device serial number')
    
    # Web UI
    ui_parser = subparsers.add_parser('ui', help='Start web UI server')
    
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'detect':
        detect_devices()
    elif args.command == 'list':
        list_devices()
    elif args.command == 'info':
        get_device_info(args.serial)
    elif args.command == 'ui':
        start_web_ui()
    else:
        # Default: detect devices
        detect_devices()

if __name__ == "__main__":
    main()