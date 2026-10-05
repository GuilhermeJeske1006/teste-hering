// Estado assíncrono genérico {data, error, loading, reload}. Mantém o dado anterior enquanto recarrega.
import { useCallback, useEffect, useState } from 'react'
import { ApiError, toApiError } from '../api/client'

export interface AsyncState<T> {
  data: T | null
  error: ApiError | null
  loading: boolean
  reload: () => void
}

interface Settled<T> {
  loader: (() => Promise<T>) | null
  nonce: number
  data: T | null
  error: ApiError | null
}

export function useAsync<T>(loader: () => Promise<T>): AsyncState<T> {
  const [nonce, setNonce] = useState(0)
  const [settled, setSettled] = useState<Settled<T>>({ loader: null, nonce: -1, data: null, error: null })

  useEffect(() => {
    let active = true
    loader().then(
      (data) => active && setSettled({ loader, nonce, data, error: null }),
      (error: unknown) => active && setSettled((prev) => ({ loader, nonce, data: prev.data, error: toApiError(error) })),
    )
    return () => {
      active = false
    }
  }, [loader, nonce])

  const reload = useCallback(() => setNonce((n) => n + 1), [])
  const done = settled.loader === loader && settled.nonce === nonce
  return { data: settled.data, error: done ? settled.error : null, loading: !done, reload }
}
