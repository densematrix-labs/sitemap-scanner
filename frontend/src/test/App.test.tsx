import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../App'
import '../lib/i18n'

// Mock ForceGraph2D
vi.mock('react-force-graph-2d', () => ({
  default: () => <div data-testid="force-graph">Mock Graph</div>,
}))

// Mock fingerprint
vi.mock('../lib/fingerprint', () => ({
  getDeviceId: vi.fn().mockResolvedValue('test-device-id'),
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the app name', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Sitemap Scanner')).toBeInTheDocument()
  })

  it('renders the navigation', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Pricing')).toBeInTheDocument()
  })

  it('renders the hero section', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Visualize Your Website Structure')).toBeInTheDocument()
  })

  it('renders the scan form', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByPlaceholderText(/Enter website URL/)).toBeInTheDocument()
    expect(screen.getByText('Scan Website')).toBeInTheDocument()
  })

  it('renders features section', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Lightning Fast')).toBeInTheDocument()
    expect(screen.getByText('Interactive Graph')).toBeInTheDocument()
    expect(screen.getByText('Safe & Respectful')).toBeInTheDocument()
  })

  it('renders footer', () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    )
    
    expect(screen.getByText(/All rights reserved/)).toBeInTheDocument()
  })
})
