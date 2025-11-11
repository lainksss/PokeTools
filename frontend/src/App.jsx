import React from 'react'
import { Outlet, Link } from 'react-router-dom'
import { useTranslation } from './i18n/LanguageContext'

export default function App() {
  const { t, language, changeLanguage } = useTranslation()
  
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Pokemon Tools</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/calculate">{t('nav.calculator')}</Link>
          <Link to="/threats">{t('nav.threats')}</Link>
        </nav>
        <div className="language-selector">
          <button 
            className={`lang-button ${language === 'fr' ? 'active' : ''}`}
            onClick={() => changeLanguage('fr')}
          >
            🇫🇷 FR
          </button>
          <button 
            className={`lang-button ${language === 'en' ? 'active' : ''}`}
            onClick={() => changeLanguage('en')}
          >
            🇬🇧 EN
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">Made by Lainkss</footer>
    </div>
  )
}
