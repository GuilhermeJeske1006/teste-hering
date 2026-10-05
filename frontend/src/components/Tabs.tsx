import type { KeyboardEvent } from 'react'
import styles from './Tabs.module.css'

export interface TabItem {
  id: string
  label: string
  count?: number
}

interface TabsProps {
  tabs: TabItem[]
  selected: string
  onSelect: (id: string) => void
  label: string
}

// Abas acessíveis: role=tab, aria-selected e navegação por setas.
export function Tabs({ tabs, selected, onSelect, label }: TabsProps) {
  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    const moves: Record<string, number> = { ArrowRight: index + 1, ArrowLeft: index - 1, Home: 0, End: tabs.length - 1 }
    if (!(event.key in moves)) return
    event.preventDefault()
    const next = tabs[(moves[event.key] + tabs.length) % tabs.length]
    onSelect(next.id)
    document.getElementById(`tab-${next.id}`)?.focus()
  }

  return (
    <div className={styles.scroller}>
      <div role="tablist" aria-label={label} className={styles.list}>
        {tabs.map((tab, index) => (
          <button
            key={tab.id}
            id={`tab-${tab.id}`}
            type="button"
            role="tab"
            data-testid={`tab-${tab.id}`}
            aria-selected={tab.id === selected}
            aria-controls={`panel-${tab.id}`}
            tabIndex={tab.id === selected ? 0 : -1}
            className={styles.tab}
            onClick={() => onSelect(tab.id)}
            onKeyDown={(event) => onKeyDown(event, index)}
          >
            {tab.label}
            {tab.count !== undefined && <span className={styles.count}>{tab.count}</span>}
          </button>
        ))}
      </div>
    </div>
  )
}
