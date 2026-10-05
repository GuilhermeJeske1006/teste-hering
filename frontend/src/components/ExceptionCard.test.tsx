import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { exceptions } from '../test/fixtures'
import { ExceptionCard } from './ExceptionCard'
import { ExceptionQueue } from './ExceptionQueue'

const open = exceptions.find((e) => e.status === 'open')!
const rejected = exceptions.find((e) => e.status === 'rejected')!

describe('ExceptionCard', () => {
  it('mostra título, severidade em texto, recomendação e fatos quando aberta', () => {
    render(<ExceptionCard exception={open} onDecide={vi.fn()} />)
    const card = screen.getByTestId('exception-card')
    expect(card).toHaveAttribute('data-rule', open.rule)
    expect(card).toHaveAttribute('data-severity', open.severity)
    expect(card).toHaveAttribute('data-status', 'open')
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent(open.title)
    expect(screen.getByText('Crítica')).toBeInTheDocument()
    expect(within(screen.getByRole('list', { name: 'Fatos' })).getAllByRole('listitem')).toHaveLength(open.facts.length)
  })

  it('chama onDecide com approve quando clico em Aprovar', async () => {
    const onDecide = vi.fn()
    render(<ExceptionCard exception={open} onDecide={onDecide} />)
    await userEvent.click(screen.getByRole('button', { name: 'Aprovar' }))
    expect(onDecide).toHaveBeenCalledWith('approve')
  })

  it('abre o select e envia o motivo quando confirmo a rejeição', async () => {
    const onDecide = vi.fn()
    render(<ExceptionCard exception={open} onDecide={onDecide} />)
    await userEvent.click(screen.getByRole('button', { name: 'Rejeitar' }))
    const confirm = screen.getByRole('button', { name: 'Confirmar rejeição' })
    expect(confirm).toBeDisabled()
    await userEvent.selectOptions(screen.getByLabelText('Motivo da rejeição'), 'Restrição comercial com o franqueado')
    await userEvent.click(confirm)
    expect(onDecide).toHaveBeenCalledWith('reject', 'Restrição comercial com o franqueado')
    expect(screen.queryByLabelText('Motivo da rejeição')).not.toBeInTheDocument()
  })

  it('fecha o formulário sem decidir quando cancelo', async () => {
    const onDecide = vi.fn()
    render(<ExceptionCard exception={open} onDecide={onDecide} />)
    await userEvent.click(screen.getByRole('button', { name: 'Rejeitar' }))
    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(screen.getByRole('button', { name: 'Aprovar' })).toBeInTheDocument()
    expect(onDecide).not.toHaveBeenCalled()
  })

  it('mostra o motivo e oferece desfazer quando já foi rejeitada', async () => {
    const onDecide = vi.fn()
    render(<ExceptionCard exception={rejected} onDecide={onDecide} />)
    expect(screen.getByTestId('decision-status')).toHaveTextContent('Rejeitada: Dado de entrada errado')
    expect(screen.queryByRole('button', { name: 'Aprovar' })).not.toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Desfazer' }))
    expect(onDecide).toHaveBeenCalledWith('undo')
  })

  it('mostra aprovada quando a decisão é de aprovação', () => {
    const approved = { ...open, status: 'approved', decision: { ...rejected.decision!, action: 'approve', reason: null } }
    render(<ExceptionCard exception={approved} onDecide={vi.fn()} />)
    expect(screen.getByTestId('decision-status')).toHaveTextContent(/^Aprovada/)
  })

  it('pergunta ao copiloto e mostra erro quando recebe as props', async () => {
    const onAsk = vi.fn()
    render(<ExceptionCard exception={open} onDecide={vi.fn()} onAsk={onAsk} error="Já decidida." busy />)
    expect(screen.getByRole('alert')).toHaveTextContent('Já decidida.')
    expect(screen.getByRole('button', { name: 'Aprovar' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: 'Perguntar ao copiloto' }))
    expect(onAsk).toHaveBeenCalledOnce()
  })

  it('renderiza regra desconhecida sem quebrar quando surge uma regra nova', () => {
    render(<ExceptionCard exception={{ ...open, rule: 'nova_regra', severity: 'weird', facts: [] }} onDecide={vi.fn()} />)
    expect(screen.getByText('nova_regra')).toBeInTheDocument()
    expect(screen.getByTestId('exception-card')).toHaveAttribute('data-sev', 'low')
  })
})

describe('ExceptionQueue', () => {
  it('lista todos os cards e conta as abertas quando há exceções', async () => {
    const onDecide = vi.fn()
    const onAsk = vi.fn()
    render(<ExceptionQueue exceptions={exceptions} onDecide={onDecide} onAsk={onAsk} />)
    expect(screen.getAllByTestId('exception-card')).toHaveLength(exceptions.length)
    expect(screen.getByText(`6 de ${exceptions.length} esperando você`)).toBeInTheDocument()
    await userEvent.click(screen.getAllByRole('button', { name: 'Aprovar' })[0])
    expect(onDecide).toHaveBeenCalledWith(exceptions[0].id, 'approve', undefined)
    await userEvent.click(screen.getAllByRole('button', { name: 'Perguntar ao copiloto' })[0])
    expect(onAsk).toHaveBeenCalledWith(exceptions[0])
  })

  it('explica o que apareceria quando a fila está vazia', () => {
    render(<ExceptionQueue exceptions={[]} onDecide={vi.fn()} />)
    expect(screen.getByText(/Nenhuma exceção nesta semana/)).toBeInTheDocument()
  })
})
