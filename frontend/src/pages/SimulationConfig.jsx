import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Play, ArrowLeft, Settings, Info, Download, Car, Truck, Bus, Bike } from 'lucide-react'
import toast from 'react-hot-toast'
import axios from 'axios'

function SimulationConfig() {
  const { networkId } = useParams()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [networkData, setNetworkData] = useState(null)
  const [selectedEntryPoints, setSelectedEntryPoints] = useState([])
  const [selectedExitPoints, setSelectedExitPoints] = useState([])
  
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

  const loadNetworkData = async () => {
    try {
      const response = await axios.get(`/api/networks/${networkId}`)
      setNetworkData(response.data)
    } catch (error) {
      console.error('Error loading network data:', error)
      toast.error('Error loading network data')
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

  const handleStartSimulation = async () => {
    setIsLoading(true)
    try {
      // TODO: Implement simulation configuration and start
      toast.success('Simulation functionality not implemented yet')
    } catch (error) {
      console.error('Error starting simulation:', error)
      toast.error('Simulation functionality not implemented yet')
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

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Simulation Configuration</h1>
          <p className="text-base-content/70">Configure your traffic simulation parameters</p>
        </div>
        <div className="flex gap-2">
          <button
            className="btn btn-outline"
            onClick={() => navigate(`/network/${networkId}`)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Network
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
            Start Simulation
          </button>
        </div>
      </div>

      {/* Entry/Exit Points Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-green-600">
              Entry Points ({selectedEntryPoints.length})
            </h3>
            <div className="space-y-1">
              {selectedEntryPoints.map(point => (
                <div key={point.id} className="text-sm p-2 bg-green-50 rounded">
                  {point.id}
                </div>
              ))}
              {selectedEntryPoints.length === 0 && (
                <p className="text-sm text-gray-500">No entry points selected</p>
              )}
            </div>
          </div>
        </div>

        <div className="card bg-base-100 shadow-xl">
          <div className="card-body">
            <h3 className="card-title text-red-600">
              Exit Points ({selectedExitPoints.length})
            </h3>
            <div className="space-y-1">
              {selectedExitPoints.map(point => (
                <div key={point.id} className="text-sm p-2 bg-red-50 rounded">
                  {point.id}
                </div>
              ))}
              {selectedExitPoints.length === 0 && (
                <p className="text-sm text-gray-500">No exit points selected</p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulation Settings */}
        <div className="lg:col-span-1 space-y-4">
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
                  className="input input-bordered"
                  value={totalVehicles}
                  onChange={(e) => setTotalVehicles(parseInt(e.target.value) || 0)}
                  min="1"
                  max="10000"
                />
                <label className="label">
                  <span className="label-text-alt">Number of vehicles in simulation</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Simulation Time (seconds)</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  value={simulationTime}
                  onChange={(e) => setSimulationTime(parseInt(e.target.value) || 3600)}
                  min="60"
                  max="7200"
                />
                <label className="label">
                  <span className="label-text-alt">Duration of simulation</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Random Seed (optional)</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
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
        </div>

        {/* Vehicle Distribution */}
        <div className="lg:col-span-2 space-y-4">
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

export default SimulationConfig 