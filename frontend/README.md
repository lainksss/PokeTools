# Frontend — PokeTools

This document explains how to run and develop the frontend (React + Vite).

Prerequisites
- Node.js 18+ and npm (or pnpm/yarn)

Setup
```powershell
cd frontend
npm install
```

Run (development)
```powershell
npm run dev
```

Build
```powershell
npm run build
# preview the build locally
npm run preview
```

Structure
- `index.html`, `vite.config.js` — Vite config
- `src/App.jsx` — main shell and routing
- `src/pages/` — pages: `Home`, `Calculate`, `Threats`, `Coverage`, `TypeCoverage`
- `src/components/` — UI components
- `src/i18n/` — `LanguageContext.jsx`, `translations.js` for simple i18n
- `src/styles.css` — global styles
- `src/pages/` — pages: `SpeedGame` (Trouve la vitesse — propose `Duel de Vitesse` et `Juste prix (vitesse)`)

Notes
- The frontend uses SSE to receive incremental results for heavy tasks (`/api/find_threats_stream`, `/api/analyze_coverage_stream`). Prefer `EventSource` in simple cases or fetch+streams when you need more control.
- If the frontend cannot reach the backend in dev, check CORS settings and the backend base URL in `src/apiConfig.js` or environment variables.
