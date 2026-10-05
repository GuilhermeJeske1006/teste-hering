import type { Summary } from '../api/types'
import { formatInt, formatPercent } from '../format'
import styles from './KpiBar.module.css'

interface KpiBarProps {
  summary: Summary | null
}

// Faixa de KPIs da semana. O elemento com data-testid tem só o número.
export function KpiBar({ summary }: KpiBarProps) {
  const share = summary && summary.total_lines ? summary.within_policy / summary.total_lines : 0
  const items = [
    { id: 'kpi-total', label: 'Linhas de decisão', value: summary?.total_lines, hint: 'loja × produto × tamanho' },
    { id: 'kpi-within-policy', label: 'Dentro da política', value: summary?.within_policy,
      hint: summary ? `${formatPercent(share)} seguem sozinhas` : '' },
    { id: 'kpi-open-exceptions', label: 'Exceções abertas', value: summary?.open_exceptions, hint: 'precisam de você',
      highlight: true },
    { id: 'kpi-transfers', label: 'Transferências', value: summary?.transfers, hint: 'entre lojas' },
  ]
  return (
    <dl className={styles.bar} aria-busy={!summary}>
      {items.map((item) => (
        <div key={item.id} className={item.highlight ? `${styles.kpi} ${styles.highlight}` : styles.kpi}>
          <dt className={styles.label}>{item.label}</dt>
          <dd className={styles.value}>
            {item.value === undefined ? (
              <span className={styles.placeholder} aria-label="Carregando">—</span>
            ) : (
              <span data-testid={item.id}>{formatInt(item.value)}</span>
            )}
          </dd>
          <dd className={styles.hint}>{item.hint}</dd>
        </div>
      ))}
    </dl>
  )
}
