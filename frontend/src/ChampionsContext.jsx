import React, { createContext, useContext, useEffect, useState } from 'react'
import { API_URL } from './apiConfig'

const ChampionsContext = createContext()

export function ChampionsProvider({ children }) {
  const [championsOnly, setChampionsOnly] = useState(() => {
    try {
      return localStorage.getItem('championsOnly') === 'true'
    } catch {
      return false
    }
  })

  // Set of champion IDs (numbers) loaded from the backend
  const [championIds, setChampionIds] = useState(new Set())
  const [championsLoaded, setChampionsLoaded] = useState(false)

  // Load champion IDs from the API on mount
  useEffect(() => {
    fetch(`${API_URL}/api/champions`)
      .then(r => r.json())
      .then(data => {
        const ids = data.champion_ids || []
        setChampionIds(new Set(ids))
        setChampionsLoaded(true)
      })
      .catch(err => {
        console.error('Failed to load champions list:', err)
        setChampionsLoaded(true) // proceed even if failed
      })
  }, [])

  const toggleChampionsOnly = () => {
    setChampionsOnly(prev => {
      const next = !prev
      try {
        localStorage.setItem('championsOnly', String(next))
      } catch {}
      return next
    })
  }

  return (
    <ChampionsContext.Provider value={{ championsOnly, toggleChampionsOnly, championIds, championsLoaded }}>
      {children}
    </ChampionsContext.Provider>
  )
}

export function useChampions() {
  const context = useContext(ChampionsContext)
  if (!context) {
    throw new Error('useChampions must be used within a ChampionsProvider')
  }
  return context
}
