import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ApiProvider } from './api/ApiProvider'
import { createApiClient, type FetchLike } from './api/client'
import { AllocationDesk } from './pages/AllocationDesk'
import './styles/tokens.css'

// ?simulate=error força erro em todas as chamadas, para revisar o estado de erro (skill validar-layout).
const simulateError = new URLSearchParams(window.location.search).get('simulate') === 'error'
const failingFetch: FetchLike = async () =>
  new Response(JSON.stringify({ error: { code: 'simulated', message: 'Erro simulado para revisão de layout.' } }),
    { status: 503 })

const client = createApiClient(simulateError ? failingFetch : undefined)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ApiProvider client={client}>
      <AllocationDesk />
    </ApiProvider>
  </StrictMode>,
)
