import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import { useTranslation } from '../i18n/LanguageContext'

export default function TypeCoverage() {
  const { t, getPokemonName } = useTranslation()
  const [attacker, setAttacker] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  async function analyzeTypeCoverage() {
    if (!attacker) {
      alert('Veuillez sélectionner un Pokémon attaquant')
      return
    }

    if (!attacker.move) {
      alert('Veuillez sélectionner au moins une attaque')
      return
    }

    setLoading(true)
    setResults([])

    // Récupérer les 4 attaques sélectionnées
    const moves = [
      attacker.move,
      attacker.move2,
      attacker.move3,
      attacker.move4
    ].filter(m => m !== null && m !== undefined)

    if (moves.length === 0) {
      alert('Veuillez sélectionner au moins une attaque')
      setLoading(false)
      return
    }

    const payload = {
      moves: moves,
      attacker: {
        is_terastallized: attacker.is_terastallized || false,
        tera_type: attacker.tera_type || null
      }
    }

    try {
      const response = await fetch('/api/analyze_type_coverage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Erreur lors de l\'analyse')
      }

      const data = await response.json()
      setResults(data.not_super_effective || [])
    } catch (e) {
      console.error('Error:', e)
      alert('Erreur: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="threats-page">
      <div className="threats-header">
        <h2>{t('typeCoverage.title')}</h2>
        <p>{t('typeCoverage.description')}</p>
      </div>

      <div className="threats-container">
        <div className="threats-left">
          <h3>{t('calculate.attacker')}</h3>
          <PokemonPanel 
            side="left" 
            value={attacker} 
            onChange={setAttacker} 
            showMultipleMoves={true} 
          />
        </div>

        <div className="threats-middle">
          <h3>{t('typeCoverage.analysisSettings')}</h3>
          
          <button 
            onClick={analyzeTypeCoverage} 
            disabled={loading || !attacker}
            className="calculate-button"
          >
            {loading ? t('common.loading') : t('typeCoverage.analyze')}
          </button>
        </div>

        <div className="threats-right">
          <h3>{t('typeCoverage.results')}</h3>
          {results.length === 0 ? (
            <p className="no-results">{t('typeCoverage.noResults')}</p>
          ) : (
            <div className="threats-results">
              <div className="threats-summary">
                {t('typeCoverage.foundCount')}: {results.length}
              </div>
              <div className="threats-list">
                {results.map((item, idx) => (
                  <div key={idx} className="threat-item">
                    <div className="threat-pokemon">
                      <strong>{getPokemonName(item.pokemon_id, item.pokemon_name)}</strong>
                      <div className="pokemon-types">
                        {item.types.map(type => (
                          <span key={type} className={`type-badge type-${type.toLowerCase()}`}>
                            {t(`types.${type.toLowerCase()}`)}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="type-coverage-info">
                      <div className="best-effectiveness">
                        {t('typeCoverage.bestEffectiveness')}: <strong>×{item.best_effectiveness.toFixed(2)}</strong>
                      </div>
                      {item.best_move && (
                        <div className="best-move-info">
                          <span className={`type-badge type-${item.best_move_type.toLowerCase()}`}>
                            {t(`types.${item.best_move_type.toLowerCase()}`)}
                          </span>
                          <span>{item.best_move}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
