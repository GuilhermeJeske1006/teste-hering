import type { AuditEvent, Policy } from '../api/types'
import { formatDateTime, formatPolicyValue } from '../format'
import { AUDIT_ACTION_LABELS, label } from '../labels'
import styles from './Lists.module.css'
import { EmptyState } from './States'

// Políticas definidas pelo planejador (somente leitura no MVP).
export function PolicyList({ policies }: { policies: Policy[] }) {
  if (policies.length === 0) return <EmptyState>Nenhuma política cadastrada. Os limites do motor aparecem aqui.</EmptyState>
  return (
    <ul className={styles.list} aria-label="Políticas">
      {policies.map((p) => (
        <li key={p.key} className={styles.row} data-testid="policy-row">
          <div className={styles.text}>
            <strong>{p.label}</strong>
            <span className={styles.muted}>{p.description}</span>
          </div>
          <span className={styles.value}>{formatPolicyValue(p.value, p.unit)}</span>
        </li>
      ))}
    </ul>
  )
}

// Registro de auditoria append-only, do mais novo para o mais antigo.
export function AuditLog({ events }: { events: AuditEvent[] }) {
  if (events.length === 0) return <EmptyState>Nenhum registro ainda. Cada aprovação, rejeição e desfazer aparece aqui.</EmptyState>
  return (
    <ol className={styles.list} aria-label="Registro de auditoria">
      {events.map((e, i) => (
        <li key={`${e.timestamp}-${i}`} className={styles.row} data-testid="audit-item">
          <div className={styles.text}>
            <strong>{label(AUDIT_ACTION_LABELS, e.action)}: {e.subject}</strong>
            {e.detail && <span className={styles.muted}>{e.detail}</span>}
          </div>
          <span className={styles.meta}>
            {e.actor} · <time dateTime={e.timestamp}>{formatDateTime(e.timestamp)}</time>
          </span>
        </li>
      ))}
    </ol>
  )
}
