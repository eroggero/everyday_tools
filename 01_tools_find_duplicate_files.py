"""
DUPLICATE FILE FINDER
======================
ER 21.11.2024

This script recursively scans a directory to find duplicate files (based on filename)
and generates an Excel report listing all duplicates found.

Features:
- Recursive search through all subdirectories
- Groups files by name to identify duplicates
- Excel report including:
  - Path of each occurrence
  - Hyperlink to open the file
  - Filename
  - File size in bytes
- Useful for identifying files with the same name in different locations

Required libraries:
- os (standard library)
- collections (standard library)
- xlsxwriter (install with: pip install xlsxwriter)

Usage:
- Modify the root_directory variable with the path to scan
- Run the script to generate the report
"""


import os
from collections import defaultdict
import xlsxwriter

def find_duplicate_files(root_path):
    files_dict = defaultdict(list)
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            files_dict[filename].append(dirpath)
    return {key: paths for key, paths in files_dict.items() if len(paths) > 1}

def generate_excel_report(duplicates, output_file):
    # Create a new workbook and add a worksheet
    wb = xlsxwriter.Workbook(output_file)
    ws = wb.add_worksheet("File Duplicati")

    # Write headers
    ws.write("A1", "Cartella (Percorso)")  # Column A for path
    ws.write("B1", "Collegamento File")    # Column B for hyperlink
    ws.write("C1", "Nome File")            # Column C for filename
    ws.write("D1", "Dimensione File (Bytes)")  # Column D for file size

    row = 1  # Start from row 2 since row 1 has headers
    valoreformula = 2  # Start at B2 for dynamic referencing
    for filename, paths in duplicates.items():
        for path in paths:
            # Column A: Just the simple path (without hyperlink)
            ws.write(row, 0, path)  # Write the simple path in column A

            # Column B: Correct formula for hyperlink with &B{valoreformula} outside quotes
            formula = f'=COLLEG.IPERTESTUALE("{path}\\"&C{valoreformula}, "{path}")'
            ws.write_formula(row, 1, formula)  # Write the hyperlink formula in column B

            # Column C: Write the name of the file
            ws.write(row, 2, filename)  # Write filename in column C

            # Column D: Write the file size in bytes
            file_path = os.path.join(path, filename)  # Full file path
            file_size = os.path.getsize(file_path)  # Get file size in bytes
            ws.write(row, 3, file_size)  # Write file size in column D

            row += 1
            valoreformula += 1

    # Close the workbook (which will save the file)
    wb.close()

if __name__ == "__main__":
    root_directory = r"C:\user\path"
    output_excel = "report_duplicati.xlsx"

    if os.path.isdir(root_directory):
        duplicates = find_duplicate_files(root_directory)
        if duplicates:
            generate_excel_report(duplicates, output_excel)
            print(f"Report Excel generato: {output_excel}")
        else:
            print("Nessun file duplicato trovato.")
    else:
        print("Il percorso specificato non è valido.")
