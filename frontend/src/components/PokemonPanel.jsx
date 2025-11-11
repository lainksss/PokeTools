import React, { useEffect, useState } from 'react'
import { useTranslation } from '../i18n/LanguageContext'

export default function PokemonPanel({ side, value, onChange }) {
  const { t } = useTranslation()
  const [allPokemon, setAllPokemon] = useState([])
  const [filteredPokemon, setFilteredPokemon] = useState([])
  const [searchText, setSearchText] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const [allTypes, setAllTypes] = useState([])
  const [allNatures, setAllNatures] = useState([])
  const [pokemonMoves, setPokemonMoves] = useState([])
  const [pokemonAbilities, setPokemonAbilities] = useState([])
  const [finalStats, setFinalStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Load pokemon list on mount
  useEffect(() => {
    let mounted = true
    setLoading(true)
    
    Promise.all([
      fetch('/api/pokemon').then(r => r.json()),
      fetch('/api/types').then(r => r.json()),
      fetch('/api/natures').then(r => r.json())
    ]).then(([pokemonData, typesData, naturesData]) => {
      if (!mounted) return
      setAllPokemon(pokemonData.results || [])
      setFilteredPokemon(pokemonData.results || [])
      setAllTypes(typesData.types || [])
      setAllNatures(naturesData.natures || [])
      
      // Initialize with first pokemon if none selected
      if (!value && pokemonData.results && pokemonData.results.length > 0) {
        const firstPoke = pokemonData.results[0]
        const initialData = {
          id: firstPoke.id,
          name: firstPoke.name,
          types: firstPoke.types,
          base_stats: firstPoke.base_stats,
          evs: { hp: 0, attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
          boosts: { attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
          nature: 'hardy',
          ability: null,
          move: null,
          is_terastallized: false,
          tera_type: null
        }
        setSearchText(firstPoke.name.charAt(0).toUpperCase() + firstPoke.name.slice(1))
        onChange && onChange(initialData)
      }
    }).catch(err => {
      console.error('Error loading data:', err)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [])

  // Filter pokemon when search text changes
  useEffect(() => {
    if (!searchText.trim()) {
      setFilteredPokemon(allPokemon)
    } else {
      const search = searchText.toLowerCase()
      const filtered = allPokemon.filter(p => 
        p.name.toLowerCase().includes(search)
      )
      setFilteredPokemon(filtered)
    }
  }, [searchText, allPokemon])

  // Load moves and abilities when pokemon changes
  useEffect(() => {
    if (!value || !value.id) return
    
    let mounted = true
    
    Promise.all([
      fetch(`/api/pokemon/${value.id}/moves`).then(r => r.json()),
      fetch(`/api/pokemon/${value.id}/abilities`).then(r => r.json())
    ]).then(([movesData, abilitiesData]) => {
      if (!mounted) return
      setPokemonMoves(movesData.moves || [])
      setPokemonAbilities(abilitiesData.abilities || [])
    }).catch(err => {
      console.error('Error loading moves/abilities:', err)
    })

    return () => { mounted = false }
  }, [value && value.id])

  // Calculate final stats when base_stats, evs or nature change
  useEffect(() => {
    if (!value || !value.base_stats) return
    
    let mounted = true
    
    fetch('/api/calc_stats', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_stats: value.base_stats,
        evs: value.evs || {},
        nature: value.nature || 'hardy'
      })
    })
      .then(r => r.json())
      .then(data => {
        if (mounted) setFinalStats(data.stats)
      })
      .catch(err => {
        console.error('Error calculating stats:', err)
      })

    return () => { mounted = false }
  }, [value && value.base_stats, value && value.evs, value && value.nature])

  const handlePokemonSearch = (searchValue) => {
    setSearchText(searchValue)
    setShowDropdown(true)
  }

  const handlePokemonSelect = (pokemonName) => {
    const pokemon = allPokemon.find(p => 
      p.name.toLowerCase() === pokemonName.toLowerCase()
    )
    
    if (pokemon) {
      setSearchText(pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1))
      setShowDropdown(false)
      onChange && onChange({
        id: pokemon.id,
        name: pokemon.name,
        types: pokemon.types,
        base_stats: pokemon.base_stats,
        evs: value?.evs || { hp: 0, attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
        boosts: value?.boosts || { attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
        nature: value?.nature || 'hardy',
        ability: null,
        move: null,
        is_terastallized: false,
        tera_type: null
      })
    }
  }

  const handleEVChange = (stat, val) => {
    const newVal = Math.max(0, Math.min(252, parseInt(val) || 0))
    
    // Calculate total of other EVs
    const currentEvs = value?.evs || {}
    const otherEvsTotal = Object.entries(currentEvs)
      .filter(([key]) => key !== stat)
      .reduce((sum, [, value]) => sum + (parseInt(value) || 0), 0)
    
    // Check if exceeding total limit of 510
    const maxAllowed = 510 - otherEvsTotal
    const finalVal = Math.min(newVal, maxAllowed, 252)
    
    onChange && onChange({
      ...value,
      evs: { ...(value.evs || {}), [stat]: finalVal }
    })
  }

  const handleBoostChange = (stat, val) => {
    const newVal = Math.max(-6, Math.min(6, parseInt(val) || 0))
    onChange && onChange({
      ...value,
      boosts: { ...(value.boosts || {}), [stat]: newVal }
    })
  }

  const handleNatureChange = (natureName) => {
    onChange && onChange({ ...value, nature: natureName })
  }

  const handleAbilityChange = (abilityName) => {
    onChange && onChange({ ...value, ability: abilityName })
  }

  const handleMoveChange = (moveSlug) => {
    const move = pokemonMoves.find(m => m.name === moveSlug)
    onChange && onChange({ ...value, move: move || null })
  }

  const handleTeraChange = (checked) => {
    onChange && onChange({
      ...value,
      is_terastallized: checked,
      tera_type: checked ? (value.tera_type || allTypes[0]) : null
    })
  }

  const handleTeraTypeChange = (type) => {
    onChange && onChange({ ...value, tera_type: type })
  }

  // Calculate stat with boost applied (using Pokemon formula)
  const calculateBoostedStat = (baseStat, boost) => {
    if (!baseStat || baseStat === '—') return '—'
    if (!boost || boost === 0) return baseStat
    
    // Pokemon boost formula: stat * (2 + boost) / 2 for positive, stat * 2 / (2 - boost) for negative
    const multiplier = boost > 0 ? (2 + boost) / 2 : 2 / (2 - boost)
    return Math.floor(baseStat * multiplier)
  }

  if (loading) {
    return <div className="pokemon-panel">{t('common.loading')}</div>
  }

  const statsOrder = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
  const statsLabels = {
    'hp': t('calculate.hp'),
    'attack': t('calculate.attack'),
    'defense': t('calculate.defense'),
    'special-attack': t('calculate.spAttack'),
    'special-defense': t('calculate.spDefense'),
    'speed': t('calculate.speed')
  }

  // Calculate total EVs
  const totalEvs = value?.evs 
    ? Object.values(value.evs).reduce((sum, val) => sum + (parseInt(val) || 0), 0)
    : 0
  const remainingEvs = 510 - totalEvs

  return (
    <div className="pokemon-panel">
      <h3>{side === 'left' ? t('calculate.attacker') : t('calculate.defender')}</h3>
      
      {/* Pokemon selection with search */}
      <div className="form-group pokemon-selector-wrapper">
        <label>{t('calculate.selectPokemon')}</label>
        <input
          type="text"
          value={searchText}
          onChange={e => handlePokemonSearch(e.target.value)}
          onFocus={() => setShowDropdown(true)}
          placeholder={t('calculate.search')}
          className="form-control pokemon-search-input"
        />
        {showDropdown && searchText && filteredPokemon.length > 0 && (
          <div className="pokemon-dropdown-container">
            {filteredPokemon.slice(0, 50).map(p => (
              <div
                key={p.id}
                className="pokemon-dropdown-item"
                onClick={() => handlePokemonSelect(p.name)}
              >
                {p.name.charAt(0).toUpperCase() + p.name.slice(1)}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Types and Tera on same row */}
      <div className="types-tera-row">
        <div className="types-section">
          <div className="types-display">
            <strong>{t('pokemon.types')}:</strong> {value?.types?.join(', ') || 'N/A'}
          </div>
        </div>

        <div className="tera-section-block">
          <label className="tera-checkbox">
            <input 
              type="checkbox" 
              checked={value?.is_terastallized || false}
              onChange={e => handleTeraChange(e.target.checked)}
            />
            {t('calculate.terastallized')}
          </label>
          {value?.is_terastallized && (
            <select 
              value={value?.tera_type || ''}
              onChange={e => handleTeraTypeChange(e.target.value)}
              className="tera-type-select"
            >
              {allTypes.map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Stats + Selectors (Nature, Ability, Move) */}
      <div className="stats-and-selectors">
        {/* Stats table */}
        <div className="stats-container">
          <div className="stats-table">
            <div className="stats-header">
              <div className="stat-label"></div>
              <div className="stat-col">Base</div>
              <div className="stat-col">EVs</div>
              <div className="stat-col">Boost</div>
              <div className="stat-col">Final</div>
            </div>
            {statsOrder.map(stat => {
              const statKey = stat.replace('-', '_')
              const baseVal = value?.base_stats?.[stat] || 0
              const evVal = value?.evs?.[statKey] || 0
              const boostVal = value?.boosts?.[statKey] || 0
              const finalVal = finalStats?.[statKey] || '—'
              const boostedVal = statKey !== 'hp' ? calculateBoostedStat(finalVal, boostVal) : finalVal
              
              // Determine color based on nature
              const currentNature = allNatures.find(n => n.name === (value?.nature || 'hardy'))
              let statColor = ''
              if (currentNature && statKey !== 'hp') {
                if (currentNature.increase === statKey.replace('_', '-')) {
                  statColor = 'nature-boosted'
                } else if (currentNature.decrease === statKey.replace('_', '-')) {
                  statColor = 'nature-nerfed'
                }
              }
              
              return (
                <div key={stat} className="stats-row">
                  <div className={`stat-label ${statColor}`}>{statsLabels[stat]}</div>
                  <div className="stat-col stat-base">{baseVal}</div>
                  <div className="stat-col stat-ev">
                    <input 
                      type="number" 
                      min="0" 
                      max="252" 
                      value={evVal}
                      onChange={e => handleEVChange(statKey, e.target.value)}
                      className="ev-input"
                    />
                  </div>
                  <div className="stat-col stat-boost">
                    {statKey !== 'hp' ? (
                      <select
                        value={boostVal}
                        onChange={e => handleBoostChange(statKey, e.target.value)}
                        className="boost-select"
                      >
                        {[-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6].map(b => (
                          <option key={b} value={b}>
                            {b > 0 ? `+${b}` : b}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <span>—</span>
                    )}
                  </div>
                  <div className="stat-col stat-final">
                    {boostVal !== 0 && statKey !== 'hp' ? (
                      <span title={`Base: ${finalVal}`}>
                        {boostedVal} <span style={{fontSize: '0.85em', opacity: 0.7}}>({finalVal})</span>
                      </span>
                    ) : (
                      finalVal
                    )}
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* Remaining EVs */}
          <div className="evs-remaining">
            {t('pokemon.evsRemaining')}: <strong style={{color: remainingEvs < 0 ? '#ef4444' : '#10b981'}}>{remainingEvs}</strong> / 510
          </div>
        </div>

        {/* Selectors on the right */}
        <div className="selectors-container">
          {/* Nature */}
          <div className="form-group">
            <label>{t('calculate.nature')}</label>
            <select 
              value={value?.nature || 'hardy'}
              onChange={e => handleNatureChange(e.target.value)}
              className="form-control"
            >
              {allNatures.map(n => {
                let display = t(`natures.${n.name}`)
                if (n.increase && n.decrease) {
                  display += ` (+${n.increase}, -${n.decrease})`
                } else if (!n.increase && !n.decrease) {
                  display += ` (${t('pokemon.neutral')})`
                }
                return (
                  <option key={n.name} value={n.name}>{display}</option>
                )
              })}
            </select>
          </div>

          {/* Ability */}
          <div className="form-group">
            <label>{t('calculate.ability')}</label>
            <select 
              value={value?.ability || ''}
              onChange={e => handleAbilityChange(e.target.value)}
              className="form-control"
            >
              <option value="">-- {t('pokemon.none')} --</option>
              {pokemonAbilities.map(ability => (
                <option key={ability} value={ability}>
                  {ability.replace(/-/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          {/* Move (only for attacker) */}
          {side === 'left' && (
            <div className="form-group">
              <label>{t('calculate.move')}</label>
              <select 
                value={value?.move?.name || ''}
                onChange={e => handleMoveChange(e.target.value)}
                className="form-control"
              >
                <option value="">-- {t('pokemon.none')} --</option>
                {pokemonMoves.map(move => (
                  <option key={move.name} value={move.name}>
                    {move.name.replace(/-/g, ' ')} ({move.type}, {move.power || '—'})
                  </option>
                ))}
              </select>
              {value?.move && (
                <div className="move-details">
                  <div><strong>{t('threats.type')}:</strong> {value.move.type}</div>
                  <div><strong>{t('threats.power')}:</strong> {value.move.power || '—'}</div>
                  <div><strong>{t('pokemon.accuracy')}:</strong> {value.move.accuracy || '—'}</div>
                  <div><strong>{t('pokemon.category')}:</strong> {value.move.damage_class}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}