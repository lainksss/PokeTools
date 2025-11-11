import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { LanguageProvider } from './i18n/LanguageContext'
import App from './App'
import Home from './pages/Home'
import Calculate from './pages/Calculate'
import Threats from './pages/Threats'
import Coverage from './pages/Coverage'
import './styles.css'

function Root() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<Home />} />
            <Route path="calculate" element={<Calculate />} />
            <Route path="threats" element={<Threats />} />
            <Route path="coverage" element={<Coverage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  )
}

createRoot(document.getElementById('root')).render(<Root />)
