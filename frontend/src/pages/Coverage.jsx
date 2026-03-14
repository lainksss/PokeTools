
import React, { useState } from 'react'
import PokemonPanel from '../components/PokemonPanel'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'
import { convertEvsToOld, newEvToOld } from '../utils/evs'
import { getMandatoryItem } from '../utils/getMandatoryItem'

export default function Coverage() {
  const { t, getPokemonName, getMoveName } = useTranslation()
  const [attacker, setAttacker] = useState(null)
  const [koMode, setKoMode] = useState('OHKO') // 'OHKO' or '2HKO'
  const [allResults, setAllResults] = useState([]) // TOUS les résultats (KO + non-KO)
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [fairyAura, setFairyAura] = useState(false)
  const [darkAura, setDarkAura] = useState(false)
  const [auraBreak, setAuraBreak] = useState(false)
  const [reflect, setReflect] = useState(false)
  const [lightScreen, setLightScreen] = useState(false)
  const [auroraVeil, setAuroraVeil] = useState(false)
  const [helpingHand, setHelpingHand] = useState(false)
  const [friendGuard, setFriendGuard] = useState(false)
  const [progress, setProgress] = useState({ processed: 0, total: 0, coverage_found: 0 })
  const [showOnlyGuaranteed, setShowOnlyGuaranteed] = useState(false)
  const [minRolls, setMinRolls] = useState(1)
  const [viewMode, setViewMode] = useState('ko') // 'ko' = afficher ceux qui sont KO, 'alive' = afficher ceux qui survivent
  const [bulkMode, setBulkMode] = useState('none') // 'none', 'custom', 'max'
  const [customEvs, setCustomEvs] = useState(0) // EVs personnalisés pour le mode custom (appliqués both Def & SpDef)
  const [customHpEvs, setCustomHpEvs] = useState(0) // EVs en PV pour bulk custom
  const [bulkAdaptNature, setBulkAdaptNature] = useState(true) // true => adapt nature by move, false => use Def
  const [bulkAssaultVest, setBulkAssaultVest] = useState(false)
  const [bulkEvoluroc, setBulkEvoluroc] = useState(false)
  const [fullyEvolvedOnly, setFullyEvolvedOnly] = useState(false)

  const ALL_WEATHERS = ['none', 'sun', 'rain', 'sandstorm', 'snow']
  const ALL_TERRAINS = ['none', 'grassy', 'electric', 'misty', 'psychic']

  async function analyzeCoverageWithMode(includeNoKO) {
    if (!attacker) {
      alert('Veuillez sélectionner un Pokémon attaquant')
      return
    }

      // Allow any of the 4 move slots to be used (slot 1..4)
      const hasAnyMove = attacker && (attacker.move || attacker.move2 || attacker.move3 || attacker.move4)
      if (!hasAnyMove) {
      alert('Veuillez sélectionner au moins une attaque')
      return
    }

    setLoading(true)
    setAllResults([])
    setProgress({ processed: 0, total: 0, coverage_found: 0 })

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
      attacker: {
        pokemon_id: attacker.id,
        base_stats: attacker.base_stats,
        evs: convertEvsToOld(attacker.evs || {}),
        nature: attacker.nature,
        types: attacker.types,
        ability: attacker.ability,
        item: attacker.item || null,
        is_terastallized: attacker.is_terastallized,
        tera_type: attacker.tera_type,
        stages: attacker.boosts || {},
        name: attacker.name
      },
      moves: moves,
      ko_mode: koMode,
      include_no_ko: true, // TOUJOURS récupérer tous les Pokémon
      bulk_mode: bulkMode,
      custom_def_evs: newEvToOld(customEvs),
      custom_spdef_evs: newEvToOld(customEvs),
      custom_hp_evs: newEvToOld(customHpEvs),
      bulk_nature_mode: bulkAdaptNature ? 'byMove' : 'def',
      bulk_assault_vest: bulkAssaultVest,
      bulk_evoluroc: bulkEvoluroc,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
        ,
        fairy_aura: fairyAura || undefined,
        dark_aura: darkAura || undefined,
        aura_break: auraBreak || undefined,
        reflect: reflect || undefined,
        light_screen: lightScreen || undefined,
        aurora_veil: auroraVeil || undefined,
        helping_hand: helpingHand || undefined,
        friend_guard: friendGuard || undefined
      }
      ,
      fully_evolved_only: fullyEvolvedOnly
    }

    // Force mandatory item for attacker (mega-gem, primal-gem)
    const mandatoryItemCov = getMandatoryItem(payload.attacker.name)
    if (mandatoryItemCov) {
      payload.attacker.item = mandatoryItemCov
    }

    try {
        const response = await fetch(`${API_URL}/api/analyze_coverage_stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Erreur lors de l\'analyse')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const foundCoverage = []

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
              setProgress({ processed: 0, total: data.total, coverage_found: 0 })
            } else if (data.type === 'coverage') {
              foundCoverage.push(data.data)
              setAllResults([...foundCoverage])
              setProgress(prev => ({ ...prev, coverage_found: foundCoverage.length }))
            } else if (data.type === 'progress') {
              setProgress({
                processed: data.processed,
                total: data.total,
                coverage_found: data.coverage_found
              })
            } else if (data.type === 'complete') {
              setProgress(prev => ({ 
                ...prev, 
                processed: data.total_processed,
                coverage_found: data.total_coverage 
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

  async function analyzeCoverageStreaming() {
    // Appeler la fonction principale (qui récupère toujours tous les résultats)
    await analyzeCoverageWithMode(true)
  }

  async function deepAnalyzeCoverageStreaming() {
    if (!attacker) {
      alert('Veuillez sélectionner un Pokémon attaquant')
      return
    }

      // Allow any of the 4 move slots to be used (slot 1..4)
      const hasAnyMove = attacker && (attacker.move || attacker.move2 || attacker.move3 || attacker.move4)
      if (!hasAnyMove) {
      alert('Veuillez sélectionner au moins une attaque')
      return
    }

    setLoading(true)
    setAllResults([])
    setProgress({ processed: 0, total: 0, coverage_found: 0 })

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
      attacker: {
        pokemon_id: attacker.id,
        base_stats: attacker.base_stats,
        evs: convertEvsToOld(attacker.evs || {}),
        nature: attacker.nature,
        types: attacker.types,
        ability: attacker.ability,
        item: attacker.item || null,
        is_terastallized: attacker.is_terastallized,
        tera_type: attacker.tera_type,
        stages: attacker.boosts || {},
        name: attacker.name
      },
      moves: moves,
      ko_mode: koMode,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain,
        fairy_aura: fairyAura || undefined,
        dark_aura: darkAura || undefined,
        aura_break: auraBreak || undefined,
        reflect: reflect || undefined,
        light_screen: lightScreen || undefined,
        aurora_veil: auroraVeil || undefined
      },
      fully_evolved_only: fullyEvolvedOnly
    }

    // Force mandatory item for attacker (mega-gem, primal-gem)
    const mandatoryItemDeepCov = getMandatoryItem(payload.attacker.name)
    if (mandatoryItemDeepCov) {
      payload.attacker.item = mandatoryItemDeepCov
    }

    try {
      const response = await fetch(`${API_URL}/api/deep_analyze_coverage_stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche approfondie')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const foundCoverage = []

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
              setProgress({ processed: 0, total: data.total, coverage_found: 0 })
            } else if (data.type === 'coverage') {
              foundCoverage.push(data.data)
              setAllResults([...foundCoverage])
              setProgress(prev => ({ ...prev, coverage_found: foundCoverage.length }))
            } else if (data.type === 'progress') {
              setProgress({
                processed: data.processed,
                total: data.total,
                coverage_found: data.coverage_found
              })
            } else if (data.type === 'complete') {
              setProgress(prev => ({ 
                ...prev, 
                processed: data.total_processed,
                coverage_found: data.total_coverage 
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

  // Filtrer les résultats selon le mode d'affichage
  const coverage = allResults.filter(item => {
    // Vérifier si l'un des moves a un KO% positif (pire cas)
    const hasAnyKO = item.moves?.some(m => (m.worst_ko_percent || 0) > 0)
    
    // Si mode 'alive' : afficher ceux qui NE sont PAS KO dans le pire cas
    if (viewMode === 'alive') {
      return !hasAnyKO
    }
    // Si mode 'ko' : afficher ceux qui PEUVENT être KO dans le pire cas
    return hasAnyKO
  })

  // Filtrer davantage selon les autres critères
  const filteredCoverage = coverage.filter(item => {
    // Si on veut voir seulement les KO garantis (seulement en mode 'ko')
    if (viewMode === 'ko' && showOnlyGuaranteed) {
      const hasGuaranteed = item.moves?.some(m => m.worst_ko_percent === 100)
      return hasGuaranteed
    }
    return true
  })

  return (
    <div className="threats-page">

      <div className="threats-container">
        <div className="threats-left">
          <h3>{t('calculate.attacker')}</h3>
          <PokemonPanel 
            side="left" 
            value={attacker} 
            onChange={setAttacker} 
            showMultipleMoves={true}
            showTitle={false}
          />
        </div>

        <div className="threats-middle">
          <h3>{t('coverage.analysisSettings')}</h3>
          
          <div className="form-group" aria-label={t('threats.koMode')}>
            <div className="ko-mode-toggle">
              <button
                type="button"
                className={`mode-button ${koMode === 'OHKO' ? 'active' : ''}`}
                onClick={() => setKoMode('OHKO')}
              >
                OHKO
              </button>
              <button
                type="button"
                className={`mode-button ${koMode === '2HKO' ? 'active' : ''}`}
                onClick={() => setKoMode('2HKO')}
              >
                2HKO
              </button>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <select
                aria-label={t('calculate.weather')}
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
                aria-label={t('calculate.terrain')}
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


          <div className="form-group" role="group" aria-label={t('calculate.auras')}>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button type="button" className={`aura-button ${fairyAura ? 'active' : ''}`} onClick={() => setFairyAura(v => !v)}>
                {t('auras.fairy') || 'Fairy Aura'}
              </button>
              <button type="button" className={`aura-button ${darkAura ? 'active' : ''}`} onClick={() => setDarkAura(v => !v)}>
                {t('auras.dark') || 'Dark Aura'}
              </button>
              <button type="button" className={`aura-button ${auraBreak ? 'active' : ''}`} onClick={() => setAuraBreak(v => !v)}>
                {t('auras.break') || 'Aura Break'}
              </button>
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

          <div className="form-group" role="group" aria-label={t('calculate.doubleEffects')}>
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
              <button type="button" className={`aura-button ${helpingHand ? 'active' : ''}`} onClick={() => setHelpingHand(v => !v)}>
                {t('doubleEffects.helpingHand') || 'Helping Hand'}
              </button>
              <button type="button" className={`aura-button ${friendGuard ? 'active' : ''}`} onClick={() => setFriendGuard(v => !v)}>
                {t('doubleEffects.friendGuard') || 'Friend Guard'}
              </button>
            </div>
          </div>

          <div className="form-group" style={{ marginTop: 8 }}>
            <button
              type="button"
              className={`tailwind-button option-button ${fullyEvolvedOnly ? 'active' : ''}`}
              onClick={() => setFullyEvolvedOnly(v => !v)}
            >
              {t('coverage.fullyEvolvedOnly') || 'Fully evolved only'}
            </button>
          </div>

          {/* Bulk mode selector moved under Fully Evolved Only and using aura-button CSS */}
          <div className="form-group">
            <label>{t('coverage.bulkMode')}</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                className={`aura-button ${bulkMode === 'none' ? 'active' : ''}`}
                onClick={() => setBulkMode('none')}
              >
                {t('coverage.bulkNone')}
              </button>

              <button
                type="button"
                className={`aura-button ${bulkMode === 'custom' ? 'active' : ''}`}
                onClick={() => setBulkMode('custom')}
              >
                {t('coverage.bulkCustom')}
              </button>

              <button
                type="button"
                className={`aura-button ${bulkMode === 'max' ? 'active' : ''}`}
                onClick={() => setBulkMode('max')}
              >
                {t('coverage.bulkMax')}
              </button>
            </div>
          </div>

          {bulkMode === 'custom' && (
            <div className="form-group">
              <label>{t('coverage.customEvs')}</label>
              <div className="ev-input-row">
                <input 
                  type="number" 
                  min="0" 
                  max="32" 
                  step="1"
                  value={customEvs}
                  onChange={e => {
                    const val = parseInt(e.target.value) || 0
                    setCustomEvs(Math.min(32, Math.max(0, val)))
                  }}
                  className="form-control ev-compact-left"
                  placeholder="Def/SpDef EVs"
                />

                <input
                  type="number"
                  min="0"
                  max="32"
                  step="1"
                  value={customHpEvs}
                  onChange={e => setCustomHpEvs(Math.min(32, Math.max(0, parseInt(e.target.value) || 0)))}
                  className="form-control ev-compact-right"
                  placeholder="HP EVs"
                />
              </div>
            </div>
          )}

          {bulkMode === 'custom' && (
            <div className="form-group">
              <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                <button
                  type="button"
                  className={`tailwind-button option-button ${bulkAdaptNature ? 'active' : ''}`}
                  onClick={() => setBulkAdaptNature(prev => !prev)}
                >
                  {t('coverage.natureDefSpDef') || 'Nature def/spe def'}
                </button>

                <button
                  type="button"
                  className={`tailwind-button option-button ${bulkAssaultVest ? 'active' : ''}`}
                  onClick={() => setBulkAssaultVest(prev => !prev)}
                >
                  {t('coverage.assaultVest') || 'Veste de Combat'}
                </button>

                <button
                  type="button"
                  className={`tailwind-button option-button ${bulkEvoluroc ? 'active' : ''}`}
                  onClick={() => setBulkEvoluroc(prev => !prev)}
                >
                  {t('coverage.evoluroc') || 'Evoluroc'}
                </button>
              </div>
            </div>
          )}

          

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button 
              onClick={analyzeCoverageStreaming} 
              disabled={loading || !attacker}
              className="calculate-button"
            >
              {loading ? t('common.loading') : t('coverage.analyze')}
            </button>

            <button 
              onClick={deepAnalyzeCoverageStreaming} 
              disabled={loading || !attacker}
              className="calculate-button"
              title="Teste tous les talents et statuts des adversaires"
            >
              {loading ? t('common.loading') : 'Recherche approfondie'}
            </button>
          </div>

          {loading && progress.total > 0 && (
            <div className="progress-container">
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${progress.total > 0 ? (progress.processed / progress.total * 100) : 0}%` }}
                />
              </div>
              <div className="progress-text">
                {t('threats.analyzing')}: {progress.processed} / {progress.total}
                <br />
                {t('coverage.found')}: {progress.coverage_found}
              </div>
            </div>
          )}
        </div>

        <div className="threats-right">
          <div className="threats-right-header">
            <h3>{t('coverage.results')} ({filteredCoverage.length} / {coverage.length})</h3>
            
            <div className="filters-group">
              <label className="guaranteed-filter">
                <input 
                  type="checkbox" 
                  checked={viewMode === 'alive'}
                  onChange={(e) => setViewMode(e.target.checked ? 'alive' : 'ko')}
                />
                <span>{t('coverage.showAlive')}</span>
              </label>
              
              {viewMode === 'ko' && (
                <>
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
                </>
              )}
            </div>
          </div>
          
          {loading && <p className="loading-text">{t('threats.analyzing')}</p>}
          
          {!loading && (filteredCoverage.length === 0) && (
            <p className="no-threats">{t('coverage.noCoverage')}</p>
          )}

          {!loading && filteredCoverage.length > 0 && (
            <div className="threats-list">
              {filteredCoverage.map((item, idx) => (
                <CoverageItem key={idx} item={item} koMode={koMode} t={t} getPokemonName={getPokemonName} getMoveName={getMoveName} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function CoverageItem({ item, koMode, t, getPokemonName, getMoveName }) {
  // Get the best move (highest worst_ko_percent)
  const bestMove = item.moves?.length > 0 ? item.moves[0] : null
  const maxChance = bestMove?.worst_ko_percent || 0
  const isGuaranteed = maxChance === 100

  return (
    <div className="threat-card">
      <div className="threat-header">
        <div className="threat-name-types">
          <h4>{getPokemonName(item.defender_id, item.defender_name)}</h4>
          <div className="threat-types">
            {item.defender_types?.map(type => (
              <span key={type} className={`type-badge type-${type}`}>
                {t(`types.${type}`)}
              </span>
            ))}
          </div>
        </div>
        <span className="threat-best-ko">{maxChance.toFixed(1)}% {koMode}</span>
      </div>

      <div className="threat-attacks">
        {item.moves?.map((move, idx) => (
          <div key={idx} className="attack-info">
            <div className="attack-name">
              <strong>{getMoveName(move.name, move.name)}</strong>
              <span className={`type-badge type-${move.type}`}>
                {t(`types.${move.type}`)}
              </span>
            </div>

            <div className="attack-stats">
              <div className="damage-range">
                <span className="damage-label">{t('threats.damage')}:</span>
                <span className="damage-values">
                  {move.damage_min} - {move.damage_max}
                </span>
                {move.defender_hp && (
                  <span className="damage-percent">
                    ({((move.damage_min / move.defender_hp) * 100).toFixed(1)}% - {((move.damage_max / move.defender_hp) * 100).toFixed(1)}%)
                  </span>
                )}
              </div>

              <div className="ko-info">
                <span className={`ko-percent ${move.worst_ko_percent === 100 ? 'guaranteed' : ''}`}>
                  {move.worst_ko_percent.toFixed(1)}% {koMode}
                </span>
              </div>
            </div>

            {move.worst_ko_percent === 100 && (
              <div className="guaranteed-badge">{koMode} {t('threats.guaranteedKO')}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
