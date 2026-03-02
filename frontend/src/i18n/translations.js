// Traductions pour l'application
export const translations = {
  fr: {
    // Navigation
    nav: {
      calculator: "Calculateur",
      threats: "Analyse des menaces",
      coverage: "Couverture offensive",
      typeCoverage: "Couverture de types",
      speedChecker: "Vérificateur de vitesse",
      speedGame: "Trouve la vitesse",
    },
    
    
    // Page Home
    home: {
      welcome: "Bienvenue",
      description: "Utilisez le menu pour accéder au calculateur de dégâts ou à l'analyse des menaces.",
      centerTitle: "PokeTools",
      centerDesc: "PokeTools est dédié au Pokemon Compétitif et a pour but de simplifier des tâches, calculs et reflexions supplémentaires pour vos équipes. Certaines fonctionnalités sont encore en développement.",
      block_calc_title: "Calculateur de dégât",
      block_calc_desc: "Calculateur de dégâts (EVs, objets, talents, météo, terrain,...). Certains talents manquent.",
      block_threats_title: "Analyseur de menace",
      block_threats_desc: "Trouvez rapidement quels Pokémon peuvent KO un défenseur donné (paramétrables !).",
      block_coverage_title: "Vérifier la couverture offensive",
      block_coverage_desc: "Analysez quelles attaques couvrent le mieux vos menaces et comblent les faiblesses (paramétrables !).",
      block_type_title: "Vérifier la couverture de type",
      block_type_desc: "Évaluez les résistances et vulnérabilités pour compléter votre équipe.",
      block_speed_title: "Vérificateur de vitesse",
      block_speed_desc: "Choisis ton pokemon, tes evs, et pleins de paramètres (pour toi ou pour les adversaires) !"
    },
    
    // Page Calculate
    calculate: {
      title: "Calculateur de dégâts Pokémon",
      attacker: "Pokémon Attaquant",
      defender: "Pokémon Défenseur",
      selectPokemon: "Sélectionner un Pokémon",
      search: "Rechercher...",
      level: "Niveau",
      nature: "Nature",
      ability: "Talent",
      evs: "EVs",
      hp: "PV",
      attack: "Attaque",
      defense: "Défense",
      spAttack: "Atq. Spé.",
      spDefense: "Déf. Spé.",
      speed: "Vitesse",
      terastallized: "Téracristallisé",
      teraType: "Type Téra",
      move: "Attaque",
      selectMove: "Sélectionner une attaque",
      searchMove: "Rechercher une attaque...",
      searchAbility: "Rechercher un talent...",
      item: "Objet tenu",
      searchItem: "Rechercher un objet...",
      critical: "Coup critique",
      attackerStatus: "Statut de l'attaquant",
      defenderStatus: "Statut du défenseur",
      battleMode: "Mode de combat",
      battleConditions: "Conditions de combat",
      single: "Simple",
      double: "Double",
      weather: "Météo",
      terrain: "Terrain",
      auras: "Auras",
      screens: "Écrans",
      calculate: "Calculer",
      results: "Résultats",
      damage: "Dégâts",
      minDamage: "Min",
      maxDamage: "Max",
      koChance: "% KO",
      guaranteed: "Garanti",
      selectPokemonError: "Veuillez sélectionner un Pokémon attaquant et défenseur",
      selectMoveError: "Veuillez sélectionner une attaque pour l'attaquant"
    },
    
    // Page Threats
    threats: {
      title: "Analyse des menaces",
      subtitle: "Trouvez tous les Pokémon pouvant KO votre défenseur",
      defender: "Défenseur",
      conditions: "Conditions",
      koMode: "Mode KO",
      ohko: "OHKO",
      twohko: "2HKO",
      weather: "Météo",
      terrain: "Terrain",
      findThreats: "Trouver les menaces",
      searching: "Recherche...",
      results: "Résultats",
      threats: "menaces",
      analyzing: "Analyse en cours...",
      noThreats: "Aucune menace trouvée ou cliquez sur \"Trouver les menaces\"",
      pokemonAnalyzed: "Pokémon analysés",
      threatsFound: "Menace(s) trouvée(s)",
      guaranteedOnly: "KO garantis (100%)",
      showOnlyGuaranteed: "Afficher uniquement les KO garantis",
      minRolls: "Minimum de rolls",
      attack: "Attaque",
      type: "Type",
      power: "Puissance",
      damage: "Dégâts",
      rolls: "rolls",
      nature: "Nature",
      guaranteedKO: "✓ KO Garanti",
      physical: "Physique",
      special: "Spécial"
      ,
      attackOptions: "Options de l'attaquant",
      noAttack: "Pas d'attaque",
      custom: "Customisé",
      maxAtk: "Max Atq/SpA",
      customEVLabel: "EVs à assigner:",
      natureBoost: "Atq/SpA nature",
      itemChoice: "Objet Choix",
      lifeOrb: "Orbe Vie"
    },

    // Page Coverage
    coverage: {
      title: "Analyse de couverture offensive",
      description: "Analysez quels Pokémon votre attaquant peut KO avec ses attaques",
      analysisSettings: "Paramètres d'analyse",
      analyze: "Analyser la couverture",
      moves: "Attaques (max 4)",
      found: "Trouvés",
      results: "Résultats",
      noCoverage: "Aucun Pokémon trouvé avec ces critères",
      showAlive: "Afficher ceux qui survivent",
      bulkMode: "Bulk des adversaires",
      bulkNone: "Aucun bulk",
      bulkCustom: "Bulk customisé",
      bulkMax: "Bulk maximum",
      customEvs: "EVs personnalisés: défenses | PV",
      bulkNatureLabel: "Nature assignée pour la défense",
      bulkNatureByMove: "Selon l'attaque",
      bulkNatureDef: "Défense",
      bulkNatureSpDef: "Déf. Spé.",
      natureDefSpDef: "Nature def/spe def",
      bulkNatureToggle: "Adapter/Fixer nature",
      hpEvsLabel: "EVs en PV",
      bulkNatureToggle: "Adapter la nature",
      assaultVest: "Veste de Combat",
      evoluroc: "Evoluroc"
    },

    // Page Type Coverage
    typeCoverage: {
      title: "Couverture de types",
      description: "Analysez les Pokémon qui ne sont PAS touchés en super efficace par vos attaques",
      analysisSettings: "Paramètres d'analyse",
      analyze: "Analyser les types",
      results: "Pokémon non couverts",
      noResults: "Tous les Pokémon sont couverts ou cliquez sur \"Analyser les types\"",
      foundCount: "Pokémon non couverts",
      bestEffectiveness: "Meilleure efficacité"
    },
    
    // Speed Checker
    speedChecker: {
      title: "Vérificateur de vitesse",
      yourPokemon: "Votre Pokémon",
      selectPokemon: "Sélectionner un Pokémon",
      choose: "Choisir...",
      level: "Niveau",
      speedEV: "EVs en Vitesse",
      nature: "Nature",
      positiveNature: "+Vitesse",
      neutralNature: "Neutre",
      negativeNature: "-Vitesse",
      tailwind: "Vent Arrière",
      finalSpeed: "Vitesse finale",
      baseSpeed: "Vitesse de base:",
      compareAgainst: "Comparer contre",
      minSpeed: "Vitesse Min",
      customSpeed: "Personnalisé",
      maxSpeed: "Vitesse Max",
      opponentEV: "EVs adversaire",
      positiveNatureCheck: "Nature +Vitesse",
      results: "Résultats",
      slowerThan: "Plus lents que vous",
      fasterThan: "Plus rapides que vous",
      slowerCount: "plus lents",
      fasterCount: "plus rapides",
      noSlower: "Aucun Pokémon plus lent que vous !",
      noFaster: "Aucun Pokémon plus rapide que vous !",
      choiceScarf: "Mouchoir Choix",
      on: "Activé",
      off: "Désactivé"
    },
    
    // Speed Game (multiple mini-games)
    speedGame: {
      title: "Trouve la vitesse",
      modeDuel: "Duel de Vitesse",
      modeGuess: "Juste prix (vitesse)",
      chooseButton: "Je choisis",
      next: "Suivant",
      conditionLabel: "Condition",
      hint: "Choisis le Pokémon le plus rapide après modificateurs",
      resultTitle: "Résultat",
      baseLabel: "Base:",
      fastestLabel: "Le plus rapide était:",
      resultWin: "TU AS GAGNÉ",
      resultLose: "MAUVAIS CHOIX",
      resultTie: "ÉGALITÉ",

      // Guess-the-speed game
      guessTitle: "Devine la vitesse",
      guessPlaceholder: "Entrez la vitesse (base)",
      submitGuess: "Valider",
      guessResultCorrect: "Exact!",
      guessResultHigher: "Trop haut",
      guessResultLower: "Trop bas",
      revealBase: "Vitesse de base:",
      playAgain: "Rejouer",
      pickNew: "Nouveau Pokémon"
    },
    
    // Pokemon Panel
    pokemon: {
      types: "Types",
      evsRemaining: "EVs restants",
      neutral: "neutral",
      none: "Aucun",
      accuracy: "Précision",
      category: "Catégorie"
    },
    
    // Météos
    weather: {
      none: "Aucune météo",
      sun: "Soleil",
      rain: "Pluie",
      sandstorm: "Tempête de sable",
      snow: "Neige"
    },
    
    // Terrains
    terrain: {
      none: "Aucun terrain",
      grassy: "Herbu",
      electric: "Électrique",
      misty: "Brumeux",
      psychic: "Psychique"
    },

    // Statuts possibles
    status: {
      none: "Aucun",
      burn: "Brûlé",
      poison: "Empoisonné",
      paralysis: "Paralysé"
    },

    // Auras (field conditions)
    auras: {
      fairy: "Aura Féerique",
      dark: "Aura Ténébreuse",
      break: "Aura Inversée"
    },

    // Screens
    screens: {
      reflect: "Protection",
      light: "Mur lumière",
      aurora: "Voile Aurore"
    },
    
    // Natures communes
    natures: {
      hardy: "Hardi",
      lonely: "Solo",
      brave: "Brave",
      adamant: "Rigide",
      naughty: "Mauvais",
      bold: "Assuré",
      relaxed: "Relax",
      impish: "Malin",
      lax: "Lâche",
      timid: "Timide",
      hasty: "Pressé",
      serious: "Sérieux",
      jolly: "Jovial",
      naive: "Naïf",
      modest: "Modeste",
      mild: "Doux",
      quiet: "Discret",
      bashful: "Pudique",
      rash: "Foufou",
      calm: "Calme",
      gentle: "Gentil",
      sassy: "Malpoli",
      careful: "Prudent",
      quirky: "Bizarre"
    },
    
    // Commun
    common: {
      loading: "Chargement...",
      error: "Erreur",
      close: "Fermer",
      clear: "Effacer",
      noResults: "Aucun résultat"
    },

    // Types
    types: {
      normal: "Normal",
      fighting: "Combat",
      flying: "Vol",
      poison: "Poison",
      ground: "Sol",
      rock: "Roche",
      bug: "Insecte",
      ghost: "Spectre",
      steel: "Acier",
      fire: "Feu",
      water: "Eau",
      grass: "Plante",
      electric: "Électrik",
      psychic: "Psy",
      ice: "Glace",
      dragon: "Dragon",
      dark: "Ténèbres",
      fairy: "Fée",
      stellar: "Stellaire"
    }
  },
  
  en: {
    // Navigation
    nav: {
      calculator: "Calculator",
      threats: "Threat Analysis",
      coverage: "Offensive Coverage",
      typeCoverage: "Type Coverage",
      speedChecker: "Speed Checker",
      speedGame: "Find Speed",
    },
    
    // Page Home
    home: {
      welcome: "Welcome",
      description: "Use the menu to access the damage calculator or threat analysis.",
      centerTitle: "PokeTools",
      centerDesc: "PokeTools is dedicated to Competitive Pokémon and aims to simplify tasks, calculations and extra thinking for your teams. Some features are still in development.",
      block_calc_title: "Damage calculator",
      block_calc_desc: "Damage calculator (EVs, items, abilities, weather, terrain, etc.). Some abilities are missing.",
      block_threats_title: "Threat analyzer",
      block_threats_desc: "Quickly find which Pokémon can KO a given defender (configurable).",
      block_coverage_title: "Check offensive coverage",
      block_coverage_desc: "Analyze which moves best cover your threats and patch weaknesses (configurable).",
      block_type_title: "Check type coverage",
      block_type_desc: "Evaluate resistances and vulnerabilities to round out your team.",
      block_speed_title: "Speed checker",
      block_speed_desc: "Choose your Pokémon, your EVs, and lots of parameters (for you or for opponents)!"
    },
    
    // Page Calculate
    calculate: {
      title: "Pokémon Damage Calculator",
      attacker: "Attacking Pokémon",
      defender: "Defending Pokémon",
      selectPokemon: "Select a Pokémon",
      search: "Search...",
      level: "Level",
      nature: "Nature",
      ability: "Ability",
      evs: "EVs",
      hp: "HP",
      attack: "Attack",
      defense: "Defense",
      spAttack: "Sp. Atk",
      spDefense: "Sp. Def",
      speed: "Speed",
      terastallized: "Terastallized",
      teraType: "Tera Type",
      move: "Move",
      selectMove: "Select a move",
      searchMove: "Search move...",
      searchAbility: "Search ability...",
      item: "Held item",
      searchItem: "Search item...",
      critical: "Critical hit",
      attackerStatus: "Attacker status",
      defenderStatus: "Defender status",
      battleMode: "Battle mode",
      battleConditions: "Battle Conditions",
      single: "Single",
      double: "Double",
      weather: "Weather",
      terrain: "Terrain",
      auras: "Auras",
      screens: "Screens",
      calculate: "Calculate",
      results: "Results",
      damage: "Damage",
      minDamage: "Min",
      maxDamage: "Max",
      koChance: "KO%",
      guaranteed: "Guaranteed",
      selectPokemonError: "Please select an attacking and defending Pokémon",
      selectMoveError: "Please select a move for the attacker"
    },
    
    // Page Threats
    threats: {
      title: "Threat Analysis",
      subtitle: "Find all Pokémon that can KO your defender",
      defender: "Defender",
      conditions: "Conditions",
      koMode: "KO Mode",
      ohko: "OHKO",
      twohko: "2HKO",
      weather: "Weather",
      terrain: "Terrain",
      findThreats: "Find Threats",
      searching: "Searching...",
      results: "Results",
      threats: "threats",
      analyzing: "Analyzing...",
      noThreats: "No threats found or click \"Find Threats\"",
      pokemonAnalyzed: "Pokémon analyzed",
      threatsFound: "Threat(s) found",
      guaranteedOnly: "Guaranteed KO (100%)",
      showOnlyGuaranteed: "Show only guaranteed KOs",
      minRolls: "Minimum rolls",
      attack: "Attack",
      type: "Type",
      power: "Power",
      damage: "Damage",
      rolls: "rolls",
      nature: "Nature",
      guaranteedKO: "✓ Guaranteed KO",
      physical: "Physical",
      special: "Special"
      ,
      attackOptions: "Attacker Options",
      noAttack: "No attack",
      custom: "Custom",
      maxAtk: "Max Atk/SpA",
      customEVLabel: "EVs to assign:",
      natureBoost: "Atk/SpA nature",
      itemChoice: "Item Choice",
      lifeOrb: "Life Orb"
    },

    // Page Coverage
    coverage: {
      title: "Offensive Coverage Analysis",
      description: "Analyze which Pokémon your attacker can KO with its moves",
      analysisSettings: "Analysis Settings",
      analyze: "Analyze Coverage",
      moves: "Moves (max 4)",
      found: "Found",
      results: "Results",
      noCoverage: "No Pokémon found with these criteria",
      showAlive: "Show survivors",
      bulkMode: "Opponents' bulk",
      bulkNone: "No bulk (0 EVs)",
      bulkCustom: "Custom bulk",
      bulkMax: "Maximum bulk",
      customEvs: "Custom EVs: defenses | hp",
      natureDefSpDef: "Nature def/spdef",
      bulkNatureToggle: "Adapt/Fixed nature",
      hpEvsLabel: "HP EVs",
      bulkNatureLabel: "Assigned defensive nature",
      bulkNatureByMove: "By move (auto)",
      bulkNatureDef: "Defense",
      bulkNatureSpDef: "Sp. Def",
      assaultVest: "Assault Vest",
      evoluroc: "Evoluroc"
    },

    // Page Type Coverage
    typeCoverage: {
      title: "Type Coverage",
      description: "Analyze Pokémon that are NOT hit super effectively by your moves",
      analysisSettings: "Analysis Settings",
      analyze: "Analyze Types",
      results: "Uncovered Pokémon",
      noResults: "All Pokémon are covered or click \"Analyze Types\"",
      foundCount: "Uncovered Pokémon",
      bestEffectiveness: "Best effectiveness"
    },
    
    // Speed Checker
    speedChecker: {
      title: "Speed Checker",
      yourPokemon: "Your Pokémon",
      selectPokemon: "Select a Pokémon",
      choose: "Choose...",
      level: "Level",
      speedEV: "Speed EVs",
      nature: "Nature",
      positiveNature: "+Speed",
      neutralNature: "Neutral",
      negativeNature: "-Speed",
      tailwind: "Tailwind",
      finalSpeed: "Final Speed",
      baseSpeed: "Base Speed:",
      compareAgainst: "Compare Against",
      minSpeed: "Min Speed",
      customSpeed: "Custom",
      maxSpeed: "Max Speed",
      opponentEV: "Opponent EVs",
      positiveNatureCheck: "+Speed Nature",
      results: "Results",
      slowerThan: "Slower Than You",
      fasterThan: "Faster Than You",
      slowerCount: "slower",
      fasterCount: "faster",
      noSlower: "No Pokémon slower than you!",
      noFaster: "No Pokémon faster than you!",
      choiceScarf: "Choice Scarf",
      on: "ON",
      off: "OFF"
    },

    // Speed Game (multiple mini-games)
    speedGame: {
      title: "Find Speed",
      modeDuel: "Speed Duel",
      modeGuess: "Guess The Speed",
      chooseButton: "I choose",
      next: "Next",
      conditionLabel: "Condition",
      hint: "Pick the faster Pokémon after modifiers",
      resultTitle: "Result",
      baseLabel: "Base:",
      fastestLabel: "The fastest was:",
      resultWin: "YOU WON",
      resultLose: "WRONG CHOICE",
      resultTie: "TIE",

      // Guess-the-speed game
      guessTitle: "Guess the speed",
      guessPlaceholder: "Enter base speed",
      submitGuess: "Submit",
      guessResultCorrect: "Correct!",
      guessResultHigher: "Too high",
      guessResultLower: "Too low",
      revealBase: "Base speed:",
      playAgain: "Play again",
      pickNew: "New Pokémon"
    },
    
    // Pokemon Panel
    pokemon: {
      types: "Types",
      evsRemaining: "EVs remaining",
      neutral: "neutral",
      none: "None",
      accuracy: "Accuracy",
      category: "Category"
    },
    
    // Weather
    weather: {
      none: "No weather",
      sun: "Sun",
      rain: "Rain",
      sandstorm: "Sandstorm",
      snow: "Snow"
    },
    
    // Terrain
    terrain: {
      none: "No terrain",
      grassy: "Grassy",
      electric: "Electric",
      misty: "Misty",
      psychic: "Psychic"
    },

    // Possible statuses
    status: {
      none: "None",
      burn: "Burn",
      poison: "Poison",
      paralysis: "Paralysis"
    },

    // Auras (field conditions)
    auras: {
      fairy: "Fairy Aura",
      dark: "Dark Aura",
      break: "Aura Break"
    },

    // Screens
    screens: {
      reflect: "Reflect",
      light: "Light Screen",
      aurora: "Aurora Veil"
    },
    
    // Common natures (keep English names)
    natures: {
      hardy: "Hardy",
      lonely: "Lonely",
      brave: "Brave",
      adamant: "Adamant",
      naughty: "Naughty",
      bold: "Bold",
      relaxed: "Relaxed",
      impish: "Impish",
      lax: "Lax",
      timid: "Timid",
      hasty: "Hasty",
      serious: "Serious",
      jolly: "Jolly",
      naive: "Naive",
      modest: "Modest",
      mild: "Mild",
      quiet: "Quiet",
      bashful: "Bashful",
      rash: "Rash",
      calm: "Calm",
      gentle: "Gentle",
      sassy: "Sassy",
      careful: "Careful",
      quirky: "Quirky"
    },
    
    // Common
    common: {
      loading: "Loading...",
      error: "Error",
      close: "Close",
      clear: "Clear",
      noResults: "No results"
    },

    // Types
    types: {
      normal: "Normal",
      fighting: "Fighting",
      flying: "Flying",
      poison: "Poison",
      ground: "Ground",
      rock: "Rock",
      bug: "Bug",
      ghost: "Ghost",
      steel: "Steel",
      fire: "Fire",
      water: "Water",
      grass: "Grass",
      electric: "Electric",
      psychic: "Psychic",
      ice: "Ice",
      dragon: "Dragon",
      dark: "Dark",
      fairy: "Fairy",
      stellar: "Stellar"
    }
  }
}

// Hook pour utiliser les traductions
export function useTranslation() {
  const [language, setLanguage] = React.useState(
    localStorage.getItem('language') || 'fr'
  )
  
  const t = (key) => {
    const keys = key.split('.')
    let value = translations[language]
    
    for (const k of keys) {
      value = value?.[k]
    }
    
    return value || key
  }
  
  const changeLanguage = (lang) => {
    setLanguage(lang)
    localStorage.setItem('language', lang)
  }
  
  return { t, language, changeLanguage }
}

// Import React pour le hook
import React from 'react'
