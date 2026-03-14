
import React, { useState } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'
import { convertEvsToOld } from '../utils/evs'

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
  const [reflect, setReflect] = useState(false)
  const [lightScreen, setLightScreen] = useState(false)
  const [auroraVeil, setAuroraVeil] = useState(false)
  const [helpingHand, setHelpingHand] = useState(false)
  const [friendGuard, setFriendGuard] = useState(false)

  // Keep local selectors synced with parent left/right values when available
  React.useEffect(() => {
    setAttackerStatus(left?.status || 'none')
  }, [left?.id, left?.status])

  React.useEffect(() => {
    setDefenderStatus(right?.status || 'none')
  }, [right?.id, right?.status])

  // When user changes the status selects, propagate into left/right via setters
  React.useEffect(() => {
    if (typeof setLeft !== 'function' || !left) return
    const desired = attackerStatus === 'none' ? null : attackerStatus
    if ((left.status || null) === desired) return
    setLeft(prev => ({ ...(prev || {}), status: desired }))
  }, [attackerStatus, left?.id, left?.status, setLeft])

  React.useEffect(() => {
    if (typeof setRight !== 'function' || !right) return
    const desired = defenderStatus === 'none' ? null : defenderStatus
    if ((right.status || null) === desired) return
    setRight(prev => ({ ...(prev || {}), status: desired }))
  }, [defenderStatus, right?.id, right?.status, setRight])

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
        evs: convertEvsToOld(left.evs || {}),
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
        evs: convertEvsToOld(right.evs || {}),
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
        aura_break: auraBreak || undefined,
        reflect: reflect || undefined,
        light_screen: lightScreen || undefined,
        aurora_veil: auroraVeil || undefined,
        helping_hand: helpingHand || undefined,
        friend_guard: friendGuard || undefined
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
      
      let data = await res.json()
      // Ensure the move object contains full metadata (multi_hit etc.). If
      // left.move lacks multi_hit, fetch details from the API and merge.
      let moveWithMeta = left.move || {}
      try {
        const hasMulti = moveWithMeta && (moveWithMeta.multi_hit || moveWithMeta.hits)
        if (!hasMulti && moveWithMeta && moveWithMeta.name) {
          const mvRes = await fetch(`${API_URL}/api/move/${encodeURIComponent(moveWithMeta.name)}`)
          if (mvRes.ok) {
            const mvData = await mvRes.json()
            moveWithMeta = { ...moveWithMeta, ...mvData }
          }
        }
      } catch (e) {
        // non-fatal: continue with original left.move
      }

      // Attach the (possibly enriched) move to the result so the ResultsPanel
      // can present multi-hit info client-side.
      setResult({ ...data, move: moveWithMeta })
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

      <div className="form-group" role="group" aria-label={t('calculate.screens')}>
        <div className="auras-toggle" style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className={`aura-button ${reflect ? 'active' : ''}`}
            onClick={() => setReflect(v => !v)}
            aria-pressed={reflect}
          >
            {t('screens.reflect') || 'Protection'}
          </button>

          <button
            type="button"
            className={`aura-button ${lightScreen ? 'active' : ''}`}
            onClick={() => setLightScreen(v => !v)}
            aria-pressed={lightScreen}
          >
            {t('screens.light') || 'Mur lumière'}
          </button>

          <button
            type="button"
            className={`aura-button ${auroraVeil ? 'active' : ''}`}
            onClick={() => setAuroraVeil(v => !v)}
            aria-pressed={auroraVeil}
          >
            {t('screens.aurora') || 'Voile Aurore'}
          </button>
        </div>
      </div>

      <div className="form-group" role="group" aria-label={t('calculate.doubleEffects')}>
        <div className="auras-toggle" style={{ display: 'flex', gap: '8px' }}>
          <button
            type="button"
            className={`aura-button ${helpingHand ? 'active' : ''}`}
            onClick={() => setHelpingHand(v => !v)}
            aria-pressed={helpingHand}
          >
            {t('doubleEffects.helpingHand') || 'Helping Hand'}
          </button>

          <button
            type="button"
            className={`aura-button ${friendGuard ? 'active' : ''}`}
            onClick={() => setFriendGuard(v => !v)}
            aria-pressed={friendGuard}
          >
            {t('doubleEffects.friendGuard') || 'Friend Guard'}
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
