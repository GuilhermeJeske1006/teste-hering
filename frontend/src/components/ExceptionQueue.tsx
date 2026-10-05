import type { AllocationException, DecisionAction } from '../api/types'
import styles from './ExceptionQueue.module.css'
import { ExceptionCard } from './ExceptionCard'
import { EmptyState } from './States'

interface ExceptionQueueProps {
  exceptions: AllocationException[]
  busyId?: string | null
  errors?: Record<string, { message: string }>
  onDecide: (id: string, action: DecisionAction, reason?: string) => void
  onAsk?: (exception: AllocationException) => void
}

// Fila de exceções na ordem de severidade que vem da API.
export function ExceptionQueue({ exceptions, busyId, errors = {}, onDecide, onAsk }: ExceptionQueueProps) {
  if (exceptions.length === 0) {
    return <EmptyState>Nenhuma exceção nesta semana. Tudo o que o motor recomendou está dentro da política.</EmptyState>
  }
  const open = exceptions.filter((e) => e.status === 'open').length
  return (
    <section aria-labelledby="queue-title">
      <div className={styles.header}>
        <h2 id="queue-title" className={styles.title}>Decisões da semana</h2>
        <p className={styles.counter}>{open} de {exceptions.length} esperando você</p>
      </div>
      <ul className={styles.list}>
        {exceptions.map((exc) => (
          <li key={exc.id}>
            <ExceptionCard
              exception={exc}
              busy={busyId === exc.id}
              error={errors[exc.id]?.message}
              onDecide={(action, reason) => onDecide(exc.id, action, reason)}
              onAsk={onAsk ? () => onAsk(exc) : undefined}
            />
          </li>
        ))}
      </ul>
    </section>
  )
}
