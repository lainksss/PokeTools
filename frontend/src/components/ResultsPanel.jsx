import React from 'react'

export default function ResultsPanel({ result, showTitle = true }) {
  if (!result) {
    return (
      <div className="results-panel">
        <p className="no-results">No results — click Calculate</p>
      </div>
    )
  }

  // Calculate statistics
  const rolls = result.damage_all || []
  // Determine number of hits to display: prefer move.multi_hit.min, then move.hits, else 1
  const hitsCount = (() => {
    if (result.move) {
      const mh = result.move.multi_hit || {}
      if (mh && mh.min) return mh.min
      if (result.move.hits) return result.move.hits
    }
    return 1
  })()
  const remainingHP = result.remaining_hp_all || []
  const defenderHP = result.defender_hp || 0
  
  // OHKO: how many rolls kill in one hit
  const ohkoCount = rolls.filter(dmg => dmg >= defenderHP).length
  const ohkoChance = rolls.length > 0 ? (ohkoCount / rolls.length * 100) : 0
  
  // Number of hits needed to guarantee KO
  let hitsToGuaranteedKO = 1
  if (ohkoCount < rolls.length) {
    // Find minimum damage
    const minDamage = Math.min(...rolls)
    if (minDamage > 0) {
      hitsToGuaranteedKO = Math.ceil(defenderHP / minDamage)
    } else {
      hitsToGuaranteedKO = Infinity
    }
  }

  return (
    <div className="results-panel">
      {showTitle && <h3>Résultats</h3>}
      
      {/* Main statistics */}
      <div className="results-stats">
        {ohkoChance === 100 ? (
          <div className="ohko-guaranteed">
            ✓ OHKO garanti (100%)
          </div>
        ) : ohkoChance > 0 ? (
          <div className="ohko-chance">
            Chance de OHKO: <strong>{ohkoChance.toFixed(2)}%</strong> ({ohkoCount}/{rolls.length})
          </div>
        ) : (
          <div className="no-ohko">
            Pas de OHKO possible
          </div>
        )}
        
        {ohkoChance < 100 && hitsToGuaranteedKO !== Infinity && (
          <div className="hits-to-ko">
            Hits needed for 100% KO: <strong>{hitsToGuaranteedKO}</strong>
          </div>
        )}
      </div>

      {/* Rolls displayed as stats table */}
      {rolls.length > 0 && (
        <div className="damage-rolls">
          <h4>Possible damage</h4>
          {/* Multi-hit summary: show min/max totals using the minimum hit count */}
          {result.move && (result.move.multi_hit || result.move.hits) && (() => {
            const mh = result.move.multi_hit || {}
            const minHits = mh && mh.min ? mh.min : (result.move.hits || 1)
            const minRoll = Math.min(...rolls)
            const maxRoll = Math.max(...rolls)
            const minTotal = minRoll * minHits
            const maxTotal = maxRoll * minHits
            return (
              <div className="damage-range" style={{marginBottom:8}}>
                <div className="damage-label">Possible damage ({hitsCount} hits) :</div>
                <div className="damage-values">{minTotal} &nbsp;--&gt; &nbsp;{maxTotal}</div>
              </div>
            )
          })()}
          <div className="rolls-inline">
            {rolls.map((dmg, i) => {
              const hpLeft = remainingHP[i] !== undefined ? remainingHP[i] : '?'
              const isKO = hpLeft <= 0
              return (
                <div key={i} className={`roll-item ${isKO ? 'roll-ko' : ''}`}>
                  <span className="roll-damage">{dmg}</span>
                  <span className="roll-percent">
                    ({defenderHP > 0 ? `${(dmg / defenderHP * 100).toFixed(1)}%` : '—'})
                  </span>
                  <span className="roll-remaining">
                    → {hpLeft} HP
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {result.note && (
        <div className="result-note">{result.note}</div>
      )}
    </div>
  )
}
