import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Rectangle, useMapEvents, useMap } from 'react-leaflet'
import { Search, Download, Upload, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

// Componente para actualizar la vista del mapa
function MapViewUpdater({ center, zoom }) {
  const map = useMap()
  
  // Actualizar la vista cuando cambien las coordenadas
  if (center && center[0] && center[1]) {
    map.setView(center, zoom)
  }
  
  return null
}

function MapSelection() {
  const navigate = useNavigate()
  const [selectedArea, setSelectedArea] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [mapId, setMapId] = useState(null)
  const [mapCenter, setMapCenter] = useState([40.4168, -3.7038]) // Madrid default
  const [mapZoom, setMapZoom] = useState(10)
  
  // Estados para drag and drop y archivos
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const fileInputRef = useRef(null)

  const handleMapClick = (e) => {
    const { lat, lng } = e.latlng
    // Create a default area (approximately 1km x 1km)
    const offset = 0.005 // About 1km
    setSelectedArea({
      north: lat + offset,
      south: lat - offset,
      east: lng + offset,
      west: lng - offset
    })
  }

  const handleAreaSelect = (bounds) => {
    setSelectedArea(bounds)
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      toast.error('Please enter a place name')
      return
    }

    setIsLoading(true)
    try {
      // Use OpenStreetMap Nominatim API for geocoding
      const response = await axios.get(
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(searchQuery)}&format=json&limit=1`
      )

      if (response.data.length > 0) {
        const place = response.data[0]
        const lat = parseFloat(place.lat)
        const lon = parseFloat(place.lon)

        // Update map center to the found location
        setMapCenter([lat, lon])
        setMapZoom(15) // Zoom in closer to the location

        // Create a default area (approximately 1km x 1km)
        const offset = 0.005 // About 1km
        setSelectedArea({
          north: lat + offset,
          south: lat - offset,
          east: lon + offset,
          west: lon - offset
        })

        toast.success(`Found: ${place.display_name}`)
      } else {
        toast.error('Place not found')
      }
    } catch (error) {
      toast.error('Error searching for place')
    } finally {
      setIsLoading(false)
    }
  }

  // Funciones para drag and drop
  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleFileUpload = (file) => {
    // Validar que sea un archivo ZIP
    if (!file.name.toLowerCase().endsWith('.zip')) {
      toast.error('Please upload a ZIP file')
      return
    }

    setUploadedFile(file)
    toast.success(`File uploaded: ${file.name}`)
  }

  const handleConvertToSumo = async () => {
    if (!selectedArea && !uploadedFile) {
      toast.error('Please select an area or upload a file first')
      return
    }

    setIsLoading(true)
    try {
      if (uploadedFile) {
        // TODO: Implementar lógica para procesar archivo ZIP
        toast.info('Processing uploaded file...')
        // Aquí iría la lógica para subir y procesar el archivo ZIP
      } else {
        // First, select the area
        const selectResponse = await axios.post('/api/maps/select-area', {
          ...selectedArea,
          place_name: searchQuery || 'Selected Area'
        })

        const tempMapId = selectResponse.data.id
        setMapId(tempMapId)

        // Then convert to SUMO
        const convertResponse = await axios.post(`/api/maps/convert-to-sumo/${tempMapId}`)

        toast.success('Map converted to SUMO format!')

        // Navigate to network editor
        navigate(`/network/${tempMapId}`)
      }
    } catch (error) {
      console.error('Error converting map:', error)
      toast.error(error.response?.data?.detail || 'Error converting map')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Map Selection</h1>
          <p className="text-base-content/70">Select an area on the map or upload a SUMO simulation ZIP file to continue editing</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Control Panel */}
        <div className="lg:col-span-1 space-y-4">
          {/* Search Location */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Search Location</h2>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Place Name</span>
                </label>
                <div className="input-group">
                  <input
                    type="text"
                    placeholder="e.g., Madrid, Spain"
                    className="input input-bordered flex-1"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                  <button
                    className="btn btn-primary"
                    onClick={handleSearch}
                    disabled={isLoading}
                  >
                    <Search className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* File Upload */}
                      <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Upload SUMO Simulation</h2>
              
              <div className="form-control">
                <label className="label">
                  <span className="label-text">Drag & Drop or Click to Upload</span>
                </label>
                
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    isDragOver 
                      ? 'border-primary bg-primary/10' 
                      : 'border-base-300 hover:border-primary/50'
                  }`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Upload className="h-12 w-12 mx-auto mb-4 text-base-content/50" />
                  <p className="text-base-content/70 mb-2">
                    Drag and drop your SUMO simulation ZIP file here, or click to browse
                  </p>
                  <p className="text-xs text-base-content/50">
                    Upload a ZIP file containing SUMO network and simulation data
                  </p>
                  
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".zip"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                </div>
              </div>

              {uploadedFile && (
                <div className="mt-4 p-4 bg-base-200 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4" />
                    <span className="font-medium">{uploadedFile.name}</span>
                  </div>
                  <p className="text-sm text-base-content/70 mt-1">
                    Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Selected Area Info */}
          {selectedArea && (
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Selected Area</h2>
                <div className="text-sm space-y-1">
                  <p>North: {selectedArea.north?.toFixed(6)}</p>
                  <p>South: {selectedArea.south?.toFixed(6)}</p>
                  <p>East: {selectedArea.east?.toFixed(6)}</p>
                  <p>West: {selectedArea.west?.toFixed(6)}</p>
                </div>
              </div>
            </div>
          )}

          {/* Convert Button */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <div className="card-actions justify-end">
                <button
                  className="btn btn-primary w-full"
                  onClick={handleConvertToSumo}
                  disabled={(!selectedArea && !uploadedFile) || isLoading}
                >
                  {isLoading ? (
                    <span className="loading loading-spinner loading-sm"></span>
                  ) : (
                    <>
                      <Download className="h-4 w-4 mr-2" />
                      Convert to SUMO
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span>You can search for a location on the map or upload a SUMO simulation ZIP file to continue editing your network.</span>
          </div>
        </div>

        {/* Map */}
        <div className="lg:col-span-2">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Interactive Map</h2>
              <div className="map-container">
                <MapContainer
                  center={mapCenter}
                  zoom={mapZoom}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />

                  <MapClickHandler onMapClick={handleMapClick} />
                  <MapViewUpdater center={mapCenter} zoom={mapZoom} />

                  {selectedArea && (
                    <Rectangle
                      bounds={[
                        [selectedArea.south, selectedArea.west],
                        [selectedArea.north, selectedArea.east]
                      ]}
                      color="red"
                      weight={2}
                      fillOpacity={0.1}
                    />
                  )}
                </MapContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: onMapClick,
  })
  return null
}

export default MapSelection 