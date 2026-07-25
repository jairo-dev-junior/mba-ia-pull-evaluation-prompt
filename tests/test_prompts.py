"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        if isinstance(data, dict):
            for key in ["bug_to_user_story_v2", "bug_to_user_story_v1"]:
                if key in data:
                    return data[key]
        return data


class TestPrompts:
    @pytest.fixture
    def prompt_v2(self):
        """Fixture para carregar o prompt v2 otimizado."""
        v2_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        assert v2_path.exists(), f"Arquivo não encontrado: {v2_path}"
        return load_prompts(str(v2_path))

    def test_prompt_has_system_prompt(self, prompt_v2):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_v2, "Campo 'system_prompt' não encontrado"
        system_prompt = prompt_v2["system_prompt"]
        assert system_prompt and len(system_prompt.strip()) > 0, "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_v2):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_v2.get("system_prompt", "")
        role_keywords = ["você é", "product manager", "agilista", "persona", "assistente"]
        has_role = any(keyword in system_prompt.lower() for keyword in role_keywords)
        assert has_role, "system_prompt não contém uma definição clara de persona/role"

    def test_prompt_mentions_format(self, prompt_v2):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2.get("system_prompt", "")
        format_keywords = ["como um", "eu quero", "para que", "critérios de aceitação", "user story", "bdd"]
        has_format = any(keyword in system_prompt.lower() for keyword in format_keywords)
        assert has_format, "system_prompt não menciona o formato exigido para a User Story"

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2.get("system_prompt", "")
        few_shot_keywords = ["exemplo", "few-shot", "entrada", "saída", "relato de bug"]
        has_few_shot = any(keyword in system_prompt.lower() for keyword in few_shot_keywords)
        assert has_few_shot, "system_prompt não contém exemplos de poucos disparos (Few-shot)"

    def test_prompt_no_todos(self, prompt_v2):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_v2.get("system_prompt", "")
        assert "[todo]" not in system_prompt.lower(), "system_prompt contém marcadores [TODO]"

    def test_minimum_techniques(self, prompt_v2):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2.get("techniques_applied", [])
        assert isinstance(techniques, list), "metadata 'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, f"Esperado ao menos 2 técnicas aplicadas, encontrado: {len(techniques)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
