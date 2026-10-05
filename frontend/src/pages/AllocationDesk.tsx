import { useCallback, useMemo, useState } from 'react'
import type { AllocationException } from '../api/types'
import { AuditLog, PolicyList } from '../components/Lists'
import { CopilotPanel } from '../components/CopilotPanel'
import { ExceptionQueue } from '../components/ExceptionQueue'
import { KpiBar } from '../components/KpiBar'
import { PlanTable } from '../components/PlanTable'
import { SignalCard, SignalTester } from '../components/Signals'
import { SkuPicker } from '../components/SkuPicker'
import { EmptyState, ErrorState, Skeleton } from '../components/States'
import { Tabs, type TabItem } from '../components/Tabs'
import { formatDayMonth } from '../format'
import {
  useAuditLog, useExceptions, usePlan, usePolicies, useSignals, useSkus, useStores, useSummary,
} from '../hooks/resources'
import { useCopilot } from '../hooks/useCopilot'
import { useDecide } from '../hooks/useDecide'
import { useSignalInterpreter } from '../hooks/useSignalInterpreter'
import type { AsyncState } from '../hooks/useAsync'
import styles from './AllocationDesk.module.css'

type TabId = 'exceptions' | 'plan' | 'signals' | 'policies' | 'audit'

const SUGGESTIONS = [
  'Quais decisões desta semana dependem de mim?',
  'Por que transferir camiseta de Brusque?',
  'O que fazer com o moletom em queda?',
]

function Loadable<T>({ state, label, children }: { state: AsyncState<T>; label: string; children: (data: T) => JSX.Element }) {
  if (state.error) return <ErrorState message={state.error.message} onRetry={state.reload} />
  if (state.data === null) return <Skeleton label={label} />
  return children(state.data)
}

// Página única da mesa: KPIs, abas de trabalho e o copiloto ao lado.
export function AllocationDesk() {
  const [tab, setTab] = useState<TabId>('exceptions')
  const [chosenSku, setChosenSku] = useState<string | null>(null)
  const summary = useSummary()
  const exceptions = useExceptions()
  const audit = useAuditLog()
  const skus = useSkus()
  const stores = useStores()
  const signals = useSignals()
  const policies = usePolicies()
  const sku = chosenSku ?? skus.data?.[0]?.id ?? null
  const plan = usePlan(sku)
  const copilot = useCopilot()
  const interpreter = useSignalInterpreter()

  const { reload: reloadSummary } = summary
  const { reload: reloadExceptions } = exceptions
  const { reload: reloadAudit } = audit
  const refresh = useCallback(() => {
    reloadSummary()
    reloadExceptions()
    reloadAudit()
  }, [reloadSummary, reloadExceptions, reloadAudit])
  const decisions = useDecide(refresh)

  const focusSku = tab === 'plan' ? sku : null
  const sourceTitles = useMemo(
    () => Object.fromEntries((exceptions.data ?? []).map((e) => [e.id, e.title])), [exceptions.data])

  function askAbout(exception: AllocationException) {
    void copilot.ask(`Explique a exceção [${exception.id}] ${exception.title}. O que você recomenda?`, focusSku)
    document.getElementById('copilot')?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  }

  const open = summary.data?.open_exceptions
  const tabs: TabItem[] = [
    { id: 'exceptions', label: 'Exceções', count: open },
    { id: 'plan', label: 'Plano por loja' },
    { id: 'signals', label: 'Sinais', count: signals.data?.length },
    { id: 'policies', label: 'Políticas' },
    { id: 'audit', label: 'Registro' },
  ]
  const week = summary.data?.week

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <div className={styles.heading}>
          <h1 className={styles.title}>Mesa de Alocação</h1>
          <p className={styles.week}>
            {week
              ? `Semana ${week.iso_week}/${week.year} · ${formatDayMonth(week.start)} a ${formatDayMonth(week.end)}`
              : 'Carregando a semana…'}
          </p>
        </div>
        <p className={styles.shadow} data-testid="shadow-mode-tag">
          <span aria-hidden="true" className={styles.shadowDot} />
          Modo sombra · nada é executado
        </p>
      </header>
      {summary.error ? <ErrorState message={summary.error.message} onRetry={summary.reload} />
        : <KpiBar summary={summary.data} />}

      <div className={styles.layout} data-layout="main">
        <main className={styles.content}>
          <Tabs tabs={tabs} selected={tab} onSelect={(id) => setTab(id as TabId)} label="Áreas da mesa" />
          <section id={`panel-${tab}`} role="tabpanel" aria-labelledby={`tab-${tab}`} className={styles.panel}
            tabIndex={-1}>
            {tab === 'exceptions' && (
              <Loadable state={exceptions} label="Carregando exceções">
                {(items) => (
                  <ExceptionQueue exceptions={items} busyId={decisions.busyId} errors={decisions.errors}
                    onDecide={(id, action, reason) => void decisions.decide(id, action, reason)} onAsk={askAbout} />
                )}
              </Loadable>
            )}
            {tab === 'plan' && (
              <>
                <h2 className={styles.sectionTitle}>Plano por loja</h2>
                <Loadable state={skus} label="Carregando produtos">
                  {(items) => <SkuPicker skus={items} selected={sku} onSelect={setChosenSku} />}
                </Loadable>
                <Loadable state={plan} label="Carregando plano">
                  {(data) => (data && data.sku === sku ? <PlanTable plan={data} /> : <Skeleton label="Carregando plano" />)}
                </Loadable>
                <p className={styles.legend}>
                  Em cada tamanho: movimento da semana (envio do CD ou sugestão de pedido, mais transferências) e
                  estoque → alvo. Passe o mouse para ver o detalhe.
                </p>
              </>
            )}
            {tab === 'signals' && (
              <>
                <h2 className={styles.sectionTitle}>Sinais das lojas</h2>
                <Loadable state={signals} label="Carregando sinais">
                  {(items) => items.length === 0
                    ? <EmptyState>Nenhum sinal recebido. Mensagens das lojas e franqueados aparecem aqui.</EmptyState>
                    : <div className={styles.cards}>{items.map((s) => <SignalCard key={s.id} signal={s} />)}</div>}
                </Loadable>
                <SignalTester stores={stores.data ?? []} result={interpreter.result} pending={interpreter.pending}
                  error={interpreter.error?.message ?? null}
                  onInterpret={(text, store) => void interpreter.interpret(text, store)} />
              </>
            )}
            {tab === 'policies' && (
              <>
                <h2 className={styles.sectionTitle}>Políticas do planejador</h2>
                <Loadable state={policies} label="Carregando políticas">
                  {(items) => <PolicyList policies={items} />}
                </Loadable>
              </>
            )}
            {tab === 'audit' && (
              <>
                <h2 className={styles.sectionTitle}>Registro de decisões</h2>
                <Loadable state={audit} label="Carregando registro">{(items) => <AuditLog events={items} />}</Loadable>
              </>
            )}
          </section>
        </main>
        <div className={styles.copilot}>
          <CopilotPanel messages={copilot.messages} pending={copilot.pending} error={copilot.error?.message ?? null}
            suggestions={SUGGESTIONS} sourceTitles={sourceTitles} focusLabel={focusSku}
            onAsk={(q) => void copilot.ask(q, focusSku)}
            onRetry={() => copilot.lastQuestion && void copilot.ask(copilot.lastQuestion, focusSku)} />
        </div>
      </div>
    </div>
  )
}
