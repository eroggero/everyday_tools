import subprocess
import os
import re

# Percorsi completi agli eseguibili MKVToolNix
MKVMERGE = r"C:\Program Files\MKVToolNix\mkvmerge.exe"
MKVEXTRACT = r"C:\Program Files\MKVToolNix\mkvextract.exe"

def get_subtitle_tracks(mkv_file):
    cmd = [MKVMERGE, "-i", mkv_file]
    try:
        # Esegui mkvmerge e stampa l'output
        output = subprocess.check_output(cmd, universal_newlines=True)
        print("Output di mkvmerge:", output)  # Aggiungi questa riga per stampare l'output completo di mkvmerge
    except subprocess.CalledProcessError as e:
        print(f"Errore analizzando {mkv_file}: {e}")
        return []

    tracks = []
    for line in output.splitlines():
        # Cerca tutte le tracce sottotitoli, non importa il formato
        if "subtitles" in line.lower():
            print(f"Trovato sottotitolo in: {line}")  # Per diagnosticare meglio
            match = re.search(r"ID traccia (\d+): subtitles", line)  # Cerchiamo la parola 'subtitles'
            if match:
                tracks.append(match.group(1))
    return tracks

def extract_subtitles(mkv_file, track_ids):
    # Crea sottocartella "sottotitoli"
    output_dir = os.path.join(os.path.dirname(mkv_file), "sottotitoli")
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(mkv_file))[0]
    for tid in track_ids:
        out_file = os.path.join(output_dir, f"{base_name}_sub{tid}.srt")
        print(f"Estraggo: {mkv_file} → Traccia {tid} → {out_file}")
        subprocess.run([MKVEXTRACT, "tracks", mkv_file, f"{tid}:{out_file}"])

def process_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".mkv"):
            mkv_path = os.path.join(folder_path, filename)
            print(f"\nAnalizzo: {mkv_path}")
            tracks = get_subtitle_tracks(mkv_path)
            if tracks:
                extract_subtitles(mkv_path, tracks)
            else:
                print("→ Nessuna traccia sottotitoli trovata.")


if __name__ == "__main__":
    folder =  r'C:\path'  # <-- Sostituisci con la tua cartella .mkv
    process_folder(folder)


