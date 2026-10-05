// Markdown restrito das respostas do copiloto (ADR 0016): parágrafos, listas, **negrito** e referências [n].
// Vira uma árvore de dados, nunca HTML: o componente monta só elementos conhecidos, então nada do texto executa.

export type Inline =
  | { kind: 'text'; text: string }
  | { kind: 'strong'; children: Inline[] }
  | { kind: 'ref'; n: number }

export type Line = Inline[]

export type Block =
  | { kind: 'paragraph'; lines: Line[] }
  | { kind: 'list'; ordered: boolean; start: number; items: Line[][] }

const ORDERED_ITEM = /^\s{0,2}(\d{1,3})[.)]\s+(.*)$/
const BULLET_ITEM = /^\s{0,2}[-*•]\s+(.*)$/
const CONTINUATION = /^\s{2,}\S/
const HEADING = /^#{1,6}\s+(.*)$/
const INLINE = /\*\*(.+?)\*\*|\[(\d{1,2})\]/g

export function parseInline(text: string): Inline[] {
  const out: Inline[] = []
  let at = 0
  for (const match of text.matchAll(INLINE)) {
    const index = match.index ?? 0
    if (index > at) out.push({ kind: 'text', text: text.slice(at, index) })
    out.push(match[1] !== undefined
      ? { kind: 'strong', children: parseInline(match[1]) }
      : { kind: 'ref', n: Number(match[2]) })
    at = index + match[0].length
  }
  if (at < text.length) out.push({ kind: 'text', text: text.slice(at) })
  return out
}

function listItem(raw: string): { ordered: boolean; start: number; content: string } | null {
  const ordered = ORDERED_ITEM.exec(raw)
  if (ordered) return { ordered: true, start: Number(ordered[1]), content: ordered[2] }
  const bullet = BULLET_ITEM.exec(raw)
  return bullet ? { ordered: false, start: 1, content: bullet[1] } : null
}

function textLine(raw: string): Line {
  const heading = HEADING.exec(raw.trim())
  return heading ? [{ kind: 'strong', children: parseInline(heading[1]) }] : parseInline(raw.trim())
}

export function parseRichText(text: string): Block[] {
  const blocks: Block[] = []
  let open = false // o último bloco ainda recebe linhas (não houve linha em branco depois dele)
  for (const raw of text.replace(/\r\n?/g, '\n').split('\n')) {
    if (!raw.trim()) {
      open = false
      continue
    }
    const last = open ? blocks[blocks.length - 1] : undefined
    const item = listItem(raw)
    if (item) {
      const line = [parseInline(item.content)]
      if (last?.kind === 'list' && last.ordered === item.ordered) last.items.push(line)
      else blocks.push({ kind: 'list', ordered: item.ordered, start: item.start, items: [line] })
    } else if (last?.kind === 'list' && CONTINUATION.test(raw)) {
      last.items[last.items.length - 1].push(parseInline(raw.trim()))
    } else if (last?.kind === 'paragraph') {
      last.lines.push(textLine(raw))
    } else {
      blocks.push({ kind: 'paragraph', lines: [textLine(raw)] })
    }
    open = true
  }
  return blocks
}
