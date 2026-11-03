"""
Tests for resolving a parent folder to the .scriv bundle it contains.
"""
import shutil
from pathlib import Path

import pytest

from scrivener_assistant import ScrivenerProject

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_SCRIV = FIXTURES_DIR / "sample.scriv"


def test_parent_folder_with_single_scriv_is_resolved(tmp_path):
    shutil.copytree(SAMPLE_SCRIV, tmp_path / "Novel.scriv")

    project = ScrivenerProject(str(tmp_path))

    assert project.path == (tmp_path / "Novel.scriv").resolve()


def test_direct_scriv_path_still_works(tmp_path):
    dest = tmp_path / "Novel.scriv"
    shutil.copytree(SAMPLE_SCRIV, dest)

    project = ScrivenerProject(str(dest))

    assert project.path == dest.resolve()


def test_parent_folder_with_multiple_scriv_is_rejected(tmp_path):
    shutil.copytree(SAMPLE_SCRIV, tmp_path / "A.scriv")
    shutil.copytree(SAMPLE_SCRIV, tmp_path / "B.scriv")

    with pytest.raises(ValueError, match="Multiple .scriv projects"):
        ScrivenerProject(str(tmp_path))


def test_parent_folder_without_scriv_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="must end with .scriv"):
        ScrivenerProject(str(tmp_path))
