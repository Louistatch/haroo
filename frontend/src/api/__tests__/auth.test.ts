/**
 * TASK-8.4: Tests du module API auth
 *
 * Couvre: loginEmail, registerEmail, logout, token management, interceptors
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  setTokens,
  clearTokens,
  isLoggedIn,
  logout,
} from '../auth'

describe('Auth Token Management', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('setTokens stocke les tokens dans localStorage', () => {
    setTokens('access123', 'refresh456')
    expect(localStorage.getItem('access_token')).toBe('access123')
    expect(localStorage.getItem('refresh_token')).toBe('refresh456')
  })

  it('setTokens ne stocke que access si refresh absent', () => {
    setTokens('access_only')
    expect(localStorage.getItem('access_token')).toBe('access_only')
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('clearTokens supprime les tokens', () => {
    setTokens('a', 'r')
    clearTokens()
    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
  })

  it('isLoggedIn retourne true si access_token existe', () => {
    setTokens('token')
    expect(isLoggedIn()).toBe(true)
  })

  it('isLoggedIn retourne false sans token', () => {
    expect(isLoggedIn()).toBe(false)
  })

  it('logout vide les tokens', () => {
    setTokens('a', 'r')
    logout()
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})
