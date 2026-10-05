import { useId, useState, type FormEvent, type KeyboardEvent } from 'react'
import type { CopilotMessage } from '../hooks/useCopilot'
import styles from './CopilotPanel.module.css'
import { ErrorState } from './States'

interface CopilotPanelProps {
  messages: CopilotMessage[]
  pending: boolean
  error: string | null
  suggestions: string[]
  sourceTitles: Record<string, string>
  focusLabel?: string | null
  onAsk: (question: string) => void
  onRetry?: () => void
}

// Copiloto: explica as decisões com base só nos dados da mesa. Nunca executa nada.
export function CopilotPanel(props: CopilotPanelProps) {
  const { messages, pending, error, suggestions, sourceTitles, focusLabel, onAsk, onRetry } = props
  const [question, setQuestion] = useState('')
  const ids = useId()

  function send() {
    const text = question.trim()
    if (!text || pending) return
    onAsk(text)
    setQuestion('')
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    send()
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      send()
    }
  }

  return (
    <aside id="copilot" className={styles.panel} aria-labelledby={`${ids}-title`}>
      <header className={styles.header}>
        <h2 id={`${ids}-title`} className={styles.title}>Copiloto</h2>
        <p className={styles.note}>Responde só com os dados da mesa e não executa nada.</p>
        {focusLabel && <p className={styles.focus}>Em foco: {focusLabel}</p>}
      </header>
      <div className={styles.log} role="log" aria-live="polite" aria-label="Conversa com o copiloto">
        {messages.length === 0 && (
          <p className={styles.empty}>Pergunte sobre as decisões da semana. A resposta cita as exceções usadas.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={styles.message} data-testid="copilot-message" data-role={m.role}>
            <span className="visually-hidden">{m.role === 'user' ? 'Você:' : 'Copiloto:'}</span>
            <p>{m.content}</p>
            {m.sources && m.sources.length > 0 && (
              <p className={styles.sources}>Fontes: {m.sources.map((id) => sourceTitles[id] ?? id).join(' · ')}</p>
            )}
          </div>
        ))}
        {pending && <p className={styles.pending} role="status">Pensando…</p>}
      </div>
      {error && <ErrorState message={error} onRetry={onRetry} />}
      <div className={styles.suggestions} aria-label="Sugestões de pergunta" role="group">
        {suggestions.map((s) => (
          <button key={s} type="button" className={styles.suggestion} data-testid="copilot-suggestion"
            disabled={pending} onClick={() => onAsk(s)}>
            {s}
          </button>
        ))}
      </div>
      <form className={styles.form} onSubmit={onSubmit}>
        <label htmlFor={`${ids}-input`} className="visually-hidden">Pergunta para o copiloto</label>
        <textarea id={`${ids}-input`} data-testid="copilot-input" rows={2} maxLength={1000} value={question}
          placeholder="Pergunte sobre as decisões da semana" onChange={(event) => setQuestion(event.target.value)}
          onKeyDown={onKeyDown} />
        <button type="submit" data-testid="btn-ask" className={styles.send} disabled={pending || !question.trim()}>
          Perguntar
        </button>
      </form>
    </aside>
  )
}
