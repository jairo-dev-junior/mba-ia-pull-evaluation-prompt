"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: username/bug_to_user_story_v2)
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print(f"❌ Erros de validação no prompt '{prompt_name}':")
        for err in errors:
            print(f"   - {err}")
        return False

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")
    description = prompt_data.get("description", "")
    tags = list(prompt_data.get("tags", []))
    techniques = prompt_data.get("techniques_applied", [])

    for t in techniques:
        if t not in tags:
            tags.append(t)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt)
    ])

    try:
        print(f"Enviando prompt '{prompt_name}' ao LangSmith Hub...")
        client = Client()
        url = client.push_prompt(
            prompt_name,
            object=prompt_template,
            is_public=True,
            description=description,
            tags=tags
        )
        print(f"✓ Push realizado com sucesso!")
        print(f"  Visualizar em: https://smith.langchain.com/prompts/{prompt_name}")
        return True
    except Exception as e:
        try:
            try:
                from langchain import hub
            except ImportError:
                from langchain_classic import hub
            hub.push(prompt_name, prompt_template, new_repo_is_public=True)
            print(f"✓ Push realizado com sucesso via hub.push!")
            return True
        except Exception as ex:
            print(f"❌ Erro ao fazer push do prompt '{prompt_name}': {e} | {ex}")
            return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    yaml_path = PROJECT_ROOT / "prompts" / "bug_to_user_story_v2.yml"

    data = load_yaml(str(yaml_path))
    if not data:
        print(f"❌ Não foi possível carregar o arquivo {yaml_path}")
        return 1

    if "bug_to_user_story_v2" in data:
        prompt_data = data["bug_to_user_story_v2"]
    else:
        prompt_data = data

    prompt_name = f"{username}/bug_to_user_story_v2"

    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
