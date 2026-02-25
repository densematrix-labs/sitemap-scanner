import { describe, it, expect, vi, beforeEach } from 'vitest'
import { scanWebsite, getQuota } from '../lib/api'

// Mock fingerprint
vi.mock('../lib/fingerprint', () => ({
  getDeviceId: vi.fn().mockResolvedValue('test-device-id'),
}))

describe('API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('scanWebsite', () => {
    it('handles successful scan response', async () => {
      const mockResponse = {
        success: true,
        root_url: 'https://example.com',
        nodes: [{ id: 0, url: 'https://example.com', title: 'Example', status: 200, depth: 0, linkCount: 5 }],
        links: [],
        stats: { totalPages: 1, totalLinks: 0, brokenPages: 0, maxDepth: 0 },
        remaining_scans: 4,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      })

      const result = await scanWebsite('https://example.com')

      expect(result.success).toBe(true)
      expect(result.root_url).toBe('https://example.com')
      expect(result.nodes).toHaveLength(1)
    })

    it('handles string error detail', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: () => Promise.resolve({ detail: 'Something went wrong' }),
      })

      await expect(scanWebsite('https://example.com'))
        .rejects.toThrow('Something went wrong')
    })

    it('handles object error detail with error field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'No scans remaining', code: 'quota_exhausted' }
        }),
      })

      await expect(scanWebsite('https://example.com'))
        .rejects.toThrow('No scans remaining')
    })

    it('handles object error detail with message field', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          detail: { message: 'Invalid URL format' }
        }),
      })

      await expect(scanWebsite('https://example.com'))
        .rejects.toThrow('Invalid URL format')
    })

    it('never throws [object Object]', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 402,
        json: () => Promise.resolve({
          detail: { error: 'Payment required', extra: { some: 'data' } }
        }),
      })

      try {
        await scanWebsite('https://example.com')
        expect.fail('Should have thrown')
      } catch (e) {
        expect((e as Error).message).not.toContain('[object Object]')
        expect((e as Error).message).not.toContain('object Object')
      }
    })
  })

  describe('getQuota', () => {
    it('returns quota info', async () => {
      const mockQuota = {
        free_remaining: 5,
        paid_remaining: 0,
        total_remaining: 5,
      }

      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockQuota),
      })

      const result = await getQuota()

      expect(result.free_remaining).toBe(5)
      expect(result.total_remaining).toBe(5)
    })
  })
})
