import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { useTranslation } from '../i18n/LanguageContext'
import { useTheme } from '../ThemeContext'

export default function Header() {
  const { t, language, changeLanguage } = useTranslation()
  const { theme, toggleTheme } = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)

  const navLinks = [
    { to: '/', label: t('nav.home') || 'Home', end: true },
    { to: '/calculate', label: t('nav.calculator') || 'Calculator' },
    { to: '/threats', label: t('nav.threats') || 'Threats' },
    { to: '/coverage', label: t('nav.coverage') || 'Coverage' },
    { to: '/type-coverage', label: t('nav.typeCoverage') || 'Type Coverage' },
    { to: '/speed-checker', label: t('nav.speedChecker') || 'Speed Checker' },
    { to: '/speed-game', label: t('nav.speedGame') || 'Speed Duel' },
  ]

  const closeMenu = () => setMenuOpen(false)
  const toggleMenu = () => setMenuOpen(v => !v)

  return (
    <header className="app-header">
      <div className="header-inner">
        {/* Logo */}
        <div className="header-logo">
          <span className="logo-icon">◆</span>
          <span className="logo-text">PokeTools</span>
        </div>

        {/* Desktop Navigation */}
        <nav className="header-nav desktop-nav">
          {navLinks.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={closeMenu}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        {/* Controls (Language, Theme, Hamburger) */}
        <div className="header-controls">
          <div className="lang-toggle">
            <button
              className={`lang-btn ${language === 'fr' ? 'active' : ''}`}
              onClick={() => changeLanguage('fr')}
              title="Français"
            >
              FR
            </button>
            <button
              className={`lang-btn ${language === 'en' ? 'active' : ''}`}
              onClick={() => changeLanguage('en')}
              title="English"
            >
              EN
            </button>
          </div>

          <button
            className="theme-btn"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? '☀' : '☾'}
          </button>

          {/* Mobile Hamburger */}
          <button
            className={`hamburger ${menuOpen ? 'active' : ''}`}
            onClick={toggleMenu}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {menuOpen && (
        <nav className="header-nav mobile-nav">
          {navLinks.map(link => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={closeMenu}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      )}
    </header>
  )
}
