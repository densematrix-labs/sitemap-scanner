import { getDeviceId } from './fingerprint'

const API_BASE = '/api/v1'

export interface ScanNode {
  id: number
  url: string
  title: string
  status: number
  depth: number
  linkCount: number
}

export interface ScanLink {
  source: number
  target: number
}

export interface ScanStats {
  totalPages: number
  totalLinks: number
  brokenPages: number
  maxDepth: number
}

export interface ScanResult {
  success: boolean
  root_url: string
  nodes: ScanNode[]
  links: ScanLink[]
  stats: ScanStats
  remaining_scans: number
}

export interface QuotaInfo {
  free_remaining: number
  paid_remaining: number
  total_remaining: number
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Request failed' }))
    // Handle both string and object detail
    const errorMessage = typeof data.detail === 'string' 
      ? data.detail 
      : data.detail?.error || data.detail?.message || 'Request failed'
    throw new Error(errorMessage)
  }
  return response.json()
}

export async function scanWebsite(url: string, maxPages?: number, maxDepth?: number): Promise<ScanResult> {
  const deviceId = await getDeviceId()
  
  const response = await fetch(`${API_BASE}/scan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Device-Id': deviceId,
    },
    body: JSON.stringify({
      url,
      max_pages: maxPages || 50,
      max_depth: maxDepth || 2,
    }),
  })
  
  return handleResponse<ScanResult>(response)
}

export async function getQuota(): Promise<QuotaInfo> {
  const deviceId = await getDeviceId()
  
  const response = await fetch(`${API_BASE}/scan/quota`, {
    headers: {
      'X-Device-Id': deviceId,
    },
  })
  
  return handleResponse<QuotaInfo>(response)
}
