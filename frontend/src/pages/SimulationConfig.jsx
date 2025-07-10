import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Play, ArrowLeft, Settings, Info, Download } from 'lucide-react'
import toast from 'react-hot-toast'

function SimulationConfig() {
  const { networkId } = useParams()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [isExporting, setIsExporting] = useState(false)

  const handleStartSimulation = async () => {
    setIsLoading(true)
    try {
      // TODO: Implement simulation configuration and start
      // - Configure simulation parameters
      // - Start simulation
      // - Navigate to monitor
      
      toast.success('Simulation functionality not implemented yet')
      
    } catch (error) {
      console.error('Error starting simulation:', error)
      toast.error('Simulation functionality not implemented yet')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExportSimulation = async () => {
    setIsExporting(true)
    try {
      // Create sample routes for export (this would come from the UI in a real implementation)
      const sampleRoutes = [
        {
          id: "route_1",
          from_edge: "entry_1",
          to_edge: "exit_1", 
          vehicle_count: 30,
          vehicle_type: "car",
          start_time: 0,
          end_time: 3600
        }
      ]

      const requestData = {
        routes: sampleRoutes,
        simulation_config: {
          simulation_time: 3600,
          step_length: 1.0,
          use_gui: false,
          random_seed: null,
          output_prefix: "simulation"
        }
      }

      const response = await fetch(`/api/simulations/export/${networkId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      })

      if (!response.ok) {
        throw new Error('Failed to export simulation')
      }

      const exportInfo = await response.json()
      
      // Download the file
      const downloadResponse = await fetch(`/api/simulations/download/${exportInfo.file_name}`)
      if (!downloadResponse.ok) {
        throw new Error('Failed to download simulation file')
      }

      const blob = await downloadResponse.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = exportInfo.file_name
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
            disabled={isExporting}
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

      {/* Export Information */}
      <div className="alert alert-success">
        <Download className="h-6 w-6" />
        <div>
          <h3 className="font-bold">Export Simulation</h3>
          <div className="text-sm">
            Click "Export Simulation" to download a ZIP file containing all necessary SUMO files.
            The exported simulation can be run independently using the included Python script.
          </div>
        </div>
      </div>

      {/* Not Implemented Notice */}
      <div className="alert alert-info">
        <Info className="h-6 w-6" />
        <div>
          <h3 className="font-bold">Simulation Configuration Not Implemented</h3>
          <div className="text-sm">
            This feature is currently a skeleton for future implementation. 
            The simulation configuration and execution logic will be added later.
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
                  <span className="label-text">Simulation Time (seconds)</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  value="3600"
                  disabled
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/50">Not implemented</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Step Length</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  value="1.0"
                  disabled
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/50">Not implemented</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label cursor-pointer">
                  <span className="label-text">Use GUI</span>
                  <input
                    type="checkbox"
                    className="checkbox checkbox-primary"
                    disabled
                  />
                </label>
                <label className="label">
                  <span className="label-text-alt text-base-content/50">Not implemented</span>
                </label>
              </div>

              <div className="form-control">
                <label className="label">
                  <span className="label-text">Random Seed</span>
                </label>
                <input
                  type="number"
                  className="input input-bordered"
                  placeholder="Auto"
                  disabled
                />
                <label className="label">
                  <span className="label-text-alt text-base-content/50">Not implemented</span>
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Routes Configuration */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <h2 className="card-title">Routes Configuration</h2>
              
              <div className="alert alert-warning">
                <Info className="h-5 w-5" />
                <div>
                  <h3 className="font-bold">Routes Configuration Not Implemented</h3>
                  <div className="text-sm">
                    Route configuration and vehicle generation will be implemented in a future update.
                  </div>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="table table-zebra">
                  <thead>
                    <tr>
                      <th>Route ID</th>
                      <th>From Edge</th>
                      <th>To Edge</th>
                      <th>Vehicle Count</th>
                      <th>Vehicle Type</th>
                      <th>Start Time</th>
                      <th>End Time</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td colSpan="8" className="text-center text-base-content/50">
                        No routes configured (not implemented)
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="flex justify-center mt-4">
                <button className="btn btn-outline" disabled>
                  Add Route
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SimulationConfig 