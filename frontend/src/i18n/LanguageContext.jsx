
import React, { createContext, useContext, useState, useEffect } from 'react'
import { translations } from './translations'
import { API_URL } from '../apiConfig'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'fr'
  })
  const [pokemonNames, setPokemonNames] = useState({})
  const [moveNames, setMoveNames] = useState({})
  
  // Charger les noms de Pokémon au démarrage
  useEffect(() => {
      fetch(`${API_URL}/api/pokemon-names`)
      .then(r => r.json())
      .then(data => setPokemonNames(data))
      .catch(err => console.error('Failed to load Pokemon names:', err))
      
      // Also load move translations for display in results
      fetch(`${API_URL}/api/move-names`)
      .then(r => r.json())
      .then(data => setMoveNames(data))
      .catch(err => console.error('Failed to load move names:', err))
  }, [])
  
  const changeLanguage = (lang) => {
    setLanguage(lang)
    localStorage.setItem('language', lang)
  }
  
  const t = (key) => {
    const keys = key.split('.')
    let value = translations[language]
    
    for (const k of keys) {
      value = value?.[k]
    }
    
    return value || key
  }
  
  // Fonction pour traduire un nom de Pokémon
  const getPokemonName = (pokemonId, fallbackName) => {
    if (!pokemonNames[pokemonId]) return fallbackName
    return pokemonNames[pokemonId][language] || pokemonNames[pokemonId]['en'] || fallbackName
  }

  // Fonction pour traduire un nom d'attaque (slug or raw name)
  const getMoveName = (moveKeyOrName, fallback) => {
    if (!moveKeyOrName) return fallback || ''
    // If moveKeyOrName is a slug key present in moveNames, return localized
    if (moveNames[moveKeyOrName]) {
      return moveNames[moveKeyOrName][language] || moveNames[moveKeyOrName]['en'] || fallback || moveKeyOrName
    }
    // Otherwise try to find by matching English name (some payloads return raw english names)
    const normalize = s => (s || '').toString().toLowerCase().replace(/[-_]/g, ' ').replace(/[’'`]/g, '').trim()
    const inputNorm = normalize(moveKeyOrName)
    for (const k of Object.keys(moveNames || {})) {
      const entry = moveNames[k]
      if (!entry) continue
      const en = normalize(entry.en)
      const fr = normalize(entry.fr)
      if (en === inputNorm || fr === inputNorm) {
        return entry[language] || entry.en || fallback || moveKeyOrName
      }
    }
    return fallback || moveKeyOrName
  }
  
  // Fonction pour vérifier si un texte correspond à un nom de Pokémon (dans n'importe quelle langue)
  const matchesPokemonName = (pokemonId, searchText) => {
    if (!pokemonNames[pokemonId]) return false
    const search = searchText.toLowerCase()
    const names = pokemonNames[pokemonId]
    // Rechercher dans toutes les langues disponibles
    return Object.values(names).some(name => 
      name && name.toLowerCase().includes(search)
    )
  }
  
  return (
    <LanguageContext.Provider value={{ t, language, changeLanguage, getPokemonName, matchesPokemonName, getMoveName }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useTranslation() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider')
  }
  return context
}
