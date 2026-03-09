/**
 * TASK-8.4: Tests du composant Dashboard
 *
 * Le Dashboard redirige vers /home.
 */
import { describe, it, expect, vi } from 'vitest'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Dashboard from '../../pages/Dashboard'

const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return { ...actual, useNavigate: () => mockNavigate }
})

describe('Dashboard', () => {
  it('redirige vers /home', () => {
    render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    )
    expect(mockNavigate).toHaveBeenCalledWith('/home', { replace: true })
  })

  it('ne rend rien visuellement', () => {
    const { container } = render(
      <MemoryRouter>
        <Dashboard />
      </MemoryRouter>
    )
    expect(container.innerHTML).toBe('')
  })
})
