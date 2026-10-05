import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { audit, interpretation, plan, policies, signals, skus, stores } from '../test/fixtures'
import { AuditLog, PolicyList } from './Lists'
import { PlanTable } from './PlanTable'
import { SignalCard, SignalTester } from './Signals'
import { SkuPicker } from './SkuPicker'

describe('PlanTable', () => {
  it('mostra envio para loja própria e sugestão de pedido para franquia quando renderiza o plano', () => {
    render(<PlanTable plan={plan} />)
    expect(screen.getAllByTestId('plan-row')).toHaveLength(8)
    const joi = screen.getAllByTestId('plan-row').find((r) => r.dataset.store === 'JOI')!
    const brq = screen.getAllByTestId('plan-row').find((r) => r.dataset.store === 'BRQ')!
    expect(joi).toHaveTextContent('envio')
    expect(brq).toHaveTextContent('sugestão de pedido')
  })

  it('mostra o movimento com sinal e a saída da transferência quando há transferência', () => {
    render(<PlanTable plan={plan} />)
    const brq = screen.getAllByTestId('plan-row').find((r) => r.dataset.store === 'BRQ')!
    expect(within(brq).getAllByText('-22').length).toBeGreaterThan(0)
    const joi = screen.getAllByTestId('plan-row').find((r) => r.dataset.store === 'JOI')!
    expect(within(joi).getByTitle(/Transferência de entrada 13/)).toBeInTheDocument()
    expect(within(brq).getAllByTitle(/Sugestão de pedido/)).toHaveLength(5)
  })

  it('marca a célula bloqueada e o tamanho ausente quando o dado é inconsistente', () => {
    const custom = { ...plan, rows: [{ ...plan.rows[0], cells: [{ ...plan.rows[0].cells[0], status: 'blocked' }] }] }
    render(<PlanTable plan={custom} />)
    expect(screen.getByText('Bloqueada')).toBeInTheDocument()
    expect(screen.getAllByText('—').length).toBeGreaterThan(0)
  })
})

describe('SkuPicker', () => {
  it('marca o produto escolhido e avisa a troca quando clico em outro', async () => {
    const onSelect = vi.fn()
    render(<SkuPicker skus={skus} selected="CB-PT" onSelect={onSelect} />)
    expect(screen.getByRole('button', { name: /CB-PT/ })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('Lançamento')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /VM-FL/ }))
    expect(onSelect).toHaveBeenCalledWith('VM-FL')
  })
})

describe('Sinais', () => {
  it('mostra mensagem, tipo e ajuste quando renderiza um sinal', () => {
    render(<SignalCard signal={signals[0]} />)
    expect(screen.getByText(/Oktoberfest começou/)).toBeInTheDocument()
    expect(screen.getByText('Evento local')).toBeInTheDocument()
    expect(screen.getByText('+40% em tudo')).toBeInTheDocument()
  })

  it('envia o texto e a loja quando interpreto uma mensagem', async () => {
    const onInterpret = vi.fn()
    render(<SignalTester stores={stores} result={null} pending={false} error={null} onInterpret={onInterpret} />)
    const button = screen.getByRole('button', { name: 'Interpretar mensagem' })
    expect(button).toBeDisabled()
    await userEvent.type(screen.getByLabelText('Mensagem da loja'), 'Vai ter Fenarreco')
    await userEvent.selectOptions(screen.getByLabelText('Loja (opcional)'), 'BRQ')
    await userEvent.click(button)
    expect(onInterpret).toHaveBeenCalledWith('Vai ter Fenarreco', 'BRQ')
  })

  it('mostra o resultado em JSON com o campo type quando há interpretação', () => {
    render(<SignalTester stores={stores} result={interpretation} pending={false} error={null} onInterpret={vi.fn()} />)
    const result = screen.getByTestId('signal-result')
    expect(result).toHaveTextContent('"type": "local_event"')
    expect(result).toHaveTextContent('Sim')
  })

  it('mostra o erro e o estado de envio quando o agente falha', () => {
    render(<SignalTester stores={stores} result={null} pending error="Não consegui interpretar." onInterpret={vi.fn()} />)
    expect(screen.getByRole('alert')).toHaveTextContent('Não consegui interpretar.')
    expect(screen.getByRole('button', { name: 'Interpretando…' })).toBeDisabled()
  })
})

describe('Listas', () => {
  it('mostra rótulo e valor formatado quando lista as políticas', () => {
    render(<PolicyList policies={policies} />)
    expect(screen.getAllByTestId('policy-row')).toHaveLength(policies.length)
    expect(screen.getByText('Ajuste automático máximo por sinal')).toBeInTheDocument()
    expect(screen.getByText('20%')).toBeInTheDocument()
  })

  it('mostra ação, assunto e motivo quando lista o registro', () => {
    render(<AuditLog events={audit} />)
    const items = screen.getAllByTestId('audit-item')
    expect(items[0]).toHaveTextContent('Rejeitou')
    expect(items[0]).toHaveTextContent('Dado de entrada errado')
  })

  it('explica o que apareceria quando as listas estão vazias', () => {
    render(<><PolicyList policies={[]} /><AuditLog events={[]} /></>)
    expect(screen.getByText(/Nenhuma política/)).toBeInTheDocument()
    expect(screen.getByText(/Nenhum registro ainda/)).toBeInTheDocument()
  })
})
