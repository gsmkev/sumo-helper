import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Play, ArrowLeft, Settings, Info } from 'lucide-react'
import toast from 'react-hot-toast'

function SimulationConfig() {
  const { networkId } = useParams()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)

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