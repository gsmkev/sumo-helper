// Suppress Leaflet deprecation warnings before any other imports
const originalWarn = console.warn;
console.warn = function(...args) {
  const message = args[0];
  if (typeof message === 'string' && (
    message.includes('MouseEvent.mozPressure') ||
    message.includes('MouseEvent.mozInputSource')
  )) {
    return; // Suppress these specific warnings
  }
  originalWarn.apply(console, args);
};

// Suppress MouseEvent deprecation warnings by providing fallback properties
if (typeof MouseEvent !== 'undefined') {
  Object.defineProperty(MouseEvent.prototype, 'mozPressure', {
    get: function() {
      return this.pressure || 0;
    },
    configurable: true
  });
  
  Object.defineProperty(MouseEvent.prototype, 'mozInputSource', {
    get: function() {
      return this.pointerType || 'mouse';
    },
    configurable: true
  });
}

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <App />
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>,
) 