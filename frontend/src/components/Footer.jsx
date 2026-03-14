import React from 'react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="app-footer">
      <p>
        Made with <span className="heart">♥</span> by <strong>Lainkss</strong> · @lainkss on Discord
      </p>
      <p className="footer-meta">
        © {currentYear} PokeTools · Using <strong>PokéAPI</strong>
      </p>
    </footer>
  )
}
