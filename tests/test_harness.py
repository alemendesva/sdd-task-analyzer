import pytest
from src.task_analyzer import analyze_tasks, TaskValidationError


# --- FIXTURES ---

@pytest.fixture
def cenario_valido_mix_tarefas():
    """Retorna um conjunto completo de tarefas válidas com diferentes status e prioridades."""
    return [
        {
            "id": 1,
            "titulo": "Tarefa Concluída no Prazo - Alta",
            "prioridade": "alta",
            "data_criacao": "2026-10-01T08:00:00",
            "data_conclusao": "2026-10-01T12:00:00",  # 4 horas
            "data_vencimento": "2026-10-01T18:00:00",
            "status": "concluida",
        },
        {
            "id": 2,
            "titulo": "Tarefa Concluída Atrasada - Média",
            "prioridade": "media",
            "data_criacao": "2026-10-02T10:00:00",
            "data_conclusao": "2026-10-02T16:00:00",  # 6 horas
            "data_vencimento": "2026-10-02T12:00:00",  # Atrasou em relação ao vencimento
            "status": "concluida",
        },
        {
            "id": 3,
            "titulo": "Tarefa Pendente no Prazo - Baixa",
            "prioridade": "baixa",
            "data_criacao": "2026-10-03T09:00:00",
            "data_conclusao": None,
            "data_vencimento": "2026-10-10T18:00:00",
            "status": "pendente",
        },
    ]


# --- TESTES DE SUCESSO E CÁLCULO DE MÉTRICAS ---

def test_calculo_metricas_cenario_sucesso(cenario_valido_mix_tarefas):
    """Valida o cálculo exato das métricas gerais e agregadas por prioridade."""
    resultado = analyze_tasks(cenario_valido_mix_tarefas)

    assert resultado["total_tarefas"] == 3
    assert resultado["total_concluidas"] == 2
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 5.0  # (4 + 6) / 2
    assert resultado["tempo_medio_conclusao_por_prioridade"]["alta"] == 4.0
    assert resultado["tempo_medio_conclusao_por_prioridade"]["media"] == 6.0
    assert resultado["tempo_medio_conclusao_por_prioridade"]["baixa"] == 0.0
    assert "taxa_atraso_percentual" in resultado


# --- TESTES DE VALIDAÇÃO E TRATAMENTO DE ERROS (EXCEÇÕES) ---

def test_excecao_data_conclusao_anterior_a_criacao():
    """Garante o disparo de TaskValidationError quando a data de conclusão precede a criação."""
    tasks = [
        {
            "id": 1,
            "titulo": "Viagem no tempo",
            "prioridade": "alta",
            "data_criacao": "2026-10-10T10:00:00",
            "data_conclusao": "2026-10-09T10:00:00",
            "status": "concluida",
        }
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(tasks)

    assert "não pode ser anterior" in str(exc_info.value)


def test_excecao_formato_data_invalido():
    """Garante disparo de TaskValidationError se a string de data for malformatada."""
    tasks = [
        {
            "id": 1,
            "titulo": "Data Inválida",
            "prioridade": "media",
            "data_criacao": "10/10/2026 10:00:00",  # Formato não ISO
            "status": "pendente",
        }
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(tasks)

    assert "inválida" in str(exc_info.value).lower()


def test_excecao_prioridade_invalida():
    """Garante o disparo de TaskValidationError para prioridades fora de ('alta', 'media', 'baixa')."""
    tasks = [
        {
            "id": 1,
            "titulo": "Tarefa Urgente",
            "prioridade": "urgente",  # Prioridade fora do padrão
            "data_criacao": "2026-10-01T08:00:00",
            "data_conclusao": "2026-10-01T10:00:00",
            "status": "concluida",
        }
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(tasks)

    assert "Prioridade inválida" in str(exc_info.value)


# --- TESTES DE CASOS DE BORDA (EDGE CASES) ---

def test_casos_de_borda_lista_vazia():
    """Valida o retorno seguro zerado para entradas vazias sem erro de divisão por zero."""
    resultado = analyze_tasks([])

    assert resultado["total_tarefas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_casos_de_borda_somente_pendentes():
    """Garante que lista composta apenas por pendentes não zere métricas incorretamente."""
    tasks = [
        {
            "id": 1,
            "titulo": "Tarefa Pendente 1",
            "prioridade": "alta",
            "data_criacao": "2026-10-01T08:00:00",
            "data_conclusao": None,
            "status": "pendente",
        }
    ]
    resultado = analyze_tasks(tasks)

    assert resultado["total_tarefas"] == 1
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 0.0