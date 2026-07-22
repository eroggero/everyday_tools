# everyday_tools
everyday tools for duplicate files, mkv with sub and srt translation (iti-kok)
This is a collection of small Python scripts I use to organize and work with media files, mainly MKV videos and subtitles.
The scripts are numbered roughly in the order in which I use them, although they can also be run independently depending on what you need to do.
### 01 — Find duplicate files
`01_tools_find_duplicate_files.py`
Searches a directory tree for files with the same name and generates an Excel report showing where the duplicates were found.
Uses `xlsxwriter`.

---
### 02 — File map
`02_tools_file_map.py`
Creates an inventory of the files in a directory, including their paths, sizes, and timestamps.
The result is saved as an Excel file.
Uses `openpyxl`.

---
### 03 — MKV subtitle manager
`03_mkv-subtitle-manager.py`
Checks MKV files for available subtitle tracks and uses that information to rename files and folders.
It also generates Excel reports with information about the subtitles found.
Requires:
- MKVToolNix
- `pandas`

---
### 04 — MKV subtitle extractor
`04_mkv-subtitle-extractor.py`
Extracts subtitle tracks from MKV files and saves them as separate `.srt` files.
The extracted subtitles are placed in a `sottotitoli` subfolder. The original MKV files are not modified.
Requires MKVToolNix.

---
### 05 — SRT translator
`05_srt_translator.py`
Translates subtitle files using Facebook's M2M100 multilingual translation model.
Translated files are saved in a `tradotti` subfolder.
A GPU is recommended for better performance.
The script uses the following Python packages:
- `transformers`
- `torch`
If you use a Hugging Face model that requires authentication, set your token as an environment variable:
```bash
HUGGINGFACE_TOKEN=your_token_here
```

---
### 06 — SRT fixer and validator
`06_srt_fixer_validator.py`
Checks and fixes common problems in SRT subtitle files.
Among other things, it can:
- fix subtitle numbering issues;
- remove the Korean `개` suffix from subtitle numbers;
- check timestamps;
- validate the subtitle structure and encoding;
- optionally embed subtitles back into MKV files.

This script only uses the Python standard library.

## Installation
Install the dependencies with:
```bash
pip install -r requirements.txt
```

Some scripts also require external software, such as MKVToolNix.
