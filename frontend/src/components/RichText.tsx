import { Fragment } from 'react'
import { parseRichText, type Block, type Line } from '../richText'
import styles from './RichText.module.css'

// Selo numerado de uma fonte citada; o mesmo selo aparece no texto e na lista de fontes.
export function SourceRef({ n }: { n: number }) {
  return (
    <span className={styles.ref}>
      <span className="visually-hidden">fonte </span>
      {n}
    </span>
  )
}

function InlineView({ nodes, refCount }: { nodes: Line; refCount: number }) {
  return (
    <>
      {nodes.map((node, i) => {
        if (node.kind === 'text') return <Fragment key={i}>{node.text}</Fragment>
        if (node.kind === 'strong') return <strong key={i}><InlineView nodes={node.children} refCount={refCount} /></strong>
        return node.n >= 1 && node.n <= refCount ? <SourceRef key={i} n={node.n} /> : <Fragment key={i}>[{node.n}]</Fragment>
      })}
    </>
  )
}

function Lines({ lines, refCount }: { lines: Line[]; refCount: number }) {
  return (
    <>
      {lines.map((line, i) => (
        <Fragment key={i}>
          {i > 0 && <br />}
          <InlineView nodes={line} refCount={refCount} />
        </Fragment>
      ))}
    </>
  )
}

function BlockView({ block, refCount }: { block: Block; refCount: number }) {
  if (block.kind === 'paragraph') return <p><Lines lines={block.lines} refCount={refCount} /></p>
  const items = block.items.map((lines, i) => <li key={i}><Lines lines={lines} refCount={refCount} /></li>)
  return block.ordered
    ? <ol className={styles.list} start={block.start}>{items}</ol>
    : <ul className={styles.list}>{items}</ul>
}

// Mostra o Markdown restrito do copiloto (parágrafos, listas, negrito e fontes [n]) sem interpretar HTML.
export function RichText({ text, refCount = 0 }: { text: string; refCount?: number }) {
  return (
    <div className={styles.rich}>
      {parseRichText(text).map((block, i) => <BlockView key={i} block={block} refCount={refCount} />)}
    </div>
  )
}
