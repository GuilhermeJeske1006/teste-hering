import { describe, expect, it, vi } from 'vitest'
import { ApiError, createApiClient, toApiError, type FetchLike } from './client'
import { summary } from '../test/fixtures'

function fakeFetch(status: number, body: unknown): FetchLike & ReturnType<typeof vi.fn> {
  return vi.fn(async () => new Response(JSON.stringify(body), { status })) as never
}

describe('createApiClient', () => {
  it('busca o resumo em /api/summary quando chamado', async () => {
    const fetchImpl = fakeFetch(200, summary)
    const result = await createApiClient(fetchImpl).getSummary()
    expect(result.total_lines).toBe(248)
    expect(fetchImpl).toHaveBeenCalledWith('/api/summary', expect.objectContaining({ headers: expect.any(Object) }))
  })

  it('envia a decisão com motivo no corpo quando rejeita', async () => {
    const fetchImpl = fakeFetch(200, {})
    await createApiClient(fetchImpl).decide('abc', 'reject', 'Dado de entrada errado')
    const [url, init] = fetchImpl.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/api/exceptions/abc/decision')
    expect(init.method).toBe('POST')
    expect(JSON.parse(init.body as string)).toEqual({ action: 'reject', reason: 'Dado de entrada errado' })
  })

  it('omite campos opcionais quando não informados', async () => {
    const fetchImpl = fakeFetch(200, {})
    const client = createApiClient(fetchImpl)
    await client.decide('abc', 'approve')
    await client.interpretSignal('texto')
    await client.askCopilot('Oi?', [])
    const bodies = fetchImpl.mock.calls.map((c) => JSON.parse((c[1] as RequestInit).body as string))
    expect(bodies).toEqual([{ action: 'approve' }, { text: 'texto' }, { question: 'Oi?', history: [] }])
  })

  it('inclui loja e produto em foco quando informados', async () => {
    const fetchImpl = fakeFetch(200, {})
    const client = createApiClient(fetchImpl)
    await client.interpretSignal('texto', 'BRQ')
    await client.askCopilot('Oi?', [], 'CB-PT')
    const bodies = fetchImpl.mock.calls.map((c) => JSON.parse((c[1] as RequestInit).body as string))
    expect(bodies).toEqual([{ text: 'texto', store: 'BRQ' }, { question: 'Oi?', history: [], focus_sku: 'CB-PT' }])
  })

  it('monta as URLs com query string quando o endpoint tem filtro', async () => {
    const fetchImpl = fakeFetch(200, [])
    const client = createApiClient(fetchImpl, 'http://x')
    await client.getPlan('CB PT')
    await client.getExceptions('open')
    await client.getExceptions()
    await client.getAuditLog()
    await Promise.all([client.health(), client.getSkus(), client.getStores(), client.getTransfers(),
      client.getSignals(), client.getPolicies()])
    expect(fetchImpl.mock.calls.map((c) => c[0])).toEqual([
      'http://x/api/plan?sku=CB%20PT', 'http://x/api/exceptions?status=open', 'http://x/api/exceptions',
      'http://x/api/audit-log?limit=50', 'http://x/api/health', 'http://x/api/skus', 'http://x/api/stores',
      'http://x/api/transfers', 'http://x/api/signals', 'http://x/api/policies',
    ])
  })

  it('lança ApiError com código e mensagem do backend quando a resposta é erro', async () => {
    const fetchImpl = fakeFetch(409, { error: { code: 'already_decided', message: 'Já decidida.' } })
    await expect(createApiClient(fetchImpl).decide('abc', 'approve')).rejects.toMatchObject({
      code: 'already_decided', message: 'Já decidida.', status: 409,
    })
  })

  it('lança ApiError genérico quando o erro não tem corpo JSON', async () => {
    const fetchImpl = vi.fn(async () => new Response('falhou', { status: 500 }))
    await expect(createApiClient(fetchImpl).getSummary()).rejects.toMatchObject({ code: 'http_error', status: 500 })
  })

  it('lança erro de rede em pt-BR quando o fetch falha', async () => {
    const fetchImpl = vi.fn(async () => { throw new TypeError('Failed to fetch') })
    await expect(createApiClient(fetchImpl).getSummary()).rejects.toMatchObject({ code: 'network_error' })
  })
})

describe('toApiError', () => {
  it('mantém ApiError e converte o resto em erro genérico quando recebe qualquer erro', () => {
    const original = new ApiError('x', 'msg', 400)
    expect(toApiError(original)).toBe(original)
    expect(toApiError(new Error('boom')).code).toBe('unexpected_error')
  })
})
