import { headerEn } from './header.js'
import { homeEn } from './home.js'
import { calculateEn } from './pages/calculate.js'
import { coverageEn } from './pages/coverage.js'
import { threatsEn } from './pages/threats.js'
import { typeCoverageEn } from './pages/typecoverage.js'
import { speedCheckerEn } from './pages/speedchecker.js'
import { speedGameEn } from './pages/speedgame.js'

export const enTranslations = {
  nav: headerEn.nav,
  home: homeEn,
  calculate: calculateEn,
  coverage: coverageEn,
  threats: threatsEn,
  typeCoverage: typeCoverageEn,
  speedChecker: speedCheckerEn,
  speedGame: speedGameEn,
  weather: headerEn.weather,
  terrain: headerEn.terrain,
  status: headerEn.status,
  auras: headerEn.auras,
  screens: headerEn.screens,
  natures: headerEn.natures,
  common: headerEn.common,
  types: headerEn.types,
  pokemon: headerEn.pokemon,
  doubleEffects: {
    helpingHand: 'Helping Hand',
    friendGuard: 'Friend Guard'
  }
}
