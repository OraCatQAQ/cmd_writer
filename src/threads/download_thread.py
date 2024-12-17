import random
import time
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal

class DownloadThread(QThread):
    update_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.total_files = 0
        self.current_file = 0
        self.base_speed = 5.0  # 基础下载速度（MB/s）
        
    def _get_dynamic_speed(self):
        variation = random.uniform(-0.5, 0.5)
        current_speed = self.base_speed + variation
        if random.random() < 0.1:  # 10%概率发生较大波动
            current_speed *= random.uniform(0.5, 1.5)
        return f"{current_speed:.1f} MB/s"
    
    def _calculate_eta(self, file_size_mb, progress):
        size = float(file_size_mb.split()[0])
        remaining_size = size * (100 - progress) / 100
        speed = float(self._get_dynamic_speed().split()[0])
        eta_seconds = int(remaining_size / speed)
        
        if eta_seconds < 60:
            return f"{eta_seconds} seconds"
        elif eta_seconds < 3600:
            return f"{eta_seconds // 60} minutes {eta_seconds % 60} seconds"
        else:
            hours = eta_seconds // 3600
            minutes = (eta_seconds % 3600) // 60
            return f"{hours} hours {minutes} minutes"

    def run(self):
        files = [
            ('System Components', [
                ('msvcrt.dll', '2.1 MB'), ('ntdll.dll', '4.8 MB'),
                ('kernel32.dll', '3.2 MB'), ('user32.dll', '2.8 MB'),
                ('shell32.dll', '5.7 MB'), ('advapi32.dll', '1.9 MB'),
                ('gdi32.dll', '2.4 MB'), ('oleaut32.dll', '1.8 MB')
            ]),
            ('Device Drivers', [
                ('nvlddmkm.sys', '185.4 MB'), ('USBXHCI.SYS', '12.8 MB'),
                ('ACPI.sys', '8.7 MB'), ('volmgr.sys', '4.2 MB'),
                ('tcpip.sys', '15.6 MB'), ('ndis.sys', '9.9 MB'),
                ('disk.sys', '6.4 MB'), ('storahci.sys', '7.8 MB')
            ]),
            ('Security Updates', [
                ('KB5032189.exe', '248.6 MB'), ('KB5032190.exe', '156.3 MB'),
                ('KB5032192.exe', '324.1 MB'), ('SecurityUpdate.exe', '89.7 MB'),
                ('CriticalUpdate.exe', '167.2 MB')
            ])
        ]

        self._show_system_info()
        
        for category, file_list in files:
            if not self._process_category(category, file_list):
                break

        self._show_cleanup_tasks()

    def _show_system_info(self):
        self.update_signal.emit("[INFO] System Update Service Started")
        self.update_signal.emit("[INFO] Initializing update components...")
        time.sleep(1)
        
        system_info = [
            "[INFO] Windows Version: Windows 10 Pro 21H2",
            "[INFO] System Architecture: x64",
            "[INFO] Processor: Intel(R) Core(TM) i7-10700K",
            "[INFO] Memory: 16.0 GB RAM",
            f"[INFO] System Drive: C:\ ({random.randint(50,200)} GB free of 512 GB)",
            "[INFO] Network Adapter: Intel(R) Wi-Fi 6 AX201 160MHz"
        ]
        
        for info in system_info:
            self.update_signal.emit(info)
            time.sleep(0.2)

    def _process_category(self, category, file_list):
        self.update_signal.emit(f"\n[INFO] Processing {category}...")
        self.update_signal.emit(f"[INFO] Found {len(file_list)} components to update")
        time.sleep(1)
        
        for file, size in file_list:
            if not self.running:
                return False
                
            if not self._process_file(file, size):
                return False
                
        self.update_signal.emit(f"[SUCCESS] {category} processing completed")
        self.update_signal.emit(f"[INFO] Verifying system stability...")
        time.sleep(1)
        self.update_signal.emit(f"[SUCCESS] System stable after {category} update\n")
        return True

    def _process_file(self, file, size):
        self.update_signal.emit(f"[INFO] Verifying: {file}")
        self.update_signal.emit(f"[INFO] Component size: {size}")
        time.sleep(0.5)
        
        if random.random() < 0.2:  # 20%概率需要重试
            self.update_signal.emit(f"[WARNING] Connection timeout while downloading {file}")
            self.update_signal.emit("[INFO] Retrying in 3 seconds...")
            time.sleep(3)
        
        for percentage in range(0, 101, 2):
            if not self.running:
                return False
                
            progress = '█' * (percentage // 5) + '░' * (20 - percentage // 5)
            current_time = datetime.now().strftime('%H:%M:%S')
            speed = self._get_dynamic_speed()
            
            if percentage < 100:
                eta = self._calculate_eta(size, percentage)
                details = f"\r[{current_time}] {file} - [{progress}] {percentage}% - {speed} - ETA: {eta}"
            else:
                details = f"\r[{current_time}] {file} - [{progress}] 100% - Download Complete - Total size: {size}"
            
            self.update_signal.emit(details)
            time.sleep(0.1)
        
        self.update_signal.emit("")
        self.update_signal.emit(f"[INFO] Installing {file}...")
        time.sleep(0.3)
        self.update_signal.emit(f"[SUCCESS] Installation completed for {file}\n")
        time.sleep(0.5)
        return True

    def _show_cleanup_tasks(self):
        cleanup_tasks = [
            "[INFO] Finalizing system updates...",
            "[INFO] Cleaning up temporary files...",
            "[INFO] Updating system registry...",
            "[INFO] Verifying system integrity...",
            "[SUCCESS] System integrity check passed",
            "[SUCCESS] All updates have been installed successfully",
            "[INFO] System is up to date and secure"
        ]
        
        for task in cleanup_tasks:
            if not self.running:
                break
            self.update_signal.emit(task)
            time.sleep(random.uniform(0.5, 1.2)) 