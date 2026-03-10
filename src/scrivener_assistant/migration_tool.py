import logging
import argparse
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate Scrivener AI Assistant data to hierarchical structure.")
    parser.add_argument("project", help="Path to the .scriv project")
    args = parser.parse_args()
    
    migrate_project(args.project)
