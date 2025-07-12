# SUMO Helper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)
[![SUMO](https://img.shields.io/badge/SUMO-1.16.0-orange.svg)](https://sumo.dlr.de/)

A modern web-based traffic simulation tool that integrates OpenStreetMap data with SUMO (Simulation of Urban MObility) for creating and managing traffic simulations.

## 🚀 Features

- **Interactive Map Selection**: Select areas from OpenStreetMap to create traffic networks
- **Automatic OSM to SUMO Conversion**: Convert OpenStreetMap data to SUMO-compatible format
- **Visual Network Editor**: Configure entry/exit points and traffic flow visually
- **Vehicle Distribution Management**: Configure different vehicle types and their percentages
- **Complete Simulation Export**: Generate ZIP packages with all necessary files
- **Simulation Reconstruction**: Load and modify previous simulations using JSON metadata
- **Modern Web Interface**: Intuitive React-based UI with interactive maps

## 🏗️ Architecture

```
sumo-helper/
├── backend/                 # FastAPI Python backend
│   ├── services/           # Business logic services
│   ├── models/             # Pydantic schemas
│   └── static/             # File storage
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application pages
│   │   └── utils/          # Utility functions
│   └── public/             # Static assets
└── docker-compose.yml      # Production deployment
```

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **OSMnx** - OpenStreetMap data processing
- **SUMO** - Traffic simulation engine
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **React Router** - Client-side routing
- **Leaflet** - Interactive maps
- **Tailwind CSS** - Styling
- **DaisyUI** - Component library

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **SUMO** (optional, for local simulation execution)

### Installing SUMO

```bash
# Ubuntu/Debian
sudo apt-get install sumo sumo-tools sumo-gui sumo-doc

# macOS
brew install sumo

# Windows
# Download from https://sumo.dlr.de/docs/Downloads.php
```

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/gsmkev/sumo-helper.git
   cd sumo-helper
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

1. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 📖 Usage Guide

### 1. Map Selection
- Navigate to the map selection page
- Choose a location or draw a custom area
- The system downloads OSM data for the selected area

### 2. Network Conversion
- Click "Convert to SUMO" to generate a SUMO network
- The system creates a `.net.xml` file compatible with SUMO

### 3. Simulation Configuration
- Navigate to the network editor
- Review network data and entry/exit points
- Configure simulation parameters

### 4. Export Simulation
- Click "Export Simulation" to download a complete package
- The ZIP file contains:
  - `nodes.nod.xml` - Network node definitions
  - `edges.edg.xml` - Network edge definitions
  - `routes.rou.xml` - Vehicle routes and flows
  - `simulation.sumocfg` - Simulation configuration
  - `traffic_lights.add.xml` - Traffic light definitions
  - `run_simulation.py` - Simulation execution script
  - `simulation_metadata.json` - Complete metadata for reconstruction

### 5. Run Simulation
```bash
# Extract the downloaded ZIP
unzip simulation_*.zip

# Run the simulation
python3 run_simulation.py
```

### 6. Load Previous Simulation
- Go to the map selection page
- Click "Load Simulation from File"
- Upload the complete simulation ZIP
- The application automatically extracts and loads the configuration

## 🔌 API Reference

### Map Management
- `POST /api/maps/select-area` - Select map area
- `GET /api/maps/preview/{map_id}` - Get map preview
- `POST /api/maps/convert-to-sumo/{map_id}` - Convert to SUMO format

### Network Analysis
- `GET /api/networks/{network_id}` - Get network data
- `GET /api/networks/{network_id}/entry-points` - Get entry points
- `GET /api/networks/{network_id}/exit-points` - Get exit points

### Simulation Management
- `POST /api/networks/{network_id}/routes` - Configure routes
- `POST /api/simulations/export/{network_id}` - Export simulation
- `GET /api/simulations/download/{filename}` - Download simulation files

### File Operations
- `POST /api/files/upload` - Upload files
- `POST /api/simulations/load-metadata` - Load simulation metadata

## 🐳 Docker Configuration

The application includes production-ready Docker configuration:

- **Multi-stage builds** for optimized image sizes
- **Non-root users** for security
- **Health checks** for monitoring
- **Volume persistence** for data storage
- **Environment-based configuration**

### Environment Variables

```bash
# Backend
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
SUMO_HOME=/usr/share/sumo
OSM_TIMEOUT=30
OSM_MAX_AREA_SIZE=0.01

# Frontend
VITE_API_URL=http://localhost:8000
```

## 🧪 Development

### Backend Development
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development dependencies
python main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
npm run lint
npm run build
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📁 Project Structure

```
sumo-helper/
├── backend/
│   ├── services/
│   │   ├── map_service.py          # Map and OSM processing
│   │   ├── simulation_service.py   # Simulation management
│   │   ├── osmnx_service.py        # OSM data handling
│   │   └── sumo_export_service.py  # SUMO file generation
│   ├── models/
│   │   └── schemas.py              # Pydantic data models
│   ├── static/                     # File storage
│   ├── main.py                     # FastAPI application
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable components
│   │   ├── pages/
│   │   │   ├── MapSelection.jsx    # Map selection interface
│   │   │   └── NetworkEditor.jsx   # Network configuration
│   │   ├── utils/                  # Utility functions
│   │   ├── App.jsx                 # Main application
│   │   └── main.jsx                # Application entry point
│   ├── public/                     # Static assets
│   └── package.json                # Node.js dependencies
├── docker-compose.yml              # Production deployment
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [SUMO](https://sumo.dlr.de/) - Traffic simulation framework
- [OpenStreetMap](https://www.openstreetmap.org/) - Map data
- [OSMnx](https://osmnx.readthedocs.io/) - OSM data processing
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [React](https://reactjs.org/) - UI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/gsmkev/sumo-helper/issues)
- **Discussions**: [GitHub Discussions](https://github.com/gsmkev/sumo-helper/discussions)
- **Documentation**: [Wiki](https://github.com/gsmkev/sumo-helper/wiki)

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

---

**Made with ❤️ for the traffic simulation community** 
