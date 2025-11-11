// Utilitaire pour choisir dynamiquement l'URL de l'API selon l'environnement

const isProd = window.location.hostname.includes('github.io');

export const API_URL = isProd
  ? 'https://poketools-1v5l.onrender.com'
  : 'http://localhost:5000';
