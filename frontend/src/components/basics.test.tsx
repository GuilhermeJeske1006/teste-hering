import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { summary } from '../test/fixtures'
import { KpiBar } from './KpiBar'
import { SeverityBadge } from './SeverityBadge'
import { EmptyState, ErrorState, Skeleton } from './States'
import { Tabs } from './Tabs'

describe('KpiBar', () => {
  it('formata números em pt-BR quando recebe o resumo', () => {
    render(<KpiBar summary={{ ...summary, total_lines: 12480, within_policy: 6240 }} />)
    expect(screen.getByTestId('kpi-total')).toHaveTextContent(/^12\.480$/)
    expect(screen.getByTestId('kpi-within-policy')).toHaveTextContent('6.240')
    expect(screen.getByText('50% seguem sozinhas')).toBeInTheDocument()
  })

  it('mostra só o número no testid de exceções abertas quando carregado', () => {
    render(<KpiBar summary={summary} />)
    expect(screen.getByTestId('kpi-open-exceptions').textContent).toBe(String(summary.open_exceptions))
  })

  it('mostra marcadores de carregamento quando ainda não há resumo', () => {
    render(<KpiBar summary={null} />)
    expect(screen.queryByTestId('kpi-total')).not.toBeInTheDocument()
    expect(screen.getAllByLabelText('Carregando')).toHaveLength(4)
  })
})

describe('SeverityBadge', () => {
  it('mostra a severidade em texto quando renderizada', () => {
    render(<SeverityBadge severity="critical" />)
    expect(screen.getByText('Crítica')).toBeInTheDocument()
  })

  it('usa um rótulo neutro quando a severidade é desconhecida', () => {
    render(<SeverityBadge severity="weird" />)
    expect(screen.getByText('Sem severidade')).toBeInTheDocument()
  })
})

describe('Tabs', () => {
  const tabs = [{ id: 'a', label: 'Primeira', count: 3 }, { id: 'b', label: 'Segunda' }, { id: 'c', label: 'Terceira' }]

  it('marca a aba selecionada e chama onSelect quando clico em outra', async () => {
    const onSelect = vi.fn()
    render(<Tabs tabs={tabs} selected="a" onSelect={onSelect} label="Seções" />)
    expect(screen.getByRole('tab', { name: /Primeira/ })).toHaveAttribute('aria-selected', 'true')
    await userEvent.click(screen.getByRole('tab', { name: 'Segunda' }))
    expect(onSelect).toHaveBeenCalledWith('b')
  })

  it('navega pelas setas, Home e End e dá a volta quando chega na ponta', async () => {
    const onSelect = vi.fn()
    render(<Tabs tabs={tabs} selected="a" onSelect={onSelect} label="Seções" />)
    screen.getByRole('tab', { name: /Primeira/ }).focus()
    await userEvent.keyboard('{ArrowLeft}{ArrowRight}{Home}{End}x')
    expect(onSelect.mock.calls.map((c) => c[0])).toEqual(['c', 'a', 'a', 'c'])
  })
})

describe('Estados', () => {
  it('mostra o erro e tenta de novo quando o botão é clicado', async () => {
    const onRetry = vi.fn()
    render(<ErrorState message="Sem conexão." onRetry={onRetry} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Sem conexão.')
    await userEvent.click(screen.getByRole('button', { name: 'Tentar de novo' }))
    expect(onRetry).toHaveBeenCalledOnce()
  })

  it('anuncia o carregamento e mostra o texto do vazio quando usados', () => {
    render(<><Skeleton label="Carregando exceções" /><EmptyState>Nada por aqui.</EmptyState></>)
    expect(screen.getByRole('status')).toHaveTextContent('Carregando exceções')
    expect(screen.getByText('Nada por aqui.')).toBeInTheDocument()
  })
})
