# Otimização de prompt: Bug Report para User Story

Este repositório transforma relatos de bugs em User Stories acionáveis e avalia a qualidade da resposta no LangSmith. A entrega inclui o prompt original (v1), o prompt otimizado (v2), scripts de pull/push e seis testes automatizados de estrutura.

## Técnicas aplicadas

O prompt [v2](prompts/bug_to_user_story_v2.yml) combina três técnicas:

- **Few-shot learning:** três pares de entrada/saída cobrem um bug simples de interface, um problema de performance e uma falha de autorização. Eles tornam explícitos o formato da User Story, os critérios BDD e quando incluir contexto técnico.
- **Chain of Thought interno:** o modelo analisa em silêncio a persona, o objetivo, impacto, detalhes técnicos e casos de borda antes de produzir somente a resposta final. Isso aumenta a consistência sem exibir raciocínio ao usuário.
- **Role prompting:** a persona de Product Manager / Agilista Sênior orienta a conversão do relato técnico em uma descrição útil para produto e desenvolvimento.

Além disso, o prompt determina o formato `Como um..., eu quero..., para que...`, exige critérios em BDD, preserva dados fornecidos e proíbe inventar requisitos. Para bugs complexos, separa critérios por tema e conserva contexto técnico, de segurança e de negócio.

## Resultados das métricas

As cinco métricas são calculadas por `src/evaluate.py` sobre os 15 exemplos do dataset. As credenciais são mantidas exclusivamente no arquivo `.env`, que não é versionado. A avaliação abaixo foi executada em 25/07/2026 com `gpt-4o-mini` para geração e `gpt-4o` como avaliador.

| Métrica | v1 (baseline do enunciado) | v2 (avaliação executada) | Mínimo exigido |
| --- | ---: | ---: | ---: |
| Helpfulness | 0,45 | **0,8813** | 0,80 |
| Correctness | 0,52 | **0,8411** | 0,80 |
| F1-Score | 0,48 | **0,8063** | 0,80 |
| Clarity | 0,50 | **0,8867** | 0,80 |
| Precision | 0,46 | **0,8760** | 0,80 |

A média do baseline v1 é **0,4820** e a média do v2 é **0,8583**. Os valores de v1 são os resultados de referência exibidos no enunciado para o prompt-base; os do v2 foram obtidos na avaliação descrita abaixo. Todas as métricas e a média geral do v2 ficaram acima de `0,80`, portanto o prompt foi aprovado. A aprovação requer **cada** métrica e a média geral maiores ou iguais a `0,80`.

## Evidência da avaliação no LangSmith

- **Prompt público:** [jairojunior/bug_to_user_story_v2](https://smith.langchain.com/prompts/jairojunior/bug_to_user_story_v2)
- **Projeto e traces:** [projeto `default` no LangSmith](https://smith.langchain.com/o/2bbbbc25-dced-4204-9206-52ac51967531/projects/p/f3c16d9e-fb12-42a0-9c29-f53ea917dd8c)
- **Dataset:** `prompt-optimization-challenge-resolved-eval` (15 relatos de bug)
- **Configuração executada:** `gpt-4o-mini` para geração e `gpt-4o` como LLM-as-a-Judge
- **Execuções registradas:** 90 runs bem-sucedidos — 15 gerações e três avaliações (F1, Clarity e Precision) para cada exemplo.

Os valores de Helpfulness e Correctness foram derivados, respectivamente, de `(Clarity + Precision) / 2` e `(F1 + Precision) / 2`, conforme `src/evaluate.py`. O link do projeto permite inspecionar os traces dos exemplos avaliados.

## Como executar

Pré-requisitos: Python 3.9+, uma chave do LangSmith e uma chave de OpenAI ou Google Gemini.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha no `.env` pelo menos `LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB`, a chave do provedor escolhido e as variáveis `LLM_PROVIDER`, `LLM_MODEL` e `EVAL_MODEL`.

```bash
# Opcional: baixar a versão base do Hub para prompts/bug_to_user_story_v1.yml
python src/pull_prompts.py

# Validar o contrato do prompt v2
pytest -q tests/test_prompts.py

# Publicar publicamente <USERNAME_LANGSMITH_HUB>/bug_to_user_story_v2
python src/push_prompts.py

# Criar/carregar o dataset e calcular as cinco métricas
python src/evaluate.py
```

## Estrutura da entrega

| Arquivo | Responsabilidade |
| --- | --- |
| `prompts/bug_to_user_story_v2.yml` | Prompt v2, exemplos e metadados das técnicas. |
| `src/pull_prompts.py` | Baixa `leonanluppi/bug_to_user_story_v1` e salva o YAML local. |
| `src/push_prompts.py` | Valida e publica o v2 como prompt público versionado. |
| `tests/test_prompts.py` | Seis validações: system prompt, persona, formato, few-shot, ausência de `[TODO]` e técnicas. |
| `src/evaluate.py` | Avalia Helpfulness, Correctness, F1-Score, Clarity e Precision. |
