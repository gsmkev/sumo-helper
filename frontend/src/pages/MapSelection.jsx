import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapContainer, TileLayer, Rectangle, useMapEvents } from 'react-leaflet'
import { Search, Download, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

function MapSelection() {
  const navigate = useNavigate()
  const [selectedArea, setSelectedArea] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [mapId, setMapId] = useState(null)

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

  const handleConvertToSumo = async () => {
    if (!selectedArea) {
      toast.error('Please select an area first')
      return
    }

    setIsLoading(true)
    try {
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
          <p className="text-base-content/70">Select an area on the map to generate a SUMO network</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Panel */}
        <div className="lg:col-span-1 space-y-4">
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

              <div className="divider">OR</div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Manual Coordinates</span>
                </label>
                              <div className="text-xs text-base-content/70 mb-2">
                Tip: Select an area (approximately 1km x 1km) near main roads for best results
              </div>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="number"
                    placeholder="North"
                    className="input input-bordered input-sm"
                    value={selectedArea?.north || ''}
                    onChange={(e) => setSelectedArea(prev => ({ ...prev, north: parseFloat(e.target.value) }))}
                  />
                  <input
                    type="number"
                    placeholder="South"
                    className="input input-bordered input-sm"
                    value={selectedArea?.south || ''}
                    onChange={(e) => setSelectedArea(prev => ({ ...prev, south: parseFloat(e.target.value) }))}
                  />
                  <input
                    type="number"
                    placeholder="East"
                    className="input input-bordered input-sm"
                    value={selectedArea?.east || ''}
                    onChange={(e) => setSelectedArea(prev => ({ ...prev, east: parseFloat(e.target.value) }))}
                  />
                  <input
                    type="number"
                    placeholder="West"
                    className="input input-bordered input-sm"
                    value={selectedArea?.west || ''}
                    onChange={(e) => setSelectedArea(prev => ({ ...prev, west: parseFloat(e.target.value) }))}
                  />
                </div>
              </div>

              {selectedArea && (
                <div className="mt-4 p-4 bg-base-200 rounded-lg">
                  <h3 className="font-semibold mb-2">Selected Area:</h3>
                  <div className="text-sm space-y-1">
                    <p>North: {selectedArea.north?.toFixed(6)}</p>
                    <p>South: {selectedArea.south?.toFixed(6)}</p>
                    <p>East: {selectedArea.east?.toFixed(6)}</p>
                    <p>West: {selectedArea.west?.toFixed(6)}</p>
                  </div>
                </div>
              )}

              <div className="card-actions justify-end mt-4">
                <button
                  className="btn btn-primary"
                  onClick={handleConvertToSumo}
                  disabled={!selectedArea || isLoading}
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

          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Instructions</h2>
              <div className="text-sm space-y-2">
                <p>1. Search for a location or click on the map</p>
                <p>2. Select an area (1km x 1km max) near main roads</p>
                <p>3. Adjust the selected area if needed</p>
                <p>4. Click "Convert to SUMO" to generate the network</p>
                <p>5. Continue to the Network Editor to configure routes</p>
              </div>
              <div className="alert alert-info mt-4">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" className="stroke-current shrink-0 w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span>Note: Roads including secondary streets (highways, primary, secondary, tertiary, residential, service) will be included in the network.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Map */}
        <div className="lg:col-span-2">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Interactive Map</h2>
              <div className="map-container">
                <MapContainer
                  center={[40.4168, -3.7038]} // Madrid default
                  zoom={10}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  
                  <MapClickHandler onMapClick={handleMapClick} />
                  
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