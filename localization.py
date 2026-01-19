import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from deep_translator import GoogleTranslator
import time
import threading
import os

class BZ98GuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Battlezone 98 Redux - Localization Tool")
        self.root.geometry("800x900")
        
        # Default Paths
        self.paths = {
            "steam": r"C:\Program Files (x86)\Steam\steamapps\common\Battlezone 98 Redux\localization_table.csv",
            "gog": r"C:\GOG Games\Battlezone 98 Redux\localization_table.csv"
        }
        
        # Start with Steam as default
        self.csv_path = tk.StringVar(value=self.paths["steam"])
        
        self.languages = ['French', 'German', 'Spanish', 'Italian', 'Russian', 'Portuguese']
        self.lang_codes = {'French': 'fr', 'German': 'de', 'Spanish': 'es', 'Italian': 'it', 'Russian': 'ru', 'Portuguese': 'pt'}

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="Battlezone 98 Redux Localization Tool", font=("Arial", 16, "bold"))
        header.pack(pady=(15, 5))

        # Instructions Panel
        instr_frame = tk.LabelFrame(self.root, text=" How to use & Security ", padx=10, pady=10, fg="#0d47a1")
        instr_frame.pack(fill="x", padx=20, pady=5)
        
        instructions = (
            "• QUICK JUMP: Use the Steam/GOG buttons to find your game folder instantly.\n"
            "• SMART PREFIX: Words use 'names:' (e.g., Tank -> names:tank).\n"
            "• MISSIONS: Use format: mapname.bzn~Human Title\n"
            "• FILE: New lines are APPENDED. Existing data is safe.\n"
            "• ONLINE CONNECTION: This app uses Google Translate API to automatically translate."
        )
        tk.Label(instr_frame, text=instructions, justify="left", font=("Segoe UI", 9)).pack(anchor="w")

        # File Selection Frame
        file_frame = tk.LabelFrame(self.root, text="Localization Table Path", padx=10, pady=10)
        file_frame.pack(fill="x", padx=20, pady=5)

        # Quick Jump Buttons
        jump_frame = tk.Frame(file_frame)
        jump_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(jump_frame, text="Jump to Steam Default", bg="#1b2838", fg="white", 
                  command=lambda: self.set_preset_path("steam")).pack(side="left", padx=2)
        tk.Button(jump_frame, text="Jump to GOG Default", bg="#4d004d", fg="white", 
                  command=lambda: self.set_preset_path("gog")).pack(side="left", padx=2)

        # Path Entry and Browse
        path_sub_frame = tk.Frame(file_frame)
        path_sub_frame.pack(fill="x")
        self.file_entry = tk.Entry(path_sub_frame, textvariable=self.csv_path, font=("Segoe UI", 9))
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Button(path_sub_frame, text="Browse...", command=self.browse_file).pack(side="right")

        # Input Area
        tk.Label(self.root, text="Paste English text here (one per line):", font=("Arial", 10, "bold")).pack(anchor='w', padx=20, pady=(10,0))
        self.text_input = scrolledtext.ScrolledText(self.root, height=12, font=("Segoe UI", 10))
        self.text_input.pack(padx=20, pady=5, fill='both', expand=True)

        # Activity Log
        tk.Label(self.root, text="Activity Log:").pack(anchor='w', padx=20)
        self.log_area = scrolledtext.ScrolledText(self.root, height=8, state='disabled', bg="#f8f8f8", font=("Consolas", 9))
        self.log_area.pack(padx=20, pady=5, fill='both')

        # Action Button
        self.btn_run = tk.Button(self.root, text="Translate & Append to CSV", bg="#2e7d32", fg="white", 
                                 font=("Arial", 11, "bold"), command=self.start_thread)
        self.btn_run.pack(pady=15, ipadx=40, ipady=10)

    def set_preset_path(self, version):
        self.csv_path.set(self.paths[version])
        if os.path.exists(self.paths[version]):
            self.log(f"Set path to {version.upper()} default. File found!")
        else:
            self.log(f"Warning: {version.upper()} default path not found on this drive.")

    def browse_file(self):
        file_selected = filedialog.askopenfilename(initialdir=os.path.dirname(self.csv_path.get()), filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
        if file_selected: self.csv_path.set(file_selected)

    def log(self, message):
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END); self.log_area.configure(state='disabled')
        self.root.update_idletasks()

    def start_thread(self):
        if not os.path.exists(self.csv_path.get()):
            messagebox.showerror("File Not Found", "Please select a valid localization_table.csv")
            return
        threading.Thread(target=self.process_translations, daemon=True).start()

    def process_translations(self):
        raw_text = self.text_input.get("1.0", tk.END).strip()
        if not raw_text: return

        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
        self.btn_run.config(state='disabled', text="Working...")
        
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
            
            self.log("--- BATCH COMPLETE ---")
            messagebox.showinfo("Success", f"Added {len(lines)} entries.")
            self.text_input.delete("1.0", tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        self.btn_run.config(state='normal', text="Translate & Append to CSV")

if __name__ == "__main__":
    root = tk.Tk(); app = BZ98GuiApp(root); root.mainloop()