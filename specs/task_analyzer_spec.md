# Especificação Técnica SDD — Módulo TaskAnalyzer

## Contrato de Execução (`analyze_tasks`)
- Entrada: Lista de dicionários contendo as tarefas:
  - `id` (int/str)
  - `titulo` (str)
  - `prioridade` (str: 'alta', 'media', 'baixa')
  - `data_criacao` (str: ISO format "YYYY-MM-DDTHH:MM:SS")
  - `data_conclusao` (str/None: ISO format "YYYY-MM-DDTHH:MM:SS" ou None)
  - `status` (str: 'concluida', 'pendente')
  - `data_vencimento` (str/None: ISO format)

- Saída (dict):
  - `total_tarefas`: int
  - `total_concluidas`: int
  - `total_pendentes`: int
  - `tempo_medio_conclusao_horas`: float (0.0 caso não haja tarefas concluídas)
  - `tempo_medio_conclusao_por_prioridade`: dict (`{'alta': float, 'media': float, 'baixa': float}`)
  - `taxa_atraso_percentual`: float (0.0 a 100.0)

- Regras de Erro:
  - Disparar `TaskValidationError` se `data_conclusao < data_criacao`.