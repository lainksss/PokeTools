import React, { useState } from 'react'

const ALL_WEATHERS = [
  'none', 'sun', 'harsh-sunlight', 'rain', 'heavy-rain', 'sandstorm', 'hail', 'snow', 'strong-winds'
]

const ALL_TERRAINS = [
  'none', 'grassy', 'electric', 'misty', 'psychic'
]

export default function MiddlePanel({ left, right, setResult }) {
  const [loading, setLoading] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  const [isCritical, setIsCritical] = useState(false)

  async function calculate() {
    if (!left || !right) {
      alert('Please select an attacking pokemon and a defending pokemon')
      return
    }

    if (!left.move) {
      alert('Please select a move for the attacker')
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
        tera_type: left.tera_type
      },
      defender: {
        pokemon_id: right.id,
        base_stats: right.base_stats,
        evs: right.evs,
        nature: right.nature,
        types: right.types,
        ability: right.ability,
        is_terastallized: right.is_terastallized,
        tera_type: right.tera_type
      },
      move: left.move,
      field: {
        weather: weather === 'none' ? null : weather,
        terrain: terrain === 'none' ? null : terrain
      },
      is_critical: isCritical
    }

    try {
      const res = await fetch('/api/calc_damage', {
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
      <h3>Conditions de combat</h3>
      
      <div className="form-group">
        <label>Météo</label>
        <select 
          value={weather}
          onChange={e => setWeather(e.target.value)}
          className="form-control"
        >
          {ALL_WEATHERS.map(w => (
            <option key={w} value={w}>
              {w === 'none' ? 'None' : w.replace(/-/g, ' ')}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Terrain</label>
        <select 
          value={terrain}
          onChange={e => setTerrain(e.target.value)}
          className="form-control"
        >
          {ALL_TERRAINS.map(t => (
            <option key={t} value={t}>
              {t === 'none' ? 'None' : t.replace(/-/g, ' ')}
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
          Coup critique
        </label>
      </div>

      <button 
        onClick={calculate} 
        disabled={loading || !left || !right || !left.move}
        className="calculate-button"
      >
        {loading ? 'Calculating...' : 'Calculate'}
      </button>
    </div>
  )
}
