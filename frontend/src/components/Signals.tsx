import { useId, useState, type FormEvent } from 'react'
import type { Signal, SignalInterpretation, Store } from '../api/types'
import { formatDateTime, formatPercent } from '../format'
import { AUTHOR_ROLE_LABELS, SIGNAL_TYPE_LABELS, label } from '../labels'
import styles from './Signals.module.css'

const scopeLabel = (scope: string) => (scope === 'all' ? 'tudo' : scope.replace(':', ' '))
const adjustmentText = (a: { scope: string; pct: number }) => `${a.pct > 0 ? '+' : ''}${a.pct}% em ${scopeLabel(a.scope)}`

// Sinal recebido de uma loja, já estruturado.
export function SignalCard({ signal }: { signal: Signal }) {
  const it = signal.interpreted
  return (
    <article className={styles.card} data-testid="signal-card">
      <header className={styles.head}>
        <strong>{signal.store}</strong>
        <span>{label(AUTHOR_ROLE_LABELS, signal.author_role)}</span>
        <time dateTime={signal.received_at}>{formatDateTime(signal.received_at)}</time>
      </header>
      <blockquote className={styles.quote}>{signal.text}</blockquote>
      <ul className={styles.tags} aria-label="Interpretação">
        <li>{label(SIGNAL_TYPE_LABELS, it.type)}</li>
        {it.event && <li>{it.event}</li>}
        {it.adjustments.map((a) => <li key={a.scope}>{adjustmentText(a)}</li>)}
        <li>Confiança {formatPercent(it.confidence)}</li>
      </ul>
    </article>
  )
}

interface SignalTesterProps {
  stores: Store[]
  result: SignalInterpretation | null
  pending: boolean
  error: string | null
  onInterpret: (text: string, store: string | null) => void
}

// Formulário para testar o agente de sinais com uma mensagem nova.
export function SignalTester({ stores, result, pending, error, onInterpret }: SignalTesterProps) {
  const [text, setText] = useState('')
  const [store, setStore] = useState('')
  const ids = useId()

  function submit(event: FormEvent) {
    event.preventDefault()
    if (text.trim()) onInterpret(text.trim(), store || null)
  }

  return (
    <section className={styles.tester} aria-labelledby={`${ids}-title`}>
      <h3 id={`${ids}-title`} className={styles.title}>Testar o agente de sinais</h3>
      <p className={styles.note}>A mensagem é tratada como dado: ela nunca muda política nem decide exceção.</p>
      <form onSubmit={submit} className={styles.form}>
        <label htmlFor={`${ids}-text`}>Mensagem da loja</label>
        <textarea id={`${ids}-text`} data-testid="signal-input" rows={3} maxLength={2000} value={text}
          placeholder="Ex.: Vai ter a Fenarreco dia 16, manda mais camiseta."
          onChange={(event) => setText(event.target.value)} />
        <label htmlFor={`${ids}-store`}>Loja (opcional)</label>
        <select id={`${ids}-store`} value={store} onChange={(event) => setStore(event.target.value)}>
          <option value="">Identificar pela mensagem</option>
          {stores.map((s) => <option key={s.id} value={s.id}>{s.id} · {s.name}</option>)}
        </select>
        <button type="submit" data-testid="btn-interpret" disabled={pending || !text.trim()}>
          {pending ? 'Interpretando…' : 'Interpretar mensagem'}
        </button>
      </form>
      {error && <p className={styles.error} role="alert">{error}</p>}
      {result && (
        <div className={styles.result} data-testid="signal-result" role="status">
          <dl className={styles.fields}>
            <dt>Tipo</dt><dd>{label(SIGNAL_TYPE_LABELS, result.type)}</dd>
            <dt>Loja</dt><dd>{result.store ?? 'não identificada'}</dd>
            <dt>Ajustes</dt><dd>{result.adjustments.map(adjustmentText).join(', ') || 'nenhum'}</dd>
            <dt>Precisa de decisão humana</dt><dd>{result.requires_human ? 'Sim' : 'Não'}</dd>
          </dl>
          <pre className={styles.json}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </section>
  )
}
