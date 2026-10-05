import { useId, useState } from 'react'
import type { AllocationException, DecisionAction } from '../api/types'
import { formatDateTime } from '../format'
import { REJECTION_REASONS, SEVERITY_META, STATUS_LABELS, label, ruleLabel } from '../labels'
import styles from './ExceptionCard.module.css'
import { SeverityBadge } from './SeverityBadge'

interface ExceptionCardProps {
  exception: AllocationException
  busy?: boolean
  error?: string | null
  onDecide: (action: DecisionAction, reason?: string) => void
  onAsk?: () => void
}

// Card de exceção: renderiza qualquer regra sem switch (rótulos e severidade vêm de mapas).
export function ExceptionCard({ exception, busy = false, error, onDecide, onAsk }: ExceptionCardProps) {
  const [rejecting, setRejecting] = useState(false)
  const [reason, setReason] = useState('')
  const ids = useId()
  const isOpen = exception.status === 'open'
  const severity = exception.severity in SEVERITY_META ? exception.severity : 'low'
  const decision = exception.decision

  function confirmReject() {
    onDecide('reject', reason)
    setRejecting(false)
    setReason('')
  }

  return (
    <article
      className={styles.card}
      data-testid="exception-card"
      data-rule={exception.rule}
      data-severity={exception.severity}
      data-status={exception.status}
      data-sev={severity}
      aria-labelledby={`${ids}-title`}
      aria-busy={busy}
    >
      <div className={styles.meta}>
        <SeverityBadge severity={exception.severity} />
        <span className={styles.rule}>{ruleLabel(exception.rule)}</span>
        {!isOpen && <span className={styles.status}>{label(STATUS_LABELS, exception.status)}</span>}
      </div>
      <h3 id={`${ids}-title`} className={styles.title}>{exception.title}</h3>
      <p className={styles.recommendation}>{exception.recommendation}</p>
      <p className={styles.explanation}>{exception.explanation}</p>
      {exception.facts.length > 0 && (
        <ul className={styles.facts} aria-label="Fatos">
          {exception.facts.map((fact) => <li key={fact}>{fact}</li>)}
        </ul>
      )}
      {decision && (
        <p className={styles.decision} data-testid="decision-status" role="status">
          {decision.action === 'reject' ? `Rejeitada: ${decision.reason ?? 'sem motivo'}` : 'Aprovada'}
          <span className={styles.when}> · {decision.actor} · {formatDateTime(decision.decided_at)}</span>
        </p>
      )}
      {error && <p className={styles.error} role="alert">{error}</p>}
      {isOpen && rejecting ? (
        <div className={styles.rejectForm}>
          <label htmlFor={`${ids}-reason`} className={styles.reasonLabel}>Motivo da rejeição</label>
          <select
            id={`${ids}-reason`}
            data-testid="select-reject-reason"
            className={styles.select}
            value={reason}
            onChange={(event) => setReason(event.target.value)}
          >
            <option value="" disabled>Escolha um motivo</option>
            {REJECTION_REASONS.map((r) => <option key={r} value={r}>{r}</option>)}
          </select>
          <div className={styles.actions}>
            <button type="button" className={styles.danger} data-testid="btn-confirm-reject"
              disabled={!reason || busy} onClick={confirmReject}>
              Confirmar rejeição
            </button>
            <button type="button" className={styles.secondary} onClick={() => setRejecting(false)}>Cancelar</button>
          </div>
        </div>
      ) : (
        <div className={styles.actions}>
          {isOpen ? (
            <>
              <button type="button" className={styles.primary} data-testid="btn-approve" disabled={busy}
                onClick={() => onDecide('approve')}>
                Aprovar
              </button>
              <button type="button" className={styles.secondary} data-testid="btn-reject" disabled={busy}
                onClick={() => setRejecting(true)}>
                Rejeitar
              </button>
            </>
          ) : (
            <button type="button" className={styles.secondary} data-testid="btn-undo" disabled={busy}
              onClick={() => onDecide('undo')}>
              Desfazer
            </button>
          )}
          {onAsk && (
            <button type="button" className={styles.ghost} data-testid="btn-ask-copilot" onClick={onAsk}>
              Perguntar ao copiloto
            </button>
          )}
        </div>
      )}
    </article>
  )
}
