
import React, { useState } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'

const ALL_WEATHERS = [
  'none', 'sun', 'rain', 'sandstorm', 'snow'
]

const ALL_TERRAINS = [
  'none', 'grassy', 'electric', 'misty', 'psychic'
]

export default function MiddlePanel({ left, right, setResult }) {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [isCritical, setIsCritical] = useState(false)
  const [battleMode, setBattleMode] = useState('single') // 'single' or 'double'

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
        is_terastallized: left.is_terastallized,
        tera_type: left.tera_type,
        stages: left.boosts || {}
      },
      defender: {
        pokemon_id: right.id,
        base_stats: right.base_stats,
        evs: right.evs,
        nature: right.nature,
        types: right.types,
        ability: right.ability,
        is_terastallized: right.is_terastallized,
        tera_type: right.tera_type,
        stages: right.boosts || {}
      },
      move: left.move,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
      },
      is_critical: isCritical,
      battle_mode: battleMode,
      debug: true  // Activer le mode debug temporairement
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
      
      <div className="form-group">
        <label>{t('calculate.battleMode')}</label>
        <div className="battle-mode-toggle">
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
      
      <div className="form-group">
        <label>{t('calculate.weather')}</label>
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
        <label>{t('calculate.terrain')}</label>
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
