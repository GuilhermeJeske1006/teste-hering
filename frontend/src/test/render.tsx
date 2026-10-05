import { render, renderHook, type RenderOptions } from '@testing-library/react'
import type { ReactElement, ReactNode } from 'react'
import { ApiProvider } from '../api/ApiProvider'
import type { ApiClient } from '../api/client'

export function renderWithApi(ui: ReactElement, client: ApiClient, options?: RenderOptions) {
  return render(<ApiProvider client={client}>{ui}</ApiProvider>, options)
}

export function renderHookWithApi<T>(hook: () => T, client: ApiClient) {
  return renderHook(hook, { wrapper: ({ children }: { children: ReactNode }) => <ApiProvider client={client}>{children}</ApiProvider> })
}
