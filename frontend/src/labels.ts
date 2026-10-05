// Rótulos de tela (pt-BR) por código. Mapas em vez de switch: um valor novo é uma linha nova (aberto/fechado).

export interface SeverityMeta {
  label: string
  rank: number
}

export const SEVERITY_META: Record<string, SeverityMeta> = {
  critical: { label: 'Crítica', rank: 0 },
  high: { label: 'Alta', rank: 1 },
  medium: { label: 'Média', rank: 2 },
  low: { label: 'Baixa', rank: 3 },
}

export const FALLBACK_SEVERITY: SeverityMeta = { label: 'Sem severidade', rank: 9 }

export const severityMeta = (severity: string): SeverityMeta => SEVERITY_META[severity] ?? FALLBACK_SEVERITY

export const RULE_LABELS: Record<string, string> = {
  launch_approval: 'Aprovação de lançamento',
  stockout_transfer: 'Transferência contra ruptura',
  signal_divergence: 'Sinal acima do limite',
  seasonal_decline: 'Queda sazonal',
  size_curve_deviation: 'Curva de tamanhos',
  negative_stock: 'Estoque negativo',
  repeated_rejection: 'Rejeição repetida',
  auto_execution_limit: 'Limite de execução automática',
}

export const ruleLabel = (rule: string): string => RULE_LABELS[rule] ?? rule

export const EXECUTION_MODE_LABELS: Record<string, string> = {
  ship: 'envio',
  order_suggestion: 'sugestão de pedido',
}

export const STATUS_LABELS: Record<string, string> = {
  open: 'Aberta',
  approved: 'Aprovada',
  rejected: 'Rejeitada',
}

export const AUDIT_ACTION_LABELS: Record<string, string> = {
  approve: 'Aprovou',
  reject: 'Rejeitou',
  undo: 'Desfez a decisão',
  recommend: 'Recomendou',
}

export const SIGNAL_TYPE_LABELS: Record<string, string> = {
  local_event: 'Evento local',
  lost_sales: 'Venda perdida',
  size_curve: 'Curva de tamanhos',
  stock_mismatch: 'Estoque divergente',
  other: 'Outro',
}

export const AUTHOR_ROLE_LABELS: Record<string, string> = {
  franchisee: 'Franqueado',
  store_manager: 'Gerente de loja',
}

export const REJECTION_REASONS = [
  'Conheço um fator que o modelo não vê',
  'Restrição comercial com o franqueado',
  'Dado de entrada errado',
  'Prefiro esperar mais uma semana',
] as const

export const label = (map: Record<string, string>, key: string): string => map[key] ?? key
