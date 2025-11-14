import React from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter, Routes, Route } from 'react-router-dom'
import { LanguageProvider } from './i18n/LanguageContext'
import App from './App'
import Home from './pages/Home'
import Calculate from './pages/Calculate'
import Threats from './pages/Threats'
import Coverage from './pages/Coverage'
import TypeCoverage from './pages/TypeCoverage'
import SpeedChecker from './pages/SpeedChecker'
import './styles.css'

function Root() {
  return (
    <LanguageProvider>
      <HashRouter>
        <Routes>
          <Route path="/" element={<App />}>
            <Route index element={<Home />} />
            <Route path="calculate" element={<Calculate />} />
            <Route path="threats" element={<Threats />} />
            <Route path="coverage" element={<Coverage />} />
            <Route path="type-coverage" element={<TypeCoverage />} />
            <Route path="speed-checker" element={<SpeedChecker />} />
          </Route>
        </Routes>
      </HashRouter>
    </LanguageProvider>
  )
}

createRoot(document.getElementById('root')).render(<Root />)
