import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import * as L from 'leaflet'

function NetworkEditor() {
  const { networkId } = useParams()
  const navigate = useNavigate()
  const [networkData, setNetworkData] = useState(null)
  const [selectedEntryPoints, setSelectedEntryPoints] = useState([])
  const [selectedExitPoints, setSelectedExitPoints] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [selectionMode, setSelectionMode] = useState('entry') // 'entry' or 'exit'

  useEffect(() => {
    loadNetworkData()
  }, [networkId])

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

  const handleContinue = () => {
    if (selectedEntryPoints.length === 0 || selectedExitPoints.length === 0) {
      toast.error('Please select at least one entry point and one exit point')
      return
    }

    // Save the selected points (you might want to save this to backend)
    localStorage.setItem(`network_${networkId}_entry_points`, JSON.stringify(selectedEntryPoints))
    localStorage.setItem(`network_${networkId}_exit_points`, JSON.stringify(selectedExitPoints))
    
    navigate(`/simulation/${networkId}`)
  }



  if (isLoading) {
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
          <h1 className="text-3xl font-bold">Network Editor</h1>
          <p className="text-base-content/70">Select entry and exit points for your simulation</p>
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-outline"
            onClick={() => window.history.back()}
          >
            Back
          </button>
          <button
            className="btn btn-primary"
            onClick={handleContinue}
            disabled={selectedEntryPoints.length === 0 || selectedExitPoints.length === 0}
          >
            <ArrowRight className="h-4 w-4 mr-2" />
            Configure Simulation
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Control Panel */}
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
              <h2 className="card-title">Network Info</h2>
              <div className="text-sm space-y-1">
                <p>Nodes: {networkData.nodes.length}</p>
                <p>Edges: {networkData.edges.length}</p>
                <p>Network ID: {networkId}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Network Visualization */}
        <div className="lg:col-span-3">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Network Visualization</h2>
              <p className="text-sm text-base-content/70 mb-4">
                Click on nodes to select {selectionMode === 'entry' ? 'entry' : 'exit'} points. <br/>
                Green = Entry points, Red = Exit points
              </p>
              <div className="network-visualization">
                <MapContainer center={[leafletNodes[0]?.lat || 40.4, leafletNodes[0]?.lon || -3.7]} zoom={15} style={{ height: '500px', width: '100%' }} scrollWheelZoom={true}>
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
                            <b>ID:</b> {node.id}<br/>
                            <b>Type:</b> {node.type}<br/>
                            <b>Lat:</b> {node.lat}<br/>
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
        </div>
      </div>
    </div>
  )
}

export default NetworkEditor 