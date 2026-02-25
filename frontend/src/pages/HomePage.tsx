import { useState, useEffect, useCallback, useRef } from 'react'
import { useTranslation } from 'react-i18next'
import ForceGraph2D from 'react-force-graph-2d'
import { scanWebsite, getQuota, ScanResult, QuotaInfo } from '../lib/api'

interface GraphData {
  nodes: { id: number; url: string; title: string; status: number; depth: number; linkCount: number }[]
  links: { source: number; target: number }[]
}

function HomePage() {
  const { t } = useTranslation()
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ScanResult | null>(null)
  const [quota, setQuota] = useState<QuotaInfo | null>(null)
  const [graphData, setGraphData] = useState<GraphData | null>(null)
  const [selectedNode, setSelectedNode] = useState<number | null>(null)
  const graphRef = useRef<any>(null)

  useEffect(() => {
    getQuota().then(setQuota).catch(console.error)
  }, [])

  useEffect(() => {
    if (result) {
      setGraphData({
        nodes: result.nodes,
        links: result.links,
      })
    }
  }, [result])

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)
    setGraphData(null)

    try {
      const scanResult = await scanWebsite(url)
      setResult(scanResult)
      setQuota(prev => prev ? { ...prev, total_remaining: scanResult.remaining_scans } : null)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.scanFailed'))
    } finally {
      setLoading(false)
    }
  }

  const nodeColor = useCallback((node: any) => {
    if (node.status !== 200) return '#ef4444' // red for broken
    if (node.depth === 0) return '#22c55e' // green for root
    if (node.depth === 1) return '#3b82f6' // blue for depth 1
    return '#8b5cf6' // purple for depth 2
  }, [])

  const nodeLabel = useCallback((node: any) => {
    return `${node.title}\n${node.url}\nStatus: ${node.status}\nLinks: ${node.linkCount}`
  }, [])

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-12">
        <h1 className="font-display text-4xl md:text-5xl font-bold text-white mb-4">
          {t('hero.title')}
        </h1>
        <p className="text-surface-400 text-lg max-w-2xl mx-auto">
          {t('hero.subtitle')}
        </p>
      </div>

      {/* Scan Form */}
      <form onSubmit={handleScan} className="max-w-2xl mx-auto mb-12">
        <div className="flex gap-4">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder={t('form.placeholder')}
            className="flex-1 px-4 py-3 bg-surface-900 border border-surface-700 rounded-lg text-white placeholder-surface-500 focus:outline-none focus:border-primary-500 font-mono text-sm"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-500 text-white font-semibold rounded-lg hover:from-primary-500 hover:to-primary-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2"
          >
            {loading ? (
              <>
                <svg className="w-5 h-5 spinner" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {t('form.scanning')}
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                {t('form.scan')}
              </>
            )}
          </button>
        </div>
        
        {quota && (
          <p className="text-surface-500 text-sm mt-2 text-center">
            {t('form.remaining', { count: quota.total_remaining })}
          </p>
        )}
      </form>

      {/* Error */}
      {error && (
        <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400">
          {error}
        </div>
      )}

      {/* Results */}
      {result && graphData && (
        <div className="space-y-8">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 bg-surface-900 rounded-lg border border-surface-800">
              <p className="text-surface-500 text-sm">{t('stats.pages')}</p>
              <p className="text-2xl font-bold text-white">{result.stats.totalPages}</p>
            </div>
            <div className="p-4 bg-surface-900 rounded-lg border border-surface-800">
              <p className="text-surface-500 text-sm">{t('stats.links')}</p>
              <p className="text-2xl font-bold text-white">{result.stats.totalLinks}</p>
            </div>
            <div className="p-4 bg-surface-900 rounded-lg border border-surface-800">
              <p className="text-surface-500 text-sm">{t('stats.broken')}</p>
              <p className="text-2xl font-bold text-red-400">{result.stats.brokenPages}</p>
            </div>
            <div className="p-4 bg-surface-900 rounded-lg border border-surface-800">
              <p className="text-surface-500 text-sm">{t('stats.depth')}</p>
              <p className="text-2xl font-bold text-white">{result.stats.maxDepth}</p>
            </div>
          </div>

          {/* Graph */}
          <div className="graph-container p-4" style={{ height: '600px' }}>
            <ForceGraph2D
              ref={graphRef}
              graphData={graphData}
              nodeColor={nodeColor}
              nodeLabel={nodeLabel}
              nodeRelSize={6}
              linkColor={() => '#3f3f46'}
              linkWidth={1}
              linkDirectionalArrowLength={3}
              linkDirectionalArrowRelPos={1}
              onNodeClick={(node: any) => setSelectedNode(node.id)}
              backgroundColor="transparent"
              width={typeof window !== 'undefined' ? window.innerWidth - 80 : 800}
              height={560}
            />
          </div>

          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
              <span className="text-surface-400">{t('legend.root')}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-blue-500"></span>
              <span className="text-surface-400">{t('legend.depth1')}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-purple-500"></span>
              <span className="text-surface-400">{t('legend.depth2')}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="text-surface-400">{t('legend.broken')}</span>
            </div>
          </div>

          {/* Page List */}
          <div className="bg-surface-900 rounded-lg border border-surface-800 overflow-hidden">
            <div className="p-4 border-b border-surface-800">
              <h3 className="font-display font-semibold text-white">{t('pageList.title')}</h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {result.nodes.map((node) => (
                <div
                  key={node.id}
                  className={`p-4 border-b border-surface-800 last:border-b-0 hover:bg-surface-800/50 transition-colors ${
                    selectedNode === node.id ? 'bg-surface-800' : ''
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <p className="text-white font-medium truncate">{node.title || t('pageList.untitled')}</p>
                      <p className="text-surface-500 font-mono text-sm truncate">{node.url}</p>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                      <span className={`px-2 py-1 rounded ${
                        node.status === 200 ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'
                      }`}>
                        {node.status || 'Error'}
                      </span>
                      <span className="text-surface-500">{node.linkCount} {t('pageList.links')}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Features */}
      {!result && (
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-lg bg-primary-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="font-display font-semibold text-white mb-2">{t('features.fast.title')}</h3>
            <p className="text-surface-400">{t('features.fast.desc')}</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-lg bg-accent-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="font-display font-semibold text-white mb-2">{t('features.visual.title')}</h3>
            <p className="text-surface-400">{t('features.visual.desc')}</p>
          </div>
          <div className="text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-lg bg-blue-500/10 flex items-center justify-center">
              <svg className="w-6 h-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="font-display font-semibold text-white mb-2">{t('features.safe.title')}</h3>
            <p className="text-surface-400">{t('features.safe.desc')}</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default HomePage
