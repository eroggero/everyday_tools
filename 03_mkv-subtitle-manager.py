"""
MKV SUBTITLE MANAGER
====================
This script processes MKV video files and their associated subtitle files in a directory structure,
extracting subtitle language information, renaming files and folders, and generating Excel reports.

Features:
- Extracts subtitle languages from MKV files using MKVToolNix (mkvinfo.exe)
- Processes files in batch mode for improved performance
- Renames MKV files to a standardized format (extracts SxxExx pattern)
- Matches subtitle (.srt) files with corresponding MKV files
- Automatically renames folders based on subtitle languages:
  - Prefixes with "it_" if Italian subtitles are found
  - Prefixes with "en_" if English subtitles are found
- Generates individual Excel reports for each folder containing:
  - Folder path
  - Original filename
  - Modified filename (standardized)
  - Subtitle languages available
- Creates a combined master Excel report with all folders

Required libraries:
- os (standard library)
- subprocess (standard library)
- re (standard library)
- pandas (install with: pip install pandas)
- xlsxwriter (install with: pip install xlsxwriter) - required for Excel export

External dependencies:
- MKVToolNix (must be installed at: C:\Program Files\MKVToolNix\mkvinfo.exe)

Usage:
- Modify the root_directory variable with the path to scan
- Run the script to process all MKV files and generate reports

Note:
- The script renames files and folders automatically - use with caution
- Requires MKVToolNix to be installed for subtitle extraction
- Designed for MKV files with naming pattern containing SxxExx (Season/Episode)
"""

import os
import subprocess
import pandas as pd
import re

def extract_subtitle_languages_batch(folder, mkv_files):
    """Extract subtitle languages for all MKV files in a folder in one batch."""
    subtitle_languages = {}
    try:
        mkv_paths = [os.path.join(folder, file) for file in mkv_files]
        file_args = ' '.join(f'"{path}"' for path in mkv_paths)
        result = subprocess.run(
            [r"C:\Program Files\MKVToolNix\mkvinfo.exe", file_args],
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8'
        )
        output = result.stdout

        current_file = None
        for line in output.splitlines():
            if line.startswith("File name:"):
                current_file = os.path.basename(line.split(":", 1)[1].strip())
                subtitle_languages[current_file] = []
            elif "Lingua:" in line or "IETF BCP 47" in line:
                lang = re.search(r"(ita|eng|iti|ENG|ITA)", line, re.IGNORECASE)
                if lang and current_file:
                    subtitle_languages[current_file].append(lang.group().lower())

        for file in subtitle_languages:
            subtitle_languages[file] = ', '.join(sorted(set(subtitle_languages[file])))
        return subtitle_languages

    except Exception as e:
        print(f"Error extracting subtitle languages in batch: {e}")
        return {file: "" for file in mkv_files}

def modify_filename(file_name):
    file_name = re.sub(r'^\[MkvDrama\.Org\]', '', file_name)
    file_name = re.sub(r'\[MkvDrama\.Org\]', '', file_name)
    match = re.search(r"S\d{2}E\d{2}", file_name)
    if match:
        return file_name[:match.end()]
    return None

def adjust_column_widths(writer, df, sheet_name):
    worksheet = writer.sheets[sheet_name]
    for i, col in enumerate(df.columns):
        max_len = df[col].astype(str).apply(len).max()
        max_len = max(max_len, len(col))
        worksheet.set_column(i, i, max_len + 2)

def compare_and_rename_subtitles(foldername, mkv_files):
    srt_files = [f for f in os.listdir(foldername) if f.lower().endswith('.srt')]
    for srt_file in srt_files:
        base_name_srt = modify_filename(srt_file)
        for mkv_file in mkv_files:
            base_name_mkv = modify_filename(mkv_file)
            if base_name_srt and base_name_mkv and base_name_srt == base_name_mkv:
                print(f"Matching subtitle file {srt_file} with {mkv_file}")
                break
        else:
            print(f"Warning: No matching MKV file found for subtitle file {srt_file}")

def generate_subtitle_report(root_dir, final_report_path):
    all_excel_data = []
    folder_list = []

    for foldername, _, filenames in os.walk(root_dir):
        if foldername == root_dir:
            continue

        mkv_files = [f for f in filenames if f.lower().endswith(".mkv")]
        if mkv_files:
            folder_data = []
            subtitle_data = extract_subtitle_languages_batch(foldername, mkv_files)

            for filename in mkv_files:
                subtitles = subtitle_data.get(filename, "None")
                modified_name = modify_filename(filename)

                if modified_name:
                    new_file_path = os.path.join(foldername, modified_name + os.path.splitext(filename)[1])
                    os.rename(os.path.join(foldername, filename), new_file_path)
                    print(f"Renamed file {filename} to {modified_name + os.path.splitext(filename)[1]}")

                folder_data.append({
                    "Folder": foldername,
                    "File Name": filename,
                    "Modified Name": modified_name if modified_name else "No renaming possible",
                    "Subtitles": subtitles
                })

            df = pd.DataFrame(folder_data, columns=["Folder", "File Name", "Modified Name", "Subtitles"])
            for index, row in df.iterrows():
                if not row["Subtitles"]:
                    df.at[index, "Subtitles"] = "None"

            sheet_name = re.sub(r'[\\/*?:"<>|]', "_", os.path.basename(foldername)[:31])
            individual_report_path = os.path.join(root_dir, f"{sheet_name}_report.xlsx")
            df.to_excel(individual_report_path, index=False)
            print(f"Generated individual report for folder {foldername} at {individual_report_path}")

            all_excel_data.append((sheet_name, df))
            compare_and_rename_subtitles(foldername, mkv_files)

            subtitle_values = ', '.join(df["Subtitles"]).lower().split(', ')
            subtitle_values = sorted(set(subtitle_values))

            if "iti" in subtitle_values and not os.path.basename(foldername).lower().startswith("it_"):
                new_folder_name = "it_" + os.path.basename(foldername)
                os.rename(foldername, os.path.join(os.path.dirname(foldername), new_folder_name))
                print(f"Renamed folder {foldername} to {new_folder_name}")
            elif "eng" in subtitle_values and not os.path.basename(foldername).lower().startswith("en_"):
                new_folder_name = "en_" + os.path.basename(foldername)
                os.rename(foldername, os.path.join(os.path.dirname(foldername), new_folder_name))
                print(f"Renamed folder {foldername} to {new_folder_name}")

        folder_list.append(os.path.basename(foldername))

    with pd.ExcelWriter(final_report_path, engine='xlsxwriter') as writer:
        pd.DataFrame(folder_list, columns=["Folders"]).to_excel(writer, sheet_name="Folders List", index=False)
        for sheet_name, df in all_excel_data:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            adjust_column_widths(writer, df, sheet_name)

        print(f"Combined report saved to {final_report_path}")

# Example usage
root_directory = r"C:\path"
final_report_path = os.path.join(root_directory, "_ALL_report_da_vedere.xlsx")

generate_subtitle_report(root_directory, final_report_path)
