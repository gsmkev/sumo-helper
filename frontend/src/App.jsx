/**
 * SUMO Helper - Main Application Component
 * 
 * This is the root component of the SUMO Helper application.
 * It provides the main layout and routing.
 * 
 * Features:
 * - Route-based navigation for different application sections
 * - Clean and modern UI using DaisyUI components
 */

import { Routes, Route } from 'react-router-dom'

// Pages
import MapSelection from './pages/MapSelection'
import NetworkEditor from './pages/NetworkEditor'

/**
 * Main application component
 * 
 * @returns {JSX.Element} The main application layout
 */
function App() {
  return (
    <div className="min-h-screen bg-base-100">
      {/* Main content area */}
      <main className="flex-1">
        <div className="p-6">
          <Routes>
            {/* Map selection and OSM data processing */}
            <Route path="/" element={<MapSelection />} />
            
            {/* Network analysis and editing */}
            <Route path="/network/:networkId" element={<NetworkEditor />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}

export default App 