#!/usr/bin/env python3
"""
eTool v2.2.0 - Mobile Device Unlock Tool
Web-based API server for device servicing operations

This module serves as the backend API for the web-based GUI.
Run this server and access the frontend at http://localhost:5173 (dev) or http://localhost:3000 (prod)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.device_detector import DeviceDetector
from core.license_manager import LicenseManager
from core.logger import setup_logger

# Setup logging
logger = setup_logger("etool-server")

def start_development_server():
    """Start the development server with Vite"""
    logger.info("Starting eTool v2.2.0 web development server...")
    logger.info("Frontend: http://localhost:5173")
    logger.info("Press Ctrl+C to stop")
    
    try:
        import subprocess
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
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def start_production_server():
    """Start the production server"""
    logger.info("Starting eTool v2.2.0 web production server...")
    logger.info("Frontend: http://localhost:3000")
    
    try:
        import subprocess
        # Build the frontend if not already built
        if not os.path.exists("dist"):
            logger.info("Building frontend...")
            subprocess.run(["npm", "run", "build"], check=True)
        
        # Serve the built frontend (using a simple HTTP server)
        logger.info("Serving production build...")
        subprocess.run([
            sys.executable, "-m", "http.server", "3000", 
            "--directory", "dist"
        ], check=False)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start production server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="eTool v2.2.0 - Mobile Device Unlock Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dev          # Start development server
  %(prog)s --prod         # Start production server
  %(prog)s --test-device  # Test device detection
        """
    )
    
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Start development server with hot reload (default)"
    )
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Start production server"
    )
    parser.add_argument(
        "--test-device",
        action="store_true",
        help="Test device detection"
    )
    
    args = parser.parse_args()
    
    # Default to dev mode
    if args.test_device:
        logger.info("Testing device detection...")
        detector = DeviceDetector()
        devices = detector.scan_devices()
        logger.info(f"Found {len(devices)} devices: {devices}")
    elif args.prod:
        start_production_server()
    else:
        # Default to dev
        start_development_server()