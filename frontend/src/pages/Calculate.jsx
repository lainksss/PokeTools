import React, { useState, useEffect } from 'react'
import { createPortal } from 'react-dom'
import PokemonPanel from '../components/PokemonPanel'
import MiddlePanel from '../components/MiddlePanel'
import ResultsPanel from '../components/ResultsPanel'

export default function Calculate() {
  const [left, setLeft] = useState(null)
  const [right, setRight] = useState(null)
  const [result, setResult] = useState(null)
  const [resultsCollapsed, setResultsCollapsed] = useState(false)

  useEffect(() => {
    // When a new result appears, expand the results panel by default
    if (result) setResultsCollapsed(false)
  }, [result])

  return (
    <div className="calculate-page">
      <div className="panels-container">
        <div className="panel-left">
          <PokemonPanel side="left" value={left} onChange={setLeft} showMultipleMoves={false} />
        </div>
        
        <div className="panel-middle">
          <MiddlePanel left={left} right={right} setLeft={setLeft} setRight={setRight} setResult={setResult} />
        </div>
        
        <div className="panel-right">
          <PokemonPanel side="right" value={right} onChange={setRight} />
        </div>
      </div>

      {result && createPortal(
        <div className={`results-section ${resultsCollapsed ? 'collapsed' : ''}`}>
          <div className="results-header">
            <div className="results-header-left">
              <strong className="results-title">Résultats</strong>
            </div>
            <div className="results-header-right">
              <button
                type="button"
                className="collapse-btn"
                onClick={() => setResultsCollapsed(prev => !prev)}
                aria-expanded={!resultsCollapsed}
              >
                {resultsCollapsed ? 'Afficher' : 'Masquer'}
              </button>
            </div>
          </div>

          {!resultsCollapsed && (
            <div className="results-content">
              <ResultsPanel result={result} showTitle={false} />
            </div>
          )}
        </div>,
        document.body
      )}
    </div>
  )
}
