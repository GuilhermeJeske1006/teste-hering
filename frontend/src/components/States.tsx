import styles from './States.module.css'

// Estados de carregamento, erro e vazio, reutilizados por todas as abas.

export function Skeleton({ lines = 3, label = 'Carregando' }: { lines?: number; label?: string }) {
  return (
    <div className={styles.skeleton} role="status">
      <span className="visually-hidden">{label}…</span>
      {Array.from({ length: lines }, (_, i) => (
        <span key={i} aria-hidden="true" className={styles.line} />
      ))}
    </div>
  )
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className={styles.error} role="alert">
      <p>{message}</p>
      {onRetry && (
        <button type="button" className={styles.retry} onClick={onRetry}>
          Tentar de novo
        </button>
      )}
    </div>
  )
}

export function EmptyState({ children }: { children: string }) {
  return <p className={styles.empty}>{children}</p>
}
