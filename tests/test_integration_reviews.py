import pytest
import shutil
from pathlib import Path
import server
from server import save_review, get_review, set_project_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_reviews(tmp_path):
    """
    Sets up the server with a temporary project copy.
    """
    dest = tmp_path / "temp_reviews.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_review_workflow(temp_project_reviews):
    # UUID for "Chapter"
    uuid = "FD75AC3C-F304-4EA6-ADCC-2C32D6589969"
    
    review_content = """# Style Review

## Strengths
- Strong character voice
- Engaging opening hook
- Good pacing in dialogue

## Weaknesses
- Too much telling, not enough showing
- Overuse of adverbs

## Suggestions
- Replace "walked slowly" with "shuffled"
- Add sensory details to the opening scene
"""
    
    # 1. Save
    res_save = save_review(uuid, review_content)
    assert "Saved style review" in res_save
    
    # Verify file exists on disk
    safe_name = uuid
    review_file = temp_project_reviews / ".ai-assistant" / "reviews" / f"{safe_name}.md"
    assert review_file.exists()
    assert "Strengths" in review_file.read_text()
    assert "Weaknesses" in review_file.read_text()
    
    # 2. Get
    res_get = get_review(uuid)
    assert "Strengths" in res_get
    assert "Weaknesses" in res_get
    assert "Suggestions" in res_get
    
def test_get_review_not_found(temp_project_reviews):
    res = get_review("non_existent_uuid")
    assert "not found" in res
