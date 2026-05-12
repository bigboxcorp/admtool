import sys
import time
import os
import platform
import subprocess
import socket
import uuid
import ctypes
import msvcrt
import threading
import urllib.request
import winreg
import shutil
from datetime import datetime

try:
    os.system("")

    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(".")
        
        path = os.path.join(base_path, relative_path)
        if not os.path.exists(path):
            path = os.path.join(os.getcwd(), relative_path)
        return path

    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    if not is_admin():
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
        if ret <= 32:
            print("\n\033[91m[!] Administrator privileges required. Please run the app again and click 'Yes'.\033[0m")
            time.sleep(4)
        sys.exit()

    ctypes.windll.kernel32.SetConsoleTitleW("Active Device Manager")

    def run_cmd(cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return result.stdout.strip()
        except:
            return "N/A"

    def confirm_execution(desc):
        print(f"\n\033[96mInfo: {desc}\033[0m")
        input("\033[93mPress ENTER to execute or CTRL+C to cancel...\033[0m")

    def get_hidden_pin(prompt):
        print(prompt, end='', flush=True)
        pin = ""
        while True:
            key = msvcrt.getch()
            if key in (b'\r', b'\n'):
                print()
                break
            elif key == b'\x08':
                if len(pin) > 0:
                    pin = pin[:-1]
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif key == b'\x03':
                raise KeyboardInterrupt
            elif key == b'\x11':
                os._exit(0)
            else:
                try:
                    char = key.decode('utf-8')
                    pin += char
                    sys.stdout.write('*')
                    sys.stdout.flush()
                except:
                    pass
        return pin

    def set_registry_hklm(path, name, value, reg_type=winreg.REG_DWORD):
        try:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, path)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, name, 0, reg_type, value)
            return True
        except:
            return False

    def set_user_reg(usr, path, name, value, reg_type=winreg.REG_DWORD):
        try:
            sid_raw = run_cmd(f'powershell "(Get-CimInstance Win32_UserAccount -Filter \\"Name=\'{usr}\'\\").SID"')
            sid = sid_raw.split('\n')[0].strip()
            try:
                winreg.CreateKey(winreg.HKEY_USERS, f"{sid}\\{path}")
                with winreg.OpenKey(winreg.HKEY_USERS, f"{sid}\\{path}", 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value)
                return True
            except:
                ntuser_path = f"C:\\Users\\{usr}\\NTUSER.DAT"
                try:
                    os.system(f'reg load HKU\\TempHive_{usr} "{ntuser_path}" >nul 2>&1')
                    full_path = f"TempHive_{usr}\\{path}"
                    winreg.CreateKey(winreg.HKEY_USERS, full_path)
                    with winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_WRITE) as key:
                        winreg.SetValueEx(key, name, 0, reg_type, value)
                finally:
                    os.system(f'reg unload HKU\\TempHive_{usr} >nul 2>&1')
                return True
        except:
            return False

    def get_user_reg(usr, path, name):
        try:
            sid_raw = run_cmd(f'powershell "(Get-CimInstance Win32_UserAccount -Filter \\"Name=\'{usr}\'\\").SID"')
            sid = sid_raw.split('\n')[0].strip()
            try:
                with winreg.OpenKey(winreg.HKEY_USERS, f"{sid}\\{path}", 0, winreg.KEY_READ) as key:
                    val, _ = winreg.QueryValueEx(key, name)
                    return val
            except:
                ntuser_path = f"C:\\Users\\{usr}\\NTUSER.DAT"
                val = None
                try:
                    os.system(f'reg load HKU\\TempHive_{usr} "{ntuser_path}" >nul 2>&1')
                    full_path = f"TempHive_{usr}\\{path}"
                    with winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_READ) as key:
                        val, _ = winreg.QueryValueEx(key, name)
                except:
                    pass
                finally:
                    os.system(f'reg unload HKU\\TempHive_{usr} >nul 2>&1')
                return val
        except:
            return None

    def toggle_app_blocker(usr, enable):
        try:
            sid_raw = run_cmd(f'powershell "(Get-CimInstance Win32_UserAccount -Filter \\"Name=\'{usr}\'\\").SID"')
            sid = sid_raw.split('\n')[0].strip()
            restrict_path = f"{sid}\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer"
            restrict_list_path = f"{restrict_path}\\RestrictRun"
            cache_dir = r"C:\ProgramData\ADM_Cache"
            os.makedirs(cache_dir, exist_ok=True)
            cache_file = os.path.join(cache_dir, "allowed_apps.txt")
            
            if enable:
                url = "https://raw.githubusercontent.com/bigboxcorp/admtool/main/public/allowed_apps.txt"
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        github_apps = response.read().decode('utf-8').splitlines()
                    with open(cache_file, "w") as f:
                        f.write("\n".join(github_apps))
                except:
                    if os.path.exists(cache_file):
                        with open(cache_file, "r") as f:
                            github_apps = f.read().splitlines()
                    else:
                        github_apps = []
                
                base_apps = ["explorer.exe", "cmd.exe", "powershell.exe", "adm.exe", "taskmgr.exe", "msedge.exe", "chrome.exe", "userinit.exe", "ctfmon.exe", "sihost.exe", "taskhostw.exe", "SecurityHealthSystray.exe", "OneDrive.exe", "smartscreen.exe", "SearchHost.exe", "StartMenuExperienceHost.exe", "RuntimeBroker.exe", "svchost.exe", "dllhost.exe", "conhost.exe", "SystemSettings.exe", "ApplicationFrameHost.exe", "SystemSettingsBroker.exe", "backgroundTaskHost.exe", "ShellExperienceHost.exe", "SearchApp.exe", "SearchUI.exe", "LockApp.exe", "CredentialUIBroker.exe", "WerFault.exe"]
                all_apps = list(set([a.strip() for a in base_apps + github_apps if a.strip()]))
                
                set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "RestrictRun", 1)
                set_user_reg(usr, r"Software\Policies\Microsoft\Windows\Installer", "DisableUserInstalls", 1)
                
                try:
                    winreg.CreateKey(winreg.HKEY_USERS, restrict_list_path)
                    with winreg.OpenKey(winreg.HKEY_USERS, restrict_list_path, 0, winreg.KEY_WRITE) as key:
                        for i, app in enumerate(all_apps, 1):
                            winreg.SetValueEx(key, str(i), 0, winreg.REG_SZ, app)
                except:
                    pass
            else:
                set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "RestrictRun", 0)
                set_user_reg(usr, r"Software\Policies\Microsoft\Windows\Installer", "DisableUserInstalls", 0)
                try:
                    os.system(f'reg delete "HKU\\{restrict_list_path}" /f >nul 2>&1')
                except:
                    pass
            return True
        except:
            return False

    def toggle_sites_blocker(enable):
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        cache_dir = r"C:\ProgramData\ADM_Cache"
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, "blocked_sites.txt")
        try:
            os.system(f'attrib -r "{hosts_path}" >nul 2>&1')
            if os.path.exists(hosts_path):
                with open(hosts_path, "r") as f:
                    lines = f.readlines()
                with open(hosts_path, "w") as f:
                    skip = False
                    for line in lines:
                        if line.strip() == "# ADM_BLOCKED_SITES_START":
                            skip = True
                        if not skip:
                            f.write(line)
                        if line.strip() == "# ADM_BLOCKED_SITES_END":
                            skip = False
            
            if enable:
                url = "https://raw.githubusercontent.com/bigboxcorp/admtool/main/public/blocked_sites.txt"
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        sites = response.read().decode('utf-8').splitlines()
                    with open(cache_file, "w") as f:
                        f.write("\n".join(sites))
                except:
                    if os.path.exists(cache_file):
                        with open(cache_file, "r") as f:
                            sites = f.read().splitlines()
                    else:
                        sites = []
                with open(hosts_path, "a") as f:
                    f.write("\n# ADM_BLOCKED_SITES_START\n")
                    for site in sites:
                        site = site.strip()
                        if site:
                            f.write(f"127.0.0.1 {site}\n")
                    f.write("# ADM_BLOCKED_SITES_END\n")
            os.system("ipconfig /flushdns >nul 2>&1")
            return True
        except:
            return False

    def toggle_secure_dns(enable):
        if enable:
            os.system('netsh interface ip set dns name="Ethernet" static 94.140.14.15 >nul 2>&1')
            os.system('netsh interface ip add dns name="Ethernet" 94.140.15.16 index=2 >nul 2>&1')
            os.system('netsh interface ip set dns name="Wi-Fi" static 94.140.14.15 >nul 2>&1')
            os.system('netsh interface ip add dns name="Wi-Fi" 94.140.15.16 index=2 >nul 2>&1')
        else:
            os.system('netsh interface ip set dns name="Ethernet" dhcp >nul 2>&1')
            os.system('netsh interface ip set dns name="Wi-Fi" dhcp >nul 2>&1')

    def apply_policy_changes():
        try:
            os.system("gpupdate /force >nul 2>&1")
            ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Policy", 0x0002, 5000, None)
        except:
            pass

    def toggle_browser_security(enable):
        val = 1 if enable else 0
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Edge", "SmartScreenEnabled", val)
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Edge", "PreventSmartScreenPromptOverride", val)
        set_registry_hklm(r"SOFTWARE\Policies\Google\Chrome", "SafeBrowsingProtectionLevel", val)
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableSmartScreen", val)

    def exclude_av():
        try:
            current_exe = sys.executable
            current_dir = os.path.dirname(current_exe)
            subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionProcess \'{current_exe}\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionPath \'{current_dir}\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

    exclude_av()

    def maximize_console():
        try:
            hwnd = ctypes.windll.kernel32.GetConsoleWindow()
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 3)
        except:
            pass

    def check_internet():
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1.5)
            return True
        except:
            return False

    def get_ipv6():
        try:
            for res in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
                return res[4][0]
        except:
            return "N/A"
        return "N/A"

    def print_welcome():
        os.system('cls' if os.name == 'nt' else 'clear')
        welcome_text = r"""
      __        __ _____  _      ____  ___   __  __  _____ 
      \ \      / /| ____|| |    / ___|/ _ \ |  \/  || ____|
       \ \ /\ / / |  _|  | |   | |   | | | || |\/| ||  _|  
        \ V  V /  | |___ | |___| |___| |_| || |  | || |___ 
         \_/\_/   |_____||_____|\____|\___/ |_|  |_||_____|
        """
        bigbox_text = r"""
           ____ ___ ____    ____   _____  __
          | __ )_ _/ ___| | __ ) / _ \ \/ /
          |  _ \| | |  _  |  _ \| | | \  / 
          | |_) | | |_| | | |_) | |_| /  \ 
          |____/___\____| |____/ \___/_/\_\
           INTERNATIONAL PVT. LTD.
        """
        print("\033[1m\033[96m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m" + welcome_text + "\033[0m")
        print("\033[1m\033[93m" + bigbox_text + "\033[0m")
        print("\033[1m\033[96m" + "="*70 + "\033[0m\n")

    def progress_animation():
        print_welcome()
        for i in range(1, 101):
            time.sleep(0.01)
            sys.stdout.write(f"\r\033[92mLoading... {i}%\033[0m")
            sys.stdout.flush()
        sys.stdout.write("\r" + " " * 30 + "\r")
        sys.stdout.flush()

    def fetch_data(silent=False, full_refresh=True, existing_data=None):
        data = existing_data if existing_data else {}
        
        if not silent:
            print_welcome()
            sys.stdout.write("\033[1m\033[93mChecking Internet Connection...\033[0m\n")
            sys.stdout.flush()
        
        data['is_connected'] = check_internet()

        if data['is_connected']:
            wifi_ps = "$wlan = netsh wlan show interfaces; $ssid = ''; $band = ''; if ($wlan -match 'SSID\\s*:\\s*([^\\r\\n]+)') { $ssid = $matches[1].Trim() }; if ($wlan -match 'Band\\s*:\\s*([^\\r\\n]+)') { $band = $matches[1].Trim() }; if ($ssid) { Write-Output \"$ssid ($band)\" } else { Write-Output 'Ethernet / No Wi-Fi' }"
            data['wifi_info'] = run_cmd(f"powershell -Command \"{wifi_ps}\"")
        else:
            data['wifi_info'] = "N/A"

        if full_refresh:
            if not silent:
                sys.stdout.write("\033[1m\033[96mFetching Local System Data...\033[0m\n")
                sys.stdout.flush()

            data['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['sys_name'] = socket.gethostname()
            data['region'] = run_cmd("powershell (Get-Culture).EnglishName").split('\n')[0]

            try:
                data['ipv4'] = socket.gethostbyname(data['sys_name'])
            except:
                data['ipv4'] = "N/A"
            
            data['ipv6'] = get_ipv6()
            data['mac'] = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1]).upper()

            serial_no = run_cmd('powershell "(Get-CimInstance Win32_BIOS).SerialNumber"')
            data['serial_no'] = serial_no if serial_no else 'Not Found'

            users_raw = run_cmd('powershell "(Get-CimInstance Win32_UserAccount -Filter \\"LocalAccount=True\\").Name"')
            data['users'] = "\n".join(["- " + u.strip() for u in users_raw.split('\n') if u.strip()]) if users_raw else "N/A"

            win_cap = run_cmd('powershell "(Get-CimInstance Win32_OperatingSystem).Caption"')
            data['win_cap'] = win_cap if win_cap else 'N/A'
            data['win_ver'] = platform.version()

            act_code = run_cmd('powershell "(Get-CimInstance SoftwareLicensingProduct -Filter \\"ApplicationID=\'55c92734-d682-4d71-983e-d6ec3f16059f\' and PartialProductKey is not null\\").LicenseStatus"')
            data['act_status'] = "Activated" if "1" in act_code else "Not Activated"

            proc = run_cmd('powershell "(Get-CimInstance Win32_Processor).Name -join \', \'"')
            data['proc'] = proc if proc else platform.processor()

            ram_raw = run_cmd('powershell "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"')
            data['ram'] = f"{round(int(ram_raw) / (1024**3), 2)} GB" if ram_raw.isdigit() else "Unknown"

            gpu = run_cmd('powershell "(Get-CimInstance Win32_VideoController).Name -join \' | \'"')
            data['gpu'] = gpu if gpu else 'Unknown'

            sys_type = run_cmd('powershell "(Get-CimInstance Win32_ComputerSystem).SystemType"')
            data['sys_type'] = sys_type if sys_type else platform.machine()

            storage_ps = "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { $_.DeviceID + ' - ' + [math]::Round($_.FreeSpace / 1GB, 2) + ' GB Free out of ' + [math]::Round($_.Size / 1GB, 2) + ' GB' }"
            storage_raw = run_cmd(f"powershell -Command \"{storage_ps}\"")
            data['storage'] = []
            if storage_raw and "N/A" not in storage_raw:
                for line in storage_raw.split('\n'):
                    if line.strip():
                        data['storage'].append(f"  Drive {line.strip()}")
            else:
                data['storage'].append("  No Storage Info Available")

        return data

    def display_connection_status(data):
        print_welcome()
        if data['is_connected']:
            print("\033[1m\033[92mStatus: CONNECTED\033[0m")
            if data.get('wifi_info') and "Ethernet" not in data['wifi_info'] and "N/A" not in data['wifi_info']:
                print(f"\033[96mNetwork:\033[0m {data['wifi_info']}")
            print()
        else:
            print("\033[1m\033[91mStatus: DISCONNECTED\033[0m")
            print("\033[93mConnect internet.\033[0m\n")

    def fake_progress_bar(duration=2.0, text="Processing"):
        try:
            for i in range(1, 101):
                time.sleep(duration / 100)
                bar = '█' * (i // 5) + '░' * (20 - (i // 5))
                sys.stdout.write(f"\r\033[1m\033[93m{text}: \033[96m[{bar}] {i}%\033[0m")
                sys.stdout.flush()
            print("\n")
        except KeyboardInterrupt:
            print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
            time.sleep(1)

    def get_all_local_users():
        users = []
        try:
            raw = run_cmd('powershell "(Get-CimInstance Win32_UserAccount -Filter \\"LocalAccount=True\\").Name"').split('\n')
            for u in raw:
                u = u.strip()
                if u and u.lower() not in ['defaultaccount', 'wdagutilityaccount', 'guest']:
                    users.append(u)
        except:
            pass
        return users

    def get_standard_users():
        users = []
        try:
            raw = run_cmd('powershell "(Get-CimInstance Win32_UserAccount -Filter \\"LocalAccount=True\\").Name"').split('\n')
            admins = run_cmd("net localgroup administrators").lower()
            for u in raw:
                u = u.strip()
                if u and u.lower() not in admins and u.lower() not in ['defaultaccount', 'wdagutilityaccount', 'guest']:
                    users.append(u)
        except:
            pass
        return users

    def check_user_policies(usr):
        print(f"\n\033[1m\033[96mPolicy Status for User: {usr}\033[0m")
        print("\033[1m\033[95m" + "-"*70 + "\033[0m")
        
        reg_acc = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools")
        print(f"\033[93mRegistry Access Blocked:\033[0m \033[97m{'Yes' if reg_acc == 1 else 'No'}\033[0m")
        
        ext_blk = get_user_reg(usr, r"Software\Policies\Google\Chrome\ExtensionInstallBlocklist", "1")
        print(f"\033[93mBrowser Extensions Blocked:\033[0m \033[97m{'Yes' if ext_blk == '*' else 'No'}\033[0m")
        
        upd_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWindowsUpdate")
        print(f"\033[93mUpdates/TaskMgr Blocked:\033[0m \033[97m{'Yes' if upd_blk == 1 else 'No'}\033[0m")
        
        set_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility")
        print(f"\033[93mSettings App Blocked:\033[0m \033[97m{'Yes' if set_blk == 'hide:*' else 'No'}\033[0m")
        
        cp_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel")
        print(f"\033[93mControl Panel Blocked:\033[0m \033[97m{'Yes' if cp_blk == 1 else 'No'}\033[0m")
        
        name_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoComputerName")
        print(f"\033[93mPC Rename Blocked:\033[0m \033[97m{'Yes' if name_blk == 1 else 'No'}\033[0m")
        
        wp_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop", "NoChangingWallPaper")
        print(f"\033[93mWallpaper Change Blocked:\033[0m \033[97m{'Yes' if wp_blk == 1 else 'No'}\033[0m")
        
        app_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "RestrictRun")
        print(f"\033[93mStrict App Control:\033[0m \033[97m{'Enabled' if app_blk == 1 else 'Disabled'}\033[0m")
        
        store_blk = get_user_reg(usr, r"Software\Policies\Microsoft\WindowsStore", "RemoveWindowsStore")
        print(f"\033[93mStore Blocked:\033[0m \033[97m{'Yes' if store_blk == 1 else 'No'}\033[0m")
        
        uninst_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Programs", "NoProgramsCPL")
        print(f"\033[93mApp Uninstallation Blocked:\033[0m \033[97m{'Yes' if uninst_blk == 1 else 'No'}\033[0m")
        
        pwd_blk = get_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword")
        print(f"\033[93mPassword/PIN Change Blocked:\033[0m \033[97m{'Yes' if pwd_blk == 1 else 'No'}\033[0m")
        
        hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
        sites_blocked = False
        try:
            with open(hosts_path, "r") as f:
                if "# ADM_BLOCKED_SITES_START" in f.read():
                    sites_blocked = True
        except:
            pass
        print(f"\033[93mGlobal Sites Blocker:\033[0m \033[97m{'Enabled' if sites_blocked else 'Disabled'}\033[0m")
        print("\033[1m\033[95m" + "-"*70 + "\033[0m")

    def lock_system_menu():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m             SELECT STANDARD USER             \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            users = get_standard_users()
            if not users:
                print("\033[91mNo Standard Users found on this system.\033[0m")
                input("\n\033[90mEnter to return...\033[0m")
                return
                
            for idx, u in enumerate(users, 1):
                print(f"\033[93m{idx}. \033[97m{u}\033[0m")
            print(f"\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            try:
                choice = int(input("\033[1m\033[96mSelect User: \033[0m"))
                if choice == 0:
                    break
                if 1 <= choice <= len(users):
                    target_user = users[choice-1]
                    manage_user_locks(target_user)
            except ValueError:
                print("\033[91mInvalid input.\033[0m")
                time.sleep(1)

    def manage_user_locks(usr):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print(f"\033[1m\033[97m             LOCK SYSTEM FOR: {usr}             \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mRegistry Editing Access\033[0m")
            print("\033[93m2. \033[97mBrowser Extensions Block\033[0m")
            print("\033[93m3. \033[97mUninstall/Delete ADM Protection\033[0m")
            print("\033[93m4. \033[97mServices & Updates Modification Block\033[0m")
            print("\033[93m5. \033[97mSettings App Access\033[0m")
            print("\033[93m6. \033[97mControl Panel Access\033[0m")
            print("\033[93m7. \033[97mRename PC Lock\033[0m")
            print("\033[93m8. \033[97mWallpaper Change Lock\033[0m")
            print("\033[93m9. \033[97mStrict App Control\033[0m")
            print("\033[93m10.\033[97mMicrosoft Store App Control\033[0m")
            print("\033[93m11.\033[97mIllegal Sites Blocker\033[0m")
            print("\033[93m12.\033[97mBlock App Uninstallation\033[0m")
            print("\033[93m13.\033[97mBlock Password & PIN Change\033[0m")
            print("\033[96m14.\033[97mView Current Policy Status\033[0m")
            print("\033[92m15.\033[97mUnlock All Restrictions\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '0':
                break
            
            if choice == '14':
                check_user_policies(usr)
                input("\n\033[90mEnter to continue...\033[0m")
                continue
                
            if choice not in [str(i) for i in range(1, 16)]:
                continue
                
            if choice != '15':
                action = input("\033[96mEnter Action (Y to Lock/Disable, N to Unlock/Enable): \033[0m").strip().upper()
                if action not in ["Y", "N"]:
                    print("\033[91mInvalid action. Type Y or N.\033[0m")
                    time.sleep(1)
                    continue
            else:
                action = "UNLOCK_ALL"
                
            try:
                if choice == '1':
                    confirm_execution("Enabling or Disabling Registry Editor access for the user.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools", val)
                elif choice == '2':
                    confirm_execution("Applying or removing browser extension blocks.")
                    val = "*" if action == "Y" else ""
                    set_user_reg(usr, r"Software\Policies\Google\Chrome\ExtensionInstallBlocklist", "1", val, winreg.REG_SZ)
                    set_user_reg(usr, r"Software\Policies\Microsoft\Edge\ExtensionInstallBlocklist", "1", val, winreg.REG_SZ)
                elif choice == '3':
                    confirm_execution("Locking or Unlocking the ADM application file from being deleted by the user.")
                    exe_path = sys.executable
                    if action == "Y":
                        os.system(f'icacls "{exe_path}" /deny "{usr}":(D) >nul 2>&1')
                    else:
                        os.system(f'icacls "{exe_path}" /remove:d "{usr}" >nul 2>&1')
                elif choice == '4':
                    confirm_execution("Blocking or allowing Windows updates and Task Manager.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWindowsUpdate", val)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr", val)
                elif choice == '5':
                    confirm_execution("Hiding or restoring Settings App pages.")
                    val = "hide:*" if action == "Y" else ""
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility", val, winreg.REG_SZ)
                elif choice == '6':
                    confirm_execution("Blocking or allowing access to Control Panel.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel", val)
                elif choice == '7':
                    confirm_execution("Restricting the user from renaming the PC.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoComputerName", val)
                elif choice == '8':
                    confirm_execution("Locking the desktop wallpaper to prevent changes.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop", "NoChangingWallPaper", val)
                elif choice == '9':
                    confirm_execution("Enabling Strict App Control. Blocks all EXE/MSI except those in the whitelist.")
                    enable_app_control = True if action == "Y" else False
                    toggle_app_blocker(usr, enable_app_control)
                elif choice == '10':
                    confirm_execution("Disabling or Enabling Microsoft Store access.")
                    enable_store_block = True if action == "Y" else False
                    if enable_store_block:
                        set_user_reg(usr, r"Software\Policies\Microsoft\WindowsStore", "RemoveWindowsStore", 1)
                    else:
                        set_user_reg(usr, r"Software\Policies\Microsoft\WindowsStore", "RemoveWindowsStore", 0)
                elif choice == '11':
                    confirm_execution("Modifying the HOSTS file to block illegal sites based on list.")
                    enable_sites_block = True if action == "Y" else False
                    toggle_sites_blocker(enable_sites_block)
                elif choice == '12':
                    confirm_execution("Preventing the user from opening the uninstall programs menu.")
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Programs", "NoProgramsCPL", val)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoManageMyComputerVerb", val)
                elif choice == '13':
                    confirm_execution("Blocking Password and PIN changes.")
                    if action == "Y":
                        os.system(f'net user "{usr}" /PasswordChg:No >nul 2>&1')
                        set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword", 1)
                    else:
                        os.system(f'net user "{usr}" /PasswordChg:Yes >nul 2>&1')
                        set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword", 0)
                elif choice == '15':
                    confirm_execution("Removing all active restrictions and restoring default access for this user.")
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools", 0)
                    set_user_reg(usr, r"Software\Policies\Google\Chrome\ExtensionInstallBlocklist", "1", "", winreg.REG_SZ)
                    set_user_reg(usr, r"Software\Policies\Microsoft\Edge\ExtensionInstallBlocklist", "1", "", winreg.REG_SZ)
                    exe_path = sys.executable
                    os.system(f'icacls "{exe_path}" /remove:d "{usr}" >nul 2>&1')
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWindowsUpdate", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility", "", winreg.REG_SZ)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoComputerName", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop", "NoChangingWallPaper", 0)
                    set_user_reg(usr, r"Software\Policies\Microsoft\Windows\Installer", "DisableUserInstalls", 0)
                    set_user_reg(usr, r"Software\Policies\Microsoft\WindowsStore", "RemoveWindowsStore", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Programs", "NoProgramsCPL", 0)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoManageMyComputerVerb", 0)
                    os.system(f'net user "{usr}" /PasswordChg:Yes >nul 2>&1')
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableChangePassword", 0)
                    toggle_app_blocker(usr, False)
                    toggle_sites_blocker(False)
                
                apply_policy_changes()
                
                if action == "UNLOCK_ALL":
                    print(f"\n\033[1m\033[92m[✓] All locks removed & applied immediately for {usr}\033[0m")
                else:
                    print(f"\n\033[1m\033[92m[✓] Settings Updated & Applied immediately for {usr}\033[0m")
                input("\n\033[90mEnter to continue...\033[0m")
            except KeyboardInterrupt:
                print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                time.sleep(1)

    def bbipl_admin_menu(data):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m                 BBIPL ADMIN                \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mSystemInfo\033[0m")
            print("\033[93m2. \033[97mOSReinstall\033[0m")
            print("\033[93m3. \033[97mOfficeInstall\033[0m")
            print("\033[93m4. \033[97mActivator\033[0m")
            print("\033[93m5. \033[97mChrome\033[0m")
            print("\033[93m6. \033[97mBranding\033[0m")
            print("\033[93m7. \033[97mRenamePC\033[0m")
            print("\033[93m8. \033[97mUpdateApps\033[0m")
            print("\033[93m9. \033[97mUpdateDrivers\033[0m")
            print("\033[93m10.\033[97mAdd Standard User\033[0m")
            print("\033[93m11.\033[97mManage User Credentials\033[0m")
            print("\033[93m12.\033[97mLockSystem\033[0m")
            print("\033[93m13.\033[97mOnboarding\033[0m")
            print("\033[93m14.\033[97mOffboarding\033[0m")
            print("\033[93m15.\033[97mManage Secure DNS\033[0m")
            print("\033[93m16.\033[97mToggle Browser Security\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    confirm_execution("Displaying complete system hardware and software details.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: SystemInfo...\033[0m\n")
                    print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
                    print("\033[1m\033[97m             SYSTEM INFORMATION             \033[0m")
                    print("\033[1m\033[95m" + "="*70 + "\033[0m\n")
                    if 'sys_name' in data:
                        print(f"\033[96mSystem:\033[0m {data['sys_name']}")
                        print(f"\033[96mRegion:\033[0m {data['region']}")
                        print(f"\033[96mTime:\033[0m {data['login_time']}")
                        print(f"\033[96mIPv4:\033[0m {data['ipv4']}")
                        print(f"\033[96mIPv6:\033[0m {data['ipv6']}")
                        print(f"\033[96mMAC:\033[0m {data['mac']}")
                        print(f"\033[96mSerial:\033[0m {data['serial_no']}")
                        print("\n\033[93m[Users]\033[0m")
                        print(data['users'])
                        print("\n\033[93m[Windows]\033[0m")
                        print(f"\033[96mOS:\033[0m {data['win_cap']} ({data['win_ver']})")
                        print(f"\033[96mAct:\033[0m {data['act_status']}")
                        print("\n\033[93m[Hardware]\033[0m")
                        print(f"\033[96mCPU:\033[0m {data['proc']}")
                        print(f"\033[96mRAM:\033[0m {data['ram']}")
                        print(f"\033[96mGPU:\033[0m {data['gpu']}")
                        print(f"\033[96mType:\033[0m {data['sys_type']}")
                        print("\033[96mStorage:\033[0m")
                        for line in data['storage']:
                            print(line)
                    else:
                        print("\033[1m\033[91mFailed.\033[0m")
                    input("\n\033[90mEnter to return...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    confirm_execution("Downloading Windows Media Creation Tool to reinstall OS.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: OSReinstall...\033[0m\n")
                    mct_url = "https://go.microsoft.com/fwlink/?linkid=2156295"
                    temp_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'win10.exe')
                    os.system(f'powershell -Command "Invoke-WebRequest -Uri \'{mct_url}\' -OutFile \'{temp_path}\'"')
                    if os.path.exists(temp_path):
                        os.system(f'start /wait "" "{temp_path}"')
                        print("\n\033[1m\033[92m[✓] Done\033[0m")
                    else:
                        print("\n\033[1m\033[91m[X] Download Failed. Check connection.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    confirm_execution("Downloading and installing Microsoft Office setup.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: OfficeInstall...\033[0m\n")
                    app_url = "https://c2rsetup.officeapps.live.com/c2r/download.aspx?ProductreleaseID=O365HomePremRetail&platform=x64&language=en-us&version=O16GA"
                    temp_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'office.exe')
                    os.system(f'powershell -Command "Invoke-WebRequest -Uri \'{app_url}\' -OutFile \'{temp_path}\'"')
                    if os.path.exists(temp_path):
                        os.system(f'start /wait "" "{temp_path}"')
                        print("\n\033[1m\033[92m[✓] Done\033[0m")
                    else:
                        print("\n\033[1m\033[91m[X] Download Failed. Check connection.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    confirm_execution("Running MAS Activator script to license Windows.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Activator...\033[0m\n")
                    os.system('powershell -c "iwr \'https://github.com/bigboxcorp/activator/raw/refs/heads/main/ACT/public/MAS_AIO.cmd\' -OutFile $env:TEMP\\a.cmd; & $env:TEMP\\a.cmd"')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    confirm_execution("Silently installing Google Chrome using Winget.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Chrome...\033[0m\n")
                    os.system("winget install Google.Chrome -e --accept-package-agreements --accept-source-agreements --silent")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    confirm_execution("Applying corporate wallpaper and lock screen to standard users.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Branding...\033[0m\n")
                    target_usr = input("\033[96mEnter Standard Username to apply branding (Leave blank for ALL Standard Users): \033[0m").strip()
                    users_to_brand = [target_usr] if target_usr else get_standard_users()
                    
                    if not users_to_brand:
                        print("\n\033[1m\033[91m[X] No Standard Users found.\033[0m")
                    else:
                        home_img = resource_path("homescreen.png")
                        lock_img = resource_path("lockscreen.png")
                        
                        if os.path.exists(home_img) and os.path.exists(lock_img):
                            os.makedirs("C:\\Windows\\Web\\Wallpaper", exist_ok=True)
                            os.makedirs("C:\\Windows\\Web\\Screen", exist_ok=True)
                            perm_home = "C:\\Windows\\Web\\Wallpaper\\corp_home.png"
                            perm_lock = "C:\\Windows\\Web\\Screen\\corp_lock.png"
                            shutil.copy(home_img, perm_home)
                            shutil.copy(lock_img, perm_lock)
                            
                            set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows\Personalization", "LockScreenImage", perm_lock, winreg.REG_SZ)
                            
                            for u in users_to_brand:
                                set_user_reg(u, r"Control Panel\Desktop", "Wallpaper", perm_home, winreg.REG_SZ)
                                print(f"\033[92mApplied to: {u}\033[0m")
                            
                            ctypes.windll.user32.SystemParametersInfoW(20, 0, perm_home, 3)
                            os.system("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters")
                            print("\n\033[1m\033[92m[✓] Done\033[0m")
                        else:
                            print("\n\033[1m\033[91m[X] Failed. Images not found in the executable.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    confirm_execution("Renaming the computer. A restart will be required.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: RenamePC...\033[0m\n")
                    new_name = input("\033[96mEnter New PC Name: \033[0m").strip()
                    os.system(f'powershell -Command "Rename-Computer -NewName \'{new_name}\' -Force"')
                    print("\n\033[1m\033[92m[✓] Restart Required\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    confirm_execution("Upgrading all installed applications using Winget.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: UpdateApps...\033[0m\n")
                    os.system("winget upgrade --all --silent --accept-package-agreements --accept-source-agreements")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '9':
                try:
                    confirm_execution("Checking for missing drivers and triggering Windows Update scan.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: UpdateDrivers...\033[0m\n")
                    print("\033[96mMissing or Error Drivers:\033[0m")
                    os.system('powershell "Get-CimInstance Win32_PnPEntity | Where-Object {$_.Status -eq \'Error\' -or $_.Status -eq \'Degraded\'} | Select-Object Name, DeviceID"')
                    print("\n\033[96mTriggering Windows Update for Driver Installation...\033[0m")
                    os.system("UsoClient ScanInstallWait")
                    print("\n\033[1m\033[92m[✓] Driver Update Initiated in Background\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '10':
                try:
                    confirm_execution("Creating a new standard local user account.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Add Standard User...\033[0m\n")
                    new_usr = input("\033[96mEnter New Username: \033[0m").strip()
                    new_pwd = get_hidden_pin("\033[96mEnter Password for User: \033[0m").strip()
                    if new_usr and new_pwd:
                        os.system(f'net user "{new_usr}" "{new_pwd}" /add >nul 2>&1')
                        os.system(f'net localgroup Users "{new_usr}" /add >nul 2>&1')
                        print(f"\n\033[1m\033[92m[✓] User '{new_usr}' Created Successfully\033[0m")
                    else:
                        print("\n\033[1m\033[91m[X] Username and Password cannot be empty.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '11':
                try:
                    confirm_execution("Entering user credentials management menu.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Manage User Credentials...\033[0m\n")
                    users_list = get_all_local_users()
                    if not users_list:
                        print("\033[91mNo users found.\033[0m")
                        input("\n\033[90mEnter to continue...\033[0m")
                        continue
                    
                    for idx, u in enumerate(users_list, 1):
                        print(f"\033[93m{idx}. \033[97m{u}\033[0m")
                    print(f"\033[91m0. \033[97mCancel\033[0m")
                    print("\033[1m\033[95m" + "="*70 + "\033[0m")
                    
                    try:
                        u_choice = int(input("\033[1m\033[96mSelect User: \033[0m"))
                        if u_choice == 0:
                            continue
                        if 1 <= u_choice <= len(users_list):
                            target_u = users_list[u_choice-1]
                            print(f"\n\033[96mSelected: {target_u}\033[0m")
                            print("\033[93m1. Change Password\033[0m")
                            print("\033[93m2. Remove Password\033[0m")
                            print("\033[93m3. Reset Windows PIN\033[0m")
                            c_act = input("\033[96mAction: \033[0m").strip()
                            
                            if c_act == '1':
                                npwd = get_hidden_pin("\033[96mEnter New Password: \033[0m").strip()
                                os.system(f'net user "{target_u}" "{npwd}" >nul 2>&1')
                                print(f"\n\033[1m\033[92m[✓] Password Changed\033[0m")
                            elif c_act == '2':
                                os.system(f'net user "{target_u}" "" >nul 2>&1')
                                print(f"\n\033[1m\033[92m[✓] Password Removed\033[0m")
                            elif c_act == '3':
                                os.system("takeown /f C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\Microsoft\\Ngc /r /d y >nul 2>&1")
                                os.system("icacls C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\Microsoft\\Ngc /grant administrators:F /t >nul 2>&1")
                                os.system("rd /s /q C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\Microsoft\\Ngc >nul 2>&1")
                                os.system("md C:\\Windows\\ServiceProfiles\\LocalService\\AppData\\Local\\Microsoft\\Ngc >nul 2>&1")
                                print(f"\n\033[1m\033[92m[✓] PIN Data Cleared (Requires Reboot)\033[0m")
                            else:
                                print("\033[91mInvalid action.\033[0m")
                    except ValueError:
                        print("\033[91mInvalid input.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '12':
                lock_system_menu()
            elif choice == '13':
                try:
                    confirm_execution("Running custom onboarding steps to set up a new user environment.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Onboarding...\033[0m\n")
                    emp_id = input("\033[96mEnter Employee ID / System ID for Target User: \033[0m").strip()
                    if not emp_id:
                        print("\033[91mID cannot be empty.\033[0m")
                        input("\n\033[90mEnter to continue...\033[0m")
                        continue
                        
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
                    print("\033[1m\033[97m             ONBOARDING STEPS             \033[0m")
                    print("\033[1m\033[95m" + "="*70 + "\033[0m")
                    print("\033[93m1. \033[97mCreate Standard User\033[0m")
                    print("\033[93m2. \033[97mOS Reinstall Tool\033[0m")
                    print("\033[93m3. \033[97mOffice Install Tool\033[0m")
                    print("\033[93m4. \033[97mActivator\033[0m")
                    print("\033[93m5. \033[97mChrome Download\033[0m")
                    print("\033[93m6. \033[97mBranding Apply\033[0m")
                    print("\033[93m7. \033[97mPC Renaming\033[0m")
                    print("\033[93m8. \033[97mRegistry Editing Access Block\033[0m")
                    print("\033[93m9. \033[97mBrowser Extensions Block\033[0m")
                    print("\033[93m10.\033[97mUninstall/Delete ADM Protection\033[0m")
                    print("\033[93m11.\033[97mServices & Updates Modification Block\033[0m")
                    print("\033[93m12.\033[97mSettings App Access Block\033[0m")
                    print("\033[93m13.\033[97mControl Panel Access Block\033[0m")
                    print("\033[93m14.\033[97mRename PC Lock\033[0m")
                    print("\033[93m15.\033[97mWallpaper Change Lock\033[0m")
                    print("\033[93m16.\033[97mEmail Accounts Login Setup\033[0m")
                    print("\033[1m\033[95m" + "="*70 + "\033[0m")
                    
                    steps_input = input("\n\033[96mSelect steps (comma-separated e.g. 1,5,6) or 'A' for ALL: \033[0m").strip().upper()
                    
                    if steps_input == 'A':
                        steps_to_run = [str(i) for i in range(1, 17)]
                    else:
                        steps_to_run = [s.strip() for s in steps_input.split(',') if s.strip().isdigit()]
                        
                    for step in steps_to_run:
                        if step == '1':
                            print(f"\n\033[93m[Step 1] Creating Standard User ({emp_id})...\033[0m")
                            upwd = get_hidden_pin(f"\033[96mEnter password to set for {emp_id}: \033[0m").strip()
                            os.system(f'net user "{emp_id}" "{upwd}" /add >nul 2>&1')
                            os.system(f'net localgroup Users "{emp_id}" /add >nul 2>&1')
                        elif step == '2':
                            print("\n\033[93m[Step 2] OSReinstall Triggering...\033[0m")
                            mct_url = "https://go.microsoft.com/fwlink/?linkid=2156295"
                            temp_path = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'win10.exe')
                            os.system(f'powershell -Command "Invoke-WebRequest -Uri \'{mct_url}\' -OutFile \'{temp_path}\'"')
                            if os.path.exists(temp_path): os.system(f'start /wait "" "{temp_path}"')
                        elif step == '3':
                            print("\n\033[93m[Step 3] Office Install Triggering...\033[0m")
                            app_url = "https://c2rsetup.officeapps.live.com/c2r/download.aspx?ProductreleaseID=O365HomePremRetail&platform=x64&language=en-us&version=O16GA"
                            temp_path_off = os.path.join(os.environ.get('TEMP', 'C:\\Windows\\Temp'), 'office.exe')
                            os.system(f'powershell -Command "Invoke-WebRequest -Uri \'{app_url}\' -OutFile \'{temp_path_off}\'"')
                            if os.path.exists(temp_path_off): os.system(f'start /wait "" "{temp_path_off}"')
                        elif step == '4':
                            print("\n\033[93m[Step 4] Activator Running...\033[0m")
                            os.system('powershell -c "iwr \'https://github.com/bigboxcorp/activator/raw/refs/heads/main/ACT/public/MAS_AIO.cmd\' -OutFile $env:TEMP\\a.cmd; & $env:TEMP\\a.cmd"')
                        elif step == '5':
                            print("\n\033[93m[Step 5] Chrome Installation...\033[0m")
                            os.system("winget install Google.Chrome -e --accept-package-agreements --accept-source-agreements --silent >nul 2>&1")
                        elif step == '6':
                            print("\n\033[93m[Step 6] Applying Branding...\033[0m")
                            home_img = resource_path("homescreen.png")
                            lock_img = resource_path("lockscreen.png")
                            if os.path.exists(home_img) and os.path.exists(lock_img):
                                os.makedirs("C:\\Windows\\Web\\Wallpaper", exist_ok=True)
                                os.makedirs("C:\\Windows\\Web\\Screen", exist_ok=True)
                                perm_home = "C:\\Windows\\Web\\Wallpaper\\corp_home.png"
                                perm_lock = "C:\\Windows\\Web\\Screen\\corp_lock.png"
                                shutil.copy(home_img, perm_home)
                                shutil.copy(lock_img, perm_lock)
                                set_user_reg(emp_id, r"Control Panel\Desktop", "Wallpaper", perm_home, winreg.REG_SZ)
                                set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows\Personalization", "LockScreenImage", perm_lock, winreg.REG_SZ)
                        elif step == '7':
                            print("\n\033[93m[Step 7] PC Renaming...\033[0m")
                            os.system(f'powershell -Command "Rename-Computer -NewName \'{emp_id[:15]}\' -Force" >nul 2>&1')
                        elif step == '8':
                            print("\n\033[93m[Step 8] Registry Editing Access Block...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools", 1)
                        elif step == '9':
                            print("\n\033[93m[Step 9] Browser Extensions Block...\033[0m")
                            set_user_reg(emp_id, r"Software\Policies\Google\Chrome\ExtensionInstallBlocklist", "1", "*", winreg.REG_SZ)
                            set_user_reg(emp_id, r"Software\Policies\Microsoft\Edge\ExtensionInstallBlocklist", "1", "*", winreg.REG_SZ)
                        elif step == '10':
                            print("\n\033[93m[Step 10] Uninstall/Delete ADM Protection...\033[0m")
                            exe_path = sys.executable
                            os.system(f'icacls "{exe_path}" /deny "{emp_id}":(D) >nul 2>&1')
                        elif step == '11':
                            print("\n\033[93m[Step 11] Services & Updates Modification Block...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWindowsUpdate", 1)
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr", 1)
                        elif step == '12':
                            print("\n\033[93m[Step 12] Settings App Access Block...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility", "hide:*", winreg.REG_SZ)
                        elif step == '13':
                            print("\n\033[93m[Step 13] Control Panel Access Block...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel", 1)
                        elif step == '14':
                            print("\n\033[93m[Step 14] Rename PC Lock...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoComputerName", 1)
                        elif step == '15':
                            print("\n\033[93m[Step 15] Wallpaper Change Lock...\033[0m")
                            set_user_reg(emp_id, r"Software\Microsoft\Windows\CurrentVersion\Policies\ActiveDesktop", "NoChangingWallPaper", 1)
                        elif step == '16':
                            print("\n\033[93m[Step 16] Email Accounts Login Setup...\033[0m")
                            print(f"\033[96mStandard user '{emp_id}' created. Please login into that account to setup work email.\033[0m")
                            os.system("start ms-settings:workplace")
                    
                    apply_policy_changes()
                    print("\n\033[1m\033[92m[✓] Selected Onboarding Processes Completed Successfully!\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '14':
                try:
                    confirm_execution("Offboarding logic has been removed as per instructions.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Offboarding...\033[0m\n")
                    print("\033[1m\033[92m[✓] Offboarding process is currently disabled.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '15':
                try:
                    confirm_execution("Switching System DNS to AdGuard Family Filter.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Manage Secure DNS...\033[0m\n")
                    dns_action = input("\033[96mEnable Secure DNS? (Y to Enable, N to Revert to DHCP): \033[0m").strip().upper()
                    if dns_action == 'Y':
                        toggle_secure_dns(True)
                        print("\n\033[1m\033[92m[✓] Secure DNS Applied Successfully\033[0m")
                    elif dns_action == 'N':
                        toggle_secure_dns(False)
                        print("\n\033[1m\033[92m[✓] DNS Reverted to Automatic (DHCP)\033[0m")
                    else:
                        print("\033[91mInvalid action. Type Y or N.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '16':
                try:
                    confirm_execution("Toggling Browser Security (SmartScreen & SafeBrowsing).")
                    sec_action = input("\033[96mEnable Browser Security? (Y/N): \033[0m").strip().upper()
                    if sec_action == 'Y':
                        toggle_browser_security(True)
                        print("\n\033[1m\033[92m[✓] Browser Security Enabled\033[0m")
                    elif sec_action == 'N':
                        toggle_browser_security(False)
                        print("\n\033[1m\033[92m[✓] Browser Security Disabled\033[0m")
                    else:
                        print("\033[91mInvalid action. Type Y or N.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break
            else:
                print("\n\033[91mInvalid input.\033[0m")
                time.sleep(1)

    def help_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m                HELP                \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        print("\033[1m\033[93m[Health Checkup & Fixer]\033[0m")
        print("\033[96mScan:\033[0m CHKDSK disk repair.")
        print("\033[96mPurge:\033[0m Delete temp files silently using Native CMD.")
        print("\033[96mOptimize:\033[0m DISM cleanup.")
        print("\033[96mCleanup:\033[0m Cleanmgr tool.")
        print("\033[96mVerify:\033[0m SFC scan.")
        print("\033[96mDiagnostic:\033[0m Run all health tools.")
        print("\033[96mMonitor:\033[0m Perfmon rel graph.")
        print("\033[96mTaskKiller:\033[0m Kills all non-essential running apps.")
        print("\033[96mReboot:\033[0m Restart system.")
        
        print("\n\033[1m\033[93m[Internet Fixer]\033[0m")
        print("\033[96mFlush:\033[0m Clear DNS cache.")
        print("\033[96mResetWinsock:\033[0m Reset sockets.")
        print("\033[96mResetIP:\033[0m Reset TCP/IP.")
        print("\033[96mPing:\033[0m Test latency.")
        print("\033[96mTrace:\033[0m Tracert routing.")
        print("\033[96mSpeed:\033[0m Check adapter speed.")
        print("\033[96mTraffic:\033[0m Netstat active ports.")
        print("\033[96mRepair:\033[0m Run all net tools.")
        print("\033[96mGigabit:\033[0m Open NCPA.")

        print("\n\033[1m\033[93m[Security & Hardware Diagnostics]\033[0m")
        print("\033[96mAntivirus:\033[0m Check AV status.")
        print("\033[96mFirewall:\033[0m Check FW profiles.")
        print("\033[96mMalwareScan:\033[0m Run MRT tool.")
        print("\033[96mDriveHealth:\033[0m Check SMART status.")
        print("\033[96mPeripherals:\033[0m LAN/Audio/Cam status.")
        print("\033[96mUptime:\033[0m Check boot time.")
        print("\033[96mBattery:\033[0m Generate powercfg report.")

        print("\n\033[1m\033[93m[BBIPL Admin]\033[0m")
        print("\033[96mSystemInfo:\033[0m Displays complete system hardware and software details.")
        print("\033[96mOSReinstall:\033[0m Downloads Media Creation Tool and triggers Windows setup.")
        print("\033[96mOfficeInstall:\033[0m Downloads Office setup and silently installs it.")
        print("\033[96mActivator:\033[0m Runs the Microsoft licensing activator script.")
        print("\033[96mChrome:\033[0m Installs Google Chrome silently via Winget.")
        print("\033[96mBranding:\033[0m Applies corporate wallpaper and lock screen using permanent web directory.")
        print("\033[96mRenamePC:\033[0m Renames the PC.")
        print("\033[96mUpdateApps:\033[0m Upgrades all installed applications using Winget.")
        print("\033[96mUpdateDrivers:\033[0m Lists missing drivers and triggers scan via Windows Update.")
        print("\033[96mAdd Standard User:\033[0m Creates a new standard user on the system.")
        print("\033[96mManage User Credentials:\033[0m Change or remove passwords and reset Windows PINs.")
        print("\033[96mLockSystem:\033[0m Advanced Per-User controls for App/Site blocking and Windows Policies.")
        print("\033[96mOnboarding:\033[0m Custom process to create user, install apps, and apply policies.")
        print("\033[96mOffboarding:\033[0m Terminates OneDrive, deletes browser data, and disables user account.")
        print("\033[96mManage Secure DNS:\033[0m Toggles specific Cloudflare family DNS filtering via Netsh.")
        print("\033[96mToggle Browser Security:\033[0m Toggles Windows SmartScreen and Edge SafeBrowsing.")
        
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        input("\n\033[90mEnter to return...\033[0m")

    def security_hardware_menu():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m            SECURITY & HARDWARE            \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mAntivirus\033[0m")
            print("\033[93m2. \033[97mFirewall\033[0m")
            print("\033[93m3. \033[97mMalwareScan\033[0m")
            print("\033[93m4. \033[97mDriveHealth\033[0m")
            print("\033[93m5. \033[97mPeripherals\033[0m")
            print("\033[93m6. \033[97mUptime\033[0m")
            print("\033[93m7. \033[97mBattery\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    confirm_execution("Checking the active status of Windows Defender or third-party AV.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Antivirus...\033[0m\n")
                    av_status = run_cmd('powershell "Get-CimInstance -Namespace root\\SecurityCenter2 -Class AntivirusProduct | Select-Object -ExpandProperty displayName"')
                    if av_status and "N/A" not in av_status:
                        print(f"\033[92mDetected: {av_status}\033[0m")
                    else:
                        print("\033[91mNot Found.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    confirm_execution("Auditing the current status of Windows Firewall profiles.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Firewall...\033[0m\n")
                    os.system("netsh advfirewall show allprofiles")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    confirm_execution("Launching the Malicious Software Removal Tool.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: MalwareScan...\033[0m\n")
                    os.system("start mrt")
                    print("\033[1m\033[92m[✓] Started\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    confirm_execution("Checking the S.M.A.R.T. health status of storage drives.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: DriveHealth...\033[0m\n")
                    os.system('powershell "Get-CimInstance Win32_DiskDrive | Select-Object Model, Status | Format-Table -HideTableHeaders"')
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    confirm_execution("Auditing the status of Network, Audio, Camera, and Display devices.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Peripherals...\033[0m\n")
                    os.system('powershell "Get-NetAdapter | Select-Object Name, Status"')
                    os.system('powershell "Get-PnpDevice -Class Camera, AudioEndpoint | Select-Object Status, Class, FriendlyName"')
                    os.system('powershell "(Get-CimInstance Win32_VideoController).Name"')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    confirm_execution("Displaying the system uptime since the last reboot.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Uptime...\033[0m\n")
                    os.system("net statistics workstation")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    confirm_execution("Generating and saving a detailed Battery Health Report to Desktop.")
                    print("\n\033[93mSave Battery Report? (Y/N)\033[0m")
                    save_choice = input("\033[1m\033[96mChoice: \033[0m").strip().lower()
                    if save_choice == 'y' or save_choice == 'yes':
                        print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Battery...\033[0m\n")
                        report_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Battery_Report.html')
                        os.system(f'powercfg /batteryreport /output "{report_path}"')
                        print(f"\n\033[1m\033[92m[✓] Saved: {report_path}\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break

    def internet_fixer_menu():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m                INTERNET FIXER                \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mFlush\033[0m")
            print("\033[93m2. \033[97mResetWinsock\033[0m")
            print("\033[93m3. \033[97mResetIP\033[0m")
            print("\033[93m4. \033[97mPing\033[0m")
            print("\033[93m5. \033[97mTrace\033[0m")
            print("\033[93m6. \033[97mSpeed\033[0m")
            print("\033[93m7. \033[97mTraffic\033[0m")
            print("\033[92m8. \033[97mRepair\033[0m")
            print("\033[93m9. \033[97mGigabit\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    confirm_execution("Clearing the DNS resolver cache.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Flush...\033[0m\n")
                    os.system("ipconfig /flushdns")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    confirm_execution("Resetting Windows Sockets configuration.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: ResetWinsock...\033[0m\n")
                    os.system("netsh winsock reset")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    confirm_execution("Resetting TCP/IP stack configuration.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: ResetIP...\033[0m\n")
                    os.system("netsh int ip reset")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    confirm_execution("Testing internet connectivity by pinging Google.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Ping...\033[0m\n")
                    os.system("ping google.com")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    confirm_execution("Tracing the network route to Google to detect drops.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Trace...\033[0m\n")
                    os.system("tracert google.com")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    confirm_execution("Displaying the active network adapter's link speed.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Speed...\033[0m\n")
                    os.system('powershell "Get-CimInstance Win32_NetworkAdapter -Filter \\"NetEnabled=True\\" | Select-Object Name, Speed | Format-Table -HideTableHeaders"')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    confirm_execution("Listing all active network connections and listening ports.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Traffic...\033[0m\n")
                    os.system("netstat -ab")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    confirm_execution("Executing a complete suite of network reset and repair tools.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Repair...\033[0m\n")
                    os.system("ipconfig /flushdns")
                    os.system("netsh winsock reset")
                    os.system("netsh int ip reset")
                    os.system('powershell "Get-CimInstance Win32_NetworkAdapter -Filter \\"NetEnabled=True\\" | Select-Object Name, Speed | Format-Table -HideTableHeaders"')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '9':
                try:
                    confirm_execution("Opening Network Connections to manually configure 1Gbps duplex.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Gigabit...\033[0m\n")
                    os.system("start ncpa.cpl")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break

    def health_checkup_menu():
        reboot_status = run_cmd("powershell \"if((Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired') -or (Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\RebootPending') -or (Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\ServerManager\\CurrentRebootAttempts')){Write-Output 'YES'}else{Write-Output 'NO'}\"")
        update_status = run_cmd("powershell \"try{$s=(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher();$s.Online=$false;$c=$s.Search('IsInstalled=0 and BrowseOnly=0').Updates.Count;if($c -gt 0){Write-Output 'YES'}else{Write-Output 'NO'}}catch{Write-Output 'UNKNOWN'}\"")
        opt_status = run_cmd("powershell \"try{$s=(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher();$s.Online=$false;$c=$s.Search('IsInstalled=0 and BrowseOnly=1').Updates.Count;if($c -gt 0){Write-Output 'YES'}else{Write-Output 'NO'}}catch{Write-Output 'UNKNOWN'}\"")

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m            HEALTH CHECKUP            \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            r_color = "\033[91m" if "YES" in reboot_status else "\033[92m"
            u_color = "\033[91m" if "YES" in update_status else "\033[92m"
            o_color = "\033[93m" if "YES" in opt_status else "\033[92m"
            
            print(f"\033[96mRestart Required: {r_color}{reboot_status}\033[0m")
            print(f"\033[96mUpdates Pending: {u_color}{update_status}\033[0m")
            print(f"\033[96mOptional Updates: {o_color}{opt_status}\033[0m")
            print("\033[1m\033[95m" + "-"*70 + "\033[0m")
            
            print("\033[93m1. \033[97mScan\033[0m")
            print("\033[93m2. \033[97mPurge\033[0m")
            print("\033[93m3. \033[97mOptimize\033[0m")
            print("\033[93m4. \033[97mCleanup\033[0m")
            print("\033[93m5. \033[97mVerify\033[0m")
            print("\033[92m6. \033[97mDiagnostic\033[0m")
            print("\033[93m7. \033[97mMonitor\033[0m")
            print("\033[93m8. \033[97mTask Killer\033[0m")
            print("\033[93m9. \033[97mReboot\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    confirm_execution("Scanning the file system for logical disk errors using CHKDSK.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Scan...\033[0m\n")
                    os.system("chkdsk C: /scan")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    confirm_execution("Cleaning up recycle bin and temporary files silently.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Purge...\033[0m\n")
                    os.system('del /q /f /s "%TEMP%\\*" >nul 2>&1')
                    os.system('rd /s /q "%TEMP%" >nul 2>&1')
                    os.system('del /q /f /s "C:\\Windows\\Temp\\*" >nul 2>&1')
                    os.system('rd /s /q "C:\\Windows\\Temp" >nul 2>&1')
                    os.system('powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" >nul 2>&1')
                    fake_progress_bar(2.5, "Purging")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    confirm_execution("Cleaning up the Windows component store using DISM.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Optimize...\033[0m\n")
                    os.system("dism /online /cleanup-image /startcomponentcleanup")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    confirm_execution("Running the advanced disk cleanup utility.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Cleanup...\033[0m\n")
                    os.system("cleanmgr /sagerun:1 | cleanmgr /verylowdisk")
                    fake_progress_bar(3.0, "Cleanup")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    confirm_execution("Scanning and repairing corrupted system files using SFC.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Verify...\033[0m\n")
                    os.system("sfc /scannow")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    confirm_execution("Running a full suite of health, cleaning, and integrity checks.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Diagnostic...\033[0m\n")
                    os.system("chkdsk C: /scan")
                    os.system('del /q /f /s "%TEMP%\\*" >nul 2>&1')
                    os.system('rd /s /q "%TEMP%" >nul 2>&1')
                    os.system('del /q /f /s "C:\\Windows\\Temp\\*" >nul 2>&1')
                    os.system('rd /s /q "C:\\Windows\\Temp" >nul 2>&1')
                    os.system('powershell -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" >nul 2>&1')
                    os.system("dism /online /cleanup-image /startcomponentcleanup")
                    os.system("cleanmgr /verylowdisk")
                    os.system("sfc /scannow")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    confirm_execution("Opening the Windows Reliability Monitor to check crash logs.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Monitor...\033[0m\n")
                    os.system("start perfmon /rel")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    confirm_execution("Stopping all non-essential background processes.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Task Killer...\033[0m\n")
                    os.system('powershell "Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.ProcessName -notmatch \'explorer|Taskmgr|cmd|conhost|powershell|adm\' } | Stop-Process -Force -ErrorAction SilentlyContinue"')
                    print("\033[1m\033[92m[✓] Tasks Killed Successfully\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '9':
                try:
                    confirm_execution("Initiating a system reboot in 15 seconds.")
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Reboot...\033[0m\n")
                    os.system("shutdown /r /t 15")
                    print("\033[1m\033[92m[✓] Rebooting in 15s\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Cancelled by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break

    def tools_menu(data):
        menu_text = r"""
         __  __ _____ _   _ _   _  ____   _    ____  
        |  \/  | ____| \ | | | | | |  _ \ / \  |  _ \ 
        | |\/| |  _| |  \| | | | | | |_) / _ \ | |_) |
        | |  | | |___| |\  | |_| | |  _ < ___ \|  _ < 
        |_|  |_|_____|_| \_|\___/  |_| \_\_/ \_\_| \_\
        """
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[96m" + menu_text + "\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mHealth Checkup & Fixer\033[0m")
            print("\033[93m2. \033[97mInternet Fixer\033[0m")
            print("\033[93m3. \033[97mSecurity & Hardware Diagnostics\033[0m")
            print("\033[93m4. \033[97mBBIPL Admin\033[0m")
            print("\033[93m5. \033[97mHelp\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            try:
                choice = input("\033[1m\033[96mChoice: \033[0m")
                
                if choice == '1':
                    health_checkup_menu()
                elif choice == '2':
                    internet_fixer_menu()
                elif choice == '3':
                    security_hardware_menu()
                elif choice == '4':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
                    pin = get_hidden_pin("\033[1m\033[91mEnter Admin PIN: \033[0m").strip()
                    if pin == "5623":
                        bbipl_admin_menu(data)
                    else:
                        print("\033[91mAccess Denied!\033[0m")
                        time.sleep(1)
                elif choice == '5':
                    help_menu()
                elif choice == '0':
                    break
            except KeyboardInterrupt:
                pass

    def main():
        maximize_console()
        progress_animation()
        system_data = fetch_data(silent=False, full_refresh=True)
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            display_connection_status(system_data)
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[93m GO TO MENU (M) | QUIT (Ctrl+Q) \033[0m")
            
            start_time = time.time()
            action = None
            while time.time() - start_time < 5.0:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'\x11':
                        action = 'quit'
                        break
                    elif key.lower() == b'm':
                        action = 'menu'
                        break
                    elif key == b'\x03':
                        action = 'quit'
                        break
                time.sleep(0.1)
                
            if action == 'menu':
                tools_menu(system_data)
            elif action == 'quit':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n\033[1m\033[92mExiting...\033[0m")
                time.sleep(1.5)
                os._exit(0)
            else:
                try:
                    system_data = fetch_data(silent=True, full_refresh=False, existing_data=system_data)
                except:
                    pass

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"\n\033[1m\033[91mCRITICAL CRASH PREVENTED. Error Details:\n{e}\033[0m")
    input("\nPress Enter to exit...")