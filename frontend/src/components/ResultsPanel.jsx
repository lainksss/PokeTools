import React from 'react'

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <div className="results-panel">
        <p className="no-results">No results — click Calculate</p>
      </div>
    )
  }

  // Calculate statistics
  const rolls = result.damage_all || []
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
      <h3>Résultats</h3>
      
      {/* Main statistics */}
      <div className="results-stats">
        {ohkoChance === 100 ? (
          <div className="ohko-guaranteed">
            ✓ OHKO garanti (100%)
          </div>
        ) : ohkoChance > 0 ? (
          <div className="ohko-chance">
            Chance de OHKO: <strong>{ohkoChance.toFixed(1)}%</strong> ({ohkoCount}/{rolls.length})
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
          <div className="rolls-table">
            {rolls.map((dmg, i) => (
              <div key={i} className="roll-row">
                <div className="roll-number">Roll {i + 1}</div>
                <div className="roll-damage">{dmg}</div>
                <div className="roll-percent">
                  {defenderHP > 0 ? `${(dmg / defenderHP * 100).toFixed(1)}%` : '—'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.note && (
        <div className="result-note">{result.note}</div>
      )}
    </div>
  )
}
