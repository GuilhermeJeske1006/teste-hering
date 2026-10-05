import { render, screen, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { RichText } from './RichText'

describe('RichText', () => {
  it('mostra parágrafo, negrito e lista numerada com o detalhe de cada item', () => {
    const { container } = render(
      <RichText text={'Há **2 exceções abertas**:\n\n1. **Crítica** · Lançamento\n   Aprovar a grade.\n2. **Alta** · Transferir'} />)
    expect(screen.getByText('2 exceções abertas').tagName).toBe('STRONG')
    const items = within(screen.getByRole('list')).getAllByRole('listitem')
    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent('Crítica · LançamentoAprovar a grade.')
    expect(items[0].querySelector('br')).not.toBeNull()
    expect(container.textContent).not.toContain('**')
  })

  it('numera a lista a partir do número que veio no texto', () => {
    render(<RichText text={'4. Quarto\n5. Quinto'} />)
    expect(screen.getByRole('list')).toHaveAttribute('start', '4')
  })

  it('mostra referência conhecida como selo de fonte e desconhecida como texto', () => {
    render(<RichText text="Veja [1] e [7]." refCount={2} />)
    expect(screen.getByText('fonte', { exact: false }).parentElement).toHaveTextContent('fonte 1')
    expect(screen.getByText(/e \[7\]\./)).toBeInTheDocument()
  })

  it('mostra HTML, imagem e link como texto, sem criar elementos', () => {
    const { container } = render(
      <RichText text={'<img src=x onerror="alert(1)"> [clique](http://exemplo.invalido) <script>x</script>'} />)
    expect(container.querySelector('img, a, script')).toBeNull()
    expect(container).toHaveTextContent('<img src=x onerror="alert(1)">')
  })
})
