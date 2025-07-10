# SUMO Helper

A web-based traffic simulation tool that integrates OpenStreetMap (OSM) data with SUMO (Simulation of Urban MObility). This application provides an intuitive interface for selecting map areas, converting OSM data to SUMO format, configuring simulations, and monitoring results.

## Features

- **Interactive Map Selection**: Select areas on OpenStreetMap for traffic simulation
- **OSM to SUMO Conversion**: Automatically convert OSM road networks to SUMO format
- **Network Visualization**: Visualize road networks with nodes and edges
- **Export Capabilities**: Export networks in various formats
- **File Upload**: Upload existing SUMO network files
- **Simulation Framework**: Skeleton for future simulation implementation (not yet implemented)

## Architecture

- **Backend**: FastAPI with Python 3.11
- **Frontend**: React with Vite, Tailwind CSS, and DaisyUI
- **Map Integration**: OpenStreetMap with Leaflet
- **Traffic Simulation**: SUMO (Simulation of Urban MObility)
- **Data Processing**: OSMnx for OSM data handling

## Prerequisites

- Python 3.11+
- Node.js 18+
- SUMO 1.16.0+
- Docker (for production deployment)

## Installation

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/sumo-helper.git
   cd sumo-helper
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Install SUMO**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install sumo sumo-tools sumo-doc
   
   # macOS
   brew install sumo
   
   # Windows
   # Download from https://sumo.dlr.de/docs/Downloads.php
   ```

5. **Start the application**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

### Production Deployment

#### Using Docker Compose (Recommended)

1. **Clone and navigate to the project**
   ```bash
   git clone https://github.com/your-username/sumo-helper.git
   cd sumo-helper
   ```

2. **Set environment variables**
   ```bash
   export ENVIRONMENT=production
   export ALLOWED_ORIGINS=https://yourdomain.com
   ```

3. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

#### Manual Production Setup

1. **Backend Production Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   export ENVIRONMENT=production
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Frontend Production Build**
   ```bash
   cd frontend
   npm run build
   # Serve the dist folder with a web server like nginx
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Application environment | `development` | No |
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `SECRET_KEY` | Secret key for security | `your-secret-key-change-in-production` | No |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5173` | No |
| `SUMO_HOME` | SUMO installation path | `/usr/share/sumo` | No |
| `OSM_TIMEOUT` | OSM download timeout (seconds) | `30` | No |
| `OSM_MAX_AREA_SIZE` | Maximum selectable area size | `0.01` | No |

### Configuration Files

- `backend/config.py`: Backend configuration settings
- `frontend/vite.config.js`: Frontend build configuration
- `docker-compose.yml`: Docker deployment configuration

## Usage

### 1. Map Selection

1. Navigate to the home page
2. Use the map interface to select an area for simulation
3. Choose a location with main roads (highways, primary roads)
4. Click "Select Area" to download OSM data

### 2. Network Conversion

1. After selecting an area, click "Convert to SUMO"
2. Wait for the conversion process to complete
3. Review the network statistics

### 3. Network Analysis

1. Navigate to the Network Editor
2. Visualize the road network
3. Select entry and exit points for traffic simulation
4. Configure routes between selected points

### 4. Simulation Configuration (Not Implemented)

1. Set simulation parameters (duration, vehicle types, etc.)
2. Configure traffic flows and routing
3. Start the simulation

### 5. Monitoring (Not Implemented)

1. Monitor simulation progress in real-time
2. View traffic flow and congestion
3. Analyze simulation results
4. Export results for further analysis

**Note**: Simulation and monitoring features are currently skeleton implementations and will be fully implemented in future updates.

## API Documentation

The backend provides a RESTful API with the following main endpoints:

- `POST /api/maps/select-area`: Select map area and download OSM data
- `POST /api/maps/convert-to-sumo/{map_id}`: Convert OSM data to SUMO format
- `GET /api/networks/{network_id}`: Get network data for visualization
- `POST /api/networks/{network_id}/routes`: Configure routes
- `POST /api/simulations/configure`: Configure simulation parameters (skeleton - not implemented)
- `POST /api/simulations/start/{simulation_id}`: Start simulation (skeleton - not implemented)
- `GET /api/simulations/{simulation_id}/status`: Get simulation status (skeleton - not implemented)
- `GET /api/simulations/{simulation_id}/results`: Get simulation results (skeleton - not implemented)

Full API documentation is available at `/docs` when the backend is running.

## Development

### Project Structure

```
sumo-helper/
├── backend/
│   ├── services/
│   │   ├── osmnx_service.py      # OSM data processing
│   │   ├── map_service.py        # Network data handling
│   │   └── simulation_service.py # Simulation management
│   ├── models/
│   │   └── schemas.py            # Pydantic models
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration settings
│   └── requirements.txt          # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Page components
│   │   ├── lib/                  # Utilities
│   │   └── App.jsx               # Main application
│   ├── package.json              # Node.js dependencies
│   └── vite.config.js            # Build configuration
├── docker-compose.yml            # Docker deployment
└── README.md                     # This file
```

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 .
black .
isort .

# Frontend linting
cd frontend
npm run lint
npm run format
```

## Troubleshooting

### Common Issues

1. **OSM Download Timeout**
   - Select a smaller area
   - Check internet connection
   - Try a different location

2. **SUMO Network Validation Errors**
   - Ensure SUMO is properly installed
   - Check network file format
   - Verify coordinate system

3. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

4. **Docker Deployment Issues**
   - Check Docker and Docker Compose versions
   - Verify port availability
   - Check container logs

### Logs

- Backend logs: `backend/sumo_helper.log`
- Docker logs: `docker-compose logs -f [service-name]`
- Frontend logs: Browser developer console

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting section

## Acknowledgments

- [SUMO](https://sumo.dlr.de/) - Simulation of Urban MObility
- [OpenStreetMap](https://www.openstreetmap.org/) - Open map data
- [OSMnx](https://osmnx.readthedocs.io/) - Python library for OSM data
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - JavaScript library for user interfaces 