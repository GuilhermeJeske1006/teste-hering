import { describe, expect, it } from 'vitest'
import {
  formatDateTime, formatDayMonth, formatDecimal, formatInt, formatPercent, formatPolicyValue, formatSigned,
} from './format'

describe('format', () => {
  it('usa ponto de milhar e vírgula decimal quando formata números em pt-BR', () => {
    expect(formatInt(12345)).toBe('12.345')
    expect(formatDecimal(8.4)).toBe('8,4')
    expect(formatPercent(0.528)).toBe('53%')
  })

  it('mostra o sinal de mais quando o movimento é positivo', () => {
    expect(formatSigned(13)).toBe('+13')
    expect(formatSigned(-22)).toBe('-22')
    expect(formatSigned(0)).toBe('0')
  })

  it('formata valor de política pela unidade quando exibe a lista', () => {
    expect(formatPolicyValue(8000, 'R$')).toMatch(/R\$\s?8\.000,00/)
    expect(formatPolicyValue(20, '%')).toBe('20%')
    expect(formatPolicyValue(1.25, '×')).toBe('1,25×')
    expect(formatPolicyValue(2, 'semanas')).toBe('2 semanas')
    expect(formatPolicyValue([0.4, 0.3], 'pesos')).toBe('0,4 · 0,3')
  })

  it('formata datas no padrão brasileiro quando recebe ISO', () => {
    expect(formatDayMonth('2026-10-05')).toBe('05/10')
    expect(formatDateTime('2026-10-05T12:00:00Z')).toMatch(/05\/10\/(20)?26/)
  })
})
