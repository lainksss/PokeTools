import React from 'react'

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <div className="results-panel">
        <p className="no-results">Aucun résultat — cliquez sur Calculer</p>
      </div>
    )
  }

  // Calculer les statistiques
  const rolls = result.damage_all || []
  const defenderHP = result.defender_hp || 0
  
  // OHKO: combien de rolls tuent en un coup
  const ohkoCount = rolls.filter(dmg => dmg >= defenderHP).length
  const ohkoChance = rolls.length > 0 ? (ohkoCount / rolls.length * 100) : 0
  
  // Nombre de hits nécessaires pour garantir le KO
  let hitsToGuaranteedKO = 1
  if (ohkoCount < rolls.length) {
    // Trouver le damage minimum
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
      
      {/* Statistiques principales */}
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
            Hits nécessaires pour KO à 100%: <strong>{hitsToGuaranteedKO}</strong>
          </div>
        )}
      </div>

      {/* Rolls affichés comme le tableau de stats */}
      {rolls.length > 0 && (
        <div className="damage-rolls">
          <h4>Dégâts possibles</h4>
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
