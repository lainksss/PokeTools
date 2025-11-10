import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import MiddlePanel from '../components/MiddlePanel'
import ResultsPanel from '../components/ResultsPanel'

export default function Calculate() {
  const [left, setLeft] = useState(null)
  const [right, setRight] = useState(null)
  const [result, setResult] = useState(null)

  return (
    <div className="calculate-page">
      <div className="panels-container">
        <div className="panel-left">
          <PokemonPanel side="left" value={left} onChange={setLeft} />
        </div>
        
        <div className="panel-middle">
          <MiddlePanel left={left} right={right} setResult={setResult} />
        </div>
        
        <div className="panel-right">
          <PokemonPanel side="right" value={right} onChange={setRight} />
        </div>
      </div>

      <div className="results-section">
        <ResultsPanel result={result} />
      </div>
    </div>
  )
}
