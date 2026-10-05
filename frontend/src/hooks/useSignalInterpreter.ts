// Testa o agente de sinais: envia o texto e guarda o resultado estruturado.
import { useCallback, useState } from 'react'
import { ApiError, toApiError } from '../api/client'
import { useApi } from '../api/context'
import type { SignalInterpretation } from '../api/types'

export interface SignalInterpreterState {
  result: SignalInterpretation | null
  pending: boolean
  error: ApiError | null
  interpret: (text: string, store?: string | null) => Promise<void>
}

export function useSignalInterpreter(): SignalInterpreterState {
  const client = useApi()
  const [result, setResult] = useState<SignalInterpretation | null>(null)
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  const interpret = useCallback(
    async (text: string, store?: string | null) => {
      setPending(true)
      setError(null)
      try {
        setResult(await client.interpretSignal(text, store))
      } catch (err) {
        setResult(null)
        setError(toApiError(err))
      } finally {
        setPending(false)
      }
    },
    [client],
  )

  return { result, pending, error, interpret }
}
