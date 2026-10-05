/* Gerado a partir da API real com o seed da semana 41 (uma exceção rejeitada para cobrir o estado decidido). */
import type { AuditEvent, CopilotAnswer, AllocationException, Policy, SignalInterpretation, Signal, Sku, SkuPlan, Store, Summary } from '../api/types'

export const summary: Summary = {
  "week": {
    "year": 2026,
    "iso_week": 41,
    "start": "2026-10-05",
    "end": "2026-10-11"
  },
  "total_lines": 248,
  "within_policy": 136,
  "open_exceptions": 6,
  "transfers": 3,
  "shadow_mode": true
}

export const exceptions: AllocationException[] = [
  {
    "id": "275c8698d6",
    "rule": "launch_approval",
    "severity": "critical",
    "title": "Lançamento VM-FL · Vestido midi floral precisa de aprovação",
    "recommendation": "Aprovar a grade inicial de 121 peças em 8 lojas",
    "explanation": "O lançamento Vestido midi floral entrou na semana 41 e está dentro da janela de 2 semanas em que a alocação precisa de aval. A previsão vem da média de 3 produtos parecidos, então a primeira grade só segue depois da sua aprovação.",
    "facts": [
      "Lançamento na semana 41",
      "Grade inicial: 121 peças (R$ 27.817,90)",
      "Por loja: BC 29 · BNU-C 14 · BNU-S 17 · BRQ 10 · GAS 10 · ITJ 13 · JGS 12 · JOI 16"
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "1d3f769caa",
    "rule": "stockout_transfer",
    "severity": "high",
    "title": "Transferir CB-PT M de Brusque para 3 lojas",
    "recommendation": "Transferir 22 peças de BRQ: 13 para JOI, 8 para BNU-S e 1 para BC",
    "explanation": "O CD tem só 50 peças de Camiseta básica algodão preta M para uma necessidade de 95. Brusque tem 9,2 semanas de cobertura e pode ceder 22 sem risco, o que evita ruptura nas lojas de destino.",
    "facts": [
      "Estoque no CD: 50 peças",
      "Necessidade das lojas: 95 peças",
      "Cobertura da origem: 9,2 semanas",
      "Frete estimado: R$ 114,00 (3 × R$ 38,00)",
      "A origem é franquia: depende do aceite do franqueado"
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "cc8dfa909e",
    "rule": "signal_divergence",
    "severity": "high",
    "title": "Sinal de Blumenau Centro pede +40% em tudo",
    "recommendation": "Decidir se aplica +40%: o limite automático é 20%",
    "explanation": "Blumenau Centro pediu 40% a mais em tudo por causa de Oktoberfest. O pedido passa do limite de 20% para ajuste automático, então não entrou na previsão. Só você pode aplicar esse ajuste.",
    "facts": [
      "Pedido: +40%",
      "Limite automático: 20%",
      "Confiança da interpretação: 80%",
      "Mensagem: \"Pessoal, Oktoberfest começou! Precisamos de pelo menos 40% a mais de tudo, a loja está lot…\""
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "6e47410b5c",
    "rule": "seasonal_decline",
    "severity": "medium",
    "title": "Queda sazonal em MC-CZ · Moletom canguru cinza",
    "recommendation": "Suspender a reposição de MC-CZ e avaliar remarcação em 8 lojas",
    "explanation": "Em 8 lojas, as vendas das últimas 3 semanas caíram 30% ou mais em relação às 3 anteriores, e o estoque cobre 6,0 semanas ou mais. É sinal de fim de estação: repor agora aumenta a sobra.",
    "facts": [
      "Queda média: 52%",
      "Cobertura média: 16,2 semanas",
      "Lojas: BC, BNU-C, BNU-S, BRQ, GAS, ITJ, JGS, JOI"
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "0545ee0e65",
    "rule": "size_curve_deviation",
    "severity": "medium",
    "title": "Curva de tamanhos fora do padrão: CJ-SL em Itajaí",
    "recommendation": "Ajustar a grade de CJ-SL em ITJ para a curva real de vendas",
    "explanation": "Nas últimas 8 semanas, Itajaí vendeu 44 peças de Calça jeans slim, e 3 tamanhos desviam 12 pontos ou mais da curva padrão. Repor pela curva padrão deixa sobra nos tamanhos que não giram.",
    "facts": [
      "38: 36% vendido × 17% padrão",
      "40: 45% vendido × 25% padrão",
      "44: 0% vendido × 17% padrão"
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "54eb97c5d0",
    "rule": "negative_stock",
    "severity": "medium",
    "title": "Estoque negativo: CV-BR P em Gaspar",
    "recommendation": "Corrigir o estoque de CV-BR P em GAS antes de alocar",
    "explanation": "O sistema registra -6 peças de Camiseta gola V branca P em Gaspar, o que é impossível. A linha ficou bloqueada: o motor não adivinha estoque e não recomenda nada até o dado ser corrigido.",
    "facts": [
      "Estoque informado: -6",
      "Linha bloqueada"
    ],
    "status": "open",
    "decision": null
  },
  {
    "id": "d5ab33d7e1",
    "rule": "repeated_rejection",
    "severity": "low",
    "title": "Rejeições repetidas: JJ-AZ em Jaraguá do Sul",
    "recommendation": "Revisar a política de JJ-AZ para JGS",
    "explanation": "A recomendação de Jaqueta jeans para Jaraguá do Sul foi rejeitada 2 vezes nas últimas semanas. Se o padrão continuar, vale ajustar a política dessa loja em vez de rejeitar toda semana.",
    "facts": [
      "Rejeições: 2",
      "Semanas: 39, 40",
      "Motivo mais citado: \"não vende aqui\""
    ],
    "status": "rejected",
    "decision": {
      "action": "reject",
      "actor": "planejador",
      "decided_at": "2026-10-05T18:22:00.221267Z",
      "reason": "Dado de entrada errado"
    }
  }
]

export const skus: Sku[] = [
  {
    "id": "CB-PT",
    "name": "Camiseta básica algodão preta",
    "category": "tees",
    "size_grid": "tops",
    "sizes": [
      "PP",
      "P",
      "M",
      "G",
      "GG"
    ],
    "price": 59.9,
    "is_basic": true,
    "is_launch": false
  },
  {
    "id": "CV-BR",
    "name": "Camiseta gola V branca",
    "category": "tees",
    "size_grid": "tops",
    "sizes": [
      "PP",
      "P",
      "M",
      "G",
      "GG"
    ],
    "price": 69.9,
    "is_basic": true,
    "is_launch": false
  },
  {
    "id": "CJ-SL",
    "name": "Calça jeans slim",
    "category": "bottoms",
    "size_grid": "bottoms",
    "sizes": [
      "36",
      "38",
      "40",
      "42",
      "44",
      "46"
    ],
    "price": 199.9,
    "is_basic": true,
    "is_launch": false
  },
  {
    "id": "MC-CZ",
    "name": "Moletom canguru cinza",
    "category": "sweatshirts",
    "size_grid": "tops",
    "sizes": [
      "PP",
      "P",
      "M",
      "G",
      "GG"
    ],
    "price": 179.9,
    "is_basic": false,
    "is_launch": false
  },
  {
    "id": "VM-FL",
    "name": "Vestido midi floral",
    "category": "dresses",
    "size_grid": "tops",
    "sizes": [
      "PP",
      "P",
      "M",
      "G",
      "GG"
    ],
    "price": 229.9,
    "is_basic": false,
    "is_launch": true
  },
  {
    "id": "JJ-AZ",
    "name": "Jaqueta jeans",
    "category": "jackets",
    "size_grid": "tops",
    "sizes": [
      "PP",
      "P",
      "M",
      "G",
      "GG"
    ],
    "price": 299.9,
    "is_basic": false,
    "is_launch": false
  }
]

export const stores: Store[] = [
  {
    "id": "BNU-S",
    "name": "Blumenau Shopping",
    "ownership": "own",
    "execution_mode": "ship"
  },
  {
    "id": "BNU-C",
    "name": "Blumenau Centro",
    "ownership": "franchise",
    "execution_mode": "order_suggestion"
  },
  {
    "id": "JOI",
    "name": "Joinville Garten",
    "ownership": "own",
    "execution_mode": "ship"
  },
  {
    "id": "ITJ",
    "name": "Itajaí",
    "ownership": "franchise",
    "execution_mode": "order_suggestion"
  },
  {
    "id": "BRQ",
    "name": "Brusque",
    "ownership": "franchise",
    "execution_mode": "order_suggestion"
  },
  {
    "id": "BC",
    "name": "Balneário Camboriú",
    "ownership": "own",
    "execution_mode": "ship"
  },
  {
    "id": "JGS",
    "name": "Jaraguá do Sul",
    "ownership": "franchise",
    "execution_mode": "order_suggestion"
  },
  {
    "id": "GAS",
    "name": "Gaspar",
    "ownership": "franchise",
    "execution_mode": "order_suggestion"
  }
]

export const plan: SkuPlan = {
  "sku": "CB-PT",
  "sizes": [
    "PP",
    "P",
    "M",
    "G",
    "GG"
  ],
  "rows": [
    {
      "store_id": "BNU-S",
      "store_name": "Blumenau Shopping",
      "execution_mode": "ship",
      "cells": [
        {
          "size": "PP",
          "stock": 3,
          "forecast_horizon": 3.9,
          "target": 5,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 6,
          "forecast_horizon": 9.76,
          "target": 13,
          "dc_allocated": 7,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 2,
          "forecast_horizon": 15.62,
          "target": 20,
          "dc_allocated": 10,
          "transfer_in": 8,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 7,
          "forecast_horizon": 11.22,
          "target": 15,
          "dc_allocated": 8,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 4,
          "forecast_horizon": 6.1,
          "target": 8,
          "dc_allocated": 4,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 39
    },
    {
      "store_id": "BNU-C",
      "store_name": "Blumenau Centro",
      "execution_mode": "order_suggestion",
      "cells": [
        {
          "size": "PP",
          "stock": 3,
          "forecast_horizon": 2.44,
          "target": 4,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 7,
          "forecast_horizon": 7.32,
          "target": 10,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 2,
          "forecast_horizon": 12.2,
          "target": 16,
          "dc_allocated": 8,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 9,
          "forecast_horizon": 8.05,
          "target": 11,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 4,
          "forecast_horizon": 4.88,
          "target": 7,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 17
    },
    {
      "store_id": "JOI",
      "store_name": "Joinville Garten",
      "execution_mode": "ship",
      "cells": [
        {
          "size": "PP",
          "stock": 2,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 8,
          "forecast_horizon": 7.6,
          "target": 10,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 4,
          "forecast_horizon": 25.3,
          "target": 32,
          "dc_allocated": 15,
          "transfer_in": 13,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 7,
          "forecast_horizon": 9.43,
          "target": 12,
          "dc_allocated": 5,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 5,
          "forecast_horizon": 4.4,
          "target": 6,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 37
    },
    {
      "store_id": "ITJ",
      "store_name": "Itajaí",
      "execution_mode": "order_suggestion",
      "cells": [
        {
          "size": "PP",
          "stock": 1,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 6,
          "forecast_horizon": 5.4,
          "target": 7,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 2,
          "forecast_horizon": 8.0,
          "target": 10,
          "dc_allocated": 4,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 5,
          "forecast_horizon": 5.4,
          "target": 7,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 3,
          "forecast_horizon": 3.8,
          "target": 5,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 11
    },
    {
      "store_id": "BRQ",
      "store_name": "Brusque",
      "execution_mode": "order_suggestion",
      "cells": [
        {
          "size": "PP",
          "stock": 1,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 4,
          "forecast_horizon": 4.0,
          "target": 5,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 33,
          "forecast_horizon": 7.2,
          "target": 9,
          "dc_allocated": 0,
          "transfer_in": 0,
          "transfer_out": 22,
          "excess": 22,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 5,
          "forecast_horizon": 5.8,
          "target": 8,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 3,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 0,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": -16
    },
    {
      "store_id": "BC",
      "store_name": "Balneário Camboriú",
      "execution_mode": "ship",
      "cells": [
        {
          "size": "PP",
          "stock": 3,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 0,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 6,
          "forecast_horizon": 6.8,
          "target": 9,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 2,
          "forecast_horizon": 11.0,
          "target": 14,
          "dc_allocated": 6,
          "transfer_in": 1,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 5,
          "forecast_horizon": 8.4,
          "target": 11,
          "dc_allocated": 6,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 5,
          "forecast_horizon": 4.0,
          "target": 5,
          "dc_allocated": 0,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 16
    },
    {
      "store_id": "JGS",
      "store_name": "Jaraguá do Sul",
      "execution_mode": "order_suggestion",
      "cells": [
        {
          "size": "PP",
          "stock": 2,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 5,
          "forecast_horizon": 5.6,
          "target": 8,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 1,
          "forecast_horizon": 7.6,
          "target": 10,
          "dc_allocated": 4,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 5,
          "forecast_horizon": 6.0,
          "target": 8,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 3,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 0,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 11
    },
    {
      "store_id": "GAS",
      "store_name": "Gaspar",
      "execution_mode": "order_suggestion",
      "cells": [
        {
          "size": "PP",
          "stock": 1,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "P",
          "stock": 4,
          "forecast_horizon": 3.6,
          "target": 5,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "M",
          "stock": 1,
          "forecast_horizon": 5.0,
          "target": 7,
          "dc_allocated": 3,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "G",
          "stock": 3,
          "forecast_horizon": 4.0,
          "target": 5,
          "dc_allocated": 2,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        },
        {
          "size": "GG",
          "stock": 2,
          "forecast_horizon": 2.0,
          "target": 3,
          "dc_allocated": 1,
          "transfer_in": 0,
          "transfer_out": 0,
          "excess": 0,
          "status": "ok"
        }
      ],
      "total_movement": 9
    }
  ]
}

export const signals: Signal[] = [
  {
    "id": "sig-001",
    "store": "BNU-C",
    "author_role": "franchisee",
    "received_at": "2026-10-03T10:12:00-03:00",
    "text": "Pessoal, Oktoberfest começou! Precisamos de pelo menos 40% a mais de tudo, a loja está lotando.",
    "interpreted": {
      "type": "local_event",
      "event": "Oktoberfest",
      "adjustments": [
        {
          "scope": "all",
          "pct": 40.0
        }
      ],
      "confidence": 0.8
    }
  },
  {
    "id": "sig-002",
    "store": "JOI",
    "author_role": "store_manager",
    "received_at": "2026-10-04T18:40:00-03:00",
    "text": "Cliente procurando muito a camiseta preta M e G, já perdemos várias vendas no fim de semana.",
    "interpreted": {
      "type": "lost_sales",
      "event": null,
      "adjustments": [
        {
          "scope": "CB-PT:M",
          "pct": 15.0
        },
        {
          "scope": "CB-PT:G",
          "pct": 15.0
        }
      ],
      "confidence": 0.9
    }
  },
  {
    "id": "sig-003",
    "store": "ITJ",
    "author_role": "franchisee",
    "received_at": "2026-10-02T09:05:00-03:00",
    "text": "Calça slim: só sai 38 e 40, os 44 e 46 estão parados desde agosto.",
    "interpreted": {
      "type": "size_curve",
      "event": null,
      "adjustments": [],
      "confidence": 0.85
    }
  },
  {
    "id": "sig-004",
    "store": "GAS",
    "author_role": "franchisee",
    "received_at": "2026-10-01T14:30:00-03:00",
    "text": "Acho que o sistema está errado, tem camiseta V branca P na prateleira mas aparece zerado/negativo.",
    "interpreted": {
      "type": "stock_mismatch",
      "event": null,
      "adjustments": [],
      "confidence": 0.95
    }
  }
]

export const policies: Policy[] = [
  {
    "key": "forecast_weights",
    "label": "Pesos da média móvel",
    "description": "Peso de cada uma das últimas semanas, da mais recente para a mais antiga.",
    "value": [
      0.4,
      0.3,
      0.2,
      0.1
    ],
    "unit": "pesos"
  },
  {
    "key": "horizon_weeks",
    "label": "Horizonte de cobertura",
    "description": "Semanas cobertas pela previsão e pelo alvo.",
    "value": 2,
    "unit": "semanas"
  },
  {
    "key": "cover_factor",
    "label": "Fator de cobertura",
    "description": "Multiplica a previsão do horizonte para chegar ao alvo.",
    "value": 1.25,
    "unit": "×"
  },
  {
    "key": "min_display_basic",
    "label": "Exposição mínima de básicos",
    "description": "Peças mínimas por tamanho em produtos básicos.",
    "value": 3,
    "unit": "peças"
  },
  {
    "key": "min_display_other",
    "label": "Exposição mínima dos demais",
    "description": "Peças mínimas por tamanho nos demais produtos.",
    "value": 1,
    "unit": "peças"
  },
  {
    "key": "excess_trigger_factor",
    "label": "Gatilho de excesso",
    "description": "Estoque acima da previsão do horizonte vezes este fator vira excesso.",
    "value": 2.4,
    "unit": "×"
  },
  {
    "key": "excess_keep_factor",
    "label": "Estoque mantido ao liberar excesso",
    "description": "Ao liberar excesso, a loja fica com a previsão do horizonte vezes este fator.",
    "value": 1.5,
    "unit": "×"
  },
  {
    "key": "auto_execution_max_value_brl",
    "label": "Limite de execução automática",
    "description": "Valor máximo de envio automático por loja própria na semana.",
    "value": 8000,
    "unit": "R$"
  },
  {
    "key": "launch_approval_weeks",
    "label": "Janela de aprovação de lançamentos",
    "description": "Semanas após o lançamento em que a grade precisa de aprovação.",
    "value": 2,
    "unit": "semanas"
  },
  {
    "key": "stockout_alert_cover_weeks",
    "label": "Alerta de ruptura",
    "description": "Cobertura abaixo da qual a loja está em risco de ruptura.",
    "value": 1.0,
    "unit": "semanas"
  },
  {
    "key": "transfer_min_source_cover_weeks",
    "label": "Cobertura mínima da origem",
    "description": "Uma loja só cede peças se a própria cobertura passar disso.",
    "value": 6.0,
    "unit": "semanas"
  },
  {
    "key": "transfer_freight_brl",
    "label": "Frete por transferência",
    "description": "Custo estimado de cada transferência entre lojas.",
    "value": 38.0,
    "unit": "R$"
  },
  {
    "key": "signal_max_auto_adjust_pct",
    "label": "Ajuste automático máximo por sinal",
    "description": "Acima disso, o ajuste pedido por uma loja exige decisão humana.",
    "value": 20,
    "unit": "%"
  },
  {
    "key": "seasonal_decline_pct",
    "label": "Queda que indica fim de estação",
    "description": "Queda de vendas entre as janelas comparadas que dispara a regra sazonal.",
    "value": 30,
    "unit": "%"
  },
  {
    "key": "seasonal_min_cover_weeks",
    "label": "Cobertura na queda sazonal",
    "description": "Cobertura mínima para considerar que há sobra de estoque.",
    "value": 6.0,
    "unit": "semanas"
  },
  {
    "key": "seasonal_min_stores",
    "label": "Lojas na queda sazonal",
    "description": "Quantas lojas precisam cair ao mesmo tempo.",
    "value": 3,
    "unit": "lojas"
  },
  {
    "key": "seasonal_window_weeks",
    "label": "Janela da queda sazonal",
    "description": "Semanas recentes comparadas com o mesmo número de semanas anteriores.",
    "value": 3,
    "unit": "semanas"
  },
  {
    "key": "size_curve_deviation_pp",
    "label": "Desvio da curva de tamanhos",
    "description": "Diferença, em pontos percentuais, que conta como desvio de um tamanho.",
    "value": 12,
    "unit": "p.p."
  },
  {
    "key": "size_curve_min_units",
    "label": "Volume mínimo para avaliar a curva",
    "description": "Peças vendidas na janela para a curva ser confiável.",
    "value": 30,
    "unit": "peças"
  },
  {
    "key": "size_curve_min_sizes",
    "label": "Tamanhos fora da curva",
    "description": "Quantos tamanhos precisam desviar ao mesmo tempo.",
    "value": 2,
    "unit": "tamanhos"
  },
  {
    "key": "size_curve_weeks",
    "label": "Janela da curva de tamanhos",
    "description": "Semanas de vendas usadas para medir a curva.",
    "value": 8,
    "unit": "semanas"
  },
  {
    "key": "repeated_rejection_count",
    "label": "Rejeições repetidas",
    "description": "Rejeições da mesma loja e produto que pedem revisão da política.",
    "value": 2,
    "unit": "rejeições"
  }
]

export const audit: AuditEvent[] = [
  {
    "timestamp": "2026-10-05T18:22:00.221820Z",
    "actor": "planejador",
    "action": "reject",
    "subject": "Rejeições repetidas: JJ-AZ em Jaraguá do Sul",
    "detail": "Dado de entrada errado",
    "exception_id": "d5ab33d7e1"
  },
  {
    "timestamp": "2026-10-05T18:22:00.201460Z",
    "actor": "sistema",
    "action": "recommend",
    "subject": "Plano da semana 41/2026",
    "detail": "248 linhas, 3 transferências e 7 exceções",
    "exception_id": null
  }
]

export const interpretation: SignalInterpretation = {
  "store": "BRQ",
  "type": "local_event",
  "event": "Fenarreco",
  "adjustments": [
    {
      "scope": "all",
      "pct": 30.0
    }
  ],
  "confidence": 0.95,
  "requires_human": true,
  "reason": "Interpretação por palavras-chave (modo sem LLM): tipo local_event, loja BRQ."
}

export const copilot: CopilotAnswer = {
  "answer": "Há **6 exceções abertas** que dependem de você, da mais urgente para a menos urgente:\n\n1. **Crítica** · Lançamento VM-FL · Vestido midi floral precisa de aprovação [275c8698d6]\n   Aprovar a grade inicial de 121 peças em 8 lojas.\n2. **Alta** · Transferir CB-PT M de Brusque para 3 lojas [1d3f769caa]\n   Transferir 22 peças de BRQ: 13 para JOI, 8 para BNU-S e 1 para BC.\n3. **Alta** · Sinal de Blumenau Centro pede +40% em tudo [cc8dfa909e]\n   Decidir se aplica +40%: o limite automático é 20%.\n\nMais 3 estão na aba Exceções.\n\nA decisão é do planejador: o sistema está em modo sombra e não executa nada.",
  "sources": [
    "275c8698d6",
    "1d3f769caa",
    "cc8dfa909e"
  ]
}

