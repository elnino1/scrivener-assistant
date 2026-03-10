import pytest
import shutil
from pathlib import Path
import server
from server import prepare_chapter_analysis, save_summary, save_review, update_metadata, set_project_path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_batch(tmp_path):
    """
    Sets up the server with a temporary project copy.
    """
    dest = tmp_path / "temp_batch.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_prepare_chapter_analysis(temp_project_batch):
    """Test that prepare_chapter_analysis returns content and workflow."""
    # UUID for "Chapter"
    uuid = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    
    result = prepare_chapter_analysis(uuid)
    
    # Verify structure
    assert "CHAPTER ANALYSIS PREPARED" in result
    assert "Document UUID" in result
    assert uuid in result
    assert "Chapter Content" in result
    assert "ANALYSIS WORKFLOW" in result
    
    # Verify workflow instructions
    assert "save_summary" in result
    assert "update_metadata" in result
    assert "save_review" in result

def test_batch_workflow_execution(temp_project_batch):
    """Test executing full batch workflow: summary + metadata + review."""
    uuid = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    
    # Step 1: Prepare analysis (gets content once)
    result = prepare_chapter_analysis(uuid)
    assert "CHAPTER ANALYSIS PREPARED" in result
    
    # Step 2: Simulate AI performing batch tasks
    
    # Task 1: Save summary
    summary_res = save_summary(uuid, "This chapter introduces the protagonist.")
    assert "Saved summary" in summary_res
    
    # Task 2: Update metadata
    metadata_res = update_metadata(uuid, "POV", "First Person")
    assert "Successfully updated" in metadata_res
    
    # Task 3: Save review
    review_res = save_review(uuid, """## Strengths
- Strong opening
## Weaknesses  
- Pacing issues
""")
    assert "Saved style review" in review_res
    
    # Verify all outputs exist
    short_uuid = uuid.split('-')[0]
    summary_files = list((temp_project_batch / ".ai-assistant" / "summaries").rglob(f"*{short_uuid}*.md"))
    review_files = list((temp_project_batch / ".ai-assistant" / "reviews").rglob(f"*{short_uuid}*.md"))
    
    assert len(summary_files) > 0, "Summary file should exist"
    assert len(review_files) > 0, "Review file should exist"

def test_prepare_analysis_no_project():
    """Test error handling when no project loaded."""
    # Reset global state
    import server
    server.current_project = None
    
    result = prepare_chapter_analysis("some-uuid")
    assert "No project loaded" in result
