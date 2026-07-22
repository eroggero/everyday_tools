"""
SRT SUBTITLE FIXER & VALIDATOR
==============================
ER 23.05.2025

This script processes SRT subtitle files to fix formatting issues and validate their structure.

Features:
- Removes Korean " 개" suffix from subtitle block numbers (e.g., "1 개" → "1")
- Validates SRT file structure:
  - Checks subtitle numbering format
  - Verifies timestamp format (-->)
  - Validates UTF-8 encoding
- Batch processes all .srt files in a directory
- Includes commented function to embed subtitles into MKV files using mkvmerge

Required libraries:
- os (standard library)
- subprocess (standard library)
- sys (standard library)
- pathlib (standard library)

External dependencies (optional - for embedding only):
- MKVToolNix (mkvmerge.exe)

Usage:
- Modify the base_dir variable with the path containing MKV files and a "sottotitoli" subfolder
- Run the script to fix and validate all SRT files

Note:
- The embedding function (embed_subtitles) is commented out - uncomment to use
- Requires MKVToolNix for embedding subtitles into MKV files
- Original SRT files are overwritten when fixing
- The validation function checks but does not modify files
"""
import subprocess
import sys
from pathlib import Path
import sys
from pathlib import Path

import os
from pathlib import Path

def fix_srt_numbers(srt_path):
    """Remove ' 개' from the first line of each subtitle block."""
    try:
        with open(srt_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()

        modified = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            # Check if line is a subtitle number (e.g., "1 개" or "2 개")
            if stripped.endswith(" 개") and stripped[:-2].isdigit():
                new_line = stripped[:-2] + "\n"  # Remove " 개"
                new_lines.append(new_line)
                modified = True
            else:
                new_lines.append(line)

        if modified:
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Fixed: {srt_path.name}")
        else:
            print(f"No changes needed: {srt_path.name}")

    except Exception as e:
        print(f"Error processing {srt_path.name}: {str(e)}")

def process_all_srts():
    # ==== CONFIGURE YOUR PATH ====
    base_dir = Path(r"C:\user\path")
    sub_dir = base_dir / "sottotitoli"
    # =============================

    if not sub_dir.exists():
        print(f"Error: Directory '{sub_dir}' not found!")
        return

    print(f"Processing SRT files in: {sub_dir}\n")
    for srt_file in sub_dir.glob("*.srt"):
        fix_srt_numbers(srt_file)



def validate_srt(srt_path):
    """Check if an SRT file is valid."""
    try:
        with open(srt_path, 'r', encoding='utf-8-sig') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

            # Basic SRT structure check
            if len(lines) < 2:
                return False, "File too short (needs at least 1 subtitle block)"

            # Check first subtitle block format
            if not lines[0].isdigit():  # Subtitle number
                return False, "First line must be a subtitle number"

            if "-->" not in lines[1]:  # Timestamps
                return False, "Second line must contain timestamps (e.g., '00:00:01,000 --> 00:00:02,000')"

            return True, "Valid SRT"

    except UnicodeDecodeError:
        return False, "Invalid encoding (use UTF-8)"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def test_srt_files():
    # ==== CONFIGURE YOUR PATH ====
    base_dir = Path(r"C:\user\path")
    sub_dir = base_dir / "sottotitoli"
    # =============================

    if not sub_dir.exists():
        print(f"Error: Directory '{sub_dir}' not found!")
        sys.exit(1)

    print(f"Checking SRT files in: {sub_dir}\n")

    for srt_file in sub_dir.glob("*.srt"):
        is_valid, reason = validate_srt(srt_file)
        status = "PASS" if is_valid else f"❌ FAIL ({reason})"
        print(f"{status} - {srt_file.name}")

if __name__ == "__main__":
    process_all_srts()
    test_srt_files()


'''
def embed_subtitles():
    # Check if MKVToolNix is installed
    try:
        subprocess.run(["mkvmerge", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: mkvmerge not found. Install MKVToolNix first.")
        print("Download from https://mkvtoolnix.download/")
        sys.exit(1)

    # ==== SET YOUR CUSTOM PATH HERE ====
    base_dir = Path(r"C:\user\path")  
    # Example: Path(r"C:\Videos\Movies")
    # ===================================

    sub_dir = base_dir / "sottotitoli"

    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' does not exist!")
        sys.exit(1)

    if not sub_dir.exists():
        print(f"Subtitle directory '{sub_dir}' not found!")
        sys.exit(1)

    # Process MKV files
    for mkv_file in base_dir.glob("*.mkv"):
        srt_file = sub_dir / f"{mkv_file.stem}.srt"

        if not srt_file.exists():
            print(f"No subtitle found for {mkv_file.name}, skipping...")
            continue

        print(f"Processing: {mkv_file.name}")

        # Create temp output file
        temp_output = mkv_file.with_name(f"{mkv_file.stem}_temp.mkv")

        try:
            # Build mkvmerge command
            cmd = [
                "mkvmerge",
                "-o", str(temp_output),
                str(mkv_file),
                "--language", "0:ita",  # Change "ita" to your subtitle language (e.g., "eng")
                "--default-track", "0:yes",
                str(srt_file)
            ]

            subprocess.run(cmd, check=True)

            # Replace original file with new version
            mkv_file.unlink()
            temp_output.rename(mkv_file)
            print(f"Successfully embedded subtitles into {mkv_file.name}\n")

        except subprocess.CalledProcessError as e:
            print(f"Error processing {mkv_file.name}: {str(e)}")
            if temp_output.exists():
                temp_output.unlink()

if __name__ == "__main__":
    embed_subtitles()

'''