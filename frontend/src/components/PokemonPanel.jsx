import React from 'react'

const SAMPLE_POKES = [
  { name: 'Abomasnow', types: ['Grass','Ice'], bases: {hp:90, attack:92, defense:75, special_attack:92, special_defense:85, speed:60} },
  { name: 'Charizard', types: ['Fire','Flying'], bases: {hp:78, attack:84, defense:78, special_attack:109, special_defense:85, speed:100} }
]

export default function PokemonPanel({ side, value, onChange }){
  const poke = value || SAMPLE_POKES[0]

  function setEV(stat, v){
    const evs = {...(value?.evs || {}) , [stat]: Number(v)}
    onChange && onChange({...poke, evs})
  }

  function setNature(n){
    onChange && onChange({...poke, nature: n})
  }

  return (
    <div className="pokemon-panel">
      <h3>{side === 'left' ? 'Attaquant' : 'Défenseur'}</h3>
      <label>Choix du Pokémon
        <select onChange={e=>onChange && onChange(SAMPLE_POKES.find(p=>p.name===e.target.value)||SAMPLE_POKES[0])}>
          {SAMPLE_POKES.map(p => <option key={p.name} value={p.name}>{p.name}</option>)}
        </select>
      </label>
      <div>Types: {poke.types.join(' / ')}</div>
      <div className="bases">
        <h4>Bases</h4>
        {Object.entries(poke.bases).map(([k,v]) => (
          <div key={k}>{k}: {v}</div>
        ))}
      </div>
      <div className="evs">
        <h4>EVs (modifiable)</h4>
        {Object.keys(poke.bases).filter(k=>k!=='hp' || true).map((k)=> (
          <div key={k} className="ev-row">
            <label>{k}</label>
            <input type="number" min="0" max="252" defaultValue={value?.evs?.[k]||0} onChange={e=>setEV(k,e.target.value)} />
          </div>
        ))}
      </div>
      <div className="nature">
        <label>Nature
          <select onChange={e=>setNature(e.target.value)}>
            <option value="neutral">Neutre</option>
            <option value="atk-def">-Atk +Def</option>
            <option value="atk-spa">-Atk +SpA</option>
          </select>
        </label>
      </div>
    </div>
  )
}
