import { useTranslation } from 'react-i18next'

function PricingPage() {
  const { t } = useTranslation()

  const plans = [
    {
      name: t('pricing.free.name'),
      price: '$0',
      period: '',
      features: [
        t('pricing.free.feature1'),
        t('pricing.free.feature2'),
        t('pricing.free.feature3'),
      ],
      cta: t('pricing.free.cta'),
      href: '/',
      highlight: false,
    },
    {
      name: t('pricing.starter.name'),
      price: '$3',
      period: '',
      features: [
        t('pricing.starter.feature1'),
        t('pricing.starter.feature2'),
        t('pricing.starter.feature3'),
      ],
      cta: t('pricing.starter.cta'),
      href: '#',
      highlight: true,
    },
    {
      name: t('pricing.pro.name'),
      price: '$9',
      period: '',
      features: [
        t('pricing.pro.feature1'),
        t('pricing.pro.feature2'),
        t('pricing.pro.feature3'),
      ],
      cta: t('pricing.pro.cta'),
      href: '#',
      highlight: false,
    },
  ]

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="font-display text-4xl font-bold text-white mb-4">
          {t('pricing.title')}
        </h1>
        <p className="text-surface-400 text-lg">
          {t('pricing.subtitle')}
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {plans.map((plan, index) => (
          <div
            key={index}
            className={`rounded-2xl p-6 ${
              plan.highlight
                ? 'bg-gradient-to-b from-primary-900/30 to-surface-900 border-2 border-primary-500'
                : 'bg-surface-900 border border-surface-800'
            }`}
          >
            <h3 className="font-display font-semibold text-xl text-white mb-2">
              {plan.name}
            </h3>
            <div className="mb-6">
              <span className="text-4xl font-bold text-white">{plan.price}</span>
              {plan.period && (
                <span className="text-surface-400 ml-2">{plan.period}</span>
              )}
            </div>
            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, i) => (
                <li key={i} className="flex items-center gap-2 text-surface-300">
                  <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <a
              href={plan.href}
              className={`block w-full py-3 rounded-lg font-semibold text-center transition-all ${
                plan.highlight
                  ? 'bg-primary-500 text-white hover:bg-primary-400'
                  : 'bg-surface-800 text-white hover:bg-surface-700'
              }`}
            >
              {plan.cta}
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PricingPage
