"""Módulo para análise de tarefas com métricas de desempenho e relatórios.

Este módulo implementa a lógica de validação e cálculo de estatísticas
sobre uma lista de tarefas, seguindo princípios de Spec-Driven Development (SDD).
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


class TaskValidationError(Exception):
    """Exceção lançada quando os dados de uma tarefa são inválidos."""

    pass


@dataclass(frozen=True)
class _ParsedTask:
    """Estrutura interna imutável para representar dados validados de uma tarefa."""

    id: int | str
    titulo: str
    prioridade: str
    status: str
    dt_criacao: datetime
    dt_conclusao: datetime | None
    dt_vencimento: datetime | None


def _parse_iso_datetime(date_str: Any) -> datetime | None:
    """Converte uma string em formato ISO 8601 para um objeto datetime.

    Args:
        date_str: String contendo a data no formato ISO 8601 ou None.

    Returns:
        Objeto datetime correspondente ou None se a entrada for None.

    Raises:
        TaskValidationError: Se a entrada não for uma string ISO 8601 válida ou None.
    """
    if date_str is None:
        return None
    if not isinstance(date_str, str):
        raise TaskValidationError(
            f"Formato de data inválido. Esperado 'str' ou 'None', recebido: '{type(date_str).__name__}'."
        )
    try:
        return datetime.fromisoformat(date_str)
    except ValueError as exc:
        raise TaskValidationError(f"Data em formato ISO inválida: '{date_str}'.") from exc


def _validate_and_parse_task(task: dict[str, Any]) -> _ParsedTask:
    """Valida os campos de uma tarefa e constrói uma instância de _ParsedTask.

    Args:
        task: Dicionário contendo os dados de uma tarefa.

    Returns:
        Instância de _ParsedTask validada.

    Raises:
        TaskValidationError: Se algum campo obrigatório estiver ausente, se os valores
            forem inválidos ou se data_conclusao for anterior a data_criacao.
    """
    if not isinstance(task, dict):
        raise TaskValidationError(f"A tarefa deve ser um dicionário, recebido: '{type(task).__name__}'.")

    required_keys = {"id", "titulo", "prioridade", "data_criacao", "status"}
    missing_keys = required_keys - task.keys()
    if missing_keys:
        raise TaskValidationError(f"Campos obrigatórios ausentes na tarefa: {sorted(missing_keys)}.")

    prioridade = task["prioridade"]
    valid_priorities = {"alta", "media", "baixa"}
    if prioridade not in valid_priorities:
        raise TaskValidationError(
            f"Prioridade inválida '{prioridade}'. Valores aceitos: {sorted(valid_priorities)}."
        )

    status = task["status"]
    valid_statuses = {"concluida", "pendente"}
    if status not in valid_statuses:
        raise TaskValidationError(
            f"Status inválido '{status}'. Valores aceitos: {sorted(valid_statuses)}."
        )

    dt_criacao = _parse_iso_datetime(task.get("data_criacao"))
    if dt_criacao is None:
        raise TaskValidationError("O campo 'data_criacao' é obrigatório e não pode ser nulo.")

    dt_conclusao = _parse_iso_datetime(task.get("data_conclusao"))
    if status == "concluida" and dt_conclusao is None:
        raise TaskValidationError("Tarefas com status 'concluida' devem conter 'data_conclusao'.")

    dt_vencimento = _parse_iso_datetime(task.get("data_vencimento"))

    if dt_conclusao is not None:
        try:
            if dt_conclusao < dt_criacao:
                raise TaskValidationError(
                    f"A data_conclusao ({dt_conclusao}) não pode ser anterior à data_criacao ({dt_criacao})."
                )
        except TypeError as exc:
            raise TaskValidationError("Incompatibilidade de timezone entre as datas informadas.") from exc

    return _ParsedTask(
        id=task["id"],
        titulo=str(task["titulo"]),
        prioridade=prioridade,
        status=status,
        dt_criacao=dt_criacao,
        dt_conclusao=dt_conclusao,
        dt_vencimento=dt_vencimento,
    )


def _is_task_delayed(task: _ParsedTask, reference_now: datetime | None = None) -> bool:
    """Verifica se uma tarefa está atrasada com base na data de vencimento.

    Args:
        task: Instância validada da tarefa.
        reference_now: Instância de datetime para comparar com tarefas pendentes.

    Returns:
        True se a tarefa estiver atrasada, False caso contrário.
    """
    if task.dt_vencimento is None:
        return False

    if task.status == "concluida":
        if task.dt_conclusao is None:
            return False
        try:
            return task.dt_conclusao > task.dt_vencimento
        except TypeError:
            return False

    if task.status == "pendente":
        if reference_now is None:
            reference_now = (
                datetime.now(task.dt_vencimento.tzinfo)
                if task.dt_vencimento.tzinfo is not None
                else datetime.now()
            )
        try:
            return reference_now > task.dt_vencimento
        except TypeError:
            return False

    return False


def _calculate_average_completion_hours(completed_tasks: list[_ParsedTask]) -> float:
    """Calcula o tempo médio de conclusão em horas para tarefas concluídas.

    Args:
        completed_tasks: Lista contendo apenas tarefas concluídas.

    Returns:
        Média em horas arredondada para 2 casas decimais, ou 0.0 se a lista estiver vazia.
    """
    if not completed_tasks:
        return 0.0

    durations: list[float] = []
    for task in completed_tasks:
        if task.dt_conclusao is not None:
            delta_seconds = (task.dt_conclusao - task.dt_criacao).total_seconds()
            durations.append(delta_seconds / 3600.0)

    if not durations:
        return 0.0

    return round(sum(durations) / len(durations), 2)


def _calculate_average_hours_by_priority(completed_tasks: list[_ParsedTask]) -> dict[str, float]:
    """Calcula a média de tempo de conclusão em horas agrupada por prioridade.

    Args:
        completed_tasks: Lista de tarefas concluídas.

    Returns:
        Dicionário com médias arredondadas para as chaves 'alta', 'media' e 'baixa'.
    """
    priorities = ("alta", "media", "baixa")
    grouped: dict[str, list[float]] = {p: [] for p in priorities}

    for task in completed_tasks:
        if task.dt_conclusao is not None and task.prioridade in grouped:
            delta_seconds = (task.dt_conclusao - task.dt_criacao).total_seconds()
            grouped[task.prioridade].append(delta_seconds / 3600.0)

    return {
        p: round(sum(grouped[p]) / len(grouped[p]), 2) if grouped[p] else 0.0
        for p in priorities
    }


def analyze_tasks(
    tasks: list[dict[str, Any]], reference_now: datetime | None = None
) -> dict[str, Any]:
    """Processa uma lista de tarefas e gera um relatório consolidado de métricas.

    Args:
        tasks: Lista de dicionários, onde cada dicionário representa uma tarefa.
        reference_now: Data/hora de referência para avaliar o atraso de tarefas
            pendentes. Se None, usa a data/hora atual.

    Returns:
        Dicionário contendo as seguintes métricas:
            - total_tarefas (int): Número total de tarefas.
            - total_concluidas (int): Quantidade de tarefas concluídas.
            - total_pendentes (int): Quantidade de tarefas pendentes.
            - tempo_medio_conclusao_horas (float): Tempo médio de conclusão em horas.
            - tempo_medio_conclusao_por_prioridade (dict): Média de tempo por prioridade.
            - taxa_atraso_percentual (float): Percentual de tarefas atrasadas (0.0 a 100.0).

    Raises:
        TaskValidationError: Se alguma tarefa contiver dados inválidos, formatos de data
            incorretos ou se data_conclusao for menor que data_criacao.
    """
    parsed_tasks: list[_ParsedTask] = [_validate_and_parse_task(task) for task in tasks]

    total_tarefas = len(parsed_tasks)
    completed_tasks = [t for t in parsed_tasks if t.status == "concluida"]
    pending_tasks = [t for t in parsed_tasks if t.status == "pendente"]

    total_concluidas = len(completed_tasks)
    total_pendentes = len(pending_tasks)

    tempo_medio_geral = _calculate_average_completion_hours(completed_tasks)
    tempo_medio_prioridade = _calculate_average_hours_by_priority(completed_tasks)

    delayed_count = sum(1 for t in parsed_tasks if _is_task_delayed(t, reference_now))

    if total_tarefas == 0:
        taxa_atraso = 0.0
    else:
        taxa_atraso = round((delayed_count / total_tarefas) * 100.0, 2)

    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": total_concluidas,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": tempo_medio_geral,
        "tempo_medio_conclusao_por_prioridade": tempo_medio_prioridade,
        "taxa_atraso_percentual": taxa_atraso,
    }