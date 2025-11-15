import React from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useTranslation } from './i18n/LanguageContext'

export default function App() {
  const { t, language, changeLanguage } = useTranslation()
  const [scale, setScale] = React.useState(() => {
    try { return localStorage.getItem('ui-scale') || 'normal' } catch { return 'normal' }
  })

  const scaleRef = React.useRef(null)
  const rootRef = React.useRef(null)

  React.useEffect(() => {
    try { localStorage.setItem('ui-scale', scale) } catch {}
  }, [scale])

  React.useEffect(() => {
    // Map the UI scale buttons to a desktop baseline width so you can
    // quickly adjust how 'large' the desktop layout is considered for scaling.
    const desktopWidth = scale === 'small' ? 900 : scale === 'large' ? 1400 : 1100
    const applyScale = () => {
      if (!scaleRef.current || !rootRef.current) return
      const vw = Math.max(document.documentElement.clientWidth, window.innerWidth || 0)
      if (vw < desktopWidth) {
        // Compute scale so the desktop baseline maps to the viewport width.
        // Apply a small multiplier <1 to leave tiny margins and avoid clipping.
        const s = Math.max(0.28, Math.min(1, (vw / desktopWidth) * 0.95))
        scaleRef.current.style.width = desktopWidth + 'px'
        scaleRef.current.style.transformOrigin = 'top center'
        // Position and translate so the scaled element is visually centered
        scaleRef.current.style.position = 'relative'
        scaleRef.current.style.left = '50%'
        scaleRef.current.style.transform = `translateX(-50%) scale(${s})`
        rootRef.current.classList.add('preserve-desktop')
        // hide horizontal overflow while scaled
        document.documentElement.style.overflowX = 'hidden'
        document.body.style.overflowX = 'hidden'
      } else {
        scaleRef.current.style.transform = ''
        scaleRef.current.style.width = ''
        scaleRef.current.style.position = ''
        scaleRef.current.style.left = ''
        rootRef.current.classList.remove('preserve-desktop')
        document.documentElement.style.overflowX = ''
        document.body.style.overflowX = ''
      }
    }
    applyScale()
    window.addEventListener('resize', applyScale)
    return () => window.removeEventListener('resize', applyScale)
  }, [scale])

  return (
    <div className="app-root" ref={rootRef}>
      <div className="app-scale" ref={scaleRef}>
      <header className="app-header">
        <h1>PokeTools</h1>
        <nav>
          <NavLink to="/" className={({isActive}) => isActive ? 'active' : ''}>Home</NavLink>
          <NavLink to="/calculate" className={({isActive}) => isActive ? 'active' : ''}>{t('nav.calculator')}</NavLink>
          <NavLink to="/threats" className={({isActive}) => isActive ? 'active' : ''}>{t('nav.threats')}</NavLink>
          <NavLink to="/coverage" className={({isActive}) => isActive ? 'active' : ''}>{t('nav.coverage') || 'Coverage'}</NavLink>
          <NavLink to="/type-coverage" className={({isActive}) => isActive ? 'active' : ''}>{t('nav.typeCoverage') || 'Type Coverage'}</NavLink>
          <NavLink to="/speed-checker" className={({isActive}) => isActive ? 'active' : ''}>{t('nav.speedChecker') || 'Speed Checker'}</NavLink>
        </nav>
        <div className="header-controls">
          <div className="display-scale" role="group" aria-label="Display scale">
            <button
              className={`scale-button ${scale === 'small' ? 'active' : ''}`}
              onClick={() => setScale('small')}
              title="Small UI"
            >S</button>
            <button
              className={`scale-button ${scale === 'normal' ? 'active' : ''}`}
              onClick={() => setScale('normal')}
              title="Normal UI"
            >M</button>
            <button
              className={`scale-button ${scale === 'large' ? 'active' : ''}`}
              onClick={() => setScale('large')}
              title="Large UI"
            >L</button>
          </div>

          <div className="language-selector">
            <button 
              className={`lang-button ${language === 'fr' ? 'active' : ''}`}
              onClick={() => changeLanguage('fr')}
              title="Français"
            >
              🇫🇷 FR
            </button>
            <button 
              className={`lang-button ${language === 'en' ? 'active' : ''}`}
              onClick={() => changeLanguage('en')}
              title="English"
            >
              🇬🇧 EN
            </button>
          </div>
        </div>
      </header>
      <main className={`app-main scale-${scale}`}>
        <Outlet />
      </main>
      <footer className="app-footer">Made by Lainkss (@lainkss on discord)</footer>
      </div>
    </div>
  )
}
