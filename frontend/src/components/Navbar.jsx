import { Menu, Map, Settings } from 'lucide-react'
import { Link } from 'react-router-dom'

function Navbar({ onMenuClick }) {
  return (
    <div className="navbar bg-base-200 shadow-lg">
      <div className="navbar-start">
        <button 
          className="btn btn-ghost btn-circle"
          onClick={onMenuClick}
        >
          <Menu className="h-6 w-6" />
        </button>
        <Link to="/" className="btn btn-ghost text-xl">
          <Map className="h-6 w-6 mr-2" />
          SUMO Helper
        </Link>
      </div>
      
      <div className="navbar-center hidden lg:flex">
        <ul className="menu menu-horizontal px-1">
          <li>
            <Link to="/" className="flex items-center gap-2">
              <Map className="h-4 w-4" />
              Map Selection
            </Link>
          </li>
          <li>
            <Link to="/network" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Network Editor
            </Link>
          </li>

        </ul>
      </div>
    </div>
  )
}

export default Navbar 