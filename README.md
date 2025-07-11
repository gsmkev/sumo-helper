# SUMO Helper

Una herramienta web para crear y gestionar simulaciones de tráfico con SUMO (Simulation of Urban MObility) usando datos de OpenStreetMap.

## Características

- **Selección de mapas**: Selecciona áreas de OpenStreetMap para crear redes de tráfico
- **Conversión automática**: Convierte datos OSM a formato SUMO compatible
- **Configuración visual**: Editor visual para configurar puntos de entrada/salida
- **Distribución de vehículos**: Configura diferentes tipos de vehículos y sus porcentajes
- **Exportación completa**: Genera paquetes ZIP con todos los archivos necesarios
- **Reconstrucción desde metadatos**: Carga simulaciones previas usando archivos JSON de metadatos
- **Interfaz web moderna**: Interfaz intuitiva con mapas interactivos

## Nueva Funcionalidad: Exportación con Metadatos JSON

### ¿Qué incluye el archivo JSON?

Cuando exportas una simulación, ahora se incluye un archivo `simulation_metadata.json` que contiene:

- **Información de la simulación**: Nombre, versión, fecha de creación
- **Datos completos de la red**: Todos los nodos con coordenadas (x, y, lat, lon), tipo, y si son puntos de entrada/salida
- **Configuración de aristas**: Conexiones entre nodos, velocidad, número de carriles
- **Configuración de simulación**: Número de vehículos, tiempo de simulación, semilla aleatoria
- **Distribución de vehículos**: Tipos de vehículos, porcentajes, colores
- **Puntos seleccionados**: Lista de puntos de entrada y salida elegidos
- **Rutas generadas**: Todas las rutas calculadas para los vehículos
- **Instrucciones de reconstrucción**: Pasos para recrear la simulación

### Cómo usar los metadatos para reconstruir

#### Opción 1: Interfaz Web
1. Ve a la página de selección de mapas
2. Haz clic en "Load Simulation from File"
3. Sube el archivo ZIP completo de la simulación exportada
4. La aplicación extraerá automáticamente el `simulation_metadata.json` y cargará toda la configuración
5. Puedes modificar y re-exportar la simulación

#### Opción 2: Análisis del JSON
1. Extrae el ZIP de la simulación
2. Abre el archivo `simulation_metadata.json`
3. Usa los datos para reconstruir la simulación programáticamente

### Estructura del archivo JSON

```json
{
  "simulation_info": {
    "name": "simulation_network_id",
    "created_at": 1234567890,
    "version": "1.0",
    "description": "SUMO simulation metadata for reconstruction"
  },
  "network_data": {
    "id": "network_id",
    "name": "network_name",
    "bounds": {"xmin": 0, "ymin": 0, "xmax": 100, "ymax": 100},
    "node_count": 50,
    "edge_count": 80
  },
  "nodes": [
    {
      "id": "node_1",
      "x": 10.5,
      "y": 20.3,
      "lat": 40.4168,
      "lon": -3.7038,
      "type": "priority",
      "is_entry_point": true,
      "is_exit_point": false
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "from": "node_1",
      "to": "node_2",
      "shape": [[40.4168, -3.7038], [40.4169, -3.7039]],
      "length": 100.0,
      "speed": 13.89,
      "lanes": 2
    }
  ],
  "simulation_config": {
    "total_vehicles": 100,
    "simulation_time": 3600,
    "random_seed": 12345,
    "vehicle_distribution": [
      {
        "vehicle_type": "car",
        "percentage": 70,
        "color": "yellow",
        "period": 0.45
      }
    ]
  },
  "selected_points": {
    "entry_points": ["node_1", "node_3"],
    "exit_points": ["node_10", "node_15"]
  },
  "routes": [
    {
      "id": "route_car_1",
      "edges": "edge_1 edge_2 edge_5",
      "vehicle_type": "car",
      "depart_time": 0.0,
      "color": "yellow"
    }
  ],
  "reconstruction_info": {
    "instructions": "Para reconstruir esta simulación:",
    "steps": [
      "1. Cargar el archivo simulation_metadata.json",
      "2. Usar los datos de nodes y edges para recrear la red",
      "3. Aplicar la configuración de simulación",
      "4. Configurar los puntos de entrada y salida seleccionados",
      "5. Aplicar la distribución de vehículos",
      "6. Generar las rutas basadas en los datos de routes"
    ]
  }
}
```

## Instalación

### Prerrequisitos

- Python 3.8+
- Node.js 16+
- SUMO (opcional, para ejecutar simulaciones localmente)

### Instalación de SUMO

```bash
# Ubuntu/Debian
sudo apt-get install sumo sumo-tools sumo-gui sumo-doc

# macOS
brew install sumo

# Windows
# Descarga desde https://sumo.dlr.de/docs/Downloads.php
```

### Configuración del proyecto

1. **Clona el repositorio**
   ```bash
   git clone <repository-url>
   cd sumo-helper
   ```

2. **Instala dependencias del backend**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

3. **Instala dependencias del frontend**
   ```bash
   cd ../frontend
   npm install
   ```

## Uso

### 1. Inicia los servicios

1. **Backend**
   ```bash
   cd backend
   source venv/bin/activate
   python3 main.py
   ```
   La API estará disponible en `http://localhost:8000`

2. **Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   La interfaz web estará disponible en `http://localhost:5173`

### 2. Selecciona un área del mapa

- Navega a la página de selección de mapas
- Elige una ubicación o dibuja un área personalizada
- El sistema descargará datos OSM para el área seleccionada

### 3. Convierte a formato SUMO

- Haz clic en "Convert to SUMO" para generar una red SUMO
- El sistema creará un archivo `.net.xml` compatible con SUMO

### 4. Configura la simulación

- Navega a la página de configuración de simulación
- Revisa los datos de la red y los puntos de entrada/salida
- Configura los parámetros de simulación

### 5. Exporta la simulación

- Haz clic en "Export Simulation" para descargar un paquete completo
- El archivo ZIP contiene:
  - `nodes.nod.xml` - Definición de nodos de la red
  - `edges.edg.xml` - Definición de aristas de la red
  - `routes.rou.xml` - Rutas y flujos de vehículos
  - `simulation.sumocfg` - Configuración de la simulación
  - `traffic_lights.add.xml` - Semáforos detectados
  - `run_simulation.py` - Script para ejecutar la simulación
  - `simulation_metadata.json` - **Metadatos completos para reconstrucción**

### 6. Ejecuta la simulación

```bash
# Extrae el archivo ZIP descargado
unzip simulation_*.zip

# Ejecuta la simulación
python3 run_simulation.py

# O analiza los metadatos
cat simulation_metadata.json
```

### 7. Reconstruye una simulación previa

#### Desde la interfaz web:
1. Ve a la página de selección de mapas
2. Haz clic en "Load Simulation from File"
3. Sube el archivo ZIP completo de la simulación exportada
4. La aplicación extraerá el `simulation_metadata.json` y cargará toda la configuración automáticamente

#### Desde línea de comandos:
```bash
cat simulation_metadata.json
```

## API Endpoints

### Gestión de Mapas
- `POST /api/maps/select-area` - Seleccionar área del mapa
- `GET /api/maps/preview/{map_id}` - Obtener vista previa del mapa
- `POST /api/maps/convert-to-sumo/{map_id}` - Convertir a formato SUMO

### Análisis de Red
- `GET /api/networks/{network_id}` - Obtener datos de la red
- `GET /api/networks/{network_id}/entry-points` - Obtener puntos de entrada
- `GET /api/networks/{network_id}/exit-points` - Obtener puntos de salida
- `POST /api/networks/{network_id}/routes` - Configurar rutas

### Exportación de Simulación
- `POST /api/simulations/export/{network_id}` - Exportar paquete de simulación
- `POST /api/simulations/load-metadata` - **Cargar metadatos de simulación**
- `POST /api/simulations/run/{network_id}` - Ejecutar simulación con GUI

## Estructura del Proyecto

```
sumo-helper/
├── backend/
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── services/
│   │   ├── map_service.py      # Gestión de mapas y redes
│   │   ├── osmnx_service.py    # Procesamiento de datos OSM
│   │   ├── simulation_service.py # Configuración de simulaciones
│   │   └── sumo_export_service.py # Exportación SUMO con metadatos
│   └── models/
│       └── schemas.py          # Esquemas de datos
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── MapSelection.jsx # Selección de mapas
│   │   │   └── NetworkEditor.jsx # Editor de red y simulación
│   │   └── components/
│   └── package.json
└── README.md
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Si tienes problemas o preguntas:

1. Revisa la documentación de SUMO: https://sumo.dlr.de/docs/
2. Abre un issue en GitHub
3. Consulta los logs del backend para errores detallados

## Changelog

### v2.0.0 - Nueva funcionalidad de metadatos
- ✅ Exportación con archivo JSON de metadatos completos
- ✅ Reconstrucción de simulaciones desde metadatos
- ✅ Interfaz web para cargar simulaciones previas
- ✅ Información completa de nodos, aristas y configuración 