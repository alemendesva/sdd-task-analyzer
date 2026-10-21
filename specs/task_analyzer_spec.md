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
- Parâmetro opcional `reference_now` (datetime/None): data/hora de referência usada
  para avaliar o atraso de tarefas pendentes. Se None, usa a data/hora atual.

- Saída (dict):
  - `total_tarefas`: int
  - `total_concluidas`: int
  - `total_pendentes`: int
  - `tempo_medio_conclusao_horas`: float (0.0 caso não haja tarefas concluídas)
  - `tempo_medio_conclusao_por_prioridade`: dict (`{'alta': float, 'media': float, 'baixa': float}`)
  - `taxa_atraso_percentual`: float (0.0 a 100.0)

- Regra de Atraso (`taxa_atraso_percentual` = tarefas atrasadas / total de tarefas * 100):
  - Tarefa sem `data_vencimento` nunca é considerada atrasada.
  - Tarefa `concluida` está atrasada se `data_conclusao > data_vencimento`.
  - Tarefa `pendente` está atrasada se `reference_now > data_vencimento`.

- Regras de Erro:
  - Disparar `TaskValidationError` se `data_conclusao < data_criacao`.