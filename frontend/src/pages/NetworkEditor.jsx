import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Play, Settings, Info, Download, Car, Truck, Bus, Bike, Maximize2, Minimize2 } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import * as L from 'leaflet'
import { useRef } from 'react'

function NetworkEditor() {
  const { networkId } = useParams()
  const [networkData, setNetworkData] = useState(null)
  const [selectedEntryPoints, setSelectedEntryPoints] = useState([])
  const [selectedExitPoints, setSelectedExitPoints] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [selectionMode, setSelectionMode] = useState('entry') // 'entry' or 'exit'
  const [isFullscreen, setIsFullscreen] = useState(false)
  const mapContainerRef = useRef(null)
  
  // Vehicle configuration state
  const [totalVehicles, setTotalVehicles] = useState(100)
  const [simulationTime, setSimulationTime] = useState(3600)
  const [randomSeed, setRandomSeed] = useState('')
  const [vehicleDistribution, setVehicleDistribution] = useState([
    { vehicle_type: 'car', percentage: 70, color: 'yellow', period: 0.45 },
    { vehicle_type: 'motorcycle', percentage: 15, color: 'green', period: 3.4 },
    { vehicle_type: 'bus', percentage: 10, color: 'orange', period: 1.0 },
    { vehicle_type: 'truck', percentage: 5, color: 'red', period: 1.7, attributes: 'accel="1.0"' }
  ])

  useEffect(() => {
    loadNetworkData()
    loadSelectedPoints()
  }, [networkId])

  // Pantalla completa nativa
  useEffect(() => {
    function handleFullscreenChange() {
      const fsElement = document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement
      setIsFullscreen(!!fsElement)
    }
    document.addEventListener('fullscreenchange', handleFullscreenChange)
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange)
    document.addEventListener('mozfullscreenchange', handleFullscreenChange)
    document.addEventListener('MSFullscreenChange', handleFullscreenChange)
    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange)
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange)
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange)
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange)
    }
  }, [])

  const enterFullscreen = () => {
    const el = mapContainerRef.current
    if (el.requestFullscreen) el.requestFullscreen()
    else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen()
    else if (el.mozRequestFullScreen) el.mozRequestFullScreen()
    else if (el.msRequestFullscreen) el.msRequestFullscreen()
  }
  const exitFullscreen = () => {
    if (document.exitFullscreen) document.exitFullscreen()
    else if (document.webkitExitFullscreen) document.webkitExitFullscreen()
    else if (document.mozCancelFullScreen) document.mozCancelFullScreen()
    else if (document.msExitFullscreen) document.msExitFullscreen()
  }

  const loadNetworkData = async () => {
    try {
      setIsLoading(true)
      const response = await axios.get(`/api/networks/${networkId}`)
      setNetworkData(response.data)
    } catch (error) {
      console.error('Error loading network data:', error)
      toast.error('Error loading network data')
    } finally {
      setIsLoading(false)
    }
  }

  const loadSelectedPoints = () => {
    try {
      const savedEntryPoints = localStorage.getItem(`network_${networkId}_entry_points`)
      const savedExitPoints = localStorage.getItem(`network_${networkId}_exit_points`)
      
      if (savedEntryPoints) {
        setSelectedEntryPoints(JSON.parse(savedEntryPoints))
      }
      if (savedExitPoints) {
        setSelectedExitPoints(JSON.parse(savedExitPoints))
      }
    } catch (error) {
      console.error('Error loading selected points:', error)
    }
  }

  const handleNodeClick = (node) => {
    if (selectionMode === 'entry') {
      if (selectedEntryPoints.find(p => p.id === node.id)) {
        setSelectedEntryPoints(prev => prev.filter(p => p.id !== node.id))
      } else {
        setSelectedEntryPoints(prev => [...prev, node])
      }
    } else {
      if (selectedExitPoints.find(p => p.id === node.id)) {
        setSelectedExitPoints(prev => prev.filter(p => p.id !== node.id))
      } else {
        setSelectedExitPoints(prev => [...prev, node])
      }
    }
  }

  const handleStartSimulation = async () => {
    if (selectedEntryPoints.length === 0) {
      toast.error('Please select at least one entry point')
      return
    }
    if (selectedExitPoints.length === 0) {
      toast.error('Please select at least one exit point')
      return
    }

    // Validate vehicle distribution percentages
    const totalPercentage = vehicleDistribution.reduce((sum, vd) => sum + vd.percentage, 0)
    if (Math.abs(totalPercentage - 100) > 0.01) {
      toast.error(`Vehicle distribution percentages must sum to 100% (currently ${totalPercentage.toFixed(1)}%)`)
      return
    }

    setIsLoading(true)
    try {
      const requestData = {
        total_vehicles: totalVehicles,
        vehicle_distribution: vehicleDistribution,
        selected_entry_points: selectedEntryPoints.map(p => p.id),
        selected_exit_points: selectedExitPoints.map(p => p.id),
        simulation_time: simulationTime,
        random_seed: randomSeed ? parseInt(randomSeed) : null
      }

      const response = await axios.post(`/api/simulations/run/${networkId}`, requestData)
      
      if (response.data.status === 'running') {
        toast.success('SUMO GUI simulation started successfully!')
      } else {
        toast.error('Failed to start simulation')
      }
      
    } catch (error) {
      console.error('Error starting simulation:', error)
      toast.error(error.response?.data?.detail || 'Failed to start simulation')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExportSimulation = async () => {
    if (selectedEntryPoints.length === 0) {
      toast.error('Please select at least one entry point')
      return
    }
    if (selectedExitPoints.length === 0) {
      toast.error('Please select at least one exit point')
      return
    }

    // Validate vehicle distribution percentages
    const totalPercentage = vehicleDistribution.reduce((sum, vd) => sum + vd.percentage, 0)
    if (Math.abs(totalPercentage - 100) > 0.01) {
      toast.error(`Vehicle distribution percentages must sum to 100% (currently ${totalPercentage.toFixed(1)}%)`)
      return
    }

    setIsExporting(true)
    try {
      const requestData = {
        total_vehicles: totalVehicles,
        vehicle_distribution: vehicleDistribution,
        selected_entry_points: selectedEntryPoints.map(p => p.id),
        selected_exit_points: selectedExitPoints.map(p => p.id),
        simulation_time: simulationTime,
        random_seed: randomSeed ? parseInt(randomSeed) : null
      }

      const response = await axios.post(`/api/simulations/export/${networkId}`, requestData, {
        responseType: 'blob'
      })

      // Create download link
      const blob = new Blob([response.data], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `simulation_${networkId}.zip`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      toast.success('Simulation exported successfully!')
      
    } catch (error) {
      console.error('Error exporting simulation:', error)
      toast.error('Failed to export simulation')
    } finally {
      setIsExporting(false)
    }
  }

  const updateVehicleDistribution = (index, field, value) => {
    const newDistribution = [...vehicleDistribution]
    newDistribution[index] = { ...newDistribution[index], [field]: value }
    setVehicleDistribution(newDistribution)
  }

  const getVehicleIcon = (vehicleType) => {
    switch (vehicleType) {
      case 'car': return <Car className="h-4 w-4" />
      case 'motorcycle': return <Bike className="h-4 w-4" />
      case 'bus': return <Bus className="h-4 w-4" />
      case 'truck': return <Truck className="h-4 w-4" />
      default: return <Car className="h-4 w-4" />
    }
  }

  const getVehicleColor = (vehicleType) => {
    const vd = vehicleDistribution.find(v => v.vehicle_type === vehicleType)
    return vd?.color || 'gray'
  }

  const handleSavePoints = () => {
    if (selectedEntryPoints.length === 0 || selectedExitPoints.length === 0) {
      toast.error('Please select at least one entry point and one exit point')
      return
    }

    // Save the selected points
    localStorage.setItem(`network_${networkId}_entry_points`, JSON.stringify(selectedEntryPoints))
    localStorage.setItem(`network_${networkId}_exit_points`, JSON.stringify(selectedExitPoints))
    
    toast.success('Entry and exit points saved successfully!')
  }

  if (isLoading && !networkData) {
    return (
      <div className="flex items-center justify-center h-64">
        <span className="loading loading-spinner loading-lg"></span>
      </div>
    )
  }

  if (!networkData) {
    return (
      <div className="alert alert-error">
        <span>Error loading network data</span>
      </div>
    )
  }

  // Nueva función para centrar el mapa en los nodos
  function FitBounds({ nodes }) {
    const map = useMap();
    if (!nodes || nodes.length === 0) return null;
    const validNodes = nodes.filter(n => n.lat && n.lon);
    if (validNodes.length === 0) return null;
    const bounds = validNodes.map(n => [n.lat, n.lon]);
    map.fitBounds(bounds, { padding: [50, 50] });
    return null;
  }

  // Visualización con react-leaflet
  const leafletNodes = networkData.nodes.filter(n => n.lat && n.lon);
  const leafletEdges = networkData.edges.filter(e => e.shape && e.shape[0] && e.shape[1]);
  
  // Remove duplicate edges based on ID to prevent React key conflicts
  const uniqueEdges = leafletEdges.filter((edge, index, self) => 
    index === self.findIndex(e => e.id === edge.id)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Network Editor & Simulation Configuration</h1>
          <p className="text-base-content/70">Select entry/exit points and configure your traffic simulation</p>
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-outline"
            onClick={() => window.history.back()}
          >
            Back
          </button>
          <button
            className="btn btn-secondary"
            onClick={handleExportSimulation}
            disabled={isExporting || selectedEntryPoints.length === 0 || selectedExitPoints.length === 0}
          >
            {isExporting ? (
              <span className="loading loading-spinner loading-sm"></span>
            ) : (
              <Download className="h-4 w-4 mr-2" />
            )}
            Export Simulation
          </button>
          <button
            className="btn btn-primary"
            onClick={handleStartSimulation}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="loading loading-spinner loading-sm"></span>
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Start with sumo-gui
          </button>
        </div>
      </div>

      <div className={`grid grid-cols-1 ${isFullscreen ? '' : 'lg:grid-cols-4'} gap-6`}>
        {/* Control Panel */}
        {!isFullscreen && (
          <div className="lg:col-span-1 space-y-4">
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Selection Mode</h2>
                
                <div className="form-control">
                  <label className="label cursor-pointer">
                    <span className="label-text">Entry Points</span>
                    <input
                      type="radio"
                      name="selection-mode"
                      className="radio radio-primary"
                      checked={selectionMode === 'entry'}
                      onChange={() => setSelectionMode('entry')}
                    />
                  </label>
                </div>
                
                <div className="form-control">
                  <label className="label cursor-pointer">
                    <span className="label-text">Exit Points</span>
                    <input
                      type="radio"
                      name="selection-mode"
                      className="radio radio-primary"
                      checked={selectionMode === 'exit'}
                      onChange={() => setSelectionMode('exit')}
                    />
                  </label>
                </div>

                <button
                  className="btn btn-sm btn-outline mt-2"
                  onClick={handleSavePoints}
                >
                  Save Points
                </button>
              </div>
            </div>

            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Selected Points</h2>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-green-600 mb-2">Entry Points ({selectedEntryPoints.length})</h3>
                    <div className="space-y-1">
                      {selectedEntryPoints.map(point => (
                        <div key={point.id} className="flex justify-between items-center p-2 bg-green-50 rounded">
                          <span className="text-sm">{point.id}</span>
                          <button
                            className="btn btn-ghost btn-xs"
                            onClick={() => setSelectedEntryPoints(prev => prev.filter(p => p.id !== point.id))}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      {selectedEntryPoints.length === 0 && (
                        <p className="text-sm text-gray-500">No entry points selected</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold text-red-600 mb-2">Exit Points ({selectedExitPoints.length})</h3>
                    <div className="space-y-1">
                      {selectedExitPoints.map(point => (
                        <div key={point.id} className="flex justify-between items-center p-2 bg-red-50 rounded">
                          <span className="text-sm">{point.id}</span>
                          <button
                            className="btn btn-ghost btn-xs"
                            onClick={() => setSelectedExitPoints(prev => prev.filter(p => p.id !== point.id))}
                          >
                            ×
                          </button>
                        </div>
                      ))}
                      {selectedExitPoints.length === 0 && (
                        <p className="text-sm text-gray-500">No exit points selected</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">
                  <Settings className="h-5 w-5" />
                  Simulation Settings
                </h2>
                
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Total Vehicles</span>
                  </label>
                  <input
                    type="number"
                    className="input input-bordered input-sm"
                    value={totalVehicles}
                    onChange={(e) => setTotalVehicles(parseInt(e.target.value) || 0)}
                    min="1"
                    max="10000"
                  />
                  <label className="label">
                    <span className="label-text-alt">Number of vehicles</span>
                  </label>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Simulation Time (seconds)</span>
                  </label>
                  <input
                    type="number"
                    className="input input-bordered input-sm"
                    value={simulationTime}
                    onChange={(e) => setSimulationTime(parseInt(e.target.value) || 3600)}
                    min="60"
                    max="7200"
                  />
                  <label className="label">
                    <span className="label-text-alt">Duration</span>
                  </label>
                </div>

                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Random Seed (optional)</span>
                  </label>
                  <input
                    type="number"
                    className="input input-bordered input-sm"
                    value={randomSeed}
                    onChange={(e) => setRandomSeed(e.target.value)}
                    placeholder="Auto"
                  />
                  <label className="label">
                    <span className="label-text-alt">For reproducible results</span>
                  </label>
                </div>
              </div>
            </div>

            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Network Info</h2>
                <div className="text-sm space-y-1">
                  <p>Nodes: {networkData.nodes.length}</p>
                  <p>Edges: {networkData.edges.length}</p>
                  <p>Network ID: {networkId}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Network Visualization and Vehicle Distribution */}
        <div className={`${isFullscreen ? '' : 'lg:col-span-3'} space-y-6`}>
          {/* Network Visualization */}
          <div
            className={`card bg-base-100 shadow-xl relative ${isFullscreen ? 'z-50' : ''}`}
            ref={mapContainerRef}
            style={isFullscreen ? { height: '100vh', width: '100vw', position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, margin: 0, borderRadius: 0 } : {}}
          >
            <div className="card-body" style={isFullscreen ? { height: '100%', padding: 0 } : {}}>
              {/* Controles ultra-minimalistas solo en pantalla completa */}
              {isFullscreen && (
                <div className="w-full flex flex-col items-center justify-center mt-6 mb-4 gap-1">
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="radio"
                        name="selection-mode"
                        className="radio radio-primary"
                        checked={selectionMode === 'entry'}
                        onChange={() => setSelectionMode('entry')}
                      />
                      <span className="label-text">Entry</span>
                    </label>
                    <label className="flex items-center gap-1 cursor-pointer">
                      <input
                        type="radio"
                        name="selection-mode"
                        className="radio radio-primary"
                        checked={selectionMode === 'exit'}
                        onChange={() => setSelectionMode('exit')}
                      />
                      <span className="label-text">Exit</span>
                    </label>
                  </div>
                  <div className="text-xs text-base-content/60 text-center mt-1">
                    Click nodes to select. Green=Entry, Red=Exit
                  </div>
                </div>
              )}

              {/* Botón pantalla completa (si no está en fullscreen) */}
              {!isFullscreen && (
                <button
                  className="absolute top-4 right-4 z-50 btn btn-circle btn-sm btn-neutral shadow"
                  onClick={enterFullscreen}
                  title="Pantalla completa"
                >
                  <Maximize2 className="h-4 w-4" />
                </button>
              )}
              {/* Botón salir de pantalla completa (si está en fullscreen) */}
              {isFullscreen && (
                <button
                  className="absolute top-4 right-4 z-50 btn btn-circle btn-sm btn-neutral shadow"
                  onClick={exitFullscreen}
                  title="Salir de pantalla completa"
                >
                  <Minimize2 className="h-4 w-4" />
                </button>
              )}

              <div 
                className={`network-visualization full-map-container ${!isFullscreen ? 'mt-6' : ''}`}
                style={isFullscreen ? { 
                  height: 'calc(100vh - 32px)', 
                  width: '100vw',
                  marginTop: '0px'
                } : {}}
              >
                <MapContainer
                  center={[leafletNodes[0]?.lat || 40.4, leafletNodes[0]?.lon || -3.7]}
                  zoom={15}
                  className="w-full h-full"
                  style={{ height: '100%', width: '100%' }}
                  scrollWheelZoom={true}
                >
                  <FitBounds nodes={leafletNodes} />
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  />
                  {uniqueEdges.map((edge, idx) => (
                    <Polyline
                      key={`edge-${edge.id}-${idx}`}
                      positions={edge.shape.map(([lat, lon]) => [lat, lon])}
                      color="#888"
                      weight={2}
                      opacity={0.7}
                    />
                  ))}
                  {leafletNodes.map((node, idx) => {
                    const isEntry = selectedEntryPoints.find(p => p.id === node.id);
                    const isExit = selectedExitPoints.find(p => p.id === node.id);
                    let markerColor = isEntry ? 'green' : isExit ? 'red' : 'blue';
                    return (
                      <Marker
                        key={`node-${node.id}-${idx}`}
                        position={[node.lat, node.lon]}
                        eventHandlers={{
                          click: () => handleNodeClick(node)
                        }}
                        icon={L.divIcon({
                          className: '',
                          html: `<div style="background:${markerColor};color:white;padding:2px 6px;border-radius:6px;font-size:12px;border:2px solid #fff;">${node.id}</div>`
                        })}
                      >
                        <Popup>
                          <div>
                            <b>ID:</b> {node.id}<br />
                            <b>Type:</b> {node.type}<br />
                            <b>Lat:</b> {node.lat}<br />
                            <b>Lon:</b> {node.lon}
                          </div>
                        </Popup>
                      </Marker>
                    )
                  })}
                </MapContainer>
              </div>
            </div>
          </div>

          {/* Vehicle Distribution */}
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Vehicle Distribution</h2>
              
              <div className="alert alert-info">
                <Info className="h-5 w-5" />
                <div>
                  <h3 className="font-bold">Vehicle Distribution</h3>
                  <div className="text-sm">
                    Configure the percentage of each vehicle type. Total must equal 100%.
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                {vehicleDistribution.map((vehicle, index) => (
                  <div key={vehicle.vehicle_type} className="card bg-base-200">
                    <div className="card-body p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getVehicleIcon(vehicle.vehicle_type)}
                          <div>
                            <h3 className="font-semibold capitalize">{vehicle.vehicle_type}</h3>
                            <p className="text-sm text-base-content/70">
                              {Math.round((vehicle.percentage / 100) * totalVehicles)} vehicles
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center gap-4">
                          <div className="form-control w-24">
                            <label className="label">
                              <span className="label-text text-xs">Percentage</span>
                            </label>
                            <input
                              type="number"
                              className="input input-bordered input-sm"
                              value={vehicle.percentage}
                              onChange={(e) => updateVehicleDistribution(index, 'percentage', parseFloat(e.target.value) || 0)}
                              min="0"
                              max="100"
                              step="0.1"
                            />
                          </div>
                          
                          <div className="form-control w-24">
                            <label className="label">
                              <span className="label-text text-xs">Color</span>
                            </label>
                            <input
                              type="color"
                              className="input input-bordered input-sm h-8"
                              value={vehicle.color}
                              onChange={(e) => updateVehicleDistribution(index, 'color', e.target.value)}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Total Percentage Display */}
              <div className="mt-4 p-4 bg-base-200 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">Total Percentage:</span>
                  <span className={`font-bold ${Math.abs(vehicleDistribution.reduce((sum, vd) => sum + vd.percentage, 0) - 100) < 0.01 ? 'text-green-600' : 'text-red-600'}`}>
                    {vehicleDistribution.reduce((sum, vd) => sum + vd.percentage, 0).toFixed(1)}%
                  </span>
                </div>
                {Math.abs(vehicleDistribution.reduce((sum, vd) => sum + vd.percentage, 0) - 100) >= 0.01 && (
                  <p className="text-sm text-red-600 mt-1">
                    Total must equal 100%
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NetworkEditor 