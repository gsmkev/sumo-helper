import { X, Map, Settings, Upload, Download } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '../lib/utils'

function Sidebar({ isOpen, onClose }) {
  return (
    <div className={cn(
      "fixed top-16 left-0 h-full w-64 bg-base-200 shadow-xl transform transition-transform duration-300 z-40",
      isOpen ? "translate-x-0" : "-translate-x-full"
    )}>
      <div className="p-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-semibold">Navigation</h2>
          <button 
            className="btn btn-ghost btn-sm btn-circle"
            onClick={onClose}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
        
        <ul className="menu bg-base-200 w-full">
          <li>
            <Link to="/" className="flex items-center gap-3 p-3 hover:bg-base-300 rounded-lg">
              <Map className="h-5 w-5" />
              <span>Map Selection</span>
            </Link>
          </li>
          <li>
            <Link to="/network" className="flex items-center gap-3 p-3 hover:bg-base-300 rounded-lg">
              <Settings className="h-5 w-5" />
              <span>Network Editor</span>
            </Link>
          </li>

        </ul>
        
        <div className="divider"></div>
        
        <div className="space-y-2">
          <h3 className="font-semibold text-sm text-base-content/70">Quick Actions</h3>
          <button className="btn btn-outline btn-sm w-full justify-start">
            <Upload className="h-4 w-4 mr-2" />
            Upload Network
          </button>
          <button className="btn btn-outline btn-sm w-full justify-start">
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </button>
        </div>
        
        <div className="divider"></div>
        
        <div className="text-xs text-base-content/50">
          <p>SUMO Helper v1.0.0</p>
          <p>Traffic Simulation Tool</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar 