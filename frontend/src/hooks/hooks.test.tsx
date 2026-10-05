import { act, renderHook, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { ApiError } from '../api/client'
import { useApi } from '../api/context'
import { makeFakeClient } from '../test/fakeClient'
import * as fx from '../test/fixtures'
import { renderHookWithApi } from '../test/render'
import {
  useAuditLog, useExceptions, usePlan, usePolicies, useSignals, useSkus, useSummary,
} from './resources'
import { useCopilot } from './useCopilot'
import { useDecide } from './useDecide'
import { useSignalInterpreter } from './useSignalInterpreter'

describe('hooks de recurso', () => {
  it('expõe loading e depois data quando o client responde', async () => {
    const { result } = renderHookWithApi(() => useSummary(), makeFakeClient())
    expect(result.current.loading).toBe(true)
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data?.total_lines).toBe(248)
    expect(result.current.error).toBeNull()
  })

  it('expõe o erro em pt-BR quando o client falha', async () => {
    const client = makeFakeClient({ getExceptions: async () => { throw new ApiError('x', 'Falhou feio.', 500) } })
    const { result } = renderHookWithApi(() => useExceptions(), client)
    await waitFor(() => expect(result.current.error?.message).toBe('Falhou feio.'))
  })

  it('busca de novo quando reload é chamado', async () => {
    const client = makeFakeClient()
    const { result } = renderHookWithApi(() => useAuditLog(), client)
    await waitFor(() => expect(result.current.loading).toBe(false))
    act(() => result.current.reload())
    await waitFor(() => expect(client.getAuditLog).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(result.current.loading).toBe(false))
  })

  it('pede o plano do produto e não pede nada quando não há produto', async () => {
    const client = makeFakeClient()
    const { result, rerender } = renderHookWithApi(() => usePlan(null), client)
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).toBeNull()
    expect(client.getPlan).not.toHaveBeenCalled()
    rerender()
    const plan = renderHookWithApi(() => usePlan('CB-PT'), client)
    await waitFor(() => expect(plan.result.current.data?.sku).toBe('CB-PT'))
    expect(client.getPlan).toHaveBeenCalledWith('CB-PT')
  })

  it('carrega sinais, políticas e produtos quando montados', async () => {
    const client = makeFakeClient()
    const signals = renderHookWithApi(() => useSignals(), client)
    const policies = renderHookWithApi(() => usePolicies(), client)
    const skus = renderHookWithApi(() => useSkus(), client)
    await waitFor(() => expect(signals.result.current.data).toHaveLength(4))
    await waitFor(() => expect(policies.result.current.data?.length).toBeGreaterThan(20))
    await waitFor(() => expect(skus.result.current.data).toHaveLength(6))
  })

  it('falha com mensagem clara quando usado fora do ApiProvider', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {})
    expect(() => renderHook(() => useApi())).toThrow(/ApiProvider/)
  })
})

describe('useCopilot', () => {
  it('envia a pergunta com o histórico e guarda a resposta quando pergunta', async () => {
    const client = makeFakeClient()
    const { result } = renderHookWithApi(() => useCopilot(), client)
    await act(() => result.current.ask('Primeira?'))
    await act(() => result.current.ask('Segunda?', 'CB-PT'))
    expect(result.current.messages.map((m) => m.role)).toEqual(['user', 'assistant', 'user', 'assistant'])
    expect(client.askCopilot).toHaveBeenLastCalledWith('Segunda?', [
      { role: 'user', content: 'Primeira?' }, { role: 'assistant', content: fx.copilot.answer },
    ], 'CB-PT')
  })

  it('ignora pergunta vazia quando só há espaços', async () => {
    const client = makeFakeClient()
    const { result } = renderHookWithApi(() => useCopilot(), client)
    await act(() => result.current.ask('   '))
    expect(client.askCopilot).not.toHaveBeenCalled()
  })

  it('guarda o erro e a última pergunta quando o client falha', async () => {
    const client = makeFakeClient({ askCopilot: async () => { throw new ApiError('llm_unavailable', 'IA fora.', 503) } })
    const { result } = renderHookWithApi(() => useCopilot(), client)
    await act(() => result.current.ask('Oi?'))
    expect(result.current.error?.message).toBe('IA fora.')
    expect(result.current.lastQuestion).toBe('Oi?')
    expect(result.current.pending).toBe(false)
  })
})

describe('useDecide', () => {
  it('chama o client e avisa quando a decisão dá certo', async () => {
    const client = makeFakeClient()
    const onDecided = vi.fn()
    const { result } = renderHookWithApi(() => useDecide(onDecided), client)
    let ok = false
    await act(async () => { ok = await result.current.decide('abc', 'reject', 'Dado de entrada errado') })
    expect(ok).toBe(true)
    expect(client.decide).toHaveBeenCalledWith('abc', 'reject', 'Dado de entrada errado')
    expect(onDecided).toHaveBeenCalledOnce()
  })

  it('guarda o erro por exceção quando a decisão falha', async () => {
    const client = makeFakeClient({ decide: async () => { throw new ApiError('already_decided', 'Já decidida.', 409) } })
    const { result } = renderHookWithApi(() => useDecide(vi.fn()), client)
    await act(async () => { await result.current.decide('abc', 'approve') })
    expect(result.current.errors.abc.message).toBe('Já decidida.')
    expect(result.current.busyId).toBeNull()
  })
})

describe('useSignalInterpreter', () => {
  it('guarda o resultado estruturado quando interpreta', async () => {
    const client = makeFakeClient()
    const { result } = renderHookWithApi(() => useSignalInterpreter(), client)
    await act(() => result.current.interpret('texto', 'BRQ'))
    expect(result.current.result?.type).toBe('local_event')
    expect(client.interpretSignal).toHaveBeenCalledWith('texto', 'BRQ')
  })

  it('limpa o resultado e mostra o erro quando falha', async () => {
    const client = makeFakeClient({ interpretSignal: async () => { throw new ApiError('unparseable', 'Não consegui interpretar.', 422) } })
    const { result } = renderHookWithApi(() => useSignalInterpreter(), client)
    await act(() => result.current.interpret('texto'))
    expect(result.current.result).toBeNull()
    expect(result.current.error?.code).toBe('unparseable')
  })
})
