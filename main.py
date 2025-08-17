# main.py
import os
import sys

# Tambahkan try-except untuk penanganan import yang lebih baik
try:
    from utils import ProgressSpinner
    from sha256_finder import find_and_move_exact_duplicates
    from phash_finder import find_and_move_perceptual_duplicates
    from ppdeep_finder import find_and_move_fuzzy_duplicates
except ImportError as e:
    print(f"Error: Gagal mengimpor modul. Pastikan semua file .py ada di direktori yang sama.")
    print(f"Detail: {e}")
    sys.exit(1)


def get_target_folder():
    """Meminta pengguna untuk memilih folder target."""
    current_dir = os.getcwd()
    print(f"Direktori saat ini adalah: '{current_dir}'")
    
    choice = input("Apakah Anda ingin memindai direktori ini? (y/n): ").lower()
    
    if choice == 'y':
        return current_dir
    else:
        while True:
            target_folder = input("Masukkan path lengkap ke folder yang ingin dipindai: ")
            if os.path.isdir(target_folder):
                return target_folder
            else:
                print("Error: Folder tidak ditemukan. Silakan coba lagi.")

def print_menu():
    """Menampilkan menu pilihan kepada pengguna."""
    print("\n" + "="*50)
    print("      PROGRAM PENCARI FILE DUPLIKAT      ")
    print("="*50)
    print("Pilih metode yang ingin digunakan:")
    print("\n--- 1. SHA-256 (Duplikat Identik) ---")
    print("    - Fungsi: Mencari file yang 100% sama persis.")
    print("    - Cocok untuk: SEMUA TIPE FILE.")
    
    print("\n--- 2. pHash (Gambar Mirip Visual) ---")
    print("    - Fungsi: Mencari file gambar yang terlihat mirip.")
    print("    - Cocok untuk: HANYA FILE GAMBAR (.jpg, .png).")

    print("\n--- 3. ppdeep (File Mirip Konten/Fuzzy) ---")
    print("    - Fungsi: Mencari file dengan konten yang sangat mirip.")
    print("    - Cocok untuk: Dokumen, Kode Sumber, File Program.")

    print("\n--- 4. Keluar ---")
    print("="*50)

def main():
    """Fungsi utama untuk menjalankan program."""
    
    print("PERHATIAN: Program ini akan MEMINDAHKAN (cut-paste) file duplikat.")
    print("Sangat disarankan untuk memiliki CADANGAN (BACKUP) data sebelum melanjutkan.")
    
    target_folder = get_target_folder()

    while True:
        print_menu()
        choice = input("Masukkan pilihan Anda (1-4): ")

        if choice == '1':
            with ProgressSpinner("[SHA-256] Memindai file..."):
                find_and_move_exact_duplicates(target_folder)
        
        elif choice == '2':
            while True:
                try:
                    threshold = int(input("Masukkan threshold pHash (0-10, rekomendasi: 5): "))
                    if 0 <= threshold <= 20: break
                    else: print("Masukkan angka antara 0 dan 20.")
                except ValueError: print("Input tidak valid, masukkan angka.")
            
            with ProgressSpinner(f"[pHash] Memindai dan membandingkan gambar (threshold={threshold})..."):
                find_and_move_perceptual_duplicates(target_folder, threshold)

        elif choice == '3':
            while True:
                try:
                    threshold = int(input("Masukkan threshold ppdeep (0-100, rekomendasi: 75): "))
                    if 0 <= threshold <= 100: break
                    else: print("Masukkan angka antara 0 dan 100.")
                except ValueError: print("Input tidak valid, masukkan angka.")
            
            try:
                with ProgressSpinner(f"[ppdeep] Memindai dan membandingkan file (threshold={threshold}%)..."):
                    find_and_move_fuzzy_duplicates(target_folder, threshold)
            except NameError: # Terjadi jika import ppdeep gagal
                 print("\nERROR: Pustaka 'ppdeep' tidak dapat digunakan.")
                 print("Pastikan Anda sudah menginstalnya dengan benar. Cek kembali petunjuk instalasi.")
            except Exception as e:
                 print(f"\nTerjadi error saat menjalankan ppdeep: {e}")

        elif choice == '4':
            print("Terima kasih telah menggunakan program ini. Keluar...")
            break
        else:
            print("Pilihan tidak valid. Silakan masukkan angka dari 1 hingga 4.")

if __name__ == "__main__":
    main()