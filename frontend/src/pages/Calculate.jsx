import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import MiddlePanel from '../components/MiddlePanel'
import ResultsPanel from '../components/ResultsPanel'

export default function Calculate() {
  const [left, setLeft] = useState(null)
  const [right, setRight] = useState(null)
  const [params, setParams] = useState({ weather: 'none', terrain: 'none', targets: 2 })
  const [result, setResult] = useState(null)

  return (
    <div className="calculate-page layout">
      <div className="side left">
        <PokemonPanel side="left" value={left} onChange={setLeft} />
      </div>
      <div className="center">
        <MiddlePanel params={params} setParams={setParams} left={left} right={right} setResult={setResult} />
      </div>
      <div className="side right">
        <PokemonPanel side="right" value={right} onChange={setRight} />
      </div>

      <div className="results-area">
        <ResultsPanel result={result} />
      </div>
    </div>
  )
}
