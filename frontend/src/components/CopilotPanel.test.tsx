import { act, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { useCopilot } from '../hooks/useCopilot'
import { makeFakeClient } from '../test/fakeClient'
import { copilot, exceptions } from '../test/fixtures'
import { renderWithApi } from '../test/render'
import { withNumberedSources } from '../format'
import { CopilotPanel } from './CopilotPanel'

function Connected() {
  const state = useCopilot()
  return (
    <CopilotPanel messages={state.messages} pending={state.pending} error={state.error?.message ?? null}
      suggestions={['Quais decisões dependem de mim?']} sourceTitles={{ [exceptions[0].id]: exceptions[0].title }}
      onAsk={(q) => void state.ask(q)} onRetry={() => state.lastQuestion && void state.ask(state.lastQuestion)} />
  )
}

describe('CopilotPanel', () => {
  it('envia a pergunta e mostra a resposta com as fontes quando o client responde', async () => {
    const client = makeFakeClient()
    renderWithApi(<Connected />, client)
    await userEvent.type(screen.getByLabelText('Pergunta para o copiloto'), 'O que depende de mim?')
    await userEvent.click(screen.getByRole('button', { name: 'Perguntar' }))
    const assistant = await screen.findByText(withNumberedSources(copilot.answer, copilot.sources))
    expect(assistant.closest('[data-role]')).toHaveAttribute('data-role', 'assistant')
    expect(screen.getAllByTestId('copilot-message').map((m) => m.dataset.role)).toEqual(['user', 'assistant'])
    expect(screen.getByRole('list', { name: 'Fontes' })).toHaveTextContent(exceptions[0].title)
    expect(client.askCopilot).toHaveBeenCalledWith('O que depende de mim?', [], undefined)
  })

  it('mostra o erro e tenta de novo quando o client falha', async () => {
    let fail = true
    const client = makeFakeClient({
      askCopilot: async () => {
        if (fail) throw new ApiError('llm_unavailable', 'O serviço de IA não respondeu agora.', 503)
        return copilot
      },
    })
    renderWithApi(<Connected />, client)
    await userEvent.click(screen.getByRole('button', { name: 'Quais decisões dependem de mim?' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('O serviço de IA não respondeu agora.')
    fail = false
    await userEvent.click(screen.getByRole('button', { name: 'Tentar de novo' }))
    await waitFor(() => expect(screen.getAllByTestId('copilot-message').at(-1)).toHaveAttribute('data-role', 'assistant'))
  })

  it('envia com Enter e quebra linha com Shift+Enter quando digito', async () => {
    const onAsk = vi.fn()
    render(<CopilotPanel messages={[]} pending={false} error={null} suggestions={[]} sourceTitles={{}} onAsk={onAsk} />)
    const input = screen.getByLabelText('Pergunta para o copiloto')
    await userEvent.type(input, 'linha 1{Shift>}{Enter}{/Shift}linha 2{Enter}')
    expect(onAsk).toHaveBeenCalledWith('linha 1\nlinha 2')
    expect(input).toHaveValue('')
  })

  it('bloqueia o envio e mostra que está pensando quando há pergunta pendente', () => {
    render(<CopilotPanel messages={[{ role: 'user', content: 'Oi?' }]} pending error={null}
      suggestions={['Sugestão']} sourceTitles={{}} focusLabel="CB-PT" onAsk={vi.fn()} />)
    expect(screen.getByRole('status')).toHaveTextContent('Pensando…')
    expect(screen.getByRole('button', { name: 'Sugestão' })).toBeDisabled()
    expect(screen.getByText('Em foco: CB-PT')).toBeInTheDocument()
    act(() => screen.getByLabelText('Pergunta para o copiloto').focus())
  })
})

describe('withNumberedSources', () => {
  it('troca ids citados por números na ordem das fontes quando há fontes', () => {
    expect(withNumberedSources('Veja [aaa] e depois [bbb]; de novo [aaa]. [zzz] fica.', ['aaa', 'bbb']))
      .toBe('Veja [1] e depois [2]; de novo [1]. [zzz] fica.')
  })

  it('mantém o texto quando não há fontes', () => {
    expect(withNumberedSources('Sem [ids] aqui.')).toBe('Sem [ids] aqui.')
  })
})
