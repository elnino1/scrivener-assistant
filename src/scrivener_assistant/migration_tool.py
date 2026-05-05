import logging
import argparse
import shutil
from pathlib import Path
from typing import Optional
from scrivener_assistant.project import ScrivenerProject
from scrivener_assistant.config import ProjectConfig

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def migrate_project(project_path: str):
    """
    Migrates existing .ai-assistant/summaries and reviews to hierarchical structure.
    """
    try:
        project = ScrivenerProject(project_path)
        config = project.config
        
        # We'll use the managers' own logic to migrate.
        # Since SummaryManager/ReviewManager inherit from BaseSceneDataManager,
        # calling save_data with existing content will move the file.
        
        managers = [
            ("Summaries", project.summary_manager),
            ("Reviews", project.review_manager)
        ]
        
        for name, manager in managers:
            logger.info(f"Checking {name} for migration...")
            if not manager.base_dir.exists():
                logger.info(f"No {name} directory found. Skipping.")
                continue
                
            # Scan for flat UUID files: {UUID}.md
            # We iterate through all .md files in the base directory (non-recursive first to avoid re-processing)
            # Actually, BaseSceneDataManager._find_existing_file can find them anywhere.
            
            # Let's get all UUIDs from the binder to see what we SHOULD have
            all_uuids = list(project.binder_map.keys())
            
            migrated_count = 0
            for uuid in all_uuids:
                # Check if we have data for this UUID
                content = manager.get_data(uuid)
                if content:
                    # save_data handles moving if it's in the wrong spot
                    target_path = manager.save_data(uuid, content)
                    logger.info(f"Migrated {uuid} -> {target_path.relative_to(project.path)}")
                    migrated_count += 1
            
            # Post-migration cleanup of orphans
            # Files that exist but aren't in the binder anymore? 
            # For now we leave them alone but log their presence.
            
            logger.info(f"Migration for {name} complete. {migrated_count} files processed.")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()

def migrate_characters_locations(project_path: Path, config: ProjectConfig) -> None:
    """
    Moves .ai-assistant/characters/ and .ai-assistant/locations/ into
    .ai-assistant/world/characters/ and .ai-assistant/world/locations/.
    Idempotent: safe to call if already migrated or if folders don't exist.
    """
    assistant_dir = project_path / config.assistant_folder

    for old_name, new_rel in [("characters", config.characters_subfolder),
                               ("locations", config.locations_subfolder)]:
        old_path = assistant_dir / old_name
        new_path = assistant_dir / new_rel

        if not old_path.exists() or old_path == new_path:
            continue

        new_path.parent.mkdir(parents=True, exist_ok=True)

        if new_path.exists():
            # Merge: move individual files that don't already exist at destination
            for src_file in old_path.rglob("*"):
                if src_file.is_file():
                    rel = src_file.relative_to(old_path)
                    dst_file = new_path / rel
                    if not dst_file.exists():
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src_file), str(dst_file))
                        logger.info(f"Moved {src_file.name} -> {dst_file.relative_to(project_path)}")
            # Remove old dir if now empty
            if not any(old_path.rglob("*")):
                old_path.rmdir()
        else:
            shutil.move(str(old_path), str(new_path))
            logger.info(f"Moved {old_name}/ -> {new_rel}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Scrivener AI Assistant data to hierarchical structure.")
    parser.add_argument("project", help="Path to the .scriv project")
    args = parser.parse_args()
    
    migrate_project(args.project)
