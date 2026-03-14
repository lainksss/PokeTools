/**
 * Central utility for mandatory Pokémon configurations (item, ability).
 * Applied to Mega, Primal, and Crowned forms.
 */

// Exact slug matches (checked before suffix patterns — crowned before mega/primal)
const MANDATORY_CONFIGS_EXACT = {
  'zacian-crowned': { item: 'rusted-sword', ability: 'intrepid-sword' },
  'zamazenta-crowned': { item: 'rusted-shield', ability: 'dauntless-shield' },
}

/**
 * Get full mandatory configuration (item, ability) for a Pokémon.
 * @param {string} pokemonName
 * @returns {{item: string, ability?: string}|null}
 */
export function getMandatoryConfig(pokemonName) {
  if (!pokemonName) return null

  const name = pokemonName.toLowerCase()

  // Exact match first
  if (MANDATORY_CONFIGS_EXACT[name]) return MANDATORY_CONFIGS_EXACT[name]

  // Suffix patterns
  if (name.includes('-mega')) return { item: 'mega-gem' }
  if (name.includes('-primal')) return { item: 'primal-gem' }

  return null
}

/**
 * Get mandatory item slug for a Pokémon, or null.
 * @param {string} pokemonName
 * @returns {string|null}
 */
export function getMandatoryItem(pokemonName) {
  const config = getMandatoryConfig(pokemonName)
  return config?.item ?? null
}

/**
 * Get mandatory ability slug for a Pokémon, or null.
 * @param {string} pokemonName
 * @returns {string|null}
 */
export function getMandatoryAbility(pokemonName) {
  const config = getMandatoryConfig(pokemonName)
  return config?.ability ?? null
}

/**
 * Check if a Pokémon has a mandatory item.
 * @param {string} pokemonName
 * @returns {boolean}
 */
export function hasMandatoryItem(pokemonName) {
  return getMandatoryItem(pokemonName) !== null
}
