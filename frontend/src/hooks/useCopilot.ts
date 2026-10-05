// Conversa com o copiloto: histórico local, pergunta em andamento e erro em pt-BR.
import { useCallback, useState } from 'react'
import { ApiError, toApiError } from '../api/client'
import { useApi } from '../api/context'
import type { ChatMessage } from '../api/types'

export interface CopilotMessage extends ChatMessage {
  sources?: string[]
}

export interface CopilotState {
  messages: CopilotMessage[]
  pending: boolean
  error: ApiError | null
  lastQuestion: string | null
  ask: (question: string, focusSku?: string | null) => Promise<void>
}

export function useCopilot(): CopilotState {
  const client = useApi()
  const [messages, setMessages] = useState<CopilotMessage[]>([])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)
  const [lastQuestion, setLastQuestion] = useState<string | null>(null)

  const ask = useCallback(
    async (question: string, focusSku?: string | null) => {
      const text = question.trim()
      if (!text) return
      const history: ChatMessage[] = messages.map(({ role, content }) => ({ role, content }))
      setMessages((prev) => [...prev, { role: 'user', content: text }])
      setPending(true)
      setError(null)
      setLastQuestion(text)
      try {
        const answer = await client.askCopilot(text, history, focusSku)
        setMessages((prev) => [...prev, { role: 'assistant', content: answer.answer, sources: answer.sources }])
      } catch (err) {
        setError(toApiError(err))
      } finally {
        setPending(false)
      }
    },
    [client, messages],
  )

  return { messages, pending, error, lastQuestion, ask }
}
