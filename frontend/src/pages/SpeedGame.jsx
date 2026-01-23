import React, { useEffect, useState } from 'react'
import { useTranslation } from '../i18n/LanguageContext'
import { API_URL } from '../apiConfig'

export default function SpeedGame() {
  const { t, getPokemonName } = useTranslation()
  const [allPokemon, setAllPokemon] = useState([])
  const [left, setLeft] = useState(null)
  const [right, setRight] = useState(null)
  const [result, setResult] = useState(null)

  useEffect(() => {
    fetch(`${API_URL}/api/pokemon`)
      .then(r => r.json())
      .then(data => {
        const list = (data.results || []).filter(p => p && p.base_stats && typeof p.base_stats.speed === 'number' && p.can_evolve === false)
        setAllPokemon(list)
      }).catch(() => setAllPokemon([]))
  }, [])

  const spriteUrl = (id) => `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`

  function pickPair() {
    setResult(null)
    if (!allPokemon || allPokemon.length < 2) return
    const pool = allPokemon.filter(p => !String(p.name).includes('-') && p.can_evolve === false)
    if (pool.length < 2) return

    // try to find two distinct pokémon with close but unequal base speed
    let a = null, b = null
    const maxAttempts = 300
    for (let i = 0; i < maxAttempts; i++) {
      const i1 = Math.floor(Math.random() * pool.length)
      let i2 = Math.floor(Math.random() * pool.length)
      while (i2 === i1) i2 = Math.floor(Math.random() * pool.length)
      const p1 = pool[i1]
      const p2 = pool[i2]
      const s1 = p1.base_stats.speed || 0
      const s2 = p2.base_stats.speed || 0
      const diff = Math.abs(s1 - s2)
      if (diff >= 1 && diff <= 8) { a = p1; b = p2; break }
    }
    if (!a || !b) {
      // fallback: pick two distinct random
      const shuffled = pool.sort(() => Math.random() - 0.5)
      a = shuffled[0]; b = shuffled[1]
      if (a && b && a.base_stats.speed === b.base_stats.speed) {
        // ensure no exact tie by nudging selection
        for (const cand of pool) {
          if (cand.id !== a.id && cand.base_stats.speed !== a.base_stats.speed) { b = cand; break }
        }
      }
    }
    setLeft(a)
    setRight(b)
  }

  useEffect(() => { pickPair() }, [allPokemon])

  const handleGuess = (side) => {
    if (!left || !right) return
    const leftBase = left.base_stats.speed || 0
    const rightBase = right.base_stats.speed || 0
    const correct = leftBase > rightBase ? 'left' : 'right'
    setResult({ chosen: side, correct, left: { base: leftBase }, right: { base: rightBase } })
  }

  return (
    <div className="speed-game-page">
      <h2>{t('speedGame.title') || 'Speed Duel'}</h2>
      <div className="speed-game-board">
        <div className="pokemon-card left">
          {left ? (
            <>
              <img src={spriteUrl(left.id)} alt={left.name} />
              <h3>{getPokemonName(left.id, left.name)}</h3>
              <div>&nbsp;</div>
              <button disabled={!left || !!result} onClick={() => handleGuess('left')}>{t('speedGame.chooseButton') || 'Je choisis'}</button>
            </>
          ) : <div>{t('common.loading') || 'Loading...'}</div>}
        </div>

        <div className="game-center">
          <div className="controls">
            <button onClick={pickPair}>{t('speedGame.next') || 'Suivant'}</button>
          </div>
        </div>

        <div className="pokemon-card right">
          {right ? (
            <>
              <img src={spriteUrl(right.id)} alt={right.name} />
              <h3>{getPokemonName(right.id, right.name)}</h3>
              <div>&nbsp;</div>
              <button disabled={!right || !!result} onClick={() => handleGuess('right')}>{t('speedGame.chooseButton') || 'Je choisis'}</button>
            </>
          ) : <div>{t('common.loading') || 'Loading...'}</div>}
        </div>
      </div>

      {result && (
        <div className="result-panel">
          <h3>{t('speedGame.resultTitle') || 'Résultat'}</h3>
          <div className="result-row">
            <div>
              <strong>{getPokemonName(left.id, left.name)}</strong>
              <div>{t('speedGame.baseLabel') || 'Base:'} {result.left.base}</div>
            </div>
            <div>
              <strong>{getPokemonName(right.id, right.name)}</strong>
              <div>{t('speedGame.baseLabel') || 'Base:'} {result.right.base}</div>
            </div>
          </div>

          <div className={`result-outcome ${result.correct === result.chosen ? 'win' : 'lose'}`}>
            {result.correct === result.chosen ? (t('speedGame.resultWin') || 'TU AS GAGNÉ') : (t('speedGame.resultLose') || 'MAUVAIS CHOIX')}
          </div>
          <div style={{marginTop:8}}><strong>{t('speedGame.fastestLabel') || 'Le plus rapide était:'}</strong> {result.correct === 'left' ? getPokemonName(left.id, left.name) : getPokemonName(right.id, right.name)}</div>

          <button onClick={() => { setResult(null); pickPair() }}>{t('speedGame.next') || 'Suivant'}</button>
        </div>
      )}
    </div>
  )
}

