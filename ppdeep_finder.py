# ssdeep_finder.py (menggunakan ppdeep sebagai alternatif)
import os
import shutil
import ppdeep # <- Menggunakan ppdeep, bukan ssdeep

def find_and_move_fuzzy_duplicates(root_folder, threshold=75):
    """
    Mencari file yang mirip menggunakan ppdeep (alternatif ssdeep) dan memindahkannya.
    """
    duplicates_dir = os.path.join(root_folder, "DUPLICATES_PPDEEP") # Nama folder diubah
    os.makedirs(duplicates_dir, exist_ok=True)
    log_file_path = os.path.join(root_folder, "log_ppdeep_duplicates.txt") # Nama log diubah

    hashes = {}

    # Langkah 1: Pindai dan hitung hash ppdeep semua file
    for dirpath, _, filenames in os.walk(root_folder):
        if dirpath.startswith(duplicates_dir):
            continue
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
                try:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                        # ppdeep hash dari konten file, bukan dari path
                        hashes[file_path] = ppdeep.hash(file_content) 
                except Exception:
                    pass # Abaikan file yang tidak bisa dibaca

    # Langkah 2: Bandingkan hash dan pindahkan duplikat
    moved_files_log = []
    moved_files_set = set()
    file_list = list(hashes.keys())

    for i in range(len(file_list)):
        file1_path = file_list[i]
        if file1_path in moved_files_set:
            continue

        group_log = []
        for j in range(i + 1, len(file_list)):
            file2_path = file_list[j]
            if file2_path in moved_files_set:
                continue

            # Pastikan kedua file memiliki hash
            if file1_path in hashes and file2_path in hashes:
                # ppdeep.compare mengembalikan skor 0-100
                score = ppdeep.compare(hashes[file1_path], hashes[file2_path])
                if score >= threshold:
                    if not group_log:
                        group_log.append(f"Grup Duplikat (Original: {file1_path}):")

                    try:
                        base_name = os.path.basename(file2_path)
                        destination_path = os.path.join(duplicates_dir, base_name)
                        counter = 1
                        while os.path.exists(destination_path):
                            name, ext = os.path.splitext(base_name)
                            destination_path = os.path.join(duplicates_dir, f"{name}_{counter}{ext}")
                            counter += 1
                        shutil.move(file2_path, destination_path)
                        moved_files_set.add(file2_path)
                        group_log.append(f"  -> DIPINDAHKAN: '{file2_path}' (Skor: {score}%)")
                    except Exception as e:
                         group_log.append(f"  -> GAGAL PINDAH: '{file2_path}' karena {e}")
        if group_log:
            moved_files_log.append("\n".join(group_log))

    # Langkah 3: Tulis log dan cetak ringkasan
    print("\n[ppdeep] Hasil Pemindaian:")
    if not moved_files_log:
        print("  -> Tidak ditemukan file duplikat mirip.")
    else:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"--- Log Pemindahan Duplikat Fuzzy (ppdeep, Threshold={threshold}%) ---\n\n")
            log_file.write("\n\n".join(moved_files_log))

        total_moved = sum(len(log.split('\n')) - 1 for log in moved_files_log)
        print(f"  -> Total {total_moved} file mirip dipindahkan ke '{duplicates_dir}'.")
        print(f"  -> Log lengkap tersimpan di '{log_file_path}'.")