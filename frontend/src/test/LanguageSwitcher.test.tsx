import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import LanguageSwitcher from '../components/LanguageSwitcher'
import '../lib/i18n'

describe('LanguageSwitcher', () => {
  it('renders current language', () => {
    render(<LanguageSwitcher />)
    
    expect(screen.getByText('English')).toBeInTheDocument()
  })

  it('opens dropdown on click', () => {
    render(<LanguageSwitcher />)
    
    const button = screen.getByTestId('lang-switcher').querySelector('button')!
    fireEvent.click(button)
    
    expect(screen.getByText('中文')).toBeInTheDocument()
    expect(screen.getByText('日本語')).toBeInTheDocument()
    expect(screen.getByText('Deutsch')).toBeInTheDocument()
    expect(screen.getByText('Français')).toBeInTheDocument()
    expect(screen.getByText('한국어')).toBeInTheDocument()
    expect(screen.getByText('Español')).toBeInTheDocument()
  })

  it('changes language on selection', async () => {
    render(<LanguageSwitcher />)
    
    const button = screen.getByTestId('lang-switcher').querySelector('button')!
    fireEvent.click(button)
    
    const zhButton = screen.getByText('中文')
    fireEvent.click(zhButton)
    
    // Dropdown should close
    expect(screen.queryByText('日本語')).not.toBeInTheDocument()
  })
})
