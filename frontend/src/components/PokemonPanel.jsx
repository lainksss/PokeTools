
import React, { useEffect, useState, useRef } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'
import { convertEvsToOld } from '../utils/evs'
import { getMandatoryItem, hasMandatoryItem } from '../utils/getMandatoryItem'

export default function PokemonPanel({ side, value, onChange, showMultipleMoves = false, showTitle = true, showItem = true }) {
  const { t, getPokemonName, matchesPokemonName, language } = useTranslation()
  // Refs for inputs (for dropdown positioning)
  const pokemonInputRef = useRef(null)
  const abilityInputRef = useRef(null)
  const itemInputRef = useRef(null)
  const moveInputRefs = useRef({ 1: null, 2: null, 3: null, 4: null })

  // State for dropdown positioning
  const [dropdownPositions, setDropdownPositions] = useState({
    pokemon: { left: 0, top: 0 },
    ability: { left: 0, top: 0 },
    item: { left: 0, top: 0 },
    move1: { left: 0, top: 0 },
    move2: { left: 0, top: 0 },
    move3: { left: 0, top: 0 },
    move4: { left: 0, top: 0 }
  })

  // Update dropdown position when input element changes or window resizes
  const updateDropdownPosition = (inputRef, key) => {
    if (!inputRef?.current) return
    const rect = inputRef.current.getBoundingClientRect()
    // Compute available space below and above the input
    const viewportHeight = window.innerHeight
    const spaceBelow = viewportHeight - rect.bottom
    const spaceAbove = rect.top
    // Dropdown max height from CSS (fallback)
    const cssMax = 500
    const dropdownMaxHeight = Math.min(cssMax, Math.floor(viewportHeight - 80))

    // If not enough space below but more space above, open upwards
    let topPos
    if (spaceBelow < 200 && spaceAbove > spaceBelow) {
      // open above: position top so dropdown bottom aligns with rect.top - 4
      topPos = rect.top + window.scrollY - dropdownMaxHeight - 4
      // ensure topPos is not negative
      if (topPos < 8) topPos = 8
    } else {
      // default: open below the input
      topPos = rect.bottom + window.scrollY + 4
    }

    setDropdownPositions(prev => ({
      ...prev,
      [key]: {
        left: rect.left + window.scrollX,
        top: topPos
      }
    }))
  }

  // Setup listeners for dropdown positioning
  useEffect(() => {
    const handlePositionUpdate = () => {
      updateDropdownPosition(pokemonInputRef, 'pokemon')
      updateDropdownPosition(abilityInputRef, 'ability')
      updateDropdownPosition(itemInputRef, 'item')
      updateDropdownPosition(moveInputRefs.current[1], 'move1')
      updateDropdownPosition(moveInputRefs.current[2], 'move2')
      updateDropdownPosition(moveInputRefs.current[3], 'move3')
      updateDropdownPosition(moveInputRefs.current[4], 'move4')
    }

    window.addEventListener('resize', handlePositionUpdate)
    window.addEventListener('scroll', handlePositionUpdate, true)
    return () => {
      window.removeEventListener('resize', handlePositionUpdate)
      window.removeEventListener('scroll', handlePositionUpdate, true)
    }
  }, [])
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
  
  // Items state
  const [allItems, setAllItems] = useState([])
  const [itemSearch, setItemSearch] = useState('')
  const [showItemDropdown, setShowItemDropdown] = useState(false)
  const [filteredItems, setFilteredItems] = useState([])

  // Abilities state (searchable like items)
  const [allAbilities, setAllAbilities] = useState([])
  const [abilitySearch, setAbilitySearch] = useState('')
  const [showAbilityDropdown, setShowAbilityDropdown] = useState(false)
  const [filteredAbilities, setFilteredAbilities] = useState([])

  // Moves state (searchable like items)
  const [filteredMoves, setFilteredMoves] = useState([])
  const [moveSearch, setMoveSearch] = useState('')
  const [showMoveDropdown, setShowMoveDropdown] = useState(false)
  // Multiple-moves UI state (for the 4-slot selectors)
  const [moveSearches, setMoveSearches] = useState({1: '', 2: '', 3: '', 4: ''})
  const [showMoveDropdowns, setShowMoveDropdowns] = useState({1: false, 2: false, 3: false, 4: false})

  // Load pokemon list on mount
  useEffect(() => {
    let mounted = true
    setLoading(true)
    
    Promise.all([
      fetch(`${API_URL}/api/pokemon`).then(r => r.json()),
      fetch(`${API_URL}/api/types`).then(r => r.json()),
      fetch(`${API_URL}/api/natures`).then(r => r.json()),
      fetch(`${API_URL}/api/items`).then(r => r.json()),
      fetch(`${API_URL}/api/abilities`).then(r => r.json())
    ]).then(([pokemonData, typesData, naturesData, itemsData, abilitiesData]) => {
      if (!mounted) return
      setAllPokemon(pokemonData.results || [])
      setFilteredPokemon(pokemonData.results || [])
      setAllTypes(typesData.types || [])
      setAllNatures(naturesData.natures || [])
      setAllItems(itemsData.items || [])
      setFilteredItems(itemsData.items || [])
      setAllAbilities((abilitiesData && abilitiesData.abilities) || [])
      setFilteredAbilities((abilitiesData && abilitiesData.abilities) || [])
      
      // Initialize with first pokemon if none selected
      if (!value && pokemonData.results && pokemonData.results.length > 0) {
        const firstPoke = pokemonData.results[0]
        const initialData = {
          id: firstPoke.id,
          name: firstPoke.name,
          types: firstPoke.types,
          base_stats: firstPoke.base_stats,
          can_evolve: firstPoke.can_evolve,
          evs: { hp: 0, attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
          boosts: { attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 },
          nature: 'hardy',
          ability: null,
          move: null,
          item: null,
          is_terastallized: false,
          tera_type: null
        }
        setSearchText(getPokemonName(firstPoke.id, firstPoke.name.charAt(0).toUpperCase() + firstPoke.name.slice(1)))
        onChange && onChange(initialData)
      }
    }).catch(err => {
      console.error('Error loading data:', err)
    }).finally(() => {
      if (mounted) setLoading(false)
    })

    return () => { mounted = false }
  }, [])

  // Filter items when search changes
  useEffect(() => {
    if (!itemSearch.trim()) {
      setFilteredItems(allItems)
    } else {
      const search = itemSearch.toLowerCase()
      const filtered = allItems.filter(item => {
        // Search in English name (slug)
        if (item.slug && item.slug.toLowerCase().includes(search)) return true
        // Search in French name
        if (item.fr && item.fr.toLowerCase().includes(search)) return true
        // Search in English name
        if (item.en && item.en.toLowerCase().includes(search)) return true
        return false
      })
      setFilteredItems(filtered)
    }
  }, [itemSearch, allItems])


  // Filter abilities when search changes — limit to abilities the current Pokémon can have
  useEffect(() => {
    // Build the available set: if pokemonAbilities provided, intersect, otherwise use allAbilities
    const available = (pokemonAbilities && pokemonAbilities.length > 0)
      ? allAbilities.filter(a => pokemonAbilities.includes(a.slug))
      : allAbilities

    if (!abilitySearch.trim()) {
      setFilteredAbilities(available)
      return
    }

    const search = abilitySearch.toLowerCase()
    const filtered = (available || []).filter(a => {
      if ((a.slug && a.slug.toLowerCase().includes(search))) return true
      if ((a.en && a.en.toLowerCase().includes(search))) return true
      if ((a.fr && a.fr.toLowerCase().includes(search))) return true
      return false
    })
    setFilteredAbilities(filtered)
  }, [abilitySearch, allAbilities, pokemonAbilities])

  // Update ability search text when language changes and an ability is selected
  useEffect(() => {
    if (value?.ability && allAbilities.length > 0) {
      const selected = allAbilities.find(a => a.slug === value.ability)
      if (selected) {
        const displayName = language === 'fr' ? selected.fr : selected.en
        setAbilitySearch(displayName || '')
      }
    }
  }, [language, value?.ability, allAbilities, pokemonAbilities])

  // Filter moves when search changes
  useEffect(() => {
    if (!moveSearch.trim()) {
      setFilteredMoves(pokemonMoves)
    } else {
      const search = moveSearch.toLowerCase()
      const filtered = (pokemonMoves || []).filter(m => {
        // search in slug
        if (m.name && m.name.toLowerCase().includes(search)) return true
        // search in translations (fr/en)
        if (m.translations && m.translations.fr && m.translations.fr.toLowerCase().includes(search)) return true
        if (m.translations && m.translations.en && m.translations.en.toLowerCase().includes(search)) return true
        // fallback: search in displayed name
        const display = (m.translations && (language === 'fr' ? m.translations.fr : m.translations.en)) || (m.name || '')
        if (display.toLowerCase().includes(search)) return true
        return false
      })
      setFilteredMoves(filtered)
    }
  }, [moveSearch, pokemonMoves, language])

  // Update move search text when language changes and a move is selected
  useEffect(() => {
    if (value?.move && (pokemonMoves || []).length > 0) {
      const selected = (pokemonMoves || []).find(m => m.name === (value.move.name || value.move))
      if (selected) {
        const displayName = language === 'fr' ? (selected.translations?.fr || selected.translations?.en) : (selected.translations?.en || selected.translations?.fr)
        setMoveSearch(displayName || '')
      }
    }
  }, [language, value?.move, pokemonMoves])

  // Update item search text when language changes and an item is selected
  useEffect(() => {
    if (value?.item && allItems.length > 0) {
      const selectedItem = allItems.find(i => i.slug === value.item)
      if (selectedItem) {
        const displayName = language === 'fr' ? selectedItem.fr : selectedItem.en
        setItemSearch(displayName || '')
      }
    }
  }, [language, value?.item, allItems])

  // Filter pokemon when search text changes
  useEffect(() => {
    if (!searchText.trim()) {
      setFilteredPokemon(allPokemon)
    } else {
      const search = searchText.toLowerCase()
      const filtered = allPokemon.filter(p => {
        // Rechercher dans TOUTES les langues (anglais + traductions)
        // Chercher d'abord dans le nom anglais
        if (p.name.toLowerCase().includes(search)) return true
        // Puis chercher dans toutes les traductions disponibles
        if (matchesPokemonName(p.id, search)) return true
        return false
      })
      setFilteredPokemon(filtered)
    }
  }, [searchText, allPokemon, matchesPokemonName, language])

  // Update searchText when language changes and a Pokemon is selected
  useEffect(() => {
    if (value && value.id) {
      setSearchText(getPokemonName(value.id, value.name.charAt(0).toUpperCase() + value.name.slice(1)))
    }
  }, [language, value?.id, getPokemonName])

  // Load moves and abilities when pokemon changes
  useEffect(() => {
    if (!value || !value.id) return
    
    let mounted = true
    
    Promise.all([
      fetch(`${API_URL}/api/pokemon/${value.id}/moves`).then(r => r.json()),
      fetch(`${API_URL}/api/pokemon/${value.id}/abilities`).then(r => r.json())
    ]).then(([movesData, abilitiesData]) => {
      if (!mounted) return
      // Try to fetch localized move names and enrich move entries
      fetch(`${API_URL}/api/move-names`).then(r => r.json()).then(moveNamesData => {
        const movesList = (movesData.moves || []).map(m => {
          // m.name is the slug (e.g. "karate-chop")
          const slugLike = m.name.replace(/-/g, ' ').toLowerCase()
          // Find matching entry in moveNamesData by English name
          let found = null
          for (const k of Object.keys(moveNamesData || {})) {
            const entry = moveNamesData[k]
            if (!entry || !entry.en) continue
            if (entry.en.toLowerCase() === slugLike) {
              found = entry
              break
            }
          }
          const translations = found ? { en: found.en, fr: found.fr } : { en: m.name.replace(/-/g, ' '), fr: m.name.replace(/-/g, ' ') }
          return { ...m, translations }
        })
        if (!mounted) return
        setPokemonMoves(movesList)
        setFilteredMoves(movesList)
      }).catch(err => {
        // If translations fail, fallback to raw moves
        console.error('Error loading move names:', err)
        setPokemonMoves(movesData.moves || [])
        setFilteredMoves(movesData.moves || [])
      })

      setPokemonAbilities(abilitiesData.abilities || [])
    }).catch(err => {
      console.error('Error loading moves/abilities:', err)
    })

    return () => { mounted = false }
  }, [value && value.id])

  // Force mandatory item (mega-gem or primal-gem) when pokemon changes
  useEffect(() => {
    if (!value || !value.name) return
    
    const mandatoryItem = getMandatoryItem(value.name)
    if (mandatoryItem && value.item !== mandatoryItem) {
      // Set the mandatory item
      onChange && onChange({
        ...value,
        item: mandatoryItem
      })
    }
  }, [value?.name])

  // Calculate final stats when base_stats, evs, nature, or item change
  useEffect(() => {
    if (!value || !value.base_stats) return
    
    let mounted = true
    
      // Convert frontend EVs (0..32 units) to backend EV format
      fetch(`${API_URL}/api/calc_stats`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        base_stats: value.base_stats,
        evs: convertEvsToOld(value.evs || {}),
        nature: value.nature || 'hardy'
      })
    })
      .then(r => r.json())
      .then(data => {
        if (!mounted) return
        
        // Apply item stat multipliers
        const stats = { ...data.stats }
        const itemSlug = value?.item?.toLowerCase() || ''
        const pokemonName = value?.name?.toLowerCase() || ''
        
        // Choice Band: Attack x1.5
        if (itemSlug === 'choice-band') {
          stats.attack = Math.floor(stats.attack * 1.5)
        }
        // Choice Specs: Special Attack x1.5
        if (itemSlug === 'choice-specs') {
          stats.special_attack = Math.floor(stats.special_attack * 1.5)
        }
        // Choice Scarf: Speed x1.5
        if (itemSlug === 'choice-scarf') {
          stats.speed = Math.floor(stats.speed * 1.5)
        }
        // Assault Vest: Special Defense x1.5
        if (itemSlug === 'assault-vest') {
          stats.special_defense = Math.floor(stats.special_defense * 1.5)
        }
        // Light Ball (Pikachu only): Attack x2, Special Attack x2
        if (itemSlug === 'light-ball' && pokemonName === 'pikachu') {
          stats.attack = Math.floor(stats.attack * 2.0)
          stats.special_attack = Math.floor(stats.special_attack * 2.0)
        }
        // Thick Club (Cubone/Marowak only): Attack x2
        if (itemSlug === 'thick-club' && (pokemonName === 'cubone' || pokemonName === 'marowak')) {
          stats.attack = Math.floor(stats.attack * 2.0)
        }
        // Deep Sea Tooth (Clamperl only): Special Attack x2
        if (itemSlug === 'deep-sea-tooth' && pokemonName === 'clamperl') {
          stats.special_attack = Math.floor(stats.special_attack * 2.0)
        }
        // Deep Sea Scale (Clamperl only): Special Defense x2
        if (itemSlug === 'deep-sea-scale' && pokemonName === 'clamperl') {
          stats.special_defense = Math.floor(stats.special_defense * 2.0)
        }
        // Eviolite: Defense x1.5, Special Defense x1.5 (only for Pokemon that can evolve)
        if (itemSlug === 'eviolite' && value?.can_evolve) {
          stats.defense = Math.floor(stats.defense * 1.5)
          stats.special_defense = Math.floor(stats.special_defense * 1.5)
        }
        
        setFinalStats(stats)
      })
      .catch(err => {
        console.error('Error calculating stats:', err)
      })

    return () => { mounted = false }
  }, [value && value.base_stats, value && value.evs, value && value.nature, value && value.item, value && value.name])

  const handlePokemonSearch = (searchValue) => {
    setSearchText(searchValue)
    setShowDropdown(true)
  }

  const handlePokemonSelect = (pokemonName) => {
    const pokemon = allPokemon.find(p => 
      p.name.toLowerCase() === pokemonName.toLowerCase()
    )
    
    if (pokemon) {
      setSearchText(getPokemonName(pokemon.id, pokemon.name.charAt(0).toUpperCase() + pokemon.name.slice(1)))
      setShowDropdown(false)
      onChange && onChange({
        id: pokemon.id,
        name: pokemon.name,
        types: pokemon.types,
        base_stats: pokemon.base_stats,
        can_evolve: pokemon.can_evolve,
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
    const newVal = Math.max(0, Math.min(32, parseInt(val) || 0))

    // Calculate total of other EVs (in new units)
    const currentEvs = value?.evs || {}
    const otherEvsTotal = Object.entries(currentEvs)
      .filter(([key]) => key !== stat)
      .reduce((sum, [, v]) => sum + (parseInt(v) || 0), 0)

    // Check if exceeding total limit of 66 (new system)
    const maxAllowed = 66 - otherEvsTotal
    const finalVal = Math.min(newVal, maxAllowed, 32)

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
    onChange && onChange({ ...value, ability: abilityName || null })
  }

  const handleItemChange = (itemSlug) => {
    onChange && onChange({ ...value, item: itemSlug || null })
  }

  const handleMoveChange = (moveName, moveNumber = 1) => {
    const move = pokemonMoves.find(m => m.name === moveName)
    const moveKey = moveNumber === 1 ? 'move' : `move${moveNumber}`
    onChange && onChange({ ...value, [moveKey]: move || null })
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

  // Check if a stat is boosted by the selected item
  const isStatBoostedByItem = (statName) => {
    if (!value?.item) return false
    
    const item = allItems.find(i => i.slug === value.item)
    if (!item) return false
    
    // Map frontend stat names to item effect names
    const statMap = {
      'attack': 'attack',
      'defense': 'defense',
      'special-attack': 'special_attack',
      'special-defense': 'special_defense',
      'speed': 'speed'
    }
    
    const itemSlug = item.slug.toLowerCase()
    
    // Choice items boost specific stats
    if (itemSlug === 'choice-band' && statName === 'attack') return true
    if (itemSlug === 'choice-specs' && statName === 'special-attack') return true
    if (itemSlug === 'choice-scarf' && statName === 'speed') return true
    if (itemSlug === 'assault-vest' && statName === 'special-defense') return true
    
    // Species-specific items
    if (itemSlug === 'light-ball' && value.name?.toLowerCase() === 'pikachu') {
      if (statName === 'attack' || statName === 'special-attack') return true
    }
    if (itemSlug === 'thick-club' && (value.name?.toLowerCase() === 'cubone' || value.name?.toLowerCase() === 'marowak')) {
      if (statName === 'attack') return true
    }
    if (itemSlug === 'deep-sea-tooth' && value.name?.toLowerCase() === 'clamperl' && statName === 'special-attack') return true
    if (itemSlug === 'deep-sea-scale' && pokemonName === 'clamperl' && statName === 'special-defense') return true
    if (itemSlug === 'eviolite' && value?.can_evolve && (statName === 'defense' || statName === 'special-defense')) return true
    
    return false
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

  // Calculate total EVs (new units) and remaining (out of 66)
  const totalEvs = value?.evs 
    ? Object.values(value.evs).reduce((sum, val) => sum + (parseInt(val) || 0), 0)
    : 0
  const remainingEvs = 66 - totalEvs

  const isParalyzed = (value && value.status === 'paralysis')

  return (
    <div className="pokemon-panel">
      {showTitle && <h3>{side === 'left' ? t('calculate.attacker') : t('calculate.defender')}</h3>}
      
      {/* Pokemon selection with search */}
      <div className="form-group pokemon-selector-wrapper">
        <label>{t('calculate.selectPokemon')}</label>
        <input
          ref={pokemonInputRef}
          type="text"
          value={searchText}
          onChange={e => handlePokemonSearch(e.target.value)}
          onFocus={() => {
            setShowDropdown(true)
            updateDropdownPosition(pokemonInputRef, 'pokemon')
          }}
          placeholder={t('calculate.search')}
          className="form-control pokemon-search-input"
        />
        {showDropdown && searchText && filteredPokemon.length > 0 && (
          <div 
            className="pokemon-dropdown-container"
            style={{ left: `${dropdownPositions.pokemon.left}px`, top: `${dropdownPositions.pokemon.top}px` }}
          >
            {filteredPokemon.slice(0, 50).map(p => (
              <div
                key={p.id}
                className="pokemon-dropdown-item"
                onClick={() => handlePokemonSelect(p.name)}
              >
                {getPokemonName(p.id, p.name.charAt(0).toUpperCase() + p.name.slice(1))}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Types and Tera on same row */}
      <div className="types-tera-row">
        <div className="types-section">
          <div className="types-display">
            <strong>{t('pokemon.types')}:</strong>{' '}
            {value?.types?.map((type, idx) => (
              <span key={idx} className={`type-badge type-${type}`}>
                {t(`types.${type}`)}
              </span>
            )) || 'N/A'}
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
              {allTypes.map(type => (
                <option key={type} value={type}>{t(`types.${type}`)}</option>
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
              const isItemBoosted = isStatBoostedByItem(stat)
              
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
                      max="32" 
                      step="1"
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
                    {statKey === 'speed' ? (
                      // Apply paralysis halving and red color when status is paralysis
                      (() => {
                        const baseDisplay = boostVal !== 0 && statKey !== 'hp' ? boostedVal : finalVal
                        const displayed = isParalyzed && typeof baseDisplay === 'number' ? Math.floor(baseDisplay / 2) : baseDisplay
                        return (
                          <span title={`Base: ${finalVal}`} style={{ color: isParalyzed ? '#ef4444' : undefined }} className={isItemBoosted ? 'item-boosted' : ''}>
                            {displayed}
                            {boostVal !== 0 && statKey !== 'hp' ? (
                              <span style={{fontSize: '0.85em', opacity: 0.7}}>({finalVal})</span>
                            ) : null}
                          </span>
                        )
                      })()
                    ) : (
                      boostVal !== 0 && statKey !== 'hp' ? (
                        <span title={`Base: ${finalVal}`} className={isItemBoosted ? 'item-boosted' : ''}>
                          {boostedVal} <span style={{fontSize: '0.85em', opacity: 0.7}}>({finalVal})</span>
                        </span>
                      ) : (
                        <span className={isItemBoosted ? 'item-boosted' : ''}>
                          {finalVal}
                        </span>
                      )
                    )}
                  </div>
                </div>
              )
            })}
          </div>
          
          {/* Remaining EVs */}
          <div className="evs-remaining">
            {t('pokemon.evsRemaining')}: <strong style={{color: remainingEvs < 0 ? '#ef4444' : '#10b981'}}>{remainingEvs}</strong> / 66
          </div>

          {/* Multiple moves for coverage: placed under EVs and aligned horizontally */}
          {side === 'left' && showMultipleMoves && (
            <div className="form-group coverage-moves-group">
              <label>{t('coverage.moves') || 'Attaques (max 4)'}</label>
              <div className="coverage-moves-row">
                {[1, 2, 3, 4].map(num => {
                  const moveKey = num === 1 ? 'move' : `move${num}`
                  const selectedMove = value?.[moveKey]
                  const searchValue = moveSearches[num]
                  const isDropdownOpen = showMoveDropdowns[num]
                  // compute filtered for this slot
                  const localFiltered = (!searchValue || !searchValue.trim())
                    ? pokemonMoves
                    : (pokemonMoves || []).filter(m => {
                        const displayEn = (m.translations?.en || (m.name || '').replace(/-/g, ' ')).toLowerCase()
                        const displayFr = (m.translations?.fr || (m.name || '').replace(/-/g, ' ')).toLowerCase()
                        const s = searchValue.toLowerCase()
                        return (m.name && m.name.toLowerCase().includes(s)) || displayEn.includes(s) || displayFr.includes(s)
                      })

                  return (
                    <div key={num} className="coverage-move">
                      <div className="form-group item-selector">
                        <div className="item-input-wrapper">
                          <input
                            ref={el => moveInputRefs.current[num] = el}
                            type="text"
                            value={searchValue || (selectedMove ? (language === 'fr' ? (selectedMove.translations?.fr || (selectedMove.name || '').replace(/-/g, ' ')) : (selectedMove.translations?.en || (selectedMove.name || '').replace(/-/g, ' '))) : '')}
                            onChange={e => setMoveSearches(prev => ({...prev, [num]: e.target.value}))}
                            onFocus={() => {
                              setShowMoveDropdowns(prev => ({...prev, [num]: true}))
                              updateDropdownPosition(moveInputRefs.current[num], `move${num}`)
                            }}
                            onBlur={() => setTimeout(() => setShowMoveDropdowns(prev => ({...prev, [num]: false})), 200)}
                            placeholder={t('calculate.searchMove') || 'Rechercher une attaque...'}
                            className="form-control item-search-input"
                          />
                          {selectedMove && (
                            <button
                              className="item-clear-btn"
                              onClick={() => {
                                handleMoveChange(null, num)
                                setMoveSearches(prev => ({...prev, [num]: ''}))
                              }}
                              title={t('common.clear') || 'Effacer'}
                            >
                              ×
                            </button>
                          )}
                        </div>

                        {isDropdownOpen && (
                          <div 
                            className="item-dropdown"
                            style={{ left: `${dropdownPositions[`move${num}`].left}px`, top: `${dropdownPositions[`move${num}`].top}px` }}
                          >
                            {(!localFiltered || localFiltered.length === 0) && (
                              <div className="item-dropdown-empty">{t('common.noResults') || 'Aucun résultat'}</div>
                            )}
                            {(localFiltered || []).slice(0, 100).map(m => {
                              const displayName = language === 'fr' ? (m.translations?.fr || m.translations?.en || (m.name || '').replace(/-/g, ' ')) : (m.translations?.en || m.translations?.fr || (m.name || '').replace(/-/g, ' '))
                              const powerDisplay = m.power != null ? m.power : '—'
                              const typeDisplay = m.type || ''
                              const categoryDisplay = m.damage_class || ''
                              return (
                                <div
                                  key={m.name}
                                  className={`item-dropdown-item ${selectedMove?.name === m.name ? 'selected' : ''}`}
                                  onClick={() => {
                                    handleMoveChange(m.name, num)
                                    setMoveSearches(prev => ({...prev, [num]: displayName}))
                                    setShowMoveDropdowns(prev => ({...prev, [num]: false}))
                                  }}
                                  title={displayName}
                                >
                                  <div className="item-left">
                                    <div className="item-name">{displayName}</div>
                                    <div className="item-description">{`${powerDisplay} • ${categoryDisplay}`}</div>
                                  </div>
                                  {typeDisplay && (
                                    <div style={{marginLeft:12}}>
                                      <span className={`type-badge type-${typeDisplay}`}>{typeDisplay}</span>
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                          </div>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
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
          <div className="form-group item-selector">
            <label>{t('calculate.ability')}</label>
            <div className="item-input-wrapper">
              <input
                ref={abilityInputRef}
                type="text"
                value={abilitySearch}
                onChange={e => setAbilitySearch(e.target.value)}
                onFocus={() => {
                  setShowAbilityDropdown(true)
                  updateDropdownPosition(abilityInputRef, 'ability')
                }}
                onBlur={() => setTimeout(() => setShowAbilityDropdown(false), 200)}
                placeholder={t('calculate.searchAbility') || 'Rechercher un talent...'}
                className="form-control item-search-input"
              />
              {value?.ability && (
                <button
                  className="item-clear-btn"
                  onClick={() => {
                    handleAbilityChange(null)
                    setAbilitySearch('')
                  }}
                  title={t('common.clear') || 'Effacer'}
                >
                  ×
                </button>
              )}
            </div>

            {showAbilityDropdown && (
              <div 
                className="item-dropdown"
                style={{ left: `${dropdownPositions.ability.left}px`, top: `${dropdownPositions.ability.top}px` }}
              >
                {filteredAbilities.length === 0 && (
                  <div className="item-dropdown-empty">{t('common.noResults') || 'Aucun résultat'}</div>
                )}
                {filteredAbilities.slice(0, 200).map(ab => {
                  const displayName = language === 'fr' ? (ab.fr || ab.en) : (ab.en || ab.fr)
                  const description = language === 'fr' ? (ab.description_fr || '') : (ab.description_en || '')
                  return (
                    <div
                      key={ab.slug}
                      className={`item-dropdown-item ${value?.ability === ab.slug ? 'selected' : ''}`}
                      onClick={() => {
                        handleAbilityChange(ab.slug)
                        setAbilitySearch(displayName)
                        setShowAbilityDropdown(false)
                      }}
                      title={description}
                    >
                      <span className="item-name">{displayName}</span>
                      {description && <span className="item-description">{description}</span>}
                    </div>
                  )
                })}
              </div>
            )}

            {value?.ability && (
              <div className="selected-item-badge">
                {(() => {
                  const selected = allAbilities.find(a => a.slug === value.ability)
                  if (!selected) return (value.ability || '')
                  const description = language === 'fr' ? (selected.description_fr || selected.fr) : (selected.description_en || selected.en)
                  return description || (language === 'fr' ? selected.fr : selected.en)
                })()}
              </div>
            )}
          </div>

          {/* Item - NEW */}
          {showItem && (
            <div className="form-group item-selector">
              <label>{t('calculate.item') || 'Objet tenu'}</label>
              {(() => {
                const isMandatory = hasMandatoryItem(value?.name)
                const mandatoryItem = getMandatoryItem(value?.name)
                const allItemsMap = allItems.reduce((acc, item) => {
                  acc[item.slug] = item
                  return acc
                }, {})
                const mandatoryItemData = mandatoryItem ? allItemsMap[mandatoryItem] : null
                
                if (isMandatory && mandatoryItemData) {
                  // Display mandatory item as non-modifiable
                  const displayName = language === 'fr' ? mandatoryItemData.fr : mandatoryItemData.en
                  const description = language === 'fr' ? mandatoryItemData.description_fr : mandatoryItemData.description_en
                  return (
                    <div className="mandatory-item-display">
                      <div className="mandatory-item-badge mandatory">
                        <img src="/lock-icon.svg" alt="locked" className="lock-icon" style={{display: 'none'}} />
                        <span className="item-name">{displayName}</span>
                        <span className="mandatory-indicator" title={t('calculate.mandatoryItem') || 'Objet obligatoire pour cette forme'}>(Obligatoire)</span>
                      </div>
                      {description && (
                        <small className="item-description">{description}</small>
                      )}
                    </div>
                  )
                }
                
                // Normal item selector
                return (
                  <>
                    <div className="item-input-wrapper">
                      <input
                        ref={itemInputRef}
                        type="text"
                        value={itemSearch}
                        onChange={e => setItemSearch(e.target.value)}
                        onFocus={() => {
                          setShowItemDropdown(true)
                          updateDropdownPosition(itemInputRef, 'item')
                        }}
                        onBlur={() => setTimeout(() => setShowItemDropdown(false), 200)}
                        placeholder={t('calculate.searchItem') || 'Rechercher un objet...'}
                        className="form-control item-search-input"
                      />
                      {value?.item && (
                        <button 
                          className="item-clear-btn"
                          onClick={() => {
                            handleItemChange(null)
                            setItemSearch('')
                          }}
                          title={t('common.clear') || 'Effacer'}
                        >
                          ×
                        </button>
                      )}
                    </div>
                    
                    {showItemDropdown && (
                      <div 
                        className="item-dropdown"
                        style={{ left: `${dropdownPositions.item.left}px`, top: `${dropdownPositions.item.top}px` }}
                      >
                        {filteredItems.length === 0 && (
                          <div className="item-dropdown-empty">
                            {t('common.noResults') || 'Aucun résultat'}
                          </div>
                        )}
                        {filteredItems.slice(0, 100).map(item => {
                          const displayName = language === 'fr' ? item.fr : item.en
                          const description = language === 'fr' ? item.description_fr : item.description_en
                          return (
                            <div
                              key={item.slug}
                              className={`item-dropdown-item ${value?.item === item.slug ? 'selected' : ''}`}
                              onClick={() => {
                                handleItemChange(item.slug)
                                setItemSearch(displayName)
                                setShowItemDropdown(false)
                              }}
                              title={description}
                            >
                              <span className="item-name">{displayName}</span>
                              {description && (
                                <span className="item-description">{description}</span>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    )}
                    
                    {value?.item && (
                      <div className="selected-item-badge">
                        {(() => {
                          const selectedItem = allItems.find(i => i.slug === value.item)
                          if (!selectedItem) return null
                          const description = language === 'fr' ? selectedItem.description_fr : selectedItem.description_en
                          return description || (language === 'fr' ? selectedItem.fr : selectedItem.en)
                        })()}
                      </div>
                    )}
                  </>
                )
              })()}
            </div>
          )}

          {/* Move (only for attacker) */}
          {side === 'left' && !showMultipleMoves && (
            <div className="form-group item-selector">
              <label>{t('calculate.move')}</label>
              <div className="item-input-wrapper">
                <input
                  ref={el => moveInputRefs.current[1] = el}
                  type="text"
                  value={moveSearch}
                  onChange={e => setMoveSearch(e.target.value)}
                  onFocus={() => {
                    setShowMoveDropdown(true)
                    updateDropdownPosition(moveInputRefs.current[1], 'move1')
                  }}
                  onBlur={() => setTimeout(() => setShowMoveDropdown(false), 200)}
                  placeholder={t('calculate.searchMove') || 'Rechercher une attaque...'}
                  className="form-control item-search-input"
                />
                {value?.move && (
                  <button
                    className="item-clear-btn"
                    onClick={() => {
                      handleMoveChange(null)
                      setMoveSearch('')
                    }}
                    title={t('common.clear') || 'Effacer'}
                  >
                    ×
                  </button>
                )}
              </div>

              {showMoveDropdown && (
                <div className="item-dropdown" style={{ left: `${dropdownPositions.move1.left}px`, top: `${dropdownPositions.move1.top}px` }}>
                  {(!filteredMoves || filteredMoves.length === 0) && (
                    <div className="item-dropdown-empty">
                      {t('common.noResults') || 'Aucun résultat'}
                    </div>
                  )}
                  {(filteredMoves || []).slice(0, 200).map(move => {
                    const displayName = language === 'fr' ? (move.translations?.fr || move.translations?.en || (move.name || '').replace(/-/g, ' ')) : (move.translations?.en || move.translations?.fr || (move.name || '').replace(/-/g, ' '))
                    const powerDisplay = move.power != null ? move.power : '—'
                    const typeDisplay = move.type || ''
                    const categoryDisplay = move.damage_class || ''
                    return (
                      <div
                        key={move.name}
                        className={`item-dropdown-item ${value?.move?.name === move.name ? 'selected' : ''}`}
                        onClick={() => {
                          handleMoveChange(move.name)
                          setMoveSearch(displayName)
                          setShowMoveDropdown(false)
                        }}
                        title={displayName}
                      >
                        <div className="item-left">
                          <div className="item-name">{displayName}</div>
                          <div className="item-description">{`${powerDisplay} • ${categoryDisplay}`}</div>
                        </div>
                        {typeDisplay && (
                          <div style={{marginLeft:12}}>
                            <span className={`type-badge type-${typeDisplay}`}>{typeDisplay}</span>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              )}

              {value?.move && (
                <div className="move-details">
                  {(() => {
                    const selected = (pokemonMoves || []).find(m => m.name === (value.move.name || value.move)) || value.move
                    if (!selected) return null
                    const displayName = language === 'fr' ? (selected.translations?.fr || selected.translations?.en || (selected.name || '').replace(/-/g, ' ')) : (selected.translations?.en || selected.translations?.fr || (selected.name || '').replace(/-/g, ' '))
                    return (
                      <>
                        <div><strong>{t('calculate.move')}:</strong> {displayName}</div>
                        <div><strong>{t('threats.type')}:</strong> {selected.type ? <span className={`type-badge type-${selected.type}`}>{selected.type}</span> : ''}</div>
                        <div><strong>{t('threats.power')}:</strong> {selected.power || '—'}</div>
                        <div><strong>{t('pokemon.accuracy')}:</strong> {selected.accuracy || '—'}</div>
                        <div><strong>{t('pokemon.category')}:</strong> {selected.damage_class || ''}</div>
                      </>
                    )
                  })()}
                </div>
              )}
            </div>
          )}

          {/* Multiple Moves (moved to stats column) - removed from selectors container */}
        </div>
      </div>
    </div>
  )
}