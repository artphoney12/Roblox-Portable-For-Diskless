import os
import sys
import ctypes
import time
import random
import urllib.request
import shutil
import subprocess
import msvcrt
import hashlib
import webbrowser
import json
import zipfile
# --- Konfigurasi ---
if getattr(sys, 'frozen', False):
    PORTABLE_DIR = os.path.dirname(sys.executable)
else:
    PORTABLE_DIR = os.path.dirname(os.path.abspath(__file__))
ROBLOX_DATA_DIR = os.path.join(PORTABLE_DIR, "RobloxData")
VERSION_FILE = os.path.join(ROBLOX_DATA_DIR, "version.txt")
LICENSE_FILE = os.path.join(PORTABLE_DIR, "license.key")
LOCAL_APPDATA = os.environ.get("LOCALAPPDATA")
ROBLOX_LOCAL_DIR = os.path.join(LOCAL_APPDATA, "Roblox")
SETUP_URL = "https://setup.rbxcdn.com/"
PAYMENT_URL = "https://rbp.artphoney.my.id"
LAUNCHER_VERSION = "260823.0300"

def check_for_updates():
    try:
        req = urllib.request.Request(f"https://rbp.artphoney.my.id/update.json?t={int(time.time())}")
        req.add_header("User-Agent", "RobloxPortableUpdater")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                latest_version = data.get("version", "")
                if latest_version and latest_version != LAUNCHER_VERSION:
                    download_url = data.get("download_url", "")
                    
                    if download_url:
                        zip_path = os.path.join(PORTABLE_DIR, "update.zip")
                        urllib.request.urlretrieve(download_url, zip_path)
                        
                        extract_dir = os.path.join(PORTABLE_DIR, "update_temp")
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_dir)
                            
                        new_exe_path = None
                        for root, dirs, files in os.walk(extract_dir):
                            for file in files:
                                if file.lower() == "robloxportable.exe":
                                    new_exe_path = os.path.join(root, file)
                                    break
                            if new_exe_path:
                                break
                                
                        if new_exe_path:
                            current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
                            current_exe_name = os.path.basename(current_exe)
                            bat_path = os.path.join(PORTABLE_DIR, "updater.bat")
                            
                            bat_content = f"""@echo off
timeout /t 2 /nobreak >nul
del "{current_exe}"
copy /y "{new_exe_path}" "{os.path.join(PORTABLE_DIR, current_exe_name)}"
rmdir /s /q "{extract_dir}"
del "{zip_path}"
start "" "{current_exe}"
del "%~f0"
"""
                            with open(bat_path, "w") as f:
                                f.write(bat_content)
                                
                            subprocess.Popen(bat_path, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                            sys.exit(0)
    except Exception as e:
        pass

def hide_console():
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        ctypes.windll.user32.ShowWindow(hwnd, 0) # SW_HIDE

def get_hwid():
    uuid_str = ""
    try:
        # Prioritas 1: Gunakan PowerShell (Metode modern Win 10/11)
        uuid_str = subprocess.check_output('powershell -NoProfile -Command "(Get-CimInstance -Class Win32_ComputerSystemProduct).UUID"', shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except:
        pass

    if not uuid_str:
        try:
            # Prioritas 2 (Fallback): Gunakan WMIC jika PowerShell gagal
            output = subprocess.check_output("wmic csproduct get uuid", shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = output.strip().split('\n')
            if len(lines) > 1:
                uuid_str = lines[1].strip()
        except:
            pass
            
    cpuid = ""
    try:
        # Prioritas 1: Gunakan PowerShell
        cpuid = subprocess.check_output('powershell -NoProfile -Command "(Get-CimInstance -Class Win32_Processor | Select-Object -First 1).ProcessorId"', shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except:
        pass

    if not cpuid:
        try:
            # Prioritas 2 (Fallback): Gunakan WMIC
            output = subprocess.check_output("wmic cpu get processorid", shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = output.strip().split('\n')
            if len(lines) > 1:
                cpuid = lines[1].strip()
        except:
            pass

    # Fallback Terakhir: Jika keduanya gagal (wmic dihapus, powershell diblokir)
    if not uuid_str and not cpuid:
        import uuid
        # Mengambil MAC Address sebagai HWID Darurat
        uuid_str = str(uuid.getnode())

    raw_hwid = f"{uuid_str}-{cpuid}"
    hashed = hashlib.sha256(raw_hwid.encode('utf-8')).hexdigest()
    return hashed[:16] 

def generate_expected_license(hwid):
    secret = "artphoney_super_secret_key"
    data = hwid + secret
    return hashlib.md5(data.encode('utf-8')).hexdigest().upper()

def check_license():
    hwid = get_hwid()
    expected_license = generate_expected_license(hwid)
    
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                saved_license = f.read().strip()
                if saved_license == expected_license:
                    return True
        except:
            pass
    return False

def save_hwid_info(hwid):
    hwid_file = os.path.join(PORTABLE_DIR, "HWID_Info.txt")
    try:
        with open(hwid_file, "w") as f:
            f.write(f"Lokasi Folder : {PORTABLE_DIR}\n")
            f.write(f"HWID Anda     : {hwid}\n")
            f.write(f"\nBerikan HWID di atas ke Admin (artphoney) jika sistem otomatis bermasalah.\n")
    except:
        pass
    return hwid_file

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def show_notification():
    os.system("color 0A")
    hwid = get_hwid()
    print("==================================================")
    print("   Portable ini dibuat oleh artphoney")
    print("   Info lebih lanjut: https://artphoney.my.id")
    print("==================================================")
    print("Silakan melakukan donasi minimal 50k rupiah atau lebih untuk menghilangkan notifikasi sekaligus mensupport pembuat portable ini...")
    print("==================================================")
    print("Tekan [D] untuk Donasi & buka Web Payment.")
    
    for i in range(120, 0, -1):
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key.lower() == b'd':
                print("\n[INFO] Membuka web payment...")
                hwid_path = save_hwid_info(hwid)
                webbrowser.open(f"{PAYMENT_URL}/index.html?hwid={hwid}")
                print(f"[INFO] HWID Anda telah disimpan di: {hwid_path}")
                print(f"[INFO] HWID: {hwid}")
                print("\n[INFO] Menunggu konfirmasi pembayaran dari server (Otomatis)...")
                print("Silakan selesaikan pembayaran donasi di browser Anda.")
                
                license_found = False
                for attempt in range(720):
                    try:
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                            'Accept-Language': 'en-US,en;q=0.5',
                            'Connection': 'keep-alive'
                        }
                        req_lic = urllib.request.Request(f"{PAYMENT_URL}/licenses/{hwid}.txt", headers=headers)
                        with urllib.request.urlopen(req_lic) as response:
                            if response.status == 200:
                                downloaded_license = response.read().decode('utf-8').strip()
                                expected_lic = generate_expected_license(hwid)
                                if downloaded_license == expected_lic:
                                    with open(LICENSE_FILE, "w") as f:
                                        f.write(downloaded_license)
                                    print("\n[SUCCESS] Lisensi berhasil didownload dan diverifikasi!")
                                    print("[INFO] Terima kasih atas donasi Anda! Memulai Roblox secara transparan...")
                                    license_found = True
                                    hide_console() 
                                    
                                    MB_OK = 0x0
                                    MB_ICONINFORMATION = 0x40
                                    ctypes.windll.user32.MessageBoxW(
                                        0, 
                                        "Terima kasih banyak atas donasi Anda!\n\nPembayaran Anda berhasil dikonfirmasi dan lisensi telah terverifikasi.\nRoblox akan segera dimulai.", 
                                        "Pembayaran Berhasil", 
                                        MB_OK | MB_ICONINFORMATION
                                    )
                                    
                                    return True
                    except Exception as e:
                        pass
                        
                    sys.stdout.write(f"\rMenunggu pembayaran... (Percobaan ke-{attempt+1}/720) ")
                    sys.stdout.flush()
                    time.sleep(5)
                
                if not license_found:
                    print("\n[TIMEOUT] Waktu tunggu habis. Tekan Enter untuk melanjutkan ke game (tanpa lisensi)...")
                    input()
                break
        
        if i % 10 == 0:
            sys.stdout.write(f"\rMelanjutkan dalam {i//10} detik... ")
            sys.stdout.flush()
            
        time.sleep(0.1)
        
    while msvcrt.kbhit():
        msvcrt.getch()
        
    print("\n\n[INFO] Melanjutkan proses...")
    return False

def rename_prochook():
    print("[INFO] Memeriksa prochook.dll...")
    sys32_path = r"C:\Windows\System32\prochook.dll"
    gbilling_path = r"C:\Program Files (x86)\GBillingClient\x64\prochook.dll"
    
    def get_random_name():
        return f"prochook_{random.randint(0, 32767)}_{random.randint(0, 32767)}.dll"
        
    try:
        if os.path.exists(sys32_path):
            new_name = os.path.join(r"C:\Windows\System32", get_random_name())
            os.rename(sys32_path, new_name)
            print(f"[SUCCESS] Rename {sys32_path} ke {new_name}")
    except Exception as e:
        pass

    try:
        if os.path.exists(gbilling_path):
            new_name = os.path.join(r"C:\Program Files (x86)\GBillingClient\x64", get_random_name())
            os.rename(gbilling_path, new_name)
            print(f"[SUCCESS] Rename {gbilling_path} ke {new_name}")
    except Exception as e:
        pass

def clean_registry():
    print("[INFO] Membersihkan Registry Roblox lama...")
    keys_to_delete = [
        r"Software\ROBLOX Corporation",
        r"Software\Roblox"
    ]
    for key_path in keys_to_delete:
        try:
            subprocess.run(["reg", "delete", f"HKCU\\{key_path}", "/f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            pass

def init_junction():
    print("[INFO] Inisialisasi Folder Junction...")
    
    if not os.path.exists(ROBLOX_DATA_DIR):
        os.makedirs(ROBLOX_DATA_DIR)

    if os.path.lexists(ROBLOX_LOCAL_DIR):
        try:
            if os.path.isjunction(ROBLOX_LOCAL_DIR) or os.path.islink(ROBLOX_LOCAL_DIR):
                os.rmdir(ROBLOX_LOCAL_DIR)
            else:
                shutil.rmtree(ROBLOX_LOCAL_DIR)
        except Exception as e:
            print(f"[ERROR] Gagal menghapus folder Roblox lama: {e}")
            return False

    try:
        subprocess.run(["cmd", "/c", "mklink", "/J", ROBLOX_LOCAL_DIR, ROBLOX_DATA_DIR], check=True, stdout=subprocess.DEVNULL)
        print("[SUCCESS] Folder Junction berhasil dibuat.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Gagal membuat Junction: {e}")
        return False

def check_update_and_launch():
    print("[INFO] Mengecek update Roblox...")
    try:
        req = urllib.request.Request(SETUP_URL + "version", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            latest_version = response.read().decode('utf-8').strip()
    except Exception as e:
        print(f"[ERROR] Gagal mengecek update: {e}")
        latest_version = None

    local_version = None
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            local_version = f.read().strip()

    print(f"Versi Lokal: {local_version}")
    print(f"Versi Terbaru: {latest_version}")

    needs_update = latest_version and (local_version != latest_version)

    if needs_update:
        print("[INFO] Mendownload update installer...")
        installer_path = os.path.join(PORTABLE_DIR, "RobloxPlayerInstaller.exe")
        try:
            req_dl = urllib.request.Request("https://www.roblox.com/download/client", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_dl) as response, open(installer_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            print("[INFO] Menjalankan installer Roblox...")
            subprocess.run([installer_path], check=True)
            
            with open(VERSION_FILE, "w") as f:
                f.write(latest_version)
                
            print("[SUCCESS] Update selesai.")
        except Exception as e:
            print(f"[ERROR] Gagal update: {e}")
            print("\nTekan Enter untuk keluar...")
            input()
            sys.exit(1)
        finally:
            try:
                if os.path.exists(installer_path):
                    print("[INFO] Menghapus file installer sementara...")
                    os.remove(installer_path)
            except Exception as cleanup_err:
                pass
    else:
        print("[INFO] Tidak ada update, menjalankan Roblox...")
    
    if latest_version or local_version:
        ver_to_run = latest_version if latest_version else local_version
        exe_found = False
        search_dirs = [
            os.path.join(ROBLOX_LOCAL_DIR, "Versions"),
            r"C:\Program Files (x86)\Roblox\Versions",
            r"C:\Program Files\Roblox\Versions"
        ]
        
        if ver_to_run:
            for base_dir in search_dirs:
                exe_path = os.path.join(base_dir, ver_to_run, "RobloxPlayerBeta.exe")
                if os.path.exists(exe_path):
                    print(f"[INFO] Membuka {exe_path}")
                    subprocess.Popen([exe_path])
                    exe_found = True
                    break
                    
        if not exe_found:
            for base_dir in search_dirs:
                if os.path.exists(base_dir):
                    for folder in os.listdir(base_dir):
                        potential_exe = os.path.join(base_dir, folder, "RobloxPlayerBeta.exe")
                        if os.path.exists(potential_exe):
                            print(f"[INFO] Menemukan executable di {potential_exe}")
                            subprocess.Popen([potential_exe])
                            exe_found = True
                            break
                if exe_found:
                    break
                    
        if not exe_found:
            print("[ERROR] File game RobloxPlayerBeta.exe tidak ditemukan di direktori mana pun.")

def check_single_instance():
    mutex_name = "RobloxPortableArtphoneyMutex"
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    last_error = kernel32.GetLastError()
    if last_error == 183:
        print("[WARNING] Launcher Roblox Portable sudah berjalan. Harap tunggu...")
        time.sleep(2)
        sys.exit(0)
    return mutex

def main():
    _mutex = check_single_instance()
    
    check_for_updates()
    
    is_licensed = check_license()
    if is_licensed:
        hide_console()
    
    if not is_admin():
        if not is_licensed:
            print("[INFO] Meminta hak akses Administrator...")
        if getattr(sys, 'frozen', False):
            args = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        else:
            args = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
        sys.exit()

    try:
        if not is_licensed:
            licensed_now = show_notification()
            if licensed_now:
                is_licensed = True
            
        rename_prochook()
        clean_registry()
        
        if init_junction():
            check_update_and_launch()
        
        if not is_licensed:
            time.sleep(2)
    except Exception as e:
        if not is_licensed:
            print(f"\n[CRITICAL ERROR] Terjadi kesalahan tidak terduga: {e}")
            print("Tekan Enter untuk keluar...")
            input()

if __name__ == "__main__":
    main()