# SDD Task Analyzer

Módulo Python que analisa uma lista de tarefas e gera métricas de desempenho
(totais, tempo médio de conclusão, média por prioridade e taxa de atraso),
desenvolvido com Spec-Driven Development (SDD).

## Estrutura

```
specs/task_analyzer_spec.md   # Especificação (contrato de entrada, saída e erros)
CONTEXT_RULES.md              # Diretrizes para agentes de IA
src/task_analyzer.py          # Implementação
tests/test_harness.py         # Testes (pytest)
```

## Requisitos

- Python 3.11+

## Instalação

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Rodando os testes

Na raiz do projeto:

```bash
pytest -v
```

## Uso

```python
from src.task_analyzer import analyze_tasks, TaskValidationError

tarefas = [
    {
        "id": 1,
        "titulo": "Escrever relatório",
        "prioridade": "alta",
        "data_criacao": "2026-10-01T08:00:00",
        "data_conclusao": "2026-10-01T12:00:00",
        "data_vencimento": "2026-10-01T18:00:00",
        "status": "concluida",
    },
]

try:
    print(analyze_tasks(tarefas))
except TaskValidationError as erro:
    print(f"Tarefa inválida: {erro}")
```

Saída:

```python
{
    "total_tarefas": 1,
    "total_concluidas": 1,
    "total_pendentes": 0,
    "tempo_medio_conclusao_horas": 4.0,
    "tempo_medio_conclusao_por_prioridade": {"alta": 4.0, "media": 0.0, "baixa": 0.0},
    "taxa_atraso_percentual": 0.0,
}
```

## Observação

Tarefas pendentes são consideradas atrasadas quando a data/hora de referência
já passou de `data_vencimento`. Por padrão a referência é a data/hora atual; para
um resultado reproduzível, informe `reference_now`:

```python
from datetime import datetime

analyze_tasks(tarefas, reference_now=datetime(2026, 10, 5, 12, 0, 0))
```
