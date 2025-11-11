import React from 'react'
import { Outlet, Link } from 'react-router-dom'

export default function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Pokemon Tools</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/calculate">Calculate damages</Link>
          <Link to="/threats">Threats Analysis</Link>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
      <footer className="app-footer">Made by Lainkss</footer>
    </div>
  )
}
