// Formatação pt-BR de números, moeda e datas.

const integer = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 0 })
const decimal = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 2 })
const percent = new Intl.NumberFormat('pt-BR', { style: 'percent', maximumFractionDigits: 0 })
const dateTime = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
const dayMonth = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })

export const formatInt = (value: number): string => integer.format(value)
export const formatDecimal = (value: number): string => decimal.format(value)
export const formatPercent = (ratio: number): string => percent.format(ratio)
export const formatSigned = (value: number): string => (value > 0 ? `+${formatInt(value)}` : formatInt(value))
export const formatDateTime = (iso: string): string => dateTime.format(new Date(iso))
export const formatDayMonth = (isoDate: string): string => dayMonth.format(new Date(`${isoDate}T00:00:00Z`))

export function formatPolicyValue(value: number | number[], unit: string): string {
  if (Array.isArray(value)) return value.map(formatDecimal).join(' · ')
  if (unit === 'R$') return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
  if (unit === '%') return `${formatDecimal(value)}%`
  if (unit === '×') return `${formatDecimal(value)}×`
  return `${formatDecimal(value)} ${unit}`
}
