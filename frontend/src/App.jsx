import React from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import { useTranslation } from './i18n/LanguageContext'

export default function App() {
  const { t, language, changeLanguage } = useTranslation()
  const [scale, setScale] = React.useState(() => {
    try { return localStorage.getItem('ui-scale') || 'normal' } catch { return 'normal' }
  })

  React.useEffect(() => {
    try { localStorage.setItem('ui-scale', scale) } catch {}
  }, [scale])

  return (
    <div className="app-root">
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
  )
}
