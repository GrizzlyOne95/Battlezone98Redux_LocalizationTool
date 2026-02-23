import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from deep_translator import GoogleTranslator
import time
import threading
import os
import ctypes
import re
import sys

# Platform check
IS_WINDOWS = sys.platform == "win32"

class ToolTip:
    def __init__(self, widget, text, bg="#1a1a1a", fg="#00ffff"):
        self.widget = widget
        self.text = text
        self.bg = bg
        self.fg = fg
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                       background=self.bg, foreground=self.fg, 
                       relief='solid', borderwidth=1, font=("Consolas", "9"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class BZ98GuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battlezone 98 Redux - Localization Tool")
        self.root.geometry("900x950")
        
        # Colors (Matched to Workshop Uploader)
        self.colors = {
            "bg": "#0a0a0a", "fg": "#d4d4d4",
            "highlight": "#00ff00", "dark_highlight": "#004400", "accent": "#00ffff"
        }
        self.root.configure(bg=self.colors["bg"])

        # Default Paths
        self.paths = {
            "steam": r"C:\Program Files (x86)\Steam\steamapps\common\Battlezone 98 Redux\localization_table.csv",
            "gog": r"C:\GOG Games\Battlezone 98 Redux\localization_table.csv"
        }
        
        self.csv_path = tk.StringVar(value=self.paths["steam"])
        self.scan_folder_path = tk.StringVar()
        self.languages = ['French', 'German', 'Spanish', 'Italian', 'Russian', 'Portuguese']
        self.lang_codes = {'French': 'fr', 'German': 'de', 'Spanish': 'es', 'Italian': 'it', 'Russian': 'ru', 'Portuguese': 'pt'}

        self.load_custom_font()
        self.setup_styles()
        self.setup_ui()

    def load_custom_font(self):
        self.main_font = "Consolas"
        self.header_font = "Consolas"
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        if IS_WINDOWS:
            font_path = os.path.join(base_path, "BZONE.ttf")
            if os.path.exists(font_path):
                try:
                    if ctypes.windll.gdi32.AddFontResourceExW(font_path, 0x10, 0) > 0:
                        self.header_font = "BZONE"
                except: pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        c = self.colors
        
        style.configure(".", background=c["bg"], foreground=c["fg"], font=(self.main_font, 10))
        style.configure("TFrame", background=c["bg"])
        style.configure("TNotebook", background=c["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background="#1a1a1a", foreground=c["fg"], padding=[15, 5])
        style.map("TNotebook.Tab", background=[("selected", c["dark_highlight"])], foreground=[("selected", c["highlight"])])
        
        style.configure("TLabelframe", background=c["bg"], bordercolor=c["highlight"])
        style.configure("TLabelframe.Label", background=c["bg"], foreground=c["highlight"], font=(self.header_font, 11, "bold"))
        
        style.configure("TLabel", background=c["bg"], foreground=c["fg"])
        style.configure("Header.TLabel", foreground=c["highlight"], font=(self.header_font, 20, "bold"))
        
        style.configure("TButton", background="#1a1a1a", foreground=c["fg"], padding=5)
        style.map("TButton", background=[("active", c["dark_highlight"])], foreground=[("active", c["highlight"])])
        
        style.configure("Primary.TButton", background=c["dark_highlight"], foreground=c["highlight"], font=(self.header_font, 12, "bold"))
        
        style.configure("TEntry", fieldbackground="#1a1a1a", foreground=c["accent"], insertcolor=c["highlight"])
        style.configure("TProgressbar", thickness=20, trowcolor=c["dark_highlight"], background=c["highlight"])

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Header
        header_label = ttk.Label(main_frame, text="LOCALIZATION TOOL", style="Header.TLabel")
        header_label.pack(pady=(0, 20))

        # CSV Path Config
        path_frame = ttk.LabelFrame(main_frame, text=" TARGET LOCALIZATION TABLE ", padding=10)
        path_frame.pack(fill="x", pady=(0, 10))
        
        jump_frame = ttk.Frame(path_frame)
        jump_frame.pack(fill="x", pady=(0, 5))
        ttk.Button(jump_frame, text="STEAM DEFAULT", command=lambda: self.set_preset_path("steam")).pack(side="left", padx=2)
        ttk.Button(jump_frame, text="GOG DEFAULT", command=lambda: self.set_preset_path("gog")).pack(side="left", padx=2)
        
        path_sub = ttk.Frame(path_frame)
        path_sub.pack(fill="x")
        ttk.Entry(path_sub, textvariable=self.csv_path).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(path_sub, text="BROWSE", command=self.browse_csv).pack(side="right")

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        self.manual_tab = ttk.Frame(self.notebook, padding=10)
        self.odf_tab = ttk.Frame(self.notebook, padding=10)

        self.notebook.add(self.manual_tab, text=" MANUAL TRANSLATE ")
        self.notebook.add(self.odf_tab, text=" ODF SCANNER ")

        self.setup_manual_tab()
        self.setup_odf_tab()

        # Shared Activity Log
        log_frame = ttk.LabelFrame(main_frame, text=" ACTIVITY LOG ", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, bg="#050505", fg=self.colors["fg"], 
                                                 font=("Consolas", 10), insertbackground=self.colors["highlight"])
        self.log_area.pack(fill="both", expand=True)
        self.log_area.configure(state='disabled')

        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.pack(fill="x", pady=(10, 0))

    def setup_manual_tab(self):
        ttk.Label(self.manual_tab, text="Paste English text (one per line):").pack(anchor="w")
        self.text_input = scrolledtext.ScrolledText(self.manual_tab, height=15, bg="#1a1a1a", fg=self.colors["accent"], 
                                                   font=("Consolas", 11), insertbackground=self.colors["highlight"])
        self.text_input.pack(fill="both", expand=True, pady=5)
        
        btn_run = ttk.Button(self.manual_tab, text="TRANSLATE & APPEND", style="Primary.TButton", command=self.start_manual_thread)
        btn_run.pack(pady=10, ipady=5, fill="x")
        self.btn_run = btn_run

    def setup_odf_tab(self):
        scan_frame = ttk.Frame(self.odf_tab)
        scan_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(scan_frame, text="Source Folder:").pack(side="left")
        ttk.Entry(scan_frame, textvariable=self.scan_folder_path).pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(scan_frame, text="BROWSE", command=self.browse_scan_folder).pack(side="left")
        
        ttk.Button(self.odf_tab, text="SCAN FOLDER FOR ODFs", command=self.start_scan_thread).pack(fill="x", pady=5)
        
        # Results List
        res_frame = ttk.LabelFrame(self.odf_tab, text=" DISCOVERED UNITS ", padding=5)
        res_frame.pack(fill="both", expand=True)
        
        self.odf_list = tk.Listbox(res_frame, bg="#1a1a1a", fg=self.colors["accent"], selectbackground=self.colors["dark_highlight"], 
                                   selectforeground=self.colors["highlight"], font=("Consolas", 10), borderwidth=0)
        self.odf_list.pack(side="left", fill="both", expand=True)
        
        sb = ttk.Scrollbar(res_frame, orient="vertical", command=self.odf_list.yview)
        sb.pack(side="right", fill="y")
        self.odf_list.config(yscrollcommand=sb.set)
        
        self.btn_bulk = ttk.Button(self.odf_tab, text="COLLECT & TRANSLATE ALL", style="Primary.TButton", command=self.start_bulk_thread, state="disabled")
        self.btn_bulk.pack(pady=10, ipady=5, fill="x")

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, f"> {message}\n")
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def set_preset_path(self, version):
        self.csv_path.set(self.paths[version])
        self.log(f"Path set to {version.upper()} default.")

    def browse_csv(self):
        f = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if f: self.csv_path.set(f)

    def browse_scan_folder(self):
        d = filedialog.askdirectory()
        if d: self.scan_folder_path.set(d)

    def get_existing_keys(self):
        keys = set()
        path = self.csv_path.get()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.split('~')
                        if parts: keys.add(parts[0].strip())
            except Exception as e:
                self.log(f"Error reading existing keys: {e}")
        return keys

    def start_manual_thread(self):
        if not os.path.exists(self.csv_path.get()):
            messagebox.showerror("Error", "Target CSV file not found!")
            return
        threading.Thread(target=self.process_manual, daemon=True).start()

    def process_manual(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text: return
        
        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        self.btn_run.config(state='disabled')
        self.progress['maximum'] = len(lines)
        self.progress['value'] = 0
        
        existing_keys = self.get_existing_keys()
        added_count = 0
        
        try:
            with open(self.csv_path.get(), 'a', encoding='utf-8') as f:
                for line in lines:
                    if "~" in line and ".bzn" in line.lower():
                        key_part, english_text = line.split("~", 1)
                        safe_key = f"mission_title:{key_part.strip()}"
                        english_text = english_text.strip()
                    else:
                        english_text = line
                        safe_key = f"names:{english_text.lower().replace(' ', '_')}"
                    
                    if safe_key in existing_keys:
                        self.log(f"Skipping (Duplicate): {safe_key}")
                        self.progress['value'] += 1
                        continue

                    self.log(f"Translating: {english_text}...")
                    row = [safe_key, english_text]
                    for lang in self.languages:
                        try:
                            time.sleep(0.4)
                            trans = GoogleTranslator(source='en', target=self.lang_codes[lang]).translate(english_text)
                            row.append(trans)
                        except:
                            row.append(english_text)
                    
                    f.write("~".join(row) + "\n")
                    existing_keys.add(safe_key)
                    added_count += 1
                    self.progress['value'] += 1
            
            self.log(f"BATCH COMPLETE! Added {added_count} new entries.")
            messagebox.showinfo("Success", f"Added {added_count} entries.")
            self.text_input.delete("1.0", tk.END)
        except Exception as e:
            self.log(f"Critical Error: {e}")
            messagebox.showerror("Error", str(e))
        
        self.btn_run.config(state='normal')
        self.progress['value'] = 0

    def start_scan_thread(self):
        if not os.path.exists(self.scan_folder_path.get()):
            messagebox.showerror("Error", "Please select a valid folder to scan.")
            return
        threading.Thread(target=self.perform_scan, daemon=True).start()

    def perform_scan(self):
        folder = self.scan_folder_path.get()
        self.log(f"Scanning folder: {folder}")
        self.odf_list.delete(0, tk.END)
        self.discovered_odfs = [] # List of tuples (path, name, key)
        
        odf_count = 0
        for root, _, files in os.walk(folder):
            for file in files:
                if file.lower().endswith(".odf"):
                    odf_count += 1
                    path = os.path.join(root, file)
                    unit_name = self.extract_unit_name(path)
                    
                    if unit_name:
                        key = f"names:{unit_name.lower().replace(' ', '_')}"
                        self.discovered_odfs.append((path, unit_name, key))
                        self.odf_list.insert(tk.END, f"{unit_name} ({file})")
                    else:
                        # Fallback to filename
                        fallback = os.path.splitext(file)[0]
                        key = f"names:{fallback.lower()}"
                        self.discovered_odfs.append((path, fallback, key))
                        self.odf_list.insert(tk.END, f"[FILENAMWE] {fallback} ({file})")

        self.log(f"Scan complete. Found {len(self.discovered_odfs)} potential units in {odf_count} ODF files.")
        if self.discovered_odfs:
            self.btn_bulk.config(state="normal")
        else:
            self.btn_bulk.config(state="disabled")

    def extract_unit_name(self, path):
        try:
            with open(path, 'r', errors='ignore') as f:
                content = f.read()
                # Regex to find unitName = "Name"
                match = re.search(r'unitName\s*=\s*"([^"]+)"', content, re.IGNORECASE)
                if match:
                    return match.group(1).strip()
        except: pass
        return None

    def start_bulk_thread(self):
        if not os.path.exists(self.csv_path.get()):
            messagebox.showerror("Error", "Target CSV file not found!")
            return
        threading.Thread(target=self.process_bulk, daemon=True).start()

    def process_bulk(self):
        self.btn_bulk.config(state="disabled")
        self.progress['maximum'] = len(self.discovered_odfs)
        self.progress['value'] = 0
        
        existing_keys = self.get_existing_keys()
        added_count = 0
        
        try:
            with open(self.csv_path.get(), 'a', encoding='utf-8') as f:
                for path, english_text, safe_key in self.discovered_odfs:
                    if safe_key in existing_keys:
                        self.log(f"Skipping (Duplicate): {safe_key}")
                        self.progress['value'] += 1
                        continue

                    self.log(f"Translating: {english_text}...")
                    row = [safe_key, english_text]
                    for lang in self.languages:
                        try:
                            time.sleep(0.4)
                            trans = GoogleTranslator(source='en', target=self.lang_codes[lang]).translate(english_text)
                            row.append(trans)
                        except:
                            row.append(english_text)
                    
                    f.write("~".join(row) + "\n")
                    existing_keys.add(safe_key)
                    added_count += 1
                    self.progress['value'] += 1
            
            self.log(f"BULK SCAN COMPLETE! Added {added_count} new entries.")
            messagebox.showinfo("Success", f"Bulk translation complete. Added {added_count} units.")
        except Exception as e:
            self.log(f"Critical Error: {e}")
            messagebox.showerror("Error", str(e))
            
        self.btn_bulk.config(state="normal")
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = BZ98GuiApp(root)
    root.mainloop()