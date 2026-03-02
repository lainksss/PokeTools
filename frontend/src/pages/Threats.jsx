
import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'
import { convertEvsToOld, newEvToOld } from '../utils/evs'

export default function Threats() {
  const { t, getPokemonName, getMoveName } = useTranslation()
  const [defender, setDefender] = useState(null)
  const [koMode, setKoMode] = useState('OHKO') // 'OHKO' or '2HKO'
  const [threats, setThreats] = useState([])
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [reflect, setReflect] = useState(false)
  const [lightScreen, setLightScreen] = useState(false)
  const [auroraVeil, setAuroraVeil] = useState(false)
  const [progress, setProgress] = useState({ processed: 0, total: 0, threats_found: 0 })
  const [useStreaming, setUseStreaming] = useState(true)
  const [showOnlyGuaranteed, setShowOnlyGuaranteed] = useState(false)
  const [minRolls, setMinRolls] = useState(1) // Minimum de rolls pour afficher (1-16)

  // Attacker analysis options
  const [attackMode, setAttackMode] = useState('none') // 'default','none','custom','max' (default changed to 'none')
  const [customAttackEV, setCustomAttackEV] = useState(0)
  const [customNatureBoost, setCustomNatureBoost] = useState(false)
  const [customItemChoice, setCustomItemChoice] = useState(false)
  const [customLifeOrb, setCustomLifeOrb] = useState(false)

  const ALL_WEATHERS = ['none', 'sun', 'rain', 'sandstorm', 'snow']
  const ALL_TERRAINS = ['none', 'grassy', 'electric', 'misty', 'psychic']

  // Derived filtered threats according to current UI filters
  const filteredThreats = threats.filter(threat => {
    if (showOnlyGuaranteed) {
      const guaranteed = threat.guaranteed_ko === true || threat.best_ko_percent === 100 || (threat.ko_attacks && threat.ko_attacks.some(a => a.ko_percent === 100))
      if (!guaranteed) return false
    }

    if (minRolls > 1) {
      // Check per-attack ko_rolls or estimate from ko_percent
      if (threat.ko_attacks && threat.ko_attacks.some(a => {
        const total = a.total_rolls || 16
        const ko = a.ko_rolls != null ? a.ko_rolls : Math.round((a.ko_percent || 0) / 100 * total)
        return ko >= minRolls
      })) return true

      if (threat.ko_percent != null) {
        const total = 16
        const ko = Math.round((threat.ko_percent || 0) / 100 * total)
        if (ko >= minRolls) return true
      }

      return false
    }

    return true
  })

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
        evs: convertEvsToOld(defender.evs || {}),
        nature: defender.nature,
        types: defender.types,
        ability: defender.ability,
        item: defender.item || null,
        is_terastallized: defender.is_terastallized,
        tera_type: defender.tera_type
      },
      ko_mode: koMode,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
        ,
        reflect: reflect || undefined,
        light_screen: lightScreen || undefined,
        aurora_veil: auroraVeil || undefined
      }
      ,
      analysis_options: {
        attack_mode: attackMode,
        custom_evs: newEvToOld(customAttackEV),
        nature_boost: customNatureBoost,
        item_choice: customItemChoice,
        life_orb: customLifeOrb
      }
    }

    try {
        const response = await fetch(`${API_URL}/api/find_threats_stream`, {
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
        evs: convertEvsToOld(defender.evs || {}),
        nature: defender.nature,
        types: defender.types,
        ability: defender.ability,
        is_terastallized: defender.is_terastallized,
        tera_type: defender.tera_type
      },
      ko_mode: koMode,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain,
        reflect: reflect || undefined,
        light_screen: lightScreen || undefined,
        aurora_veil: auroraVeil || undefined
      }
      ,
      analysis_options: {
        attack_mode: attackMode,
        custom_evs: newEvToOld(customAttackEV),
        nature_boost: customNatureBoost,
        item_choice: customItemChoice,
        life_orb: customLifeOrb
      }
    }

    try {
  const res = await fetch(`${API_URL}/api/find_threats`, {
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
            showTitle={false}
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

          <div className="form-row">
            <div className="form-group">
              <select
                aria-label={t('threats.weather')}
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
              <select
                aria-label={t('threats.terrain')}
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
          </div>

          <div className="form-group" role="group" aria-label={t('calculate.screens')}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button type="button" className={`aura-button ${reflect ? 'active' : ''}`} onClick={() => setReflect(v => !v)}>
                {t('screens.reflect') || 'Protection'}
              </button>
              <button type="button" className={`aura-button ${lightScreen ? 'active' : ''}`} onClick={() => setLightScreen(v => !v)}>
                {t('screens.light') || 'Mur lumière'}
              </button>
              <button type="button" className={`aura-button ${auroraVeil ? 'active' : ''}`} onClick={() => setAuroraVeil(v => !v)}>
                {t('screens.aurora') || 'Voile Aurore'}
              </button>
            </div>
          </div>

          {/* Analysis options: horizontal buttons inspired by SpeedChecker */}
          <div className="form-group">
            <label>{t('threats.attackOptions') || 'Attacker Options'}</label>
            <div className="analysis-options">
              <button
                type="button"
                className={`tailwind-button small option-button ${attackMode === 'none' ? 'active' : ''}`}
                onClick={() => {
                  setAttackMode('none')
                  setCustomAttackEV(0)
                  setCustomNatureBoost(false)
                  setCustomItemChoice(false)
                  setCustomLifeOrb(false)
                }}
              >
                {t('threats.noAttack') || "Pas d'attaque"}
              </button>

              <button
                type="button"
                className={`tailwind-button large option-button ${attackMode === 'custom' ? 'active' : ''}`}
                onClick={() => setAttackMode(prev => prev === 'custom' ? 'default' : 'custom')}
              >
                {t('threats.custom') || 'Personnalisé'}
              </button>

              <button
                type="button"
                className={`tailwind-button small option-button ${attackMode === 'max' ? 'active' : ''}`}
                onClick={() => {
                  setAttackMode('max')
                  setCustomAttackEV(252)
                  setCustomNatureBoost(true)
                }}
              >
                {t('threats.maxAtk') || 'Max Atk/SpA'}
              </button>
            </div>

            {/* Custom sub-options shown only when 'custom' is active */}
            {attackMode === 'custom' && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <label style={{ minWidth: 180 }}>{t('threats.customEVLabel') || 'EVs to assign (Atk & SpA each):'}</label>
                  <input
                    type="number"
                    min="0"
                    max="252"
                    value={customAttackEV}
                    onChange={(e) => setCustomAttackEV(Math.max(0, Math.min(252, parseInt(e.target.value) || 0)))}
                  />
                </div>

                <div style={{ marginTop: 8, display: 'flex', gap: 8, alignItems: 'center' }}>
                    <button
                      type="button"
                      className={`tailwind-button option-button ${customNatureBoost ? 'active' : ''}`}
                      onClick={() => setCustomNatureBoost(prev => !prev)}
                    >
                      {t('threats.natureBoost') || '+ Atk/SpA nature'}
                    </button>

                    <button
                      type="button"
                      className={`tailwind-button option-button ${customItemChoice ? 'active' : ''}`}
                      onClick={() => {
                        setCustomItemChoice(prev => !prev)
                        if (!customItemChoice) setCustomLifeOrb(false)
                      }}
                    >
                      {t('threats.itemChoice') || 'Item Choix'}
                    </button>

                    <button
                      type="button"
                      className={`tailwind-button option-button ${customLifeOrb ? 'active' : ''}`}
                      onClick={() => {
                        setCustomLifeOrb(prev => !prev)
                        if (!customLifeOrb) setCustomItemChoice(false)
                      }}
                    >
                      {t('threats.lifeOrb') || 'Orbe Vie'}
                    </button>
                </div>
              </div>
            )}

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
                {filteredThreats.length} {t('threats.threatsFound')}
              </div>
            </div>
          )}
        </div>

        <div className="threats-right">
          <div className="threats-right-header">
            <h3>{t('threats.results')} ({filteredThreats.length} {t('threats.threats')})</h3>
            
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
              {filteredThreats.map((threat, idx) => (
                <div key={idx} className="threat-card">
                  <div className="threat-header">
                    <h4>{getPokemonName(threat.attacker_id, threat.attacker_name)}</h4>
                    <span className="threat-best-ko">{threat.best_ko_percent}% KO</span>
                  </div>
                  
                  <div className="threat-attacks">
                    {threat.ko_attacks && threat.ko_attacks.map((attack, attackIdx) => (
                      <div key={attackIdx} className="attack-info">
                        <div className="attack-name">
                          <strong>{getMoveName(attack.move_name, attack.move_name)}</strong>
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
