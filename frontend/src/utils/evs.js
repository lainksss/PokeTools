// EV conversion utilities
// New frontend EV system: 0..32 per stat, total 66
// Backend expects traditional EVs (0..252, steps of 4). Convert accordingly.

export function newEvToOld(newEv) {
  const n = parseInt(newEv) || 0
  if (n <= 0) return 0
  const capped = Math.min(32, n)
  return 4 + (capped - 1) * 8
}

export function convertEvsToOld(evsObj) {
  if (!evsObj) return { hp: 0, attack: 0, defense: 0, special_attack: 0, special_defense: 0, speed: 0 }
  return {
    hp: newEvToOld(evsObj.hp),
    attack: newEvToOld(evsObj.attack),
    defense: newEvToOld(evsObj.defense),
    special_attack: newEvToOld(evsObj.special_attack),
    special_defense: newEvToOld(evsObj.special_defense),
    speed: newEvToOld(evsObj.speed)
  }
}
