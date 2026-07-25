"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt leonanluppi/bug_to_user_story_v1 e salva em prompts/bug_to_user_story_v1.yml
    """
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    prompt_handle = "leonanluppi/bug_to_user_story_v1"
    output_path = PROJECT_ROOT / "prompts" / "bug_to_user_story_v1.yml"

    try:
        print(f"Puxando prompt: {prompt_handle}...")
        client = Client()
        try:
            prompt_obj = client.pull_prompt(prompt_handle, dangerously_pull_public_prompt=True)
        except Exception:
            try:
                from langchain import hub
                prompt_obj = hub.pull(prompt_handle)
            except Exception:
                from langchain_classic import hub
                prompt_obj = hub.pull(prompt_handle)

        system_prompt = ""
        user_prompt = "{bug_report}"

        if hasattr(prompt_obj, "messages"):
            for msg in prompt_obj.messages:
                msg_type = str(getattr(msg, "role", getattr(msg, "__class__", "").__name__))
                prompt_inner = getattr(msg, "prompt", None)
                template_text = getattr(prompt_inner, "template", str(msg))
                if "System" in msg_type or "system" in msg_type:
                    system_prompt = template_text
                elif "Human" in msg_type or "user" in msg_type or "human" in msg_type:
                    user_prompt = template_text

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"]
            }
        }

        if not save_yaml(prompt_data, str(output_path)):
            return False
        print(f"✓ Prompt salvo com sucesso em: {output_path}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
