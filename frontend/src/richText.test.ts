import { describe, expect, it } from 'vitest'
import { parseInline, parseRichText } from './richText'

describe('parseRichText', () => {
  it('separa parágrafos por linha em branco e junta linhas seguidas no mesmo parágrafo', () => {
    expect(parseRichText('Primeira.\nContinua.\n\nSegunda.')).toEqual([
      { kind: 'paragraph', lines: [[{ kind: 'text', text: 'Primeira.' }], [{ kind: 'text', text: 'Continua.' }]] },
      { kind: 'paragraph', lines: [[{ kind: 'text', text: 'Segunda.' }]] },
    ])
  })

  it('agrupa itens numerados, guarda o número inicial e junta a linha recuada ao item', () => {
    const [list] = parseRichText('3. Título\n   Detalhe.\n4. Outro')
    expect(list).toEqual({
      kind: 'list', ordered: true, start: 3,
      items: [[[{ kind: 'text', text: 'Título' }], [{ kind: 'text', text: 'Detalhe.' }]], [[{ kind: 'text', text: 'Outro' }]]],
    })
  })

  it('separa parágrafo e lista com marcador quando a lista vem logo depois do texto', () => {
    const blocks = parseRichText('Fatos:\n- um\n* dois\n• três')
    expect(blocks.map((b) => b.kind)).toEqual(['paragraph', 'list'])
    expect(blocks[1]).toMatchObject({ ordered: false, items: [[[{ text: 'um' }]], [[{ text: 'dois' }]], [[{ text: 'três' }]]] })
  })

  it('transforma título Markdown em linha em negrito', () => {
    expect(parseRichText('## Resumo')).toEqual([
      { kind: 'paragraph', lines: [[{ kind: 'strong', children: [{ kind: 'text', text: 'Resumo' }] }]] },
    ])
  })

  it('aceita quebra de linha do Windows e ignora linhas em branco extras', () => {
    expect(parseRichText('\r\n\r\nA\r\n\r\n\r\nB\r\n')).toHaveLength(2)
  })
})

describe('parseInline', () => {
  it('reconhece negrito e referências numeradas, inclusive dentro do negrito', () => {
    expect(parseInline('Veja **[1] urgente** e [2].')).toEqual([
      { kind: 'text', text: 'Veja ' },
      { kind: 'strong', children: [{ kind: 'ref', n: 1 }, { kind: 'text', text: ' urgente' }] },
      { kind: 'text', text: ' e ' },
      { kind: 'ref', n: 2 },
      { kind: 'text', text: '.' },
    ])
  })

  it('mantém como texto o negrito sem fechamento e os ids que não são números', () => {
    expect(parseInline('**aberto e [abc123]')).toEqual([{ kind: 'text', text: '**aberto e [abc123]' }])
  })
})
