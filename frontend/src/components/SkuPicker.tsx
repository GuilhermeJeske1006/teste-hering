import type { Sku } from '../api/types'
import styles from './SkuPicker.module.css'

interface SkuPickerProps {
  skus: Sku[]
  selected: string | null
  onSelect: (sku: string) => void
}

// Chips para escolher o produto do plano.
export function SkuPicker({ skus, selected, onSelect }: SkuPickerProps) {
  return (
    <div role="group" aria-label="Produto" className={styles.group}>
      {skus.map((sku) => (
        <button
          key={sku.id}
          type="button"
          className={styles.chip}
          data-testid="sku-chip"
          data-sku={sku.id}
          aria-pressed={sku.id === selected}
          onClick={() => onSelect(sku.id)}
        >
          <span className={styles.id}>{sku.id}</span>
          <span className={styles.name}>{sku.name}</span>
          {sku.is_launch && <span className={styles.tag}>Lançamento</span>}
        </button>
      ))}
    </div>
  )
}
