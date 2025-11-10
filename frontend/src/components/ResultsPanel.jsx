import React from 'react'

export default function ResultsPanel({ result }){
  if(!result) return <div className="results-panel">Aucun résultat — cliquez sur Calculer</div>
  return (
    <div className="results-panel">
      <h3>Résultats</h3>
      {result.note && <div className="note">{result.note}</div>}
      {result.rolls && (
        <div>
          <h4>16 rolls (dégâts ou pourcentages)</h4>
          <div className="rolls">{result.rolls.map((r,i)=> <div key={i} className="roll">{i+1}: {r}</div>)}</div>
        </div>
      )}
      {result.avg_damage && <div>Moyenne dégâts: {result.avg_damage}</div>}
      {result.ohko_percent !== undefined && <div>Chance OHKO: {result.ohko_percent}%</div>}
      {result.hits_to_ko && <div>Guaranteed hits to KO (worst roll): {result.hits_to_ko}</div>}
    </div>
  )
}
