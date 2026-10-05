import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { ApiError } from '../api/client'
import { makeFakeClient } from '../test/fakeClient'
import { exceptions, summary } from '../test/fixtures'
import { renderWithApi } from '../test/render'
import { AllocationDesk } from './AllocationDesk'

describe('AllocationDesk', () => {
  it('mostra título, semana, modo sombra, KPIs e a fila quando abre a mesa', async () => {
    renderWithApi(<AllocationDesk />, makeFakeClient())
    expect(screen.getByRole('heading', { level: 1, name: 'Mesa de Alocação' })).toBeInTheDocument()
    expect(screen.getByTestId('shadow-mode-tag')).toHaveTextContent('Modo sombra · nada é executado')
    expect(await screen.findByTestId('kpi-total')).toHaveTextContent('248')
    expect(screen.getByText('Semana 41/2026 · 05/10 a 11/10')).toBeInTheDocument()
    expect(await screen.findAllByTestId('exception-card')).toHaveLength(exceptions.length)
    expect(document.querySelector('[data-layout="main"]')).not.toBeNull()
    expect(screen.getByRole('tab', { name: /Exceções/ })).toHaveTextContent(String(summary.open_exceptions))
  })

  it('aprova e recarrega resumo, fila e registro quando clico em Aprovar', async () => {
    const client = makeFakeClient()
    renderWithApi(<AllocationDesk />, client)
    const [first] = await screen.findAllByRole('button', { name: 'Aprovar' })
    await userEvent.click(first)
    expect(client.decide).toHaveBeenCalledWith(exceptions[0].id, 'approve', undefined)
    await waitFor(() => expect(client.getSummary).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(client.getExceptions).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(client.getAuditLog).toHaveBeenCalledTimes(2))
  })

  it('mostra o erro no card quando a decisão falha', async () => {
    const client = makeFakeClient({ decide: async () => { throw new ApiError('already_decided', 'Esta exceção já foi decidida.', 409) } })
    renderWithApi(<AllocationDesk />, client)
    const [first] = await screen.findAllByRole('button', { name: 'Aprovar' })
    await userEvent.click(first)
    expect(await screen.findByText('Esta exceção já foi decidida.')).toBeInTheDocument()
  })

  it('abre o plano do primeiro produto e troca de produto quando uso a aba Plano', async () => {
    const client = makeFakeClient()
    renderWithApi(<AllocationDesk />, client)
    await userEvent.click(await screen.findByRole('tab', { name: 'Plano por loja' }))
    expect(screen.getByRole('tab', { name: 'Plano por loja' })).toHaveAttribute('aria-selected', 'true')
    expect(await screen.findByTestId('plan-table')).toBeInTheDocument()
    expect(client.getPlan).toHaveBeenCalledWith('CB-PT')
    expect(screen.getByText('Em foco: CB-PT')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /VM-FL/ }))
    await waitFor(() => expect(client.getPlan).toHaveBeenCalledWith('VM-FL'))
  })

  it('lista sinais e interpreta uma mensagem nova quando uso a aba Sinais', async () => {
    const client = makeFakeClient()
    renderWithApi(<AllocationDesk />, client)
    await userEvent.click(await screen.findByRole('tab', { name: /Sinais/ }))
    expect(await screen.findAllByTestId('signal-card')).toHaveLength(4)
    await userEvent.type(screen.getByTestId('signal-input'), 'Vai ter Fenarreco, manda mais camiseta')
    await userEvent.click(screen.getByTestId('btn-interpret'))
    expect(await screen.findByTestId('signal-result')).toHaveTextContent('"type"')
  })

  it('mostra políticas e registro quando abro as abas', async () => {
    renderWithApi(<AllocationDesk />, makeFakeClient())
    await userEvent.click(await screen.findByRole('tab', { name: 'Políticas' }))
    expect((await screen.findAllByTestId('policy-row')).length).toBeGreaterThan(20)
    await userEvent.click(screen.getByRole('tab', { name: 'Registro' }))
    expect((await screen.findAllByTestId('audit-item')).length).toBeGreaterThan(0)
  })

  it('pergunta ao copiloto sobre a exceção quando clico no botão do card', async () => {
    const client = makeFakeClient()
    renderWithApi(<AllocationDesk />, client)
    const [ask] = await screen.findAllByTestId('btn-ask-copilot')
    await userEvent.click(ask)
    expect(client.askCopilot).toHaveBeenCalledWith(expect.stringContaining(exceptions[0].id), [], null)
    const log = screen.getByRole('log')
    await waitFor(() => expect(within(log).getAllByTestId('copilot-message')).toHaveLength(2))
  })

  it('mostra erro com tentar de novo quando a API está fora', async () => {
    const down = async () => { throw new ApiError('network_error', 'Sem conexão com o servidor.', 0) }
    const client = makeFakeClient({ getSummary: down, getExceptions: down })
    renderWithApi(<AllocationDesk />, client)
    const alerts = await screen.findAllByRole('alert')
    expect(alerts[0]).toHaveTextContent('Sem conexão com o servidor.')
    expect(screen.getByText('Semana indisponível')).toBeInTheDocument()
    expect(screen.queryByText('Carregando a semana…')).not.toBeInTheDocument()
    await userEvent.click(within(alerts[0]).getByRole('button', { name: 'Tentar de novo' }))
    await waitFor(() => expect(client.getSummary).toHaveBeenCalledTimes(2))
  })

  it('explica a fila vazia e os sinais vazios quando não há dados', async () => {
    const client = makeFakeClient({ getExceptions: async () => [], getSignals: async () => [] })
    renderWithApi(<AllocationDesk />, client)
    expect(await screen.findByText(/Nenhuma exceção nesta semana/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('tab', { name: /Sinais/ }))
    expect(await screen.findByText(/Nenhum sinal recebido/)).toBeInTheDocument()
  })
})
