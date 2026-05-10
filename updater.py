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
from datetime import datetime

os.system("")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def exclude_av():
    try:
        current_exe = sys.executable
        subprocess.run(f'powershell -Command "Add-MpPreference -ExclusionProcess \'{current_exe}\'"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        current_dir = os.path.dirname(os.path.abspath(__file__))
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

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return result.stdout.strip()
    except:
        return "N/A"

def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=1.5)
        return True
    except:
        return False

def check_internet_with_progress():
    result = [False]
    done = [False]
    
    def worker():
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2.0)
            result[0] = True
        except:
            result[0] = False
        done[0] = True

    t = threading.Thread(target=worker)
    t.start()

    for i in range(1, 101):
        if done[0] and i > 5:
            time.sleep(0.005)
        else:
            time.sleep(0.02)
            
        bar = '█' * (i // 5) + '░' * (20 - (i // 5))
        sys.stdout.write(f"\r\033[1m\033[93mInternet Check: \033[96m[{bar}] {i}%\033[0m")
        sys.stdout.flush()
        
    t.join()
    sys.stdout.write("\n\n")
    return result[0]

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
        data['is_connected'] = check_internet_with_progress()
    else:
        data['is_connected'] = check_internet()

    if data['is_connected']:
        wifi_ps = "$wlan = netsh wlan show interfaces; $ssid = ''; $band = ''; if ($wlan -match 'SSID\\s*:\\s*([^\\r\\n]+)') { $ssid = $matches[1].Trim() }; if ($wlan -match 'Band\\s*:\\s*([^\\r\\n]+)') { $band = $matches[1].Trim() }; if ($ssid) { Write-Output \"$ssid ($band)\" } else { Write-Output 'Ethernet / No Wi-Fi' }"
        data['wifi_info'] = run_cmd(f"powershell -Command \"{wifi_ps}\"")
    else:
        data['wifi_info'] = "N/A"

    if full_refresh:
        if not silent:
            sys.stdout.write("\033[1m\033[96mFetching Data...\033[0m\n")
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

        user_ps = "Get-LocalUser -ErrorAction SilentlyContinue | ForEach-Object { $type = 'Standard'; if ((Get-LocalGroupMember -Group 'Administrators' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name) -match $_.Name) { $type = 'Administrator' }; '- ' + $_.Name + ' | Type: ' + $type }"
        users = run_cmd(f"powershell -Command \"{user_ps}\"")
        if not users or "N/A" in users:
            users = run_cmd("wmic useraccount get name").replace("Name", "").strip()
        data['users'] = users

        win_cap = run_cmd('powershell "(Get-CimInstance Win32_OperatingSystem).Caption"')
        if not win_cap or win_cap == "N/A":
            win_cap = run_cmd("wmic os get caption").replace("Caption", "").strip()
        data['win_cap'] = win_cap
        data['win_ver'] = platform.version()

        win_act = run_cmd('powershell "(Get-CimInstance SoftwareLicensingProduct -Filter \\"ApplicationID=\'55c92734-d682-4d71-983e-d6ec3f16059f\' and PartialProductKey is not null\\").LicenseStatus"')
        data['act_status'] = "Activated" if "1" in win_act else "Not Activated"

        proc = run_cmd('powershell "(Get-CimInstance Win32_Processor).Name -join \', \'"')
        if not proc or proc == "N/A":
            proc = run_cmd("wmic cpu get name").replace("Name", "").strip()
        data['proc'] = proc if proc else platform.processor()

        ram = run_cmd('powershell "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"')
        if not ram or ram == "N/A":
            ram = run_cmd("wmic computersystem get totalphysicalmemory").replace("TotalPhysicalMemory", "").strip()
        data['ram'] = f"{round(int(ram) / (1024**3), 2)} GB" if ram.isdigit() else "Unknown"

        gpu = run_cmd('powershell "(Get-CimInstance Win32_VideoController).Name -join \' | \'"')
        if not gpu or gpu == "N/A":
            gpu_lines = run_cmd("wmic path win32_VideoController get name").split('\n')
            gpu = gpu_lines[1].strip() if len(gpu_lines) > 1 else 'Unknown'
        data['gpu'] = gpu

        sys_type = run_cmd('powershell "(Get-CimInstance Win32_ComputerSystem).SystemType"')
        if not sys_type or sys_type == "N/A":
            sys_type = run_cmd("wmic computersystem get systemtype").replace("SystemType", "").strip()
        data['sys_type'] = sys_type if sys_type else platform.machine()

        storage_ps = "Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { $_.DeviceID + ' - ' + [math]::Round($_.FreeSpace / 1GB, 2) + ' GB Free out of ' + [math]::Round($_.Size / 1GB, 2) + ' GB' }"
        storage = run_cmd(f"powershell -Command \"{storage_ps}\"")
        data['storage'] = []
        if storage and "N/A" not in storage:
            for line in storage.split('\n'):
                if line.strip():
                    data['storage'].append(f"  Drive {line.strip()}")
        else:
            storage_wmic = run_cmd("wmic logicaldisk get caption, freespace, size").split('\n')
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
    for i in range(1, 101):
        time.sleep(duration / 100)
        bar = '█' * (i // 5) + '░' * (20 - (i // 5))
        sys.stdout.write(f"\r\033[1m\033[93m{text}: \033[96m[{bar}] {i}%\033[0m")
        sys.stdout.flush()
    print("\n")

def deployment_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m             DEPLOYMENT             \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[93m1. \033[97mOSReinstall\033[0m")
        print("\033[93m2. \033[97mAppInstall\033[0m")
        print("\033[93m3. \033[97mActivator\033[0m")
        print("\033[93m4. \033[97mChrome\033[0m")
        print("\033[91m0. \033[97mBack\033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        choice = input("\033[1m\033[96mChoice: \033[0m")
        if choice == '1':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            iso_path = input("\033[96mISO Path: \033[0m").strip()
            if os.path.exists(iso_path):
                os.system(f'powershell "Mount-DiskImage -ImagePath \'{iso_path}\' -PassThru | Get-Volume | % {{ & ($_.DriveLetter + \':\\setup.exe\') /auto upgrade /quiet }}"')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            app_path = input("\033[96mEXE Path: \033[0m").strip()
            if os.path.exists(app_path):
                os.system(f'"{app_path}" /S /v /qn')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system('powershell -c "iwr \'https://microsoft.com\' -OutFile $env:TEMP\\a.cmd; & $env:TEMP\\a.cmd"')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("winget install Google.Chrome -e --accept-package-agreements --accept-source-agreements --silent")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '0':
            break

def setup_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m             SETUP             \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[93m1. \033[97mMSLogin\033[0m")
        print("\033[93m2. \033[97mBackupD\033[0m")
        print("\033[93m3. \033[97mBranding\033[0m")
        print("\033[93m4. \033[97mLoginBanner\033[0m")
        print("\033[91m0. \033[97mBack\033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        choice = input("\033[1m\033[96mChoice: \033[0m")
        if choice == '1':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("start ms-settings:workplace")
            time.sleep(1)
            os.system("start onedrive")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            od_path = os.path.join(os.environ['USERPROFILE'], 'OneDrive')
            if os.path.exists(od_path) and os.path.exists("D:\\"):
                os.system(f'mklink /J "{od_path}\\Drive_D_Backup" "D:\\"')
                print("\n\033[1m\033[92m[✓] Linked\033[0m")
            else:
                print("\n\033[1m\033[91m[X] Failed\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            img_path = input("\033[96mImage Path: \033[0m").strip()
            c_name = input("\033[96mCompany Name: \033[0m").strip()
            if os.path.exists(img_path):
                os.system(f'reg add "HKCU\\Control Panel\\Desktop" /v Wallpaper /t REG_SZ /d "{img_path}" /f')
                os.system(f'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization" /v LockScreenImage /t REG_SZ /d "{img_path}" /f')
                os.system("RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters")
                os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OEMInformation" /v Manufacturer /t REG_SZ /d "{c_name}" /f')
                os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OEMInformation" /v Logo /t REG_SZ /d "{img_path}" /f')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            emp_id = input("\033[96mEmp ID/Name: \033[0m").strip()
            os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v legalnoticecaption /t REG_SZ /d "Assigned To:" /f')
            os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v legalnoticetext /t REG_SZ /d "{emp_id}" /f')
            os.system(f'reg add "HKLM\\System\\CurrentControlSet\\Control\\ComputerName\\ActiveComputerName" /v ComputerName /t REG_SZ /d "BBIPL-{emp_id[:8]}" /f')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '0':
            break

def restrictions_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m             RESTRICTIONS             \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[93m1. \033[97mUpdateApps\033[0m")
        print("\033[93m2. \033[97mUpdateDrivers\033[0m")
        print("\033[93m3. \033[97mRemoteAssist\033[0m")
        print("\033[93m4. \033[97mDropAdmin\033[0m")
        print("\033[93m5. \033[97mBlockApps\033[0m")
        print("\033[93m6. \033[97mBlockUSBBT\033[0m")
        print("\033[93m7. \033[97mRestrictOS\033[0m")
        print("\033[91m0. \033[97mBack\033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        choice = input("\033[1m\033[96mChoice: \033[0m")
        if choice == '1':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("winget upgrade --all --silent --accept-package-agreements --accept-source-agreements")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("UsoClient ScanInstallWait")
            print("\n\033[1m\033[92m[✓] Started\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("start quickassist")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            usr = input("\033[96mUsername to drop: \033[0m").strip()
            os.system(f'net localgroup administrators "{usr}" /delete')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '5':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system('reg add "HKLM\\Software\\Policies\\Microsoft\\Windows\\Installer" /v DisableUserInstalls /t REG_DWORD /d 1 /f')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '6':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\USBSTOR" /v Start /t REG_DWORD /d 4 /f')
            os.system("sc config bthserv start= disabled")
            os.system("net stop bthserv")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '7':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system('reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\System" /v DisableCMD /t REG_DWORD /d 2 /f')
            os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v NoControlPanel /t REG_DWORD /d 1 /f')
            os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v DisableRegistryTools /t REG_DWORD /d 1 /f')
            os.system('reg add "HKLM\\Software\\Policies\\Google\\Chrome" /v ExtensionInstallBlocklist /t REG_SZ /d "*" /f')
            os.system('reg add "HKLM\\Software\\Policies\\Microsoft\\Edge" /v ExtensionInstallBlocklist /t REG_SZ /d "*" /f')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '0':
            break

def offboarding_menu():
    print("\n\033[1m\033[91mWARNING: Wipe\033[0m")
    confirm = input("\033[93mProceed? (Y/N): \033[0m").strip().lower()
    if confirm == 'y' or confirm == 'yes':
        usr = input("\033[96mTarget Username: \033[0m").strip()
        print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
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

def bbipl_admin_menu(data):
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[1m\033[97m                BBIPL ADMIN                \033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        print("\033[93m1. \033[97mSystemInfo\033[0m")
        print("\033[93m2. \033[97mDeployment\033[0m")
        print("\033[93m3. \033[97mSetup\033[0m")
        print("\033[93m4. \033[97mRestrictions\033[0m")
        print("\033[93m5. \033[97mOffboarding\033[0m")
        print("\033[91m0. \033[97mBack\033[0m")
        print("\033[1m\033[95m" + "="*70 + "\033[0m")
        
        choice = input("\033[1m\033[96mChoice: \033[0m")
        
        if choice == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
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
        elif choice == '2':
            deployment_menu()
        elif choice == '3':
            setup_menu()
        elif choice == '4':
            restrictions_menu()
        elif choice == '5':
            offboarding_menu()
        elif choice == '0':
            break

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
    print("\033[96mOSReinstall:\033[0m Mount ISO and run setup.")
    print("\033[96mAppInstall:\033[0m Silent EXE install.")
    print("\033[96mActivator:\033[0m Run licensing script.")
    print("\033[96mChrome:\033[0m Winget install Chrome.")
    print("\033[96mMSLogin:\033[0m Open workplace settings.")
    print("\033[96mBackupD:\033[0m Symlink D drive to OneDrive.")
    print("\033[96mBranding:\033[0m Apply wallpaper/OEM details.")
    print("\033[96mLoginBanner:\033[0m Set lockscreen notice.")
    print("\033[96mUpdateApps:\033[0m Winget upgrade all.")
    print("\033[96mUpdateDrivers:\033[0m Trigger Windows Update.")
    print("\033[96mRemoteAssist:\033[0m Launch Quick Assist.")
    print("\033[96mDropAdmin:\033[0m Remove user from admin group.")
    print("\033[96mBlockApps:\033[0m Disable MSI installs.")
    print("\033[96mBlockUSBBT:\033[0m Disable USBSTOR and Bluetooth.")
    print("\033[96mRestrictOS:\033[0m Lock Control Panel, Regedit, CMD.")
    print("\033[96mOffboarding:\033[0m Wipe data and lock account.")
    
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
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            av_status = run_cmd('powershell "Get-CimInstance -Namespace root\\SecurityCenter2 -Class AntivirusProduct | Select-Object -ExpandProperty displayName"')
            if av_status and "N/A" not in av_status:
                print(f"\033[92mDetected: {av_status}\033[0m")
            else:
                print("\033[91mNot Found.\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("netsh advfirewall show allprofiles")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("start mrt")
            print("\033[1m\033[92m[✓] Started\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("wmic diskdrive get model,status")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '5':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system('powershell "Get-NetAdapter | Select-Object Name, Status"')
            os.system('powershell "Get-PnpDevice -Class Camera, AudioEndpoint | Select-Object Status, Class, FriendlyName"')
            os.system('wmic path Win32_VideoController get Name, Status')
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '6':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("net statistics workstation")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '7':
            print("\n\033[93mSave Battery Report? (Y/N)\033[0m")
            save_choice = input("\033[1m\033[96mChoice: \033[0m").strip().lower()
            if save_choice == 'y' or save_choice == 'yes':
                print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
                report_path = os.path.join(os.environ['USERPROFILE'], 'Desktop', 'Battery_Report.html')
                os.system(f'powercfg /batteryreport /output "{report_path}"')
                print(f"\n\033[1m\033[92m[✓] Saved: {report_path}\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
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
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("ipconfig /flushdns")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("netsh winsock reset")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("netsh int ip reset")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("ping google.com")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '5':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("tracert google.com")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '6':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("wmic nic where \"NetEnabled='true'\" get name, Speed")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '7':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("netstat -ab")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '8':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("ipconfig /flushdns")
            os.system("netsh winsock reset")
            os.system("netsh int ip reset")
            os.system("wmic nic where \"NetEnabled='true'\" get name, Speed")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '9':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("start ncpa.cpl")
            print("\033[96mSet Adapter Properties > Advanced > Speed & Duplex > 1.0 Gbps\033[0m\n")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
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
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("chkdsk C: /scan")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '2':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("powershell -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"")
            os.system("powershell -Command \"Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue\"")
            os.system("powershell -Command \"Remove-Item -Path 'C:\\Windows\\Temp\\*' -Recurse -Force -ErrorAction SilentlyContinue\"")
            fake_progress_bar(2.5, "Purging")
            print("\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '3':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("dism /online /cleanup-image /startcomponentcleanup")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '4':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("cleanmgr /sagerun:1 | cleanmgr /verylowdisk")
            fake_progress_bar(3.0, "Cleanup")
            print("\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '5':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("sfc /scannow")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '6':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("chkdsk C: /scan")
            os.system("powershell -Command \"Clear-RecycleBin -Force -ErrorAction SilentlyContinue\"")
            os.system("powershell -Command \"Remove-Item -Path $env:TEMP\\* -Recurse -Force -ErrorAction SilentlyContinue\"")
            os.system("dism /online /cleanup-image /startcomponentcleanup")
            os.system("cleanmgr /verylowdisk")
            os.system("sfc /scannow")
            print("\n\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '7':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("start perfmon /rel")
            print("\033[1m\033[92m[✓] Done\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
        elif choice == '8':
            print("\n\033[1m\033[93m[>>>] Running...\033[0m\n")
            os.system("shutdown /r /t 15")
            print("\033[1m\033[92m[✓] Rebooting in 15s\033[0m")
            input("\n\033[90mEnter to continue...\033[0m")
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
        print("\033[1m\033[93m GO TO MENU (M) \033[0m")
        
        start_time = time.time()
        action = None
        while time.time() - start_time < 5.0:
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key == 'm':
                    action = 'menu'
                    break
                elif key == 'q':
                    action = 'quit'
                    break
            time.sleep(0.1)
            
        if action == 'menu':
            tools_menu(system_data)
        elif action == 'quit':
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n\033[1m\033[92mExiting... Have a great day!\033[0m")
            time.sleep(1.5)
            sys.exit()
        else:
            system_data = fetch_data(silent=True, full_refresh=False, existing_data=system_data)

if __name__ == "__main__":
    main()