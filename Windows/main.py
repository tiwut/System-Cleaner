import os
import shutil
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import threading
import tempfile
import subprocess
import glob

def is_admin():
    """Check if script is running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Relaunch the script with admin privileges."""
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )

class AdvancedCleaner:
    def __init__(self, root):
        self.root = root
        self.root.title("Tiwut System Cleaner")
        self.root.geometry("750x600")
        
        style = ttk.Style()
        style.configure("Bold.TCheckbutton", font=("Segoe UI", 9, "bold"))
        
        self.vars = {
            "temp_user": tk.BooleanVar(value=True),
            "temp_sys": tk.BooleanVar(value=True),
            "prefetch": tk.BooleanVar(value=False),
            "recycle": tk.BooleanVar(value=False),
            "dumps": tk.BooleanVar(value=False),
            "logs": tk.BooleanVar(value=False),
            "dns": tk.BooleanVar(value=False),
            "win_update": tk.BooleanVar(value=False),
            "chrome_cache": tk.BooleanVar(value=False),
            "edge_cache": tk.BooleanVar(value=False),
            "firefox_cache": tk.BooleanVar(value=False),
        }

        self.create_ui()

    def create_ui(self):
        header = tk.Label(self.root, text="Select items to clean", font=("Segoe UI", 14, "bold"))
        header.pack(pady=10)
        options_frame = tk.Frame(self.root)
        options_frame.pack(fill="x", padx=20)
        grp_sys = tk.LabelFrame(options_frame, text="System", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        grp_sys.grid(row=0, column=0, sticky="nsew", padx=5)

        self.add_chk(grp_sys, "User Temp Files (%TEMP%)", "temp_user")
        self.add_chk(grp_sys, "System Temp (Windows/Temp)", "temp_sys")
        self.add_chk(grp_sys, "Prefetch Data", "prefetch")
        self.add_chk(grp_sys, "Empty Recycle Bin", "recycle")
        self.add_chk(grp_sys, "Memory Dumps (.dmp)", "dumps")
        self.add_chk(grp_sys, "Windows Event Logs", "logs")
        grp_net = tk.LabelFrame(options_frame, text="Network & Update", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        grp_net.grid(row=0, column=1, sticky="nsew", padx=5)
        self.add_chk(grp_net, "Flush DNS Cache", "dns")
        self.add_chk(grp_net, "Windows Update Cache\n(Stops wuauserv service)", "win_update")
        grp_browser = tk.LabelFrame(options_frame, text="Browsers (Cache only)", font=("Segoe UI", 10, "bold"), padx=10, pady=5)
        grp_browser.grid(row=0, column=2, sticky="nsew", padx=5)
        self.add_chk(grp_browser, "Google Chrome Cache", "chrome_cache")
        self.add_chk(grp_browser, "Microsoft Edge Cache", "edge_cache")
        self.add_chk(grp_browser, "Mozilla Firefox Cache", "firefox_cache")
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Select All", command=lambda: self.toggle_all(True)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Deselect All", command=lambda: self.toggle_all(False)).pack(side="left", padx=5)
        action_btn = tk.Button(self.root, text="START CLEANING", bg="#d9534f", fg="white", 
                               font=("Segoe UI", 12, "bold"), height=2, width=20,
                               command=self.start_thread)
        action_btn.pack(pady=15)
        lbl_log = tk.Label(self.root, text="Activity Log:", anchor="w")
        lbl_log.pack(fill="x", padx=20)
        
        self.log_text = scrolledtext.ScrolledText(self.root, height=12, state='disabled', font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def add_chk(self, parent, text, var_key):
        cb = tk.Checkbutton(parent, text=text, variable=self.vars[var_key], anchor="w", justify="left")
        cb.pack(fill="x", anchor="w")

    def toggle_all(self, state):
        for key in self.vars:
            self.vars[key].set(state)

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_thread(self):
        if not any(v.get() for v in self.vars.values()):
            messagebox.showwarning("No Selection", "Please select at least one option.")
            return
        
        t = threading.Thread(target=self.run_cleaning)
        t.start()

    def remove_folder_contents(self, folder_path, desc):
        if not os.path.exists(folder_path):
            self.log(f"Skipping (Not Found): {desc}")
            return

        self.log(f"--- Cleaning: {desc} ---")
        count = 0
        size_freed = 0
        
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                path = os.path.join(root, file)
                try:
                    fsize = os.path.getsize(path)
                    os.remove(path)
                    size_freed += fsize
                    count += 1
                except:
                    pass
        
        mb = size_freed / (1024 * 1024)
        self.log(f"Removed {count} files ({mb:.2f} MB) from {desc}")

    def run_cmd(self, cmd_list, desc):
        self.log(f"Running: {desc}...")
        try:
            subprocess.run(cmd_list, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log(f"Done: {desc}")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_cleaning(self):
        self.log("=== STARTING CLEANUP PROCESS ===")
        if self.vars["temp_user"].get():
            self.remove_folder_contents(tempfile.gettempdir(), "User Temp")
        
        if self.vars["temp_sys"].get():
            self.remove_folder_contents(os.path.join(os.environ['WINDIR'], 'Temp'), "System Temp")

        if self.vars["prefetch"].get():
            self.remove_folder_contents(os.path.join(os.environ['WINDIR'], 'Prefetch'), "Prefetch")

        user_profile = os.environ['USERPROFILE']
        
        if self.vars["chrome_cache"].get():
            path = os.path.join(user_profile, r"AppData\Local\Google\Chrome\User Data\Default\Cache\Cache_Data")
            self.remove_folder_contents(path, "Chrome Cache")

        if self.vars["edge_cache"].get():
            path = os.path.join(user_profile, r"AppData\Local\Microsoft\Edge\User Data\Default\Cache\Cache_Data")
            self.remove_folder_contents(path, "Edge Cache")

        if self.vars["firefox_cache"].get():
            base = os.path.join(user_profile, r"AppData\Local\Mozilla\Firefox\Profiles")
            if os.path.exists(base):
                for profile in os.listdir(base):
                    cache_path = os.path.join(base, profile, "cache2", "entries")
                    self.remove_folder_contents(cache_path, f"Firefox Cache ({profile})")

        if self.vars["dumps"].get():
            dump_path = os.path.join(os.environ['WINDIR'], 'Minidump')
            self.remove_folder_contents(dump_path, "System Minidumps")
        
        if self.vars["logs"].get():
            log_path = os.path.join(os.environ['WINDIR'], r"System32\winevt\Logs")
            self.remove_folder_contents(log_path, "Windows Event Logs")

        if self.vars["win_update"].get():
            self.log("--- Cleaning Windows Update ---")
            self.run_cmd("net stop wuauserv", "Stopping Windows Update Service")
            update_path = os.path.join(os.environ['WINDIR'], r"SoftwareDistribution\Download")
            self.remove_folder_contents(update_path, "Update Downloads")
            self.run_cmd("net start wuauserv", "Restarting Windows Update Service")

        if self.vars["dns"].get():
            self.run_cmd("ipconfig /flushdns", "Flush DNS")

        if self.vars["recycle"].get():
            self.log("--- Emptying Recycle Bin ---")
            try:
                ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
                self.log("Recycle Bin Emptied.")
            except:
                self.log("Could not empty Recycle Bin (Access Denied or already empty).")

        self.log("\n=== CLEANUP FINISHED ===")
        messagebox.showinfo("Success", "System cleanup completed successfully.")

if __name__ == "__main__":
    if not is_admin():
        run_as_admin()
        sys.exit()

    root = tk.Tk()
    app = AdvancedCleaner(root)
    root.mainloop()
