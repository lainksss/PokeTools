import React, { createContext, useContext, useState, useEffect } from 'react'
import { translations } from './translations'

const LanguageContext = createContext()

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('language') || 'fr'
  })
  const [pokemonNames, setPokemonNames] = useState({})
  
  // Charger les noms de Pokémon au démarrage
  useEffect(() => {
    fetch('/api/pokemon-names')
      .then(r => r.json())
      .then(data => setPokemonNames(data))
      .catch(err => console.error('Failed to load Pokemon names:', err))
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
    <LanguageContext.Provider value={{ t, language, changeLanguage, getPokemonName, matchesPokemonName }}>
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
