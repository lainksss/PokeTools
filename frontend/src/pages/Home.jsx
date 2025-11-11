import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from '../i18n/LanguageContext'

export default function Home() {
  const { t } = useTranslation()

  return (
    <div className="home-page">
      <div className="home-grid">
        <Link to="/calculate" className="home-block block-tl">
          <h3 className="block-title">{t('home.block_calc_title')}</h3>
          <p className="block-desc">{t('home.block_calc_desc')}</p>
        </Link>

        <Link to="/threats" className="home-block block-tr">
          <h3 className="block-title">{t('home.block_threats_title')}</h3>
          <p className="block-desc">{t('home.block_threats_desc')}</p>
        </Link>

        <div className="home-center">
          <h2 className="center-title">{t('home.centerTitle')}</h2>
          <p className="center-desc">{t('home.centerDesc')}</p>
        </div>

        <Link to="/coverage" className="home-block block-bl">
          <h3 className="block-title">{t('home.block_coverage_title')}</h3>
          <p className="block-desc">{t('home.block_coverage_desc')}</p>
        </Link>

        <Link to="/type-coverage" className="home-block block-br">
          <h3 className="block-title">{t('home.block_type_title')}</h3>
          <p className="block-desc">{t('home.block_type_desc')}</p>
        </Link>
      </div>
    </div>
  )
}
