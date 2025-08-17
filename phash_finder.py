# phash_finder.py

import os
import shutil
from PIL import Image
import imagehash

# Blok ini secara otomatis mencoba mengaktifkan dukungan untuk HEIC/AVIF.
# Jika 'pillow-heif' tidak terinstal, blok ini akan dilewati tanpa error.
try:
    import pillow_heif
    # Mendaftarkan format HEIF/AVIF ke Pillow agar bisa dibuka dengan Image.open()
    pillow_heif.register_heif_opener()
    print("[Info] Plugin HEIC/AVIF terdeteksi dan diaktifkan untuk pHash.")
except ImportError:
    print("[Info] Plugin 'pillow-heif' tidak ditemukan. Format HEIC/AVIF akan dilewati.")
    pass

def find_and_move_perceptual_duplicates(root_folder, threshold=5):
    """
    Mencari duplikat gambar yang mirip secara visual menggunakan pHash dan memindahkannya.
    Fungsi ini telah diperbarui untuk mendukung lebih banyak format dan lebih mudah dikonfigurasi.
    """
    
    # --- PENGATURAN ---
    # Anda bisa menambah/mengurangi ekstensi di sini sesuai kebutuhan.
    # Ekstensi .heic & .avif hanya akan berfungsi jika Anda sudah menjalankan:
    # pip install pillow-heif
    SUPPORTED_EXTENSIONS = (
        '.png', '.jpg', '.jpeg', '.bmp',  # Format standar
        '.gif', '.webp',                  # Format umum lainnya
        '.heic', '.avif'                  # Format modern (membutuhkan plugin)
    )

    # Nama folder dan file log
    duplicates_dir = os.path.join(root_folder, "DUPLICATES_PHASH")
    os.makedirs(duplicates_dir, exist_ok=True)
    log_file_path = os.path.join(root_folder, "log_phash_duplicates.txt")

    hashes = {}
    
    # --- LANGKAH 1: Pindai dan Hitung Hash Semua Gambar ---
    # Proses ini berjalan di latar belakang saat spinner ditampilkan.
    for dirpath, _, filenames in os.walk(root_folder):
        # Hindari memindai direktori duplikat itu sendiri
        if dirpath.startswith(duplicates_dir):
            continue
            
        for filename in filenames:
            # Memeriksa apakah ekstensi file ada dalam daftar yang didukung
            if filename.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(dirpath, filename)
                try:
                    with Image.open(file_path) as img:
                        # Khusus untuk GIF animasi, kita hanya proses frame pertama
                        if img.format == 'GIF':
                            img.seek(0)
                        # Menghitung perceptual hash dan menyimpannya
                        hashes[file_path] = imagehash.phash(img)
                except Exception:
                    # Abaikan file gambar yang korup atau tidak bisa dibaca
                    pass

    # --- LANGKAH 2: Bandingkan Hash dan Pindahkan Duplikat ---
    moved_files_log = []
    moved_files_set = set() # Untuk melacak file yang sudah dipindah agar tidak diproses ulang
    file_list = list(hashes.keys())

    for i in range(len(file_list)):
        file1_path = file_list[i]
        if file1_path in moved_files_set:
            continue

        # Membuat grup untuk setiap set duplikat di file log
        group_log = []
        for j in range(i + 1, len(file_list)):
            file2_path = file_list[j]
            if file2_path in moved_files_set:
                continue

            distance = hashes[file1_path] - hashes[file2_path]
            if distance <= threshold:
                # Saat duplikat pertama untuk sebuah grup ditemukan, catat originalnya
                if not group_log:
                    group_log.append(f"Grup Duplikat (Original: {file1_path}):")
                
                try:
                    # Pindahkan file kedua jika tingkat kemiripannya sesuai threshold
                    base_name = os.path.basename(file2_path)
                    destination_path = os.path.join(duplicates_dir, base_name)
                    
                    # Menangani jika ada nama file yang sama di folder tujuan
                    counter = 1
                    while os.path.exists(destination_path):
                        name, ext = os.path.splitext(base_name)
                        destination_path = os.path.join(duplicates_dir, f"{name}_{counter}{ext}")
                        counter += 1

                    shutil.move(file2_path, destination_path)
                    moved_files_set.add(file2_path)
                    group_log.append(f"  -> DIPINDAHKAN: '{file2_path}' (Jarak: {distance})")
                except Exception as e:
                    group_log.append(f"  -> GAGAL PINDAH: '{file2_path}' karena {e}")
        
        # Hanya tambahkan grup ke log jika ada file yang dipindahkan
        if group_log:
            moved_files_log.append("\n".join(group_log))


    # --- LANGKAH 3: Tulis Log dan Cetak Ringkasan Hasil ---
    # Pencetakan ini terjadi setelah spinner berhenti.
    print(f"\n[pHash] Hasil Pemindaian (Threshold Jarak = {threshold}):")
    if not moved_files_log:
        print("  -> Tidak ditemukan gambar yang cukup mirip.")
    else:
        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(f"--- Log Pemindahan Gambar Mirip (pHash, Threshold={threshold}) ---\n\n")
            log_file.write("\n\n".join(moved_files_log))
        
        total_moved = len(moved_files_set)
        print(f"  -> Total {total_moved} gambar mirip dipindahkan ke '{duplicates_dir}'.")
        print(f"  -> Log lengkap tersimpan di '{log_file_path}'.")