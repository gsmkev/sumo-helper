# SUMO Helper

A web-based traffic simulation tool with OSM integration that allows users to select map areas, convert them to SUMO format, and export complete simulation packages.

## Features

### 🗺️ Map Selection & OSM Integration
- Select custom areas on OpenStreetMap
- Download and process OSM road network data
- Convert OSM data to SUMO-compatible format
- Preview selected areas with interactive maps

### 🌐 Network Analysis
- Extract network data (nodes, edges, coordinates)
- Identify entry and exit points automatically
- Configure routes between entry and exit points
- Support for multiple vehicle types

### 🚗 Simulation Export
- **NEW**: Export complete SUMO simulation packages
- Generate SUMO-compatible files (nodes.nod.xml, edges.edg.xml, routes.rou.xml, simulation.sumocfg)
- **NEW**: Include traffic lights (automatically detected from OSM data and converted to SUMO format)
- **NEW**: Support for secondary streets (tertiary, residential, service roads)
- **NEW**: Increased export area to 1km x 1km
- Include Python execution script for independent simulation
- ZIP package with all necessary files
- Compatible with SUMO 1.8.0+ and follows the same format as `simple_network_robust_gui.py`

### 📊 Simulation Management
- Configure simulation parameters
- Monitor simulation progress
- View simulation results and statistics
- Export simulation data

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- SUMO (for running exported simulations)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sumo-helper
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

1. **Start the backend**
   ```bash
   cd backend
   source venv/bin/activate
   python3 main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   The web interface will be available at `http://localhost:5173`

## Usage

### 1. Select a Map Area
- Navigate to the Map Selection page
- Choose a location or draw a custom area
- The system will download OSM data for the selected area

### 2. Convert to SUMO Format
- Click "Convert to SUMO" to generate a SUMO network
- The system will create a `.net.xml` file compatible with SUMO

### 3. Configure Simulation
- Navigate to the Simulation Configuration page
- Review the network data and entry/exit points
- Configure simulation parameters

### 4. Export Simulation
- Click "Export Simulation" to download a complete simulation package
- The ZIP file contains:
  - `nodes.nod.xml` - SUMO nodes definition
  - `edges.edg.xml` - SUMO edges definition
  - `traffic_lights.add.xml` - Traffic lights configuration (detected from OSM data)
  - `routes.rou.xml` - Vehicle routes and flows
  - `simulation.sumocfg` - SUMO configuration
  - `run_simulation.py` - Python script to execute the simulation

### 5. Run the Simulation
```bash
# Extract the downloaded ZIP file
unzip simulation_*.zip

# Run the simulation
python3 run_simulation.py
```

## API Endpoints

### Map Management
- `POST /api/maps/select-area` - Select map area
- `GET /api/maps/preview/{map_id}` - Get map preview
- `POST /api/maps/convert-to-sumo/{map_id}` - Convert to SUMO format

### Network Analysis
- `GET /api/networks/{network_id}` - Get network data
- `GET /api/networks/{network_id}/entry-points` - Get entry points
- `GET /api/networks/{network_id}/exit-points` - Get exit points
- `POST /api/networks/{network_id}/routes` - Configure routes

### Simulation Export
- `POST /api/simulations/export/{network_id}` - Export simulation package
- `GET /api/simulations/download/{filename}` - Download exported file

### Vehicle Types
- `GET /api/vehicle-types` - Get available vehicle types

## Architecture

### Backend (FastAPI)
- **MapService**: Handles network data processing and analysis
- **OSMNXService**: Manages OSM data download and conversion
- **SimulationService**: Manages simulation configuration and execution
- **SUMOExportService**: Generates SUMO-compatible simulation files

### Frontend (React + Vite)
- **MapSelection**: Interactive map area selection
- **NetworkEditor**: Network visualization and analysis
- **SimulationConfig**: Simulation parameter configuration
- **SimulationMonitor**: Real-time simulation monitoring

## File Structure
```
sumo-helper/
├── backend/
│   ├── services/
│   │   ├── map_service.py
│   │   ├── osmnx_service.py
│   │   ├── simulation_service.py
│   │   └── sumo_export_service.py
│   ├── models/
│   │   └── schemas.py
│   ├── static/
│   │   ├── maps/
│   │   ├── networks/
│   │   └── exports/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── MapSelection.jsx
│   │   │   ├── NetworkEditor.jsx
│   │   │   ├── SimulationConfig.jsx
│   │   │   └── SimulationMonitor.jsx
│   │   └── components/
│   └── package.json
└── README.md
```

## Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python3 main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Testing
```bash
# Backend tests
cd backend
python3 -m pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [SUMO](https://sumo.dlr.de/) - Simulation of Urban MObility
- [OSMnx](https://osmnx.readthedocs.io/) - Python package for working with OpenStreetMap
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [React](https://reactjs.org/) - JavaScript library for building user interfaces 