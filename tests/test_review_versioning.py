import pytest
import shutil
import time
from pathlib import Path
from server import save_review, get_review_history, get_previous_review, get_archived_review, set_project_path, get_review

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"

@pytest.fixture
def temp_project_versioning(tmp_path):
    """
    Sets up the server with a temporary project copy for versioning tests.
    """
    dest = tmp_path / "temp_versioning.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)
    
    # Initialize server with this path
    set_project_path(str(dest))
    return dest

def test_review_archiving(temp_project_versioning):
    uuid = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    
    # 1. Save Initial Review
    content_v1 = "# Review V1\nInitial feedback."
    save_review(uuid, content_v1)
    
    # Wait a second to ensure timestamp difference (filesystems can be fast)
    time.sleep(1.1)
    
    # 2. Save Second Review (should archive V1)
    content_v2 = "# Review V2\nUpdated feedback."
    save_review(uuid, content_v2)
    
    # 3. Verify Current Review is V2
    current = get_review(uuid)
    assert "Review V2" in current
    
    # 4. Verify History
    history_json = get_review_history(uuid)
    assert "timestamp" in history_json
    
    # 5. Get Previous Review (should be V1)
    prev = get_previous_review(uuid)
    assert "Review V1" in prev

def test_get_specific_archive(temp_project_versioning):
    uuid = "87D59B4E-F1D6-4025-9FBA-33F60ED8F985"
    content_v1 = "Version 1"
    save_review(uuid, content_v1)
    time.sleep(1.1)
    
    content_v2 = "Version 2"
    save_review(uuid, content_v2)
    
    # Get history to find the timestamp
    import json
    history = json.loads(get_review_history(uuid))
    assert len(history) == 1
    timestamp = history[0]['timestamp']
    
    # Fetch specific version
    archived_content = get_archived_review(uuid, timestamp)
    assert content_v1 == archived_content
