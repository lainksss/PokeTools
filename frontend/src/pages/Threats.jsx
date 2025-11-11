import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import { useTranslation } from '../i18n/LanguageContext'

export default function Threats() {
  const { t, getPokemonName } = useTranslation()
  const [defender, setDefender] = useState(null)
  const [koMode, setKoMode] = useState('OHKO') // 'OHKO' or '2HKO'
  const [threats, setThreats] = useState([])
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [progress, setProgress] = useState({ processed: 0, total: 0, threats_found: 0 })
  const [useStreaming, setUseStreaming] = useState(true)
  const [showOnlyGuaranteed, setShowOnlyGuaranteed] = useState(false)
  const [minRolls, setMinRolls] = useState(1) // Minimum de rolls pour afficher (1-16)

  const ALL_WEATHERS = ['none', 'sun', 'rain', 'sandstorm', 'snow']
  const ALL_TERRAINS = ['none', 'grassy', 'electric', 'misty', 'psychic']

  async function findThreatsStreaming() {
    if (!defender) {
      alert(t('threats.noThreats'))
      return
    }

    setLoading(true)
    setThreats([])
    setProgress({ processed: 0, total: 0, threats_found: 0 })

    const payload = {
      defender: {
        pokemon_id: defender.id,
        base_stats: defender.base_stats,
        evs: defender.evs,
        nature: defender.nature,
        types: defender.types,
        ability: defender.ability,
        is_terastallized: defender.is_terastallized,
        tera_type: defender.tera_type
      },
      ko_mode: koMode,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
      }
    }

    try {
      const response = await fetch('/api/find_threats_stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const foundThreats = []

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6))
            
            if (data.type === 'init') {
              setProgress({ processed: 0, total: data.total, threats_found: 0 })
            } else if (data.type === 'threat') {
              foundThreats.push(data.data)
              setThreats([...foundThreats])
              setProgress(prev => ({ ...prev, threats_found: foundThreats.length }))
            } else if (data.type === 'progress') {
              setProgress({
                processed: data.processed,
                total: data.total,
                threats_found: data.threats_found
              })
            } else if (data.type === 'complete') {
              setProgress(prev => ({ 
                ...prev, 
                processed: data.total_processed,
                threats_found: data.total_threats 
              }))
            } else if (data.type === 'error') {
              throw new Error(data.message)
            }
          }
        }
      }
    } catch (e) {
      console.error('Error:', e)
      alert('Erreur: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  async function findThreats() {
    // Fonction de fallback sans streaming
    if (!defender) {
      alert('Veuillez sélectionner un Pokémon défenseur')
      return
    }

    setLoading(true)
    setThreats([])

    const payload = {
      defender: {
        pokemon_id: defender.id,
        base_stats: defender.base_stats,
        evs: defender.evs,
        nature: defender.nature,
        types: defender.types,
        ability: defender.ability,
        is_terastallized: defender.is_terastallized,
        tera_type: defender.tera_type
      },
      ko_mode: koMode,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
      }
    }

    try {
      const res = await fetch('/api/find_threats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.message || 'Erreur lors de la recherche')
      }

      const data = await res.json()
      setThreats(data.threats || [])
    } catch (e) {
      console.error('Error:', e)
      alert('Erreur: ' + e.message)
    } finally {
      setLoading(false)
    }
  }

  function handleSearch() {
    if (useStreaming) {
      findThreatsStreaming()
    } else {
      findThreats()
    }
  }

  return (
    <div className="threats-page">
      <div className="threats-header">
        <h2>{t('threats.title')}</h2>
        <p>{t('threats.subtitle')}</p>
      </div>

      <div className="threats-container">
        <div className="threats-left">
          <h3>{t('threats.defender')}</h3>
          <PokemonPanel 
            side="defender" 
            value={defender} 
            onChange={setDefender}
          />
        </div>

        <div className="threats-middle">
          <h3>{t('threats.conditions')}</h3>
          
          <div className="form-group">
            <label>{t('threats.koMode')}</label>
            <div className="ko-mode-toggle">
              <button
                type="button"
                className={`mode-button ${koMode === 'OHKO' ? 'active' : ''}`}
                onClick={() => setKoMode('OHKO')}
              >
                {t('threats.ohko')}
              </button>
              <button
                type="button"
                className={`mode-button ${koMode === '2HKO' ? 'active' : ''}`}
                onClick={() => setKoMode('2HKO')}
              >
                {t('threats.twohko')}
              </button>
            </div>
          </div>

          <div className="form-group">
            <label>{t('threats.weather')}</label>
            <select 
              value={weather}
              onChange={e => setWeather(e.target.value)}
              className="form-control"
            >
              {ALL_WEATHERS.map(w => (
                <option key={w} value={w}>
                  {t(`weather.${w}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>{t('threats.terrain')}</label>
            <select 
              value={terrain}
              onChange={e => setTerrain(e.target.value)}
              className="form-control"
            >
              {ALL_TERRAINS.map(ter => (
                <option key={ter} value={ter}>
                  {t(`terrain.${ter}`)}
                </option>
              ))}
            </select>
          </div>

          <button 
            onClick={handleSearch} 
            disabled={loading || !defender}
            className="calculate-button"
          >
            {loading ? t('threats.searching') : t('threats.findThreats')}
          </button>

          {loading && progress.total > 0 && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${(progress.processed / progress.total) * 100}%` }}
                />
              </div>
              <div className="progress-text">
                {progress.processed} / {progress.total} {t('threats.pokemonAnalyzed')}
                <br />
                {progress.threats_found} {t('threats.threatsFound')}
              </div>
            </div>
          )}
        </div>

        <div className="threats-right">
          <div className="threats-right-header">
            <h3>{t('threats.results')} ({threats.length} {t('threats.threats')})</h3>
            
            <div className="filters-group">
              <label className="guaranteed-filter">
                <input 
                  type="checkbox" 
                  checked={showOnlyGuaranteed}
                  onChange={(e) => setShowOnlyGuaranteed(e.target.checked)}
                />
                <span>{t('threats.guaranteedOnly')}</span>
              </label>
              
              <label className="rolls-filter">
                <span>{t('threats.minRolls')}:</span>
                <input 
                  type="number" 
                  min="1" 
                  max="16" 
                  value={minRolls}
                  onChange={(e) => setMinRolls(Math.max(1, Math.min(16, parseInt(e.target.value) || 1)))}
                />
                <span className="rolls-label">/ 16</span>
              </label>
            </div>
          </div>
          
          {loading && <p className="loading-text">{t('threats.analyzing')}</p>}
          
          {!loading && threats.length === 0 && (
            <p className="no-threats">{t('threats.noThreats')}</p>
          )}

          {!loading && threats.length > 0 && (
            <div className="threats-list">
              {threats
                .filter(threat => {
                  // Si le filtre "garantis seulement" est activé
                  if (showOnlyGuaranteed && threat.best_ko_percent !== 100) {
                    return false
                  }
                  
                  // Filtrer par nombre minimum de rolls
                  // Vérifier si au moins une attaque a >= minRolls
                  const hasEnoughRolls = threat.ko_attacks && threat.ko_attacks.some(
                    attack => attack.ko_rolls >= minRolls
                  )
                  
                  return hasEnoughRolls
                })
                .map((threat, idx) => (
                <div key={idx} className="threat-card">
                  <div className="threat-header">
                    <h4>{getPokemonName(threat.attacker_id, threat.attacker_name)}</h4>
                    <span className="threat-best-ko">{threat.best_ko_percent}% KO</span>
                  </div>
                  
                  <div className="threat-attacks">
                    {threat.ko_attacks && threat.ko_attacks.map((attack, attackIdx) => (
                      <div key={attackIdx} className="attack-info">
                        <div className="attack-name">
                          <strong>{attack.move_name}</strong>
                          <span className={`type-badge type-${attack.move_type}`}>
                            {t(`types.${attack.move_type}`)}
                          </span>
                          <span className={`damage-class ${attack.damage_class}`}>
                            {attack.damage_class === 'physical' ? '💪 ' : '✨ '}
                            {t(`threats.${attack.damage_class}`)}
                          </span>
                          {attack.move_power && <span className="attack-power">⚡{attack.move_power}</span>}
                        </div>
                        
                        <div className="attack-stats">
                          <div className="damage-range">
                            <span className="damage-label">{t('threats.damage')}:</span>
                            <span className="damage-values">{attack.damage_min} - {attack.damage_max}</span>
                          </div>
                          
                          <div className="ko-info">
                            <span className="ko-rolls">{attack.ko_rolls}/{attack.total_rolls} {t('threats.rolls')}</span>
                            <span className={`ko-percent ${attack.ko_percent === 100 ? 'guaranteed' : ''}`}>
                              {attack.ko_percent}%
                            </span>
                          </div>
                          
                          <div className="nature-info">
                            <span className="nature-label">{t('threats.nature')}:</span>
                            <span className="nature-value">{attack.nature_used}</span>
                          </div>
                        </div>
                        
                        {attack.ko_percent === 100 && (
                          <div className="guaranteed-badge">{t('threats.guaranteedKO')}</div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
