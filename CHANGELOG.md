# Changelog

All notable changes to SUMO Helper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production-ready Docker configuration
- Comprehensive documentation in English
- MIT License
- Contributing guidelines
- Changelog tracking
- Improved security with non-root users
- Health checks for all services
- Multi-stage Docker builds for optimization

### Changed
- Updated README with professional FOSS repository structure
- Removed nginx dependency for simplified deployment
- Improved Docker Compose configuration
- Enhanced error handling and logging
- Better environment variable management

### Fixed
- Docker volume permissions
- Health check configurations
- Build optimization issues

## [1.0.0]

### Added
- Initial release of SUMO Helper
- Interactive map selection from OpenStreetMap
- Automatic OSM to SUMO conversion
- Visual network editor with entry/exit point configuration
- Vehicle distribution management
- Complete simulation export with ZIP packages
- Simulation reconstruction from JSON metadata
- Real-time WebSocket communication
- Modern React-based web interface
- FastAPI backend with comprehensive API
- Docker support for easy deployment

### Features
- **Map Selection**: Select areas from OpenStreetMap to create traffic networks
- **Network Conversion**: Convert OSM data to SUMO-compatible format
- **Visual Editor**: Configure network parameters and traffic flow
- **Simulation Export**: Generate complete simulation packages
- **Metadata Reconstruction**: Load and modify previous simulations
- **Real-time Updates**: Live progress updates during processing

### Technical Stack
- **Backend**: FastAPI, OSMnx, SUMO, Pydantic
- **Frontend**: React 18, Vite, Leaflet, Tailwind CSS
- **Deployment**: Docker, Docker Compose
- **Communication**: WebSockets, REST API

---

## Version History

- **1.0.0**: Initial release with core functionality
- **Unreleased**: Production preparation and documentation improvements

## Migration Guide

### From Development to Production

1. **Update Docker Compose**: Use the new production-ready configuration
2. **Environment Variables**: Review and set appropriate production values
3. **Volume Permissions**: Ensure proper file permissions for data persistence
4. **Health Checks**: Monitor service health with the new health check endpoints

### Breaking Changes

None in current version.

### Deprecations

None in current version.

---

For detailed information about each release, see the [GitHub releases page](https://github.com/gsmkev/sumo-helper/releases). 
