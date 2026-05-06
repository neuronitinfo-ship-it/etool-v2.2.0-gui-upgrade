# v2master Android Servicing Toolkit

A combined ADB and EDL-based Android servicing platform with a modern web-based UI.

## What this repo contains

- `unlock_tool/`: Main portable tool with **modern React/TypeScript web-based UI** for ADB-based unlocking, FRP bypass, bootloader unlock, screen lock removal, and firmware operations.
- `src/`: React/TypeScript components for the visionOS-inspired web interface
- `public/`: Assets and static files for the web UI
- `Tools/`: EDL helper scripts from the `edl-master` project for Qualcomm and MediaTek service modes
- `Drivers/`: Linux udev rules and driver configuration for USB/EDL device access

## New Web-Based UI

The project now uses a **modern React/Vite web interface** with:
- ✨ Responsive, component-based design (Tailwind CSS)
- 🎨 Light/dark theme support
- 🔧 Real-time device detection and status
- 📱 Mobile-friendly interface
- 🚀 Hot module reloading for development

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for web UI)
- npm or yarn

### 1. Setup Python Environment
```bash
cd unlock_tool
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Linux Rules (Linux/macOS only)
```bash
sudo cp ../Drivers/*.rules /etc/udev/rules.d/
sudo cp ../Drivers/blacklist-qcserial.conf /etc/modprobe.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 3. Run the Application

**Development Mode (with hot reload):**
```bash
cd unlock_tool
python main.py --dev
# Frontend available at http://localhost:5173
```

**Production Mode:**
```bash
cd unlock_tool
python main.py --prod
# Frontend available at http://localhost:3000
```

**Test Device Detection:**
```bash
python main.py --test-device
```

## Web UI Features

- **Device Selector**: Search and filter connected devices by brand, model, and features
- **Status Dashboard**: Real-time connection status, operation progress, and queue management
- **Operation History**: Timestamped logs with color-coded status indicators
- **Theme Management**: Switch between light and dark modes
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Building for Production

### Build Frontend
```bash
cd unlock_tool
npm run build
```

### Create Standalone Executable (Windows)
```bash
# Use PyInstaller to bundle Python backend + web frontend
python build_windows.bat
```

## Project Structure

```
unlock_tool/
├── src/                    # React/TypeScript source
│   ├── components/        # Reusable UI components
│   ├── pages/            # Page components
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utility functions
│   ├── App.tsx           # Main React app
│   └── main.tsx          # Entry point
├── public/               # Static assets
├── core/                 # Python backend services
├── database/             # Device profiles and configs
├── modules/              # Feature modules
├── index.html            # HTML template
├── package.json          # Node dependencies
├── vite.config.ts        # Vite configuration
├── tailwind.config.ts    # Tailwind CSS config
├── main.py               # Python entry point
└── requirements.txt      # Python dependencies
```

## Windows Deployment

The project includes Windows build support:
- **Portable executable**: Run without installation
- **System requirements**: Windows 10/11 64-bit, administrator privileges
- **Key features**: FRP bypass, bootloader unlock, IMEI repair, screen lock bypass, device recovery
- **Build files**: `build_windows.bat` for automated packaging

## Technology Stack

### Backend
- Python 3.9+
- ADB/Fastboot APIs
- EDL protocol support

### Frontend
- React 18+
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui components

## Notes

- `unlock_tool/` is the active development framework
- `Tools/` contains legacy EDL scripts for low-level Qualcomm flashing
- The web UI provides a modern, responsive alternative to the legacy PyQt6 interface
- All device profiles and configurations are JSON-based in `database/`
- Use `unlock_tool/INSTALLATION.md` for detailed setup guidance

## Migration from v2.1.0

If you're upgrading from the previous PyQt6 GUI version:
- The old GUI files have been removed
- All backend logic remains compatible
- Device profiles and configurations are unchanged
- API endpoints are backward compatible
