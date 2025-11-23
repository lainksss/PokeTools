
import React, { useState } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'

const ALL_WEATHERS = [
  'none', 'sun', 'rain', 'sandstorm', 'snow'
]

const ALL_TERRAINS = [
  'none', 'grassy', 'electric', 'misty', 'psychic'
]

const ALL_STATUSES = [
  'none', 'burn', 'poison', 'paralysis'
]

export default function MiddlePanel({ left, right, setLeft, setRight, setResult }) {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [attackerStatus, setAttackerStatus] = useState('none')
  const [defenderStatus, setDefenderStatus] = useState('none')
  const [isCritical, setIsCritical] = useState(false)
  const [battleMode, setBattleMode] = useState('double') // 'single' or 'double'
  const [fairyAura, setFairyAura] = useState(false)
  const [darkAura, setDarkAura] = useState(false)
  const [auraBreak, setAuraBreak] = useState(false)

  // Keep local selectors synced with parent left/right values when available
  React.useEffect(() => {
    try { setAttackerStatus(left?.status || 'none') } catch (e) {}
  }, [left && left.status])

  React.useEffect(() => {
    try { setDefenderStatus(right?.status || 'none') } catch (e) {}
  }, [right && right.status])

  // When user changes the status selects, propagate into left/right via setters
  React.useEffect(() => {
    if (typeof setLeft === 'function' && left) {
      setLeft(prev => ({ ...(prev || {}), status: attackerStatus === 'none' ? null : attackerStatus }))
    }
  }, [attackerStatus])

  React.useEffect(() => {
    if (typeof setRight === 'function' && right) {
      setRight(prev => ({ ...(prev || {}), status: defenderStatus === 'none' ? null : defenderStatus }))
    }
  }, [defenderStatus])

  async function calculate() {
    if (!left || !right) {
      alert(t('calculate.selectPokemonError'))
      return
    }

    if (!left.move) {
      alert(t('calculate.selectMoveError'))
      return
    }

    setLoading(true)
    
    const payload = {
      attacker: {
        pokemon_id: left.id,
        base_stats: left.base_stats,
        evs: left.evs,
        nature: left.nature,
        types: left.types,
        ability: left.ability,
        item: left.item || null,
        is_terastallized: left.is_terastallized,
        tera_type: left.tera_type,
        stages: left.boosts || {}
      ,
        status: attackerStatus === 'none' ? null : attackerStatus
      },
      defender: {
        pokemon_id: right.id,
        base_stats: right.base_stats,
        evs: right.evs,
        nature: right.nature,
        types: right.types,
        ability: right.ability,
        item: right.item || null,
        is_terastallized: right.is_terastallized,
        tera_type: right.tera_type,
        stages: right.boosts || {}
      ,
        status: defenderStatus === 'none' ? null : defenderStatus
      },
      move: left.move,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
        ,
        fairy_aura: fairyAura || undefined,
        dark_aura: darkAura || undefined,
        aura_break: auraBreak || undefined
      },
      is_critical: isCritical,
      battle_mode: battleMode,
      debug: true
    }

    try {
        const res = await fetch(`${API_URL}/api/calc_damage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      
      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.message || 'Calculation error')
      }
      
      const data = await res.json()
      setResult(data)
    } catch (e) {
      console.error('Error:', e)
      alert('Calculation error: ' + e.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="middle-panel">
      <h3>{t('calculate.battleConditions')}</h3>
      
      <div className="form-group" role="group" aria-label={t('calculate.battleMode')}>
        <div className="battle-mode-toggle" role="group" aria-label={t('calculate.battleMode')}>
          <button
            type="button"
            className={`mode-button ${battleMode === 'single' ? 'active' : ''}`}
            onClick={() => setBattleMode('single')}
          >
            {t('calculate.single')}
          </button>
          <button
            type="button"
            className={`mode-button ${battleMode === 'double' ? 'active' : ''}`}
            onClick={() => setBattleMode('double')}
          >
            {t('calculate.double')}
          </button>
        </div>
      </div>

      <div className="form-group" role="group" aria-label={t('calculate.auras')}>
        <div className="auras-toggle" style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className={`aura-button ${fairyAura ? 'active' : ''}`}
            onClick={() => setFairyAura(v => !v)}
            aria-pressed={fairyAura}
          >
            {t('auras.fairy') || 'Fairy Aura'}
          </button>

          <button
            type="button"
            className={`aura-button ${darkAura ? 'active' : ''}`}
            onClick={() => setDarkAura(v => !v)}
            aria-pressed={darkAura}
          >
            {t('auras.dark') || 'Dark Aura'}
          </button>

          <button
            type="button"
            className={`aura-button ${auraBreak ? 'active' : ''}`}
            onClick={() => setAuraBreak(v => !v)}
            aria-pressed={auraBreak}
          >
            {t('auras.break') || 'Aura Break'}
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

      <div className="form-row">
        <div className="form-group">
          <label>{t('calculate.attackerStatus')}</label>
          <select
            value={attackerStatus}
            onChange={e => setAttackerStatus(e.target.value)}
            className="form-control"
          >
            {ALL_STATUSES.map(s => (
              <option key={s} value={s}>{t(`status.${s}`) || s}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>{t('calculate.defenderStatus')}</label>
          <select
            value={defenderStatus}
            onChange={e => setDefenderStatus(e.target.value)}
            className="form-control"
          >
            {ALL_STATUSES.map(s => (
              <option key={s} value={s}>{t(`status.${s}`) || s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="form-group">
        <label className="checkbox-label">
          <input 
            type="checkbox"
            checked={isCritical}
            onChange={e => setIsCritical(e.target.checked)}
          />
          {t('calculate.critical')}
        </label>
      </div>

      <button 
        onClick={calculate} 
        disabled={loading || !left || !right || !left.move}
        className="calculate-button"
      >
        {loading ? t('common.loading') : t('calculate.calculate')}
      </button>
    </div>
  )
}
