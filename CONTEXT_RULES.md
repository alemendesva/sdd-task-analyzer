# CONTEXT_RULES — Diretrizes para Agentes de IA

## Diretrizes Arquiteturais
- Linguagem: Python 3.11+.
- Type Hints: Uso obrigatório em 100% das funções, parâmetros e retornos.
- Princípios: SRP (Single Responsibility Principle) e PEP 8.
- Documentação: Docstrings no padrão Google.
- Tratamento de Erros: Lançar exceção customizada `TaskValidationError` para dados inválidos.
- Prevenção de Falhas: Garantir tratamento contra divisão por zero.

## Proibições Explicitas
- Não utilizar bibliotecas externas não autorizadas (usar apenas biblioteca padrão e pytest).
- Não alterar nomes de funções públicas, parâmetros ou estrutura de dados definida na especificação.
- Não assumir comportamentos não especificados no contrato de negócio.