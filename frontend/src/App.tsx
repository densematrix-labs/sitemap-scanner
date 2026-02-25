import { Routes, Route } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import HomePage from './pages/HomePage'
import PricingPage from './pages/PricingPage'
import LanguageSwitcher from './components/LanguageSwitcher'

function App() {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen bg-surface-950">
      {/* Header */}
      <header className="border-b border-surface-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <a href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
              </svg>
            </div>
            <span className="font-display font-bold text-xl text-white">{t('appName')}</span>
          </a>
          
          <nav className="flex items-center gap-6">
            <a href="/pricing" className="text-surface-400 hover:text-white transition-colors">
              {t('nav.pricing')}
            </a>
            <LanguageSwitcher />
          </nav>
        </div>
      </header>

      {/* Main content */}
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/pricing" element={<PricingPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <p className="text-center text-surface-500 text-sm">
            © 2026 Sitemap Scanner. {t('footer.rights')}
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
