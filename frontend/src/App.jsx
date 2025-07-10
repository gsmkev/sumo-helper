/**
 * SUMO Helper - Main Application Component
 * 
 * This is the root component of the SUMO Helper application.
 * It provides the main layout with navigation, sidebar, and routing.
 * 
 * Features:
 * - Responsive navigation with collapsible sidebar
 * - Route-based navigation for different application sections
 * - Clean and modern UI using DaisyUI components
 */

import { Routes, Route } from 'react-router-dom'
import { useState } from 'react'

// Components
import Navbar from './components/Navbar'
import Sidebar from './components/Sidebar'

// Pages
import MapSelection from './pages/MapSelection'
import NetworkEditor from './pages/NetworkEditor'
import SimulationConfig from './pages/SimulationConfig'
import SimulationMonitor from './pages/SimulationMonitor'

// Utilities
import { cn } from './lib/utils'

/**
 * Main application component
 * 
 * @returns {JSX.Element} The main application layout
 */
function App() {
  // State for sidebar visibility
  const [sidebarOpen, setSidebarOpen] = useState(false)

  /**
   * Toggle sidebar visibility
   */
  const toggleSidebar = () => setSidebarOpen(!sidebarOpen)

  /**
   * Close sidebar
   */
  const closeSidebar = () => setSidebarOpen(false)

  return (
    <div className="min-h-screen bg-base-100">
      {/* Navigation bar */}
      <Navbar onMenuClick={toggleSidebar} />
      
      <div className="flex">
        {/* Sidebar navigation */}
        <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
        
        {/* Main content area */}
        <main className={cn(
          "flex-1 transition-all duration-300 ease-in-out",
          sidebarOpen ? "ml-64" : "ml-0"
        )}>
          <div className="p-6">
            <Routes>
              {/* Map selection and OSM data processing */}
              <Route path="/" element={<MapSelection />} />
              
              {/* Network analysis and editing */}
              <Route path="/network/:networkId" element={<NetworkEditor />} />
              
              {/* Simulation configuration */}
              <Route path="/simulation/:networkId" element={<SimulationConfig />} />
              
              {/* Simulation monitoring and results */}
              <Route path="/monitor/:simulationId" element={<SimulationMonitor />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App 