"""
SRT SUBTITLE TRANSLATOR (AI-POWERED)
=====================================
ER 23.05.2025

This script uses Facebook's M2M100 multilingual translation model to translate
SRT subtitle files from Korean to Italian (or other target languages).

Features:
- Uses state-of-the-art M2M100 model (418M parameters) for high-quality translation
- Preserves SRT formatting (subtitle numbers, timestamps, line breaks)
- Batch processing for improved performance (configurable batch size)
- GPU acceleration support (CUDA) for faster translation
- Progressive saving (creates partial files after each batch)
- Memory optimization with half-precision (FP16) on GPU
- Automatic detection of translation direction (Korean → target language)
- Handles multiple SRT files in a folder

Translation Pipeline:
1. Reads SRT file line by line
2. Groups text lines (skipping numbers and timestamps)
3. Translates in batches using M2M100
4. Reconstructs the SRT with translated text
5. Saves to a "tradotti" subfolder

Required libraries:
- transformers (install with: pip install transformers)
- torch (install with: pip install torch)
- huggingface_hub (install with: pip install huggingface_hub)
- re (standard library)
- time (standard library)
- os (standard library)
- glob (standard library)

Hardware Requirements:
- GPU with at least 4GB VRAM recommended (for faster processing)
- CPU fallback available but slower

Usage:
- Modify the cartella_sottotitoli variable with the path containing SRT files
- Set lingua_dest to your target language (e.g., "it" for Italian)
- Run the script to translate all SRT files in the folder

Note:
- The Hugging Face token is hardcoded - use environment variables for security!
- The model downloads the first time you run the script (~1.5GB)
- Translations are not perfect - review before using professionally
"""

from huggingface_hub import login
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import re
import torch
import time
import os
import glob

torch.backends.cudnn.benchmark = True

# Token
token = "TOKEN-HERE"
login(token)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(f"Usando device: {device}")

model_name = "facebook/m2m100_418M"
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name)
model = model.half().to(device)

print(f"Nome GPU: {torch.cuda.get_device_name(device)}")

def get_gpu_memory():
    if device.type == 'cuda':
        mem_alloc = torch.cuda.memory_allocated(device) / (1024 ** 2)
        mem_reserved = torch.cuda.memory_reserved(device) / (1024 ** 2)
        print(f"GPU Memory — Allocata: {mem_alloc:.2f} MB, Riservata: {mem_reserved:.2f} MB")

def traduci_batch(frasi, lingua_destinazione="it"):
    tokenizer.src_lang = "ko"
    encoded = tokenizer(frasi, return_tensors="pt", padding=True, truncation=True)
    encoded = {k: v.to(device) for k, v in encoded.items()}

    # Debug dispositivi
    print(f"Devices encoded tensors: {[v.device for v in encoded.values()]}")
    print(f"Model device: {next(model.parameters()).device}")

    with torch.no_grad():
        generated_tokens = model.generate(
            **encoded,
            forced_bos_token_id=tokenizer.get_lang_id(lingua_destinazione),
            max_length=400,
            num_beams=8,
            early_stopping=True,
            no_repeat_ngram_size=3
        )
    traduzioni = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return traduzioni

def raggruppa_righe_testo(righe):
    frasi = []
    idx_mappa = []
    buffer = ""
    indices = []
    for i, riga in enumerate(righe):
        r = riga.strip()
        if (r and
            not re.match(r'^\d+$', r) and
            not re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', r) and
            r != "*"):
            buffer += " " + r if buffer else r
            indices.append(i)
        else:
            if buffer:
                frasi.append(buffer.strip())
                idx_mappa.append(indices)
                buffer = ""
                indices = []
    if buffer:
        frasi.append(buffer.strip())
        idx_mappa.append(indices)
    return frasi, idx_mappa

def traduci_srt(file_path, lingua_destinazione="ko", batch_size=32):
    print(f"\nTraduzione in corso per: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        righe = f.readlines()

    testo_da_tradurre, idx_map = raggruppa_righe_testo(righe)
    total = len(testo_da_tradurre)
    tempo_batch = []

    # Creo cartella di output
    base_dir = os.path.dirname(file_path)
    output_dir = os.path.join(base_dir, "tradotti")
    os.makedirs(output_dir, exist_ok=True)

    nome_file = os.path.basename(file_path).rsplit(".", 1)[0]

    for start in range(0, total, batch_size):
        batch = testo_da_tradurre[start:start + batch_size]
        start_time = time.time()
        traduzioni = traduci_batch(batch, lingua_destinazione)
        durata = time.time() - start_time
        tempo_batch.append(durata / len(batch))

        for trad, idxs in zip(traduzioni, idx_map[start:start + batch_size]):
            trad_righe = trad.split('\n')
            if len(trad_righe) == len(idxs):
                for idx, trad_riga in zip(idxs, trad_righe):
                    righe[idx] = trad_riga + "\n"
            else:
                righe[idxs[0]] = trad + "\n"
                for idx in idxs[1:]:
                    righe[idx] = "\n"

        print(f"Batch {start}–{start+len(batch)} | Durata: {durata:.2f}s | Media per frase: {tempo_batch[-1]:.3f}s")
        get_gpu_memory()

        if len(tempo_batch) >= 1:
            media_attuale = sum(tempo_batch) / len(tempo_batch)
            restante = total - (start + batch_size)
            stima_sec = media_attuale * restante
            print(f" Stima tempo rimanente: {stima_sec/60:.1f} minuti")

        # Salvataggio PARZIALE ad ogni batch completato
        partial_path = os.path.join(output_dir, f"{nome_file}_{lingua_destinazione}_partial_{start+len(batch)}.srt")
        with open(partial_path, "w", encoding="utf-8") as f_out:
            f_out.writelines(righe)
        print(f" Salvato parziale: {partial_path}")

    # Salvataggio finale
    output_finale = os.path.join(output_dir, f"{nome_file}_{lingua_destinazione}.srt")
    with open(output_finale, "w", encoding="utf-8") as f_out:
        f_out.writelines(righe)
    print(f" Traduzione completata: {output_finale}")

def traduci_cartella(cartella, lingua_destinazione="ko", batch_size=128):
    pattern = os.path.join(cartella, "*.srt")
    files = glob.glob(pattern)
    print(f"Trovati {len(files)} file .srt nella cartella {cartella}")
    for f in files:
        traduci_srt(f, lingua_destinazione=lingua_destinazione, batch_size=batch_size)

if __name__ == "__main__":
    cartella_sottotitoli = r"C:\user\path"
    lingua_dest = "it"  # Da coreano a italiano
    traduci_cartella(cartella_sottotitoli, lingua_destinazione=lingua_dest, batch_size=128)
