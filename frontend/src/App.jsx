import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Pokemon for nerds</h1>
        <nav>
          <Link to="/">Accueil</Link>
          <Link to="/calculate">Calculate damages</Link>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">made by Lainkss</footer>
    </div>
  )
}
