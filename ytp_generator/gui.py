"""
Simple Tkinter GUI for YTP Deluxe Generator (Windows-friendly).
This GUI is intentionally simple for compatibility with Windows 8.1's Tkinter.
It allows selecting input/output, ffmpeg path, assets dir, toggling effects and adjusting probabilities.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import threading
import os

from . import config as cfg, processor, assets

class YTPGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YTP Deluxe Generator - GUI")
        self.root.geometry("800x600")
        self._build_ui()
        self.config = cfg.default_config()
        self._load_config_into_ui(self.config)

    def _build_ui(self):
        frm = ttk.Frame(self.root)
        frm.pack(fill="both", expand=True, padx=8, pady=8)

        # Top row: input, output, ffmpeg path, assets dir
        top = ttk.Frame(frm)
        top.pack(fill="x", pady=(0,8))

        ttk.Label(top, text="Input:").grid(row=0, column=0, sticky="w")
        self.input_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.input_var, width=60).grid(row=0, column=1, padx=4)
        ttk.Button(top, text="Browse", command=self._browse_input).grid(row=0, column=2, padx=4)

        ttk.Label(top, text="Output:").grid(row=1, column=0, sticky="w")
        self.output_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.output_var, width=60).grid(row=1, column=1, padx=4)
        ttk.Button(top, text="Browse", command=self._browse_output).grid(row=1, column=2, padx=4)

        ttk.Label(top, text="ffmpeg path:").grid(row=2, column=0, sticky="w")
        self.ffmpeg_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.ffmpeg_var, width=60).grid(row=2, column=1, padx=4)
        ttk.Button(top, text="Browse", command=self._browse_ffmpeg).grid(row=2, column=2, padx=4)

        ttk.Label(top, text="Assets dir:").grid(row=3, column=0, sticky="w")
        self.assets_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.assets_var, width=60).grid(row=3, column=1, padx=4)
        ttk.Button(top, text="Browse", command=self._browse_assets).grid(row=3, column=2, padx=4)

        # Middle: effects list with toggle & probability
        mid = ttk.LabelFrame(frm, text="Effects")
        mid.pack(fill="both", expand=True, pady=(0,8))

        self.effects_frame = ttk.Frame(mid)
        self.effects_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # We'll create effect rows dynamically
        self.effect_rows = []

        # Bottom: controls and log
        bottom = ttk.Frame(frm)
        bottom.pack(fill="both", expand=False)

        btn_frame = ttk.Frame(bottom)
        btn_frame.pack(fill="x", pady=(0,8))
        self.run_btn = ttk.Button(btn_frame, text="Run", command=self._on_run)
        self.run_btn.pack(side="left", padx=4)
        self.dry_btn = ttk.Button(btn_frame, text="Dry Run", command=self._on_dry_run)
        self.dry_btn.pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Load Config...", command=self._on_load_config).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Save Config...", command=self._on_save_config).pack(side="left", padx=4)

        self.log = tk.Text(bottom, height=12)
        self.log.pack(fill="both", expand=True)

    def _browse_input(self):
        p = filedialog.askopenfilename(title="Select input video", filetypes=[("Video files", "*.mp4;*.mov;*.mkv;*.avi"), ("All files","*.*")])
        if p:
            self.input_var.set(p)

    def _browse_output(self):
        p = filedialog.asksaveasfilename(title="Select output file", defaultextension=".mp4", filetypes=[("MP4", "*.mp4")])
        if p:
            self.output_var.set(p)

    def _browse_ffmpeg(self):
        p = filedialog.askopenfilename(title="Select ffmpeg.exe", filetypes=[("ffmpeg executable","ffmpeg.exe"),("All files","*.*")])
        if p:
            self.ffmpeg_var.set(p)

    def _browse_assets(self):
        p = filedialog.askdirectory(title="Select assets directory")
        if p:
            self.assets_var.set(p)
            # ensure asset structure exists
            assets.ensure_asset_dirs(p)

    def _load_config_into_ui(self, config):
        self.ffmpeg_var.set(config.get("ffmpeg_path", "ffmpeg"))
        self.assets_var.set(config.get("assets_dir", "assets"))
        # Clear current effect rows
        for child in self.effects_frame.winfo_children():
            child.destroy()
        self.effect_rows.clear()
        # Build rows
        effects_list = config.get("effect_chain", cfg.default_config()["effect_chain"])
        for i, eff in enumerate(effects_list):
            row = {}
            frame = ttk.Frame(self.effects_frame)
            frame.pack(fill="x", pady=2)
            row['enabled'] = tk.BooleanVar(value=eff.get("enabled", True))
            cb = ttk.Checkbutton(frame, text=eff["name"], variable=row['enabled'])
            cb.pack(side="left", padx=(2,8))
            ttk.Label(frame, text="Prob:").pack(side="left")
            row['prob'] = tk.DoubleVar(value=eff.get("probability", 1.0))
            s = ttk.Scale(frame, from_=0.0, to=1.0, variable=row['prob'], orient="horizontal", length=200)
            s.pack(side="left", padx=4)
            val_lbl = ttk.Label(frame, text=f"{row['prob'].get():.2f}")
            val_lbl.pack(side="left", padx=4)
            # update label when slider moves
            def _make_update(var, lbl):
                def _u(*_):
                    lbl.config(text=f"{var.get():.2f}")
                return _u
            row['prob'].trace_add("write", _make_update(row['prob'], val_lbl))
            row['conf'] = eff.copy()
            self.effect_rows.append(row)

    def _collect_config_from_ui(self):
        c = cfg.default_config()
        c["ffmpeg_path"] = self.ffmpeg_var.get() or c["ffmpeg_path"]
        c["assets_dir"] = self.assets_var.get() or c["assets_dir"]
        # refill effect chain from UI rows
        new_chain = []
        for row in self.effect_rows:
            conf = row['conf'].copy()
            conf['enabled'] = bool(row['enabled'].get())
            conf['probability'] = float(row['prob'].get())
            new_chain.append(conf)
        c['effect_chain'] = new_chain
        return c

    def _on_load_config(self):
        p = filedialog.askopenfilename(title="Load config JSON", filetypes=[("JSON","*.json"),("All","*.*")])
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.config = data
            self._load_config_into_ui(self.config)
            self._log(f"Loaded config: {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")

    def _on_save_config(self):
        p = filedialog.asksaveasfilename(title="Save config JSON", defaultextension=".json", filetypes=[("JSON","*.json")])
        if not p:
            return
        c = self._collect_config_from_ui()
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=2)
            self._log(f"Saved config: {p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def _log(self, text):
        self.log.insert("end", str(text) + "\n")
        self.log.see("end")

    def _run_processing_thread(self, cfg_data, input_path, output_path, dry_run=False):
        # Disable run buttons
        self.run_btn.config(state="disabled")
        self.dry_btn.config(state="disabled")
        def progress(stage, total, msg):
            self._log(f"[{stage}/{total}] {msg}")
        def target():
            try:
                processor.process_video(input_path, output_path, cfg_data, dry_run=dry_run, progress_callback=progress)
                self._log("Processing finished.")
            except Exception as e:
                self._log(f"Error: {e}")
            finally:
                self.run_btn.config(state="normal")
                self.dry_btn.config(state="normal")
        t = threading.Thread(target=target, daemon=True)
        t.start()

    def _on_run(self):
        input_path = self.input_var.get()
        output_path = self.output_var.get()
        if not input_path or not os.path.isfile(input_path):
            messagebox.showerror("Error", "Please choose a valid input file.")
            return
        if not output_path:
            messagebox.showerror("Error", "Please choose an output file path.")
            return
        cfg_data = self._collect_config_from_ui()
        self._run_processing_thread(cfg_data, input_path, output_path, dry_run=False)

    def _on_dry_run(self):
        input_path = self.input_var.get()
        output_path = self.output_var.get() or "<dry-run-output.mp4>"
        cfg_data = self._collect_config_from_ui()
        self._run_processing_thread(cfg_data, input_path, output_path, dry_run=True)

    def run(self):
        self.root.mainloop()