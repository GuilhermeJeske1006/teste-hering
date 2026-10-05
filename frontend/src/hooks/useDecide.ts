// Envia decisões e expõe qual exceção está em andamento e o erro por exceção.
import { useCallback, useState } from 'react'
import { ApiError, toApiError } from '../api/client'
import { useApi } from '../api/context'
import type { DecisionAction } from '../api/types'

export interface DecideState {
  busyId: string | null
  errors: Record<string, ApiError>
  decide: (id: string, action: DecisionAction, reason?: string) => Promise<boolean>
}

export function useDecide(onDecided: () => void): DecideState {
  const client = useApi()
  const [busyId, setBusyId] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, ApiError>>({})

  const decide = useCallback(
    async (id: string, action: DecisionAction, reason?: string) => {
      setBusyId(id)
      setErrors((prev) => Object.fromEntries(Object.entries(prev).filter(([key]) => key !== id)))
      try {
        await client.decide(id, action, reason)
        onDecided()
        return true
      } catch (err) {
        setErrors((prev) => ({ ...prev, [id]: toApiError(err) }))
        return false
      } finally {
        setBusyId(null)
      }
    },
    [client, onDecided],
  )

  return { busyId, errors, decide }
}
