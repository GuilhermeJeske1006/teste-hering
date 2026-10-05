// Tipos que espelham os schemas da API (backend/app/api/schemas.py e api.md).

export type Severity = 'critical' | 'high' | 'medium' | 'low'
export type ExceptionStatus = 'open' | 'approved' | 'rejected'
export type DecisionAction = 'approve' | 'reject' | 'undo'
export type ExecutionMode = 'ship' | 'order_suggestion'
export type SignalType = 'local_event' | 'lost_sales' | 'size_curve' | 'stock_mismatch' | 'other'

export interface Week {
  year: number
  iso_week: number
  start: string
  end: string
}

export interface Summary {
  week: Week
  total_lines: number
  within_policy: number
  open_exceptions: number
  transfers: number
  shadow_mode: boolean
}

export interface Sku {
  id: string
  name: string
  category: string
  size_grid: string
  sizes: string[]
  price: number
  is_basic: boolean
  is_launch: boolean
}

export interface Store {
  id: string
  name: string
  ownership: string
  execution_mode: string
}

export interface PlanCell {
  size: string
  stock: number
  forecast_horizon: number
  target: number
  dc_allocated: number
  transfer_in: number
  transfer_out: number
  excess: number
  status: string
}

export interface PlanRow {
  store_id: string
  store_name: string
  execution_mode: string
  cells: PlanCell[]
  total_movement: number
}

export interface SkuPlan {
  sku: string
  sizes: string[]
  rows: PlanRow[]
}

export interface Transfer {
  sku: string
  size: string
  source: string
  destination: string
  qty: number
}

export interface Decision {
  action: string
  actor: string
  decided_at: string
  reason: string | null
}

export interface AllocationException {
  id: string
  rule: string
  severity: string
  title: string
  recommendation: string
  explanation: string
  facts: string[]
  status: string
  decision: Decision | null
}

export interface Adjustment {
  scope: string
  pct: number
}

export interface Signal {
  id: string
  store: string
  author_role: string
  received_at: string
  text: string
  interpreted: { type: string; event: string | null; adjustments: Adjustment[]; confidence: number }
}

export interface SignalInterpretation {
  store: string | null
  type: string
  event: string | null
  adjustments: Adjustment[]
  confidence: number
  requires_human: boolean
  reason: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface CopilotAnswer {
  answer: string
  sources: string[]
}

export interface Policy {
  key: string
  label: string
  description: string
  value: number | number[]
  unit: string
}

export interface AuditEvent {
  timestamp: string
  actor: string
  action: string
  subject: string
  detail: string | null
  exception_id?: string | null
}

export interface Health {
  status: 'ok'
  llm: 'anthropic' | 'deterministic'
}
