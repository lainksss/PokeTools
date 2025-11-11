import React from 'react'
import { useTranslation } from '../i18n/LanguageContext'

export default function Home() {
  const { t } = useTranslation()
  
  return (
    <div className="home-page">
      <h2>{t('home.welcome')}</h2>
      <p>{t('home.description')}</p>
    </div>
  )
}
