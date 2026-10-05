import { severityMeta } from '../labels'
import styles from './SeverityBadge.module.css'

// Severidade por cor E por texto, nunca só pela cor.
export function SeverityBadge({ severity }: { severity: string }) {
  const meta = severityMeta(severity)
  return (
    <span className={styles.badge} data-severity={severity}>
      <span aria-hidden="true" className={styles.dot} />
      {meta.label}
    </span>
  )
}
