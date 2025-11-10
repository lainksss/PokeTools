import React, { useState } from 'react'

export default function MiddlePanel({ params, setParams, left, right, setResult }){
  const [loading, setLoading] = useState(false)

  async function calculate(){
    setLoading(true)
    const payload = {
      left, right, field: { weather: params.weather, terrain: params.terrain }, targets: params.targets
    }
    try{
      const res = await fetch('/api/calc_damage', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)})
      if(!res.ok) throw new Error('No backend')
      const data = await res.json()
      setResult(data)
    }catch(e){
      // fallback demo: build fake 16-rolls using randoms
      const rolls = Array.from({length:16}, ()=> Math.floor(Math.random()*100)+1)
      const avg = Math.floor(rolls.reduce((a,b)=>a+b,0)/rolls.length)
      setResult({ rolls, avg_damage: avg, note: 'Fallback demo (backend not reachable)'} )
    }finally{ setLoading(false) }
  }

  return (
    <div className="middle-panel">
      <h3>Paramètres</h3>
      <label>Météo
        <select value={params.weather} onChange={e=>setParams({...params, weather:e.target.value})}>
          <option value="none">Aucune</option>
          <option value="sun">Sunny</option>
          <option value="rain">Rain</option>
        </select>
      </label>
      <label>Terrain
        <select value={params.terrain} onChange={e=>setParams({...params, terrain:e.target.value})}>
          <option value="none">Aucun</option>
          <option value="grassy">Grassy</option>
          <option value="electric">Electric</option>
        </select>
      </label>
      <label>Pokemons à taper
        <input type="number" min="1" max="2" value={params.targets} onChange={e=>setParams({...params, targets: Number(e.target.value)})} />
      </label>
      <button onClick={calculate} disabled={loading}>{loading ? 'Calcul en cours...' : 'Calculer'}</button>
    </div>
  )
}
