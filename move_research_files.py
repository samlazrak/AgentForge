#!/usr/bin/env python3
"""
Script to move all files that start with "research_" into a research folder.
This script will:
1. Create a 'research' directory if it doesn't exist
2. Find all files in the current directory that start with "research_"
3. Move them into the research folder
4. Handle conflicts by appending a number if files already exist
"""

import os
import shutil
import glob
from pathlib import Path

def move_research_files():
    """Move all files starting with 'research_' to the research folder."""
    
    # Get current directory
    current_dir = Path.cwd()
    research_dir = current_dir / "research"
    
    # Create research directory if it doesn't exist
    research_dir.mkdir(exist_ok=True)
    print(f"✓ Research directory ready: {research_dir}")
    
    # Find all files starting with "research_"
    research_files = list(current_dir.glob("research_*"))
    
    if not research_files:
        print("ℹ️  No files starting with 'research_' found in current directory.")
        return
    
    print(f"📁 Found {len(research_files)} files to move:")
    
    moved_count = 0
    skipped_count = 0
    
    for file_path in research_files:
        # Skip if it's a directory
        if file_path.is_dir():
            print(f"⏭️  Skipping directory: {file_path.name}")
            skipped_count += 1
            continue
        
        # Determine destination path
        dest_path = research_dir / file_path.name
        
        # Handle name conflicts
        if dest_path.exists():
            # Find a unique name by appending a number
            base_name = file_path.stem
            suffix = file_path.suffix
            counter = 1
            
            while dest_path.exists():
                new_name = f"{base_name}_{counter}{suffix}"
                dest_path = research_dir / new_name
                counter += 1
            
            print(f"⚠️  File exists, renaming to: {dest_path.name}")
        
        try:
            # Move the file
            shutil.move(str(file_path), str(dest_path))
            print(f"✅ Moved: {file_path.name} → research/{dest_path.name}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Error moving {file_path.name}: {e}")
            skipped_count += 1
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Files moved: {moved_count}")
    print(f"   Files skipped: {skipped_count}")
    print(f"   Total files processed: {moved_count + skipped_count}")
    
    if moved_count > 0:
        print(f"\n✨ Successfully moved {moved_count} files to the research directory!")
    
def main():
    """Main function."""
    print("🔄 Moving research files...")
    print("=" * 50)
    
    try:
        move_research_files()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 