# Everyday Tools
A few Python scripts I wrote to deal with media files, mostly MKV videos and subtitles.
They are not really a single application. Each script does one specific job, and most of them can be used on their own.

The scripts cover things like:
- finding duplicate files;
- creating file inventories;
- checking and extracting subtitles from MKV files;
- translating Korean subtitles into Italian;
- fixing and validating SRT files.

## Scripts
### 01 - Find duplicate files
'01_tools_find_duplicate_files.py'
Looks for files with the same name inside a directory tree and creates an Excel report with the locations where they were found.
Uses 'xlsxwriter'.

### 02 - File map
'02_tools_file_map.py'
Creates an inventory of the files in a directory, including their paths, sizes and timestamps.
The result is saved as an Excel file.
Uses 'openpyxl'.

### 03 - MKV subtitle manager
'03_mkv-subtitle-manager.py'
Checks MKV files for subtitle tracks and uses the information found to rename files and folders.
It can also match SRT files with their corresponding MKV files and create Excel reports with the subtitle information.
The script uses:
- MKVToolNix ('mkvinfo.exe')
- 'pandas'
- 'xlsxwriter'

### 04 - MKV subtitle extractor
'04_mkv-subtitle-extractor.py'
Extracts subtitle tracks from MKV files and saves them as separate '.srt' files.

The extracted subtitles are put into a 'sottotitoli' subfolder. The original
MKV files are left untouched.

Requires MKVToolNix ('mkvmerge.exe' and 'mkvextract.exe').

### 05 - SRT translator
'05_srt_translator.py'
Translates Korean SRT subtitles into Italian using Facebook's M2M100 model.
The script processes subtitles in batches and saves the results progressively, so a long translation job does not necessarily have to start over from the beginning if something goes wrong.
CUDA is supported and recommended if you have a suitable GPU. CPU processing is also possible, but considerably slower.
Python dependencies:
- 'transformers'
- 'torch'
- 'huggingface_hub'
- 'sentencepiece'
- 'protobuf'
- 'python-dotenv'
The model may require a Hugging Face token. You can alternatevely add it as an environment variable:
    HUGGINGFACE_TOKEN=your_token_here

### 06 - SRT fixer and validator
'06_srt_fixer_validator.py'
Checks SRT files and fixes some common formatting problems.
It currently handles things such as:
- removing the Korean '개' suffix from subtitle numbers ('1 개' -> '1');
- checking subtitle numbering;
- checking timestamps;
- checking UTF-8 encoding.
There is also an optional mode for embedding subtitles back into MKV files using MKVToolNix.
The basic script only uses the Python standard library.

## Installation
Clone the repository and install the Python dependencies:
    git clone https://github.com/eroggero/everyday_tools.git
    cd everyday_tools
    pip install -r requirements.txt
Some scripts also require MKVToolNix. On Windows, the default installation directory is usually: C:\Program Files\MKVToolNix\

## Usage
The scripts are run individually. In most cases, the directory to process is configured directly in the script.
For example:
    python scripts/01_tools_find_duplicate_files.py
or:
    python scripts/05_srt_translator.py
The exact options and paths depend on the script being used.

## Requirements
Python packages:
    xlsxwriter
    openpyxl
    pandas
    transformers
    torch
    huggingface_hub
    sentencepiece
    protobuf
    python-dotenv

MKVToolNix is needed for the scripts that inspect, extract, or embed MKV subtitle tracks.

## Notes
- The M2M100 model is downloaded the first time the translator is run and can take up around 1.5 GB of disk space.
- Some scripts rename files and folders. Check the paths before running them.
- A CUDA-compatible GPU makes a big difference when translating large numbers of subtitles.
  
