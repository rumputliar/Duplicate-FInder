# sha256_finder.py
import os
import hashlib
import shutil
from collections import defaultdict

def find_and_move_exact_duplicates(root_folder):
    duplicates_dir = os.path.join(root_folder, "DUPLICATES_SHA256")
    os.makedirs(duplicates_dir, exist_ok=True)
    log_file_path = os.path.join(root_folder, "log_sha256_duplicates.txt")

    hashes = defaultdict(list)
    
    # Langkah 1: Pindai dan hitung hash
    for dirpath, _, filenames in os.walk(root_folder):
        if dirpath.startswith(duplicates_dir):
            continue
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                        hashes[file_hash].append(file_path)
                except Exception:
                    pass # Abaikan file yang tidak bisa dibaca

    # Langkah 2: Identifikasi dan pindahkan
    moved_files_log = []
    for file_list in hashes.values():
        if len(file_list) > 1:
            original_file = file_list[0]
            duplicates_to_move = file_list[1:]
            
            group_log = [f"Grup Duplikat (Original: {original_file}):"]
            for dup_path in duplicates_to_move:
                try:
                    base_name = os.path.basename(dup_path)
                    destination_path = os.path.join(duplicates_dir, base_name)
                    counter = 1
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(base_name)
                        destination_path = os.path.join(duplicates_dir, f"{name}_{counter}{ext}")
                        counter += 1
                    shutil.move(dup_path, destination_path)
                    group_log.append(f"  -> DIPINDAHKAN: '{dup_path}' ke '{destination_path}'")
                except Exception as e:
                    group_log.append(f"  -> GAGAL PINDAH: '{dup_path}' karena {e}")
            moved_files_log.append("\n".join(group_log))

    # Langkah 3: Tulis log dan cetak ringkasan
    print("\n[SHA-256] Hasil Pemindaian:")
    if not moved_files_log:
        print("  -> Tidak ditemukan file duplikat identik.")
    else:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write("--- Log Pemindahan Duplikat Identik (SHA-256) ---\n\n")
            log_file.write("\n".join(moved_files_log))
        
        total_moved = sum(len(log.split('\n')) - 1 for log in moved_files_log)
        print(f"  -> Total {total_moved} file duplikat dipindahkan ke '{duplicates_dir}'.")
        print(f"  -> Log lengkap tersimpan di '{log_file_path}'.")