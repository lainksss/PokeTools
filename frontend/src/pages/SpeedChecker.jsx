import React, { useState, useEffect, useRef } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'
import { newEvToOld } from '../utils/evs'
import { getMandatoryItem } from '../utils/getMandatoryItem'

export default function SpeedChecker() {
  const { t, language, getPokemonName, matchesPokemonName } = useTranslation()
  const speedPokemonInputRef = useRef(null)
  
  // State for dropdown positioning
  const [dropdownPos, setDropdownPos] = useState({ left: 0, top: 0, width: 320 })
  
  const dropdownRef = useRef(null)

  const updateDropdownPosition = () => {
    if (!speedPokemonInputRef?.current) return
    const rect = speedPokemonInputRef.current.getBoundingClientRect()
    const viewportHeight = window.innerHeight
    const spaceBelow = viewportHeight - rect.bottom
    const spaceAbove = rect.top
    const cssMax = 300
    const dropdownMaxHeight = Math.min(cssMax, Math.floor(viewportHeight - 80))
    let topPos
    if (spaceBelow < 160 && spaceAbove > spaceBelow) {
      topPos = rect.top + window.scrollY - dropdownMaxHeight - 4
      if (topPos < 8) topPos = 8
    } else {
      topPos = rect.bottom + window.scrollY + 4
    }

    // compute width from input rect but cap it so the list isn't ultra-wide
    const desiredWidth = Math.min(rect.width || 320, 420)
    let leftPos = rect.left + window.scrollX
    // avoid overflow off the right edge
    if (leftPos + desiredWidth > window.innerWidth - 8) {
      leftPos = Math.max(8, window.innerWidth - desiredWidth - 8)
    }

    setDropdownPos({
      left: leftPos,
      top: topPos,
      width: desiredWidth
    })
  }
  
  useEffect(() => {
    window.addEventListener('resize', updateDropdownPosition)
    window.addEventListener('scroll', updateDropdownPosition, true)

    const handleClickOutside = (e) => {
      const target = e.target
      if (speedPokemonInputRef.current && speedPokemonInputRef.current.contains(target)) return
      if (dropdownRef.current && dropdownRef.current.contains(target)) return
      setShowDropdown(false)
    }

    document.addEventListener('mousedown', handleClickOutside)

    return () => {
      window.removeEventListener('resize', updateDropdownPosition)
      window.removeEventListener('scroll', updateDropdownPosition, true)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])
  const [allPokemon, setAllPokemon] = useState([])
  const [allNatures, setAllNatures] = useState([])
  const [allAbilities, setAllAbilities] = useState([])
  const [pokemonAbilitiesMap, setPokemonAbilitiesMap] = useState({}) // Map pokemon_id -> [abilities]
  
  // Left panel - User's Pokémon
  const [selectedPokemon, setSelectedPokemon] = useState(null)
  const [value, setValue] = useState({ nature: 'hardy' })
  const [speedEVUnits, setSpeedEVUnits] = useState(0) // 0..32 UI units
  const [speedNature, setSpeedNature] = useState('neutral') // 'positive', 'neutral', 'negative'
  const [ability, setAbility] = useState(null)
  const [speedBoost, setSpeedBoost] = useState(0) // -6 to +6
  const [tailwind, setTailwind] = useState(false)
  const [weather, setWeather] = useState('none')
  const [terrain, setTerrain] = useState('none')
  // Choice Scarf toggle (user)
  const [choiceScarf, setChoiceScarf] = useState(false)
  const [fullyEvolvedOnly, setFullyEvolvedOnly] = useState(false)
  const level = 50 // Always level 50
  
  // Search functionality
  const [searchText, setSearchText] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const [filteredPokemon, setFilteredPokemon] = useState([])
  const [pokemonAbilities, setPokemonAbilities] = useState([])
  
  // Middle panel - Comparison mode
  const [comparisonMode, setComparisonMode] = useState('min') // 'min', 'custom', 'max'
  const [customEV, setCustomEV] = useState(0) // in UI units 0..32
  const [customNature, setCustomNature] = useState(false)
  // Choice Scarf toggle (middle panel)
  const [choiceScarfMiddle, setChoiceScarfMiddle] = useState(false)
  
  // Right panel - Results
  const [showSlower, setShowSlower] = useState(true) // true = slower, false = faster
  const [results, setResults] = useState([])

  const ALL_WEATHERS = ['none', 'sun', 'rain', 'sandstorm', 'snow']
  const ALL_TERRAINS = ['none', 'grassy', 'electric', 'psychic', 'misty']

  // Load Pokémon data
  useEffect(() => {
    Promise.all([
      fetch(`${API_URL}/api/pokemon`).then(r => r.json()),
      fetch(`${API_URL}/api/natures`).then(r => r.json()),
      fetch(`${API_URL}/api/abilities`).then(r => r.json()),
      fetch(`${API_URL}/api/pokemon-abilities-all`).then(r => r.json())
    ]).then(([pokemon, natures, abilities, abilitiesMap]) => {
      const pokemonList = pokemon.results || []
      setAllPokemon(pokemonList)
      setFilteredPokemon(pokemonList)
      setAllNatures(natures.natures || [])
      setAllAbilities(abilities.abilities || [])
      setPokemonAbilitiesMap(abilitiesMap.abilities_map || {})
    }).catch(err => console.error('Error loading data:', err))
  }, [])
  
  // Filter pokemon based on search
  useEffect(() => {
    if (!searchText.trim()) {
      setFilteredPokemon(allPokemon)
    } else {
      const s = searchText.toLowerCase()
      const filtered = allPokemon.filter(p => {
        try {
          // match on localized names if available
          const localized = getPokemonName(p.id, p.name || '').toLowerCase()
          if (localized.includes(s)) return true
        } catch (e) {
          // ignore
        }
        // fallback: match on slug/internal name (replace - with space)
        const slug = (p.name || '').toString().toLowerCase().replace(/[-_]/g, ' ')
        if (slug.includes(s)) return true
        // last fallback: try matchesPokemonName if translations are loaded
        try {
          if (matchesPokemonName(p.id, searchText)) return true
        } catch (e) {
          // ignore
        }
        return false
      })
      setFilteredPokemon(filtered)
    }
  }, [searchText, allPokemon, matchesPokemonName])
  
  // Load abilities when pokemon selected
  useEffect(() => {
    if (!selectedPokemon) {
      setPokemonAbilities([])
      setAbility(null)
      return
    }
    
    fetch(`${API_URL}/api/pokemon/${selectedPokemon.id}/abilities`)
      .then(r => r.json())
      .then(data => {
        const raw = data.abilities || []
        // Normalize to array of slugs (API may return strings)
        const slugs = raw.map(a => (typeof a === 'string' ? a : (a.slug || ''))).filter(Boolean)
        setPokemonAbilities(slugs)
        if (slugs.length > 0) {
          setAbility(slugs[0])
        } else {
          setAbility(null)
        }
      })
      .catch(err => console.error('Error loading abilities:', err))
  }, [selectedPokemon])

  // Calculate final speed stat
  const calculateSpeed = (baseStat, level, ev, nature, boost = 0) => {
    const iv = 31 // Always assume max IVs
    const base = Math.floor(((2 * baseStat + iv + Math.floor(ev / 4)) * level) / 100) + 5
    let multiplier = 1.0
    if (nature === 'positive') multiplier = 1.1
    if (nature === 'negative') multiplier = 0.9
    let stat = Math.floor(base * multiplier)
    
    // Apply boost multiplier
    if (boost !== 0) {
      const boostMultiplier = boost > 0 
        ? (2 + boost) / 2 
        : 2 / (2 - boost)
      stat = Math.floor(stat * boostMultiplier)
    }
    
    return stat
  }

  // Calculate any stat (for determining highest stat)
  const calculateStat = (baseStat, level, ev = 0, nature = 'neutral') => {
    const iv = 31 // Always assume max IVs
    const base = Math.floor(((2 * baseStat + iv + Math.floor(ev / 4)) * level) / 100) + 5
    let multiplier = 1.0
    if (nature === 'positive') multiplier = 1.1
    if (nature === 'negative') multiplier = 0.9
    return Math.floor(base * multiplier)
  }

  // Determine if speed is the highest stat (with priority tie-breaker)
  // For user's Pokémon: only speed gets EVs
  const getHighestStatUser = (pokemon) => {
    if (!pokemon) return null
    
    const stats = {
      attack: calculateStat(pokemon.base_stats.attack, level, 0, 'neutral'),
      defense: calculateStat(pokemon.base_stats.defense, level, 0, 'neutral'),
      special_attack: calculateStat(pokemon.base_stats['special-attack'], level, 0, 'neutral'),
      special_defense: calculateStat(pokemon.base_stats['special-defense'], level, 0, 'neutral'),
      speed: calculateStat(pokemon.base_stats.speed, level, effectiveSpeedEV, speedNature)
    }
    
    // Priority order: attack > defense > special_attack > special_defense > speed
    const priorityOrder = ['attack', 'defense', 'special_attack', 'special_defense', 'speed']
    let highest = null
    let highestValue = -1
    
    for (const statName of priorityOrder) {
      if (stats[statName] > highestValue) {
        highestValue = stats[statName]
        highest = statName
      }
    }
    
    return highest
  }

  // Determine if speed is the highest stat for an opponent
  const getHighestStatOpponent = (pokemon, opponentEV, opponentNature) => {
    if (!pokemon) return null
    
    const stats = {
      attack: calculateStat(pokemon.base_stats.attack, level, 0, 'neutral'),
      defense: calculateStat(pokemon.base_stats.defense, level, 0, 'neutral'),
      special_attack: calculateStat(pokemon.base_stats['special-attack'], level, 0, 'neutral'),
      special_defense: calculateStat(pokemon.base_stats['special-defense'], level, 0, 'neutral'),
      speed: calculateStat(pokemon.base_stats.speed, level, opponentEV, opponentNature)
    }
    
    // Priority order: attack > defense > special_attack > special_defense > speed
    const priorityOrder = ['attack', 'defense', 'special_attack', 'special_defense', 'speed']
    let highest = null
    let highestValue = -1
    
    for (const statName of priorityOrder) {
      if (stats[statName] > highestValue) {
        highestValue = stats[statName]
        highest = statName
      }
    }
    
    return highest
  }

  // Calculate user's speed
  // convert UI units (0..32) to backend EVs using shared helper
  const effectiveSpeedEV = newEvToOld(speedEVUnits)

  const userSpeed = selectedPokemon 
    ? calculateSpeed(selectedPokemon.base_stats.speed, level, effectiveSpeedEV, speedNature, speedBoost)
    : 0
  let finalUserSpeed = userSpeed
  
  // Apply Quark Drive boost if terrain is electric and speed is highest stat
  let hasQuarkDrive = false
  if (ability === 'quark-drive' && terrain === 'electric') {
    const highestStat = getHighestStatUser(selectedPokemon)
    if (highestStat === 'speed') {
      finalUserSpeed = Math.floor(finalUserSpeed * 1.5)
      hasQuarkDrive = true
    }
  }
  
  // Apply Protosynthesis boost if weather is sun and speed is highest stat
  let hasProtosynthesis = false
  if (ability === 'protosynthesis' && weather === 'sun') {
    const highestStat = getHighestStatUser(selectedPokemon)
    if (highestStat === 'speed') {
      finalUserSpeed = Math.floor(finalUserSpeed * 1.5)
      hasProtosynthesis = true
    }
  }
  
  // Weather-affected abilities multiplier (user)
  const weatherAbilityMultiplier = (abilitySlug, currentWeather) => {
    if (!abilitySlug || !currentWeather || currentWeather === 'none') return 1
    const slug = abilitySlug.toLowerCase()
    if (slug === 'chlorophyll' && currentWeather === 'sun') return 2
    if (slug === 'swift-swim' && currentWeather === 'rain') return 2
    if (slug === 'sand-rush' && currentWeather === 'sandstorm') return 2
    if (slug === 'slush-rush' && currentWeather === 'snow') return 2
    return 1
  }

  const abilityMult = weatherAbilityMultiplier(ability, weather)
  finalUserSpeed = Math.floor(finalUserSpeed * abilityMult)
  // Prevent Choice Scarf on Mega/Primal forms (they must use mandatory gems)
  const isMegaOrPrimal = selectedPokemon && (selectedPokemon.name?.includes('-mega') || selectedPokemon.name?.includes('-primal'))
  if (choiceScarf && !isMegaOrPrimal) finalUserSpeed = Math.floor(finalUserSpeed * 1.5)
  if (tailwind) finalUserSpeed = finalUserSpeed * 2
  
  // Get speed-related natures
  const speedNatures = allNatures.filter(n => 
    n.increased === 'speed' || n.decreased === 'speed' || (!n.increased && !n.decreased)
  )
  
  // Select pokemon handler
  const handleSelectPokemon = (pokemon) => {
    setSelectedPokemon(pokemon)
    setSearchText(getPokemonName(pokemon.id, pokemon.name))
    setShowDropdown(false)
  }

  // Compare speeds
  useEffect(() => {
    if (!selectedPokemon || allPokemon.length === 0) {
      setResults([])
      return
    }

      const pool = fullyEvolvedOnly ? allPokemon.filter(p => p.can_evolve === false) : allPokemon

      const comparisons = pool.map(pokemon => {
      let opponentEV = 0
      let opponentNature = 'neutral'
      
      if (comparisonMode === 'min') {
        opponentEV = 0
        opponentNature = 'neutral'
      } else if (comparisonMode === 'custom') {
        opponentEV = newEvToOld(customEV)
        opponentNature = customNature ? 'positive' : 'neutral'
      } else if (comparisonMode === 'max') {
        opponentEV = newEvToOld(32)
        opponentNature = 'positive'
      }

      const opponentSpeed = calculateSpeed(pokemon.base_stats.speed, level, opponentEV, opponentNature)
      let opponentFinalSpeed = opponentSpeed
      
      // Get opponent's primary ability (first in list)
      const opponentAbilities = pokemonAbilitiesMap[pokemon.id] || []
      const opponentPrimaryAbility = opponentAbilities.length > 0 ? opponentAbilities[0] : null
      
      // Apply weather-based ability multipliers for opponent
      if (opponentPrimaryAbility) {
        const abilityLower = opponentPrimaryAbility.toLowerCase()
        if (abilityLower === 'chlorophyll' && weather === 'sun') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 2)
        } else if (abilityLower === 'swift-swim' && weather === 'rain') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 2)
        } else if (abilityLower === 'sand-rush' && weather === 'sandstorm') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 2)
        } else if (abilityLower === 'slush-rush' && weather === 'snow') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 2)
        }
      }
      
      // Apply Quark Drive for opponent (electric terrain + speed is highest stat)
      if (opponentPrimaryAbility && opponentPrimaryAbility.toLowerCase() === 'quark-drive' && terrain === 'electric') {
        const highestStat = getHighestStatOpponent(pokemon, opponentEV, opponentNature)
        if (highestStat === 'speed') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 1.5)
        }
      }
      
      // Apply Protosynthesis for opponent (sun weather + speed is highest stat)
      if (opponentPrimaryAbility && opponentPrimaryAbility.toLowerCase() === 'protosynthesis' && weather === 'sun') {
        const highestStat = getHighestStatOpponent(pokemon, opponentEV, opponentNature)
        if (highestStat === 'speed') {
          opponentFinalSpeed = Math.floor(opponentFinalSpeed * 1.5)
        }
      }
      
      // Prevent Choice Scarf on Mega/Primal opponent forms (they can only use mandatory gems)
      const isOpponentMegaOrPrimal = pokemon.name?.includes('-mega') || pokemon.name?.includes('-primal')
      if (choiceScarfMiddle && !isOpponentMegaOrPrimal) opponentFinalSpeed = Math.floor(opponentFinalSpeed * 1.5)
      const isFaster = finalUserSpeed > opponentFinalSpeed
      const speedDiff = finalUserSpeed - opponentFinalSpeed

      return {
        name: getPokemonName(pokemon.id, pokemon.name),
        nameEn: pokemon.name,
        types: pokemon.types,
        baseSpeed: pokemon.base_stats.speed,
        finalSpeed: opponentFinalSpeed,
        isFaster,
        speedDiff: Math.abs(speedDiff)
      }
    })    // Filter and sort
    const filtered = comparisons.filter(c => 
      showSlower ? c.isFaster : !c.isFaster
    ).sort((a, b) => {
      // Sort by distance to user's speed (closest first in both categories)
      return a.speedDiff - b.speedDiff
    })

    setResults(filtered)
  }, [selectedPokemon, level, speedEVUnits, speedNature, speedBoost, tailwind, choiceScarf, comparisonMode, customEV, customNature, choiceScarfMiddle, showSlower, allPokemon, ability, weather, terrain, fullyEvolvedOnly, pokemonAbilitiesMap])

  return (
    <div className="speed-checker-page">
      
      <div className="speed-checker-container">
        {/* Left Panel - User's Pokémon */}
        <div className="speed-panel speed-panel-left">
          <h3>{t('speedChecker.yourPokemon') || 'Your Pokémon'}</h3>
          
          {/* Pokemon Search */}
          <div className="form-group">
            <label>{t('calculate.selectPokemon')}</label>
            <div className="pokemon-search-container">
              <input
                ref={speedPokemonInputRef}
                type="text"
                className="pokemon-search-input"
                placeholder={t('calculate.search')}
                value={searchText}
                onChange={(e) => {
                  setSearchText(e.target.value)
                  setShowDropdown(true)
                }}
                onFocus={() => {
                  setShowDropdown(true)
                  updateDropdownPosition()
                }}
              />
              {showDropdown && filteredPokemon.length > 0 && (
                <div 
                  ref={dropdownRef}
                  className="pokemon-dropdown"
                  style={{ left: `${dropdownPos.left}px`, top: `${dropdownPos.top}px`, position: 'fixed', width: `${dropdownPos.width}px` }}
                >
                  {filteredPokemon.slice(0, 50).map(p => (
                    <div
                      key={p.id}
                      className="pokemon-dropdown-item"
                      onClick={() => handleSelectPokemon(p)}
                    >
                      <span className="pokemon-name">{getPokemonName(p.id, p.name)}</span>
                      <span className="pokemon-speed">Speed: {p.base_stats.speed}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          

          {selectedPokemon && (
            <>
              {/* Pokemon Info Display */}
              <div className="pokemon-info-display">
                <div className="pokemon-header">
                  <h4>{getPokemonName(selectedPokemon.id, selectedPokemon.name)}</h4>
                  <div className="pokemon-types">
                    {selectedPokemon.types.map((type, idx) => (
                      <span key={idx} className={`type-badge type-${type.toLowerCase()}`}>
                        {type}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="base-speed-display">
                  <span className="label">{t('speedChecker.baseSpeed') || 'Base Speed:'}</span>
                  <span className="value">{selectedPokemon.base_stats.speed}</span>
                </div>
              </div>

              {/* Nature Selection */}
              <div className="form-group">
                <label>{t('calculate.nature')}</label>
                <select 
                  value={value.nature || 'hardy'} 
                  onChange={(e) => {
                    const selectedNature = allNatures.find(n => n.name === e.target.value)
                    if (selectedNature) {
                      if (selectedNature.increase === 'speed') {
                        setSpeedNature('positive')
                      } else if (selectedNature.decrease === 'speed') {
                        setSpeedNature('negative')
                      } else {
                        setSpeedNature('neutral')
                      }
                    }
                    setValue({...value, nature: e.target.value})
                  }}
                  className="nature-select"
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

              {/* Ability Selection */}
              <div className="form-group">
                <label>{t('calculate.ability')}</label>
                <select 
                  value={ability || ''} 
                  onChange={(e) => setAbility(e.target.value)}
                  className="ability-select"
                >
                  <option value="">{t('pokemon.none')}</option>
                    {allAbilities
                      .filter(a => pokemonAbilities.includes(a.slug))
                      .map(a => (
                        <option key={a.slug} value={a.slug}>
                          {a[language] || a.en}
                        </option>
                      ))}
                </select>
              </div>

              {/* EVs Input */}
              <div className="form-group">
                <label>{t('calculate.evs')} - {t('calculate.speed')}</label>
                <div className="ev-input-container">
                  <input
                    type="number"
                    value={speedEVUnits}
                    onChange={(e) => setSpeedEVUnits(Math.max(0, Math.min(32, parseInt(e.target.value) || 0)))}
                    min="0"
                    max="32"
                    step="1"
                  />
                </div>
              </div>

              {/* Speed Boost */}
              <div className="form-group">
                <label>Speed Boost</label>
                <div className="boost-selector">
                  <button 
                    className="boost-btn" 
                    onClick={() => setSpeedBoost(Math.max(-6, speedBoost - 1))}
                    disabled={speedBoost <= -6}
                  >
                    -
                  </button>
                  <span className="boost-value">{speedBoost > 0 ? '+' : ''}{speedBoost}</span>
                  <button 
                    className="boost-btn" 
                    onClick={() => setSpeedBoost(Math.min(6, speedBoost + 1))}
                    disabled={speedBoost >= 6}
                  >
                    +
                  </button>
                </div>
              </div>

              {/* Weather Effects Toggles */}
              <div className="form-group horizontal">
                {/* Tailwind Toggle */}
                <button 
                  className={`tailwind-button ${tailwind ? 'active' : ''}`}
                  onClick={() => setTailwind(!tailwind)}
                >
                  <span className="tailwind-icon">🌪️</span>
                  {t('speedChecker.tailwind') || 'Tailwind'}: {tailwind ? 'ON' : 'OFF'}
                </button>

                {/* Choice Scarf Toggle */}
                <button 
                  className={`tailwind-button${choiceScarf ? ' active' : ''}`}
                  onClick={() => setChoiceScarf(!choiceScarf)}
                  type="button"
                  disabled={isMegaOrPrimal}
                  title={isMegaOrPrimal ? 'Mega/Primal forms can only use mandatory gems' : ''}
                >
                  <span className="tailwind-icon">🧣</span>
                  {t('speedChecker.choiceScarf') || 'Choice Scarf'}: {choiceScarf ? t('speedChecker.on') || 'ON' : t('speedChecker.off') || 'OFF'}
                </button>
                
                  {/* Weather selector moved to middle panel */}
              </div>

              {/* Final Speed Display */}
              <div className="speed-display">
                <div className="stat-display">
                  <span className="stat-label">{t('speedChecker.finalSpeed') || 'Final Speed'}</span>
                  <div className={`speed-value ${tailwind ? 'tailwind-active' : ''}`}>
                    {finalUserSpeed}
                  </div>
                  <div className="speed-breakdown">
                    {userSpeed}
                    {choiceScarf && (
                      <>
                        × 1.5 = {Math.floor(userSpeed * 1.5)}
                      </>
                    )}
                    {tailwind && (
                      <>
                        {choiceScarf ? ' × 2' : '× 2'} = {finalUserSpeed}
                      </>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Middle Panel - Comparison Options */}
        <div className="speed-panel speed-panel-middle">
          <h3>{t('speedChecker.compareAgainst') || 'Compare Against'}</h3>
          
          {/* Weather selector */}
          <div className="form-group">
            <label>{t('calculate.weather')}</label>
            <select
              aria-label={t('calculate.weather')}
              value={weather}
              onChange={e => setWeather(e.target.value)}
              className="form-control"
              style={{ maxWidth: 220 }}
            >
              {ALL_WEATHERS.map(w => (
                <option key={w} value={w}>{t(`weather.${w}`)}</option>
              ))}
            </select>
          </div>

          {/* Terrain selector */}
          <div className="form-group">
            <label>{t('speedChecker.terrain') || 'Terrain'}</label>
            <select
              aria-label={t('speedChecker.terrain') || 'Terrain'}
              value={terrain}
              onChange={e => setTerrain(e.target.value)}
              className="form-control"
              style={{ maxWidth: 220 }}
            >
              {ALL_TERRAINS.map(t => (
                <option key={t} value={t}>{t === 'none' ? 'None' : t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>
          </div>

          <div style={{ marginTop: 10 }}>
            <button
              type="button"
              className={`tailwind-button option-button ${fullyEvolvedOnly ? 'active' : ''}`}
              onClick={() => setFullyEvolvedOnly(v => !v)}
            >
              {t('speedChecker.fullyEvolvedOnly') || 'Fully evolved only'}
            </button>
          </div>
          <div className="comparison-buttons">
            <button
              className={`comparison-mode-btn ${comparisonMode === 'min' ? 'active' : ''}`}
              onClick={() => setComparisonMode('min')}
            >
              <div className="btn-title">{t('speedChecker.minSpeed') || 'Min Speed'}</div>
              <div className="btn-desc">0 EVs, Neutral</div>
            </button>

            <button
              className={`comparison-mode-btn ${comparisonMode === 'custom' ? 'active' : ''}`}
              onClick={() => setComparisonMode('custom')}
            >
              <div className="btn-title">{t('speedChecker.customSpeed') || 'Custom'}</div>
              <div className="btn-desc">Personalized EVs</div>
            </button>

            <button
              className={`comparison-mode-btn ${comparisonMode === 'max' ? 'active' : ''}`}
              onClick={() => setComparisonMode('max')}
            >
              <div className="btn-title">{t('speedChecker.maxSpeed') || 'Max Speed'}</div>
              <div className="btn-desc">32 units, +Nature</div>
            </button>
          </div>

          {comparisonMode === 'custom' && (
            <div className="custom-options">
              <div className="form-group">
                <label>{t('speedChecker.opponentEV') || 'Opponent EVs'}</label>
                <input 
                  type="number" 
                  value={customEV} 
                  onChange={(e) => setCustomEV(Math.max(0, Math.min(32, parseInt(e.target.value) || 0)))}
                  min="0"
                  max="32"
                  step="1"
                />
              </div>
              <div className="form-group">
                <button
                  type="button"
                  className={`tailwind-button ${customNature ? 'active' : ''}`}
                  onClick={() => setCustomNature(!customNature)}
                  aria-pressed={customNature}
                >
                  <span className="tailwind-icon">🍀</span>
                  {t('speedChecker.positiveNatureCheck') || '+Speed Nature'}: {customNature ? t('speedChecker.on') || 'ON' : t('speedChecker.off') || 'OFF'}
                </button>
              </div>
              {/* Choice Scarf Toggle (middle panel, custom only) */}
              <div className="form-group">
                <button 
                  className={`tailwind-button${choiceScarfMiddle ? ' active' : ''}`}
                  onClick={() => setChoiceScarfMiddle(!choiceScarfMiddle)}
                  type="button"
                >
                  <span className="tailwind-icon">🧣</span>
                  {t('speedChecker.choiceScarf') || 'Choice Scarf'}: {choiceScarfMiddle ? t('speedChecker.on') || 'ON' : t('speedChecker.off') || 'OFF'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Results */}
        <div className="speed-panel speed-panel-right">
          <h3>{t('speedChecker.results') || 'Results'}</h3>
          
          <div className="results-toggle">
            <button
              className={`toggle-btn ${showSlower ? 'active' : ''}`}
              onClick={() => setShowSlower(true)}
            >
              {t('speedChecker.slowerThan') || 'Slower Than You'}
            </button>
            <button
              className={`toggle-btn ${!showSlower ? 'active' : ''}`}
              onClick={() => setShowSlower(false)}
            >
              {t('speedChecker.fasterThan') || 'Faster Than You'}
            </button>
          </div>
          
          {selectedPokemon && (
            <div className="speed-counter">
              {(() => {
                const pool = fullyEvolvedOnly ? allPokemon.filter(p => p.can_evolve === false) : allPokemon
                const countOpp = (pred) => pool.filter(p => {
                  const oppEv = comparisonMode === 'min' ? 0 : comparisonMode === 'max' ? newEvToOld(32) : newEvToOld(customEV)
                  const oppSpeed = calculateSpeed(p.base_stats.speed, level, oppEv, comparisonMode === 'min' ? 'neutral' : comparisonMode === 'max' ? 'positive' : customNature ? 'positive' : 'neutral')
                  const oppFinalSpeed = choiceScarfMiddle ? Math.floor(oppSpeed * 1.5) : oppSpeed
                  return pred(finalUserSpeed, oppFinalSpeed)
                }).length

                return showSlower
                  ? `${results.length} ${t('speedChecker.slowerCount') || 'slower'} • ${countOpp((you, opp) => you <= opp)} ${t('speedChecker.fasterCount') || 'faster'}`
                  : `${results.length} ${t('speedChecker.fasterCount') || 'faster'} • ${countOpp((you, opp) => you > opp)} ${t('speedChecker.slowerCount') || 'slower'}`
              })()}
            </div>
          )}

          <div className="results-list">
            {results.length === 0 && selectedPokemon && (
              <div className="no-results">
                {showSlower 
                  ? (t('speedChecker.noSlower') || 'No Pokémon slower than you!')
                  : (t('speedChecker.noFaster') || 'No Pokémon faster than you!')}
              </div>
            )}
            
            {results.map((result, idx) => (
              <div key={idx} className="result-item">
                <div className="result-header">
                  <div className="result-name">{result.name}</div>
                  <div className="result-types">
                    {result.types && result.types.map((type, i) => (
                      <span key={i} className={`type-badge type-${type.toLowerCase()}`}>
                        {t(`types.${type}`)}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="result-stats">
                  <span className="base-speed">Base: {result.baseSpeed}</span>
                  <span className="final-speed">Final: {result.finalSpeed}</span>
                  <span className={`speed-diff ${result.isFaster ? 'faster' : 'slower'}`}>
                    {result.isFaster ? '+' : '-'}{result.speedDiff}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
