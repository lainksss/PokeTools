/**
 * Détermine l'item obligatoire pour un Pokémon en fonction de son nom
 * @param {string} pokemonName - Le nom du Pokémon (ex: "charizard-mega-x", "kyogre-primal")
 * @returns {string|null} Le slug de l'item obligatoire ("mega-gem", "primal-gem") ou null
 */
export function getMandatoryItem(pokemonName) {
  if (!pokemonName) return null
  
  const name = pokemonName.toLowerCase()
  
  if (name.includes('-mega')) {
    return 'mega-gem'
  }
  
  if (name.includes('-primal')) {
    return 'primal-gem'
  }
  
  return null
}

/**
 * Vérifie si un Pokémon a un item obligatoire
 * @param {string} pokemonName - Le nom du Pokémon
 * @returns {boolean}
 */
export function hasMandatoryItem(pokemonName) {
  return getMandatoryItem(pokemonName) !== null
}
