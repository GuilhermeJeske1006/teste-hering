import type { PlanCell, SkuPlan } from '../api/types'
import { formatDecimal, formatInt, formatSigned } from '../format'
import { EXECUTION_MODE_LABELS, label } from '../labels'
import styles from './PlanTable.module.css'

const movement = (c: PlanCell) => c.dc_allocated + c.transfer_in - c.transfer_out

function describe(c: PlanCell, mode: string): string {
  const supply = mode === 'ship' ? 'Envio do CD' : 'Sugestão de pedido'
  return [`Estoque ${formatInt(c.stock)}`, `Alvo ${formatInt(c.target)}`,
    `Previsão 2 semanas ${formatDecimal(c.forecast_horizon)}`, `${supply} ${formatInt(c.dc_allocated)}`,
    `Transferência de entrada ${formatInt(c.transfer_in)}`, `Transferência de saída ${formatInt(c.transfer_out)}`,
    `Excesso ${formatInt(c.excess)}`].join(' · ')
}

// Grade loja × tamanho de um produto, com o modo de execução de cada loja.
export function PlanTable({ plan }: { plan: SkuPlan }) {
  return (
    <div className={styles.scroller} role="region" aria-label={`Plano de ${plan.sku} por loja`} tabIndex={0}>
      <table className={styles.table} data-testid="plan-table">
        <caption className="visually-hidden">
          Plano de {plan.sku}: movimento por tamanho (envio ou sugestão de pedido mais transferências) e estoque
          comparado ao alvo.
        </caption>
        <thead>
          <tr>
            <th scope="col">Loja</th>
            <th scope="col">Execução</th>
            {plan.sizes.map((size) => <th scope="col" key={size} className={styles.num}>{size}</th>)}
            <th scope="col" className={styles.num}>Movimento</th>
          </tr>
        </thead>
        <tbody>
          {plan.rows.map((row) => (
            <tr key={row.store_id} data-testid="plan-row" data-store={row.store_id}>
              <th scope="row" className={styles.store}>
                {row.store_name}
                <span className={styles.storeId}>{row.store_id}</span>
              </th>
              <td>
                <span className={styles.mode} data-mode={row.execution_mode}>
                  {label(EXECUTION_MODE_LABELS, row.execution_mode)}
                </span>
              </td>
              {plan.sizes.map((size) => {
                const cell = row.cells.find((c) => c.size === size)
                if (!cell) return <td key={size} className={styles.num}>—</td>
                const blocked = cell.status === 'blocked'
                const move = movement(cell)
                return (
                  <td key={size} className={styles.num} title={describe(cell, row.execution_mode)}
                    data-blocked={blocked || undefined}>
                    <span className={styles.move} data-direction={move > 0 ? 'in' : move < 0 ? 'out' : 'none'}>
                      {blocked ? 'Bloqueada' : move === 0 ? '—' : formatSigned(move)}
                    </span>
                    <span className={styles.stock}>{formatInt(cell.stock)} → {formatInt(cell.target)}</span>
                  </td>
                )
              })}
              <td className={`${styles.num} ${styles.total}`}>{formatSigned(row.total_movement)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
