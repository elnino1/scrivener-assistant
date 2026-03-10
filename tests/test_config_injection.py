"""
Test demonstrating dependency injection with custom configuration.
"""
import pytest
from pathlib import Path
import shutil
from scrivener_assistant import ScrivenerProject
from scrivener_assistant.config import ProjectConfig

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"


def test_custom_config_injection(tmp_path):
    """Test that custom config is properly injected into managers."""
    # Create custom config with different folder names
    custom_config = ProjectConfig(
        assistant_folder=".custom-assistant",
        prompts_subfolder="my-prompts",
        summaries_subfolder="my-summaries",
        max_backups=3
    )
    
    # Copy project
    dest = tmp_path / "custom_config.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Create project with custom config
    project = ScrivenerProject(str(dest), config=custom_config)
    
    # Verify config is injected
    assert project.config.assistant_folder == ".custom-assistant"
    assert project.config.max_backups == 3
    
    # Verify managers use custom config
    assert ".custom-assistant" in str(project.prompt_manager.prompts_dir)
    assert "my-prompts" in str(project.prompt_manager.prompts_dir)
    assert "my-summaries" in str(project.summary_manager.base_dir)
    
    # Test that the config actually works
    project.save_prompt("test_prompt", "Custom config test")
    
    # Verify file was created in custom location
    expected_path = dest / ".custom-assistant" / "my-prompts" / "test_prompt.md"
    assert expected_path.exists()
    assert expected_path.read_text() == "Custom config test"


def test_default_config_backward_compatibility(tmp_path):
    """Test that default config maintains backward compatibility."""
    dest = tmp_path / "default_config.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Create project without config (should use defaults)
    project = ScrivenerProject(str(dest))
    
    # Verify default config is used
    assert project.config.assistant_folder == ".ai-assistant"
    assert project.config.prompts_subfolder == "prompts"
    assert project.config.summaries_subfolder == "summaries"
    assert project.config.max_backups == 5
    
    # Verify backward compatibility with existing tests
    project.save_prompt("backward_compat", "Test content")
    expected_path = dest / ".ai-assistant" / "prompts" / "backward_compat.md"
    assert expected_path.exists()
