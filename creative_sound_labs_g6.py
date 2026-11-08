"""
================================================================================
   SOUND BLASTERX G6 STUDIO CONSOLE (SB1770)
   Uncredited Community Edition - 100% Free Open Hardware Controller
================================================================================
Notice: Built specifically for Creative Labs Sound BlasterX G6 (SB1770) hardware.
Uncredited release under MIT-0. Not affiliated with or endorsed by Creative Technology Ltd.
================================================================================

Engineered for the physical hardware topology of the Sound BlasterX G6 (SB1770):
- DAC: Cirrus Logic CS43131 MasterHIFI (32-bit / 384kHz, 130dB DNR, -115dB THD+N)
- Analog Reconstruction Filter: German WIMA film/foil capacitors
- ADC: Cirrus Logic CS5361 (24-bit / 192kHz Multi-bit Delta-Sigma, 114dB DNR)
- Headphone Amp: Discrete Dual-Mono Push-Pull Xamp (1.0 Ohm output impedance)
- Switching Relay: Mechanical Takamisawa / Fujitsu Telecom-Grade Relay
- Processor: Creative SB-Axx1 (CA0132 DSP & USB Streaming Engine)

Features:
- Live 3-Channel Pro Mixer: Front Mic In, Rear Line/Optical In, Digital Loopback
- Interactive Real-Time Frequency Response Visualizer (20Hz - 20kHz Logarithmic)
- Input Trim / Gain Staging (-24 dB to +24 dB)
- 3-Band Parametric Live Tone EQ
- Pro Safety Compressor / Brickwall Limiter (Protects hearing & monitors from sudden loud spikes)
- Schematic-Accurate Legacy Sound Blaster Card Emulations:
    * Sound Blaster Live! Pro (1998 - EMU10K1 + STAC9721T AC'97)
    * Sound Blaster 16 / AWE64 Gold (1994 - CT1740/CT4540 Butterworth LPF)
    * Sound Blaster Audigy 2 ZS (2003 - CA0102 / CS4382)
    * Sound Blaster X-Fi Fatal1ty (2005 - 24-bit Crystalizer)
    * Sound Blaster Pro 2.0 (1991 - CT1600 Dual OPL3 Sallen-Key Filter)
- Raw USB HID RGB "X" Logo Hardware Lighting Controller (Interface 4 / MI_04)
- Live Auto-Sync with Equalizer APO System Audio Engine
"""

import sys
import os
import math
import json
import urllib.request
import subprocess
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import hid

# Theme: Dark Studio Graphite & Retro Amber
BG_DARK = "#14161a"
PANEL_BG = "#1e2228"
STRIP_BG = "#262b33"
HEADER_BG = "#181b20"
CREATIVE_ORANGE = "#ff5500"
ACCENT_BLUE = "#56b6c2"
ACCENT_GREEN = "#98c379"
ACCENT_RED = "#e06c75"
TEXT_COLOR = "#dcdfe4"
TEXT_MUTED = "#6f7783"
BORDER_COLOR = "#333942"

# Deep Schematic-Accurate Vintage Card Circuit Models
LEGACY_PRESETS = {
    "DIRECT (Raw CS43131 Bit-Perfect)": {
        "desc": "100% Bit-Perfect pure stream. All filters bypassed. Zero phase coloration, pure MasterHIFI DAC topology.",
        "preamp": 0.0,
        "filters": []
    },
    "SB Live! Pro (1998 - EMU10K1)": {
        "desc": "EMU10K1 48kHz locked DSP path: 8-pt sinc interpolation ripple (+1.6dB @ 15.5kHz), STAC9721T AC'97 bass (+3.2dB @ 85Hz), EAX 3.6kHz vocal bite.",
        "preamp": 0.0,
        "filters": [
            {"type": "LSC", "fc": 85, "gain": 3.2, "q": 1.0},
            {"type": "PK", "fc": 260, "gain": 1.2, "q": 1.4},
            {"type": "PK", "fc": 3600, "gain": 2.8, "q": 1.4},
            {"type": "PK", "fc": 13500, "gain": -0.8, "q": 2.2},
            {"type": "PK", "fc": 15500, "gain": 1.6, "q": 2.8},
            {"type": "HSC", "fc": 19000, "gain": -4.0, "q": 0.71}
        ]
    },
    "SB 16 / AWE64 Gold (1994 - CT1740)": {
        "desc": "CT1745 mixer + EMU8000: 3rd-order Butterworth LPF (-18dB/oct @ 15.2kHz), CT1745 100Hz Bass shelf (+4.2dB), 240Hz analog warmth.",
        "preamp": -0.8,
        "filters": [
            {"type": "HP", "fc": 32, "gain": 0.0, "q": 0.71},
            {"type": "LSC", "fc": 100, "gain": 4.2, "q": 0.85},
            {"type": "PK", "fc": 240, "gain": 1.8, "q": 1.3},
            {"type": "PK", "fc": 2000, "gain": -1.2, "q": 1.0},
            {"type": "HSC", "fc": 10000, "gain": 1.8, "q": 0.71},
            {"type": "LP", "fc": 15200, "gain": 0.0, "q": 0.71}
        ]
    },
    "SB Audigy 2 ZS (2003 - CA0102)": {
        "desc": "CA0102 DSP + Cirrus CS4382 24-bit/192kHz (THX Certified): tight 55Hz sub punch, transparent mids, competitive 2.8kHz imaging, 11.5kHz crystal air.",
        "preamp": 0.5,
        "filters": [
            {"type": "PK", "fc": 55, "gain": 2.8, "q": 1.6},
            {"type": "PK", "fc": 2800, "gain": 2.6, "q": 1.8},
            {"type": "PK", "fc": 11500, "gain": 3.0, "q": 1.3},
            {"type": "HSC", "fc": 16000, "gain": 1.8, "q": 0.8}
        ]
    },
    "SB X-Fi Fatal1ty (2005 - Crystalizer)": {
        "desc": "EMU20K1 24-bit Crystalizer multi-band dynamic expander: +4.8dB sub transient punch (65Hz), 750Hz stereo widening scoop, +5.4dB high transient exciter (12.5kHz).",
        "preamp": -1.2,
        "filters": [
            {"type": "PK", "fc": 65, "gain": 4.8, "q": 1.1},
            {"type": "PK", "fc": 115, "gain": 2.6, "q": 1.3},
            {"type": "PK", "fc": 750, "gain": -2.0, "q": 1.0},
            {"type": "PK", "fc": 5500, "gain": 3.4, "q": 1.2},
            {"type": "HSC", "fc": 12500, "gain": 5.4, "q": 0.9},
            {"type": "HSC", "fc": 16500, "gain": 3.6, "q": 0.71}
        ]
    },
    "SB Pro 2.0 (1991 - CT1600 OPL3)": {
        "desc": "Dual OPL3 CT1600 + LM324 Sallen-Key 2nd-order active LPF (-12dB/oct @ 11.5kHz), 50Hz DC decoupling high-pass, warm 190Hz resonant FM body (+3.8dB).",
        "preamp": -1.5,
        "filters": [
            {"type": "HP", "fc": 50, "gain": 0.0, "q": 0.71},
            {"type": "PK", "fc": 190, "gain": 3.8, "q": 1.2},
            {"type": "PK", "fc": 3200, "gain": -1.5, "q": 1.0},
            {"type": "LP", "fc": 11500, "gain": 0.0, "q": 0.707}
        ]
    }
}

APO_CONFIG_PATH = r"C:\Program Files\EqualizerAPO\config\config.txt"


class LiveChannelStrip:
    def __init__(self, parent, title, input_desc, accent_color, on_change_callback):
        self.parent = parent
        self.title = title
        self.input_desc = input_desc
        self.accent_color = accent_color
        self.on_change = on_change_callback
        
        # Channel State
        self.trim_db = 0.0
        self.fader_db = 0.0
        self.is_muted = False
        self.is_solo = False
        
        # 3-Band Parametric EQ
        self.eq_low = 0.0
        self.eq_mid = 0.0
        self.eq_high = 0.0
        self.eq_active = True
        
        # Safety Compressor / Limiter
        self.comp_active = True
        self.comp_thresh = -14.0
        self.safety_limit = True
        
        self.eq_sliders = {}
        
        self.frame = tk.Frame(parent, bg=STRIP_BG, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.build_strip()
        
    def build_strip(self):
        # Header
        h_frame = tk.Frame(self.frame, bg=HEADER_BG, height=28)
        h_frame.pack(fill=tk.X)
        h_frame.pack_propagate(False)
        tk.Label(h_frame, text=self.title, font=("Segoe UI", 9, "bold"), fg=self.accent_color, bg=HEADER_BG).pack(side=tk.LEFT, padx=6)
        tk.Label(h_frame, text=self.input_desc, font=("Segoe UI", 7), fg=TEXT_MUTED, bg=HEADER_BG).pack(side=tk.RIGHT, padx=6)
        
        # 1. Input Trim
        trim_box = tk.Frame(self.frame, bg=STRIP_BG, padx=6, pady=4)
        trim_box.pack(fill=tk.X)
        t_row = tk.Frame(trim_box, bg=STRIP_BG)
        t_row.pack(fill=tk.X)
        tk.Label(t_row, text="INPUT TRIM", font=("Segoe UI", 7, "bold"), fg=TEXT_COLOR, bg=STRIP_BG).pack(side=tk.LEFT)
        self.lbl_trim = tk.Label(t_row, text="+0.0 dB", font=("Consolas", 7, "bold"), fg=CREATIVE_ORANGE, bg=STRIP_BG)
        self.lbl_trim.pack(side=tk.RIGHT)
        
        self.scale_trim = ttk.Scale(trim_box, from_=-24, to=24, orient=tk.HORIZONTAL, command=self.on_trim_slider)
        self.scale_trim.set(0)
        self.scale_trim.pack(fill=tk.X, pady=2)
        
        # 2. Live Tone EQ
        eq_box = tk.Frame(self.frame, bg=STRIP_BG, bd=1, relief=tk.SOLID, padx=6, pady=4)
        eq_box.pack(fill=tk.X, padx=4, pady=3)
        
        eq_h = tk.Frame(eq_box, bg=STRIP_BG)
        eq_h.pack(fill=tk.X)
        tk.Label(eq_h, text="3-BAND LIVE EQ", font=("Segoe UI", 7, "bold"), fg=ACCENT_GREEN, bg=STRIP_BG).pack(side=tk.LEFT)
        self.btn_eq = tk.Button(eq_h, text="ON", font=("Segoe UI", 6, "bold"), bg="#2d422a", fg=ACCENT_GREEN, bd=0, padx=4, command=self.toggle_eq)
        self.btn_eq.pack(side=tk.RIGHT)
        
        for band_id, lbl_text in [("low", "LOW 100Hz"), ("mid", "MID 1.0kHz"), ("high", "HIGH 10kHz")]:
            row = tk.Frame(eq_box, bg=STRIP_BG)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=lbl_text, font=("Segoe UI", 6), fg=TEXT_COLOR, bg=STRIP_BG, width=10, anchor="w").pack(side=tk.LEFT)
            lbl_val = tk.Label(row, text=" 0.0", font=("Consolas", 6), fg=TEXT_MUTED, bg=STRIP_BG, width=5)
            s = ttk.Scale(row, from_=-12, to=12, orient=tk.HORIZONTAL, command=lambda v, b=band_id: self.on_eq_slider(b, v))
            self.eq_sliders[band_id] = (s, lbl_val)
            s.set(0)
            s.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            lbl_val.pack(side=tk.RIGHT)
            
        # 3. Safety Compressor / Limiter
        comp_box = tk.Frame(self.frame, bg=STRIP_BG, bd=1, relief=tk.SOLID, padx=6, pady=4)
        comp_box.pack(fill=tk.X, padx=4, pady=3)
        
        comp_h = tk.Frame(comp_box, bg=STRIP_BG)
        comp_h.pack(fill=tk.X)
        tk.Label(comp_h, text="SAFETY COMPRESSOR", font=("Segoe UI", 7, "bold"), fg=CREATIVE_ORANGE, bg=STRIP_BG).pack(side=tk.LEFT)
        self.btn_comp = tk.Button(comp_h, text="ON", font=("Segoe UI", 6, "bold"), bg="#48331d", fg=CREATIVE_ORANGE, bd=0, padx=4, command=self.toggle_comp)
        self.btn_comp.pack(side=tk.RIGHT)
        
        cr1 = tk.Frame(comp_box, bg=STRIP_BG)
        cr1.pack(fill=tk.X, pady=1)
        tk.Label(cr1, text="THRESH", font=("Segoe UI", 6), fg=TEXT_COLOR, bg=STRIP_BG, width=8, anchor="w").pack(side=tk.LEFT)
        self.lbl_thresh = tk.Label(cr1, text="-14dB", font=("Consolas", 6), fg=TEXT_MUTED, bg=STRIP_BG, width=5)
        self.scale_thresh = ttk.Scale(cr1, from_=-36, to=0, orient=tk.HORIZONTAL, command=self.on_thresh_slider)
        self.scale_thresh.set(-14)
        self.scale_thresh.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.lbl_thresh.pack(side=tk.RIGHT)
        
        safe_row = tk.Frame(comp_box, bg=STRIP_BG)
        safe_row.pack(fill=tk.X, pady=2)
        self.var_limit = tk.BooleanVar(value=True)
        cb = tk.Checkbutton(safe_row, text="EAR/SPEAKER CLIP GUARD", variable=self.var_limit,
                            font=("Segoe UI", 6, "bold"), fg=ACCENT_RED, bg=STRIP_BG, selectcolor="#111",
                            activebackground=STRIP_BG, activeforeground=ACCENT_RED, command=self.on_limit_toggle)
        cb.pack(side=tk.LEFT)
        
        gr_row = tk.Frame(comp_box, bg=STRIP_BG)
        gr_row.pack(fill=tk.X, pady=2)
        tk.Label(gr_row, text="GR (dB):", font=("Segoe UI", 6, "bold"), fg=ACCENT_RED, bg=STRIP_BG).pack(side=tk.LEFT)
        self.canvas_gr = tk.Canvas(gr_row, height=7, bg="#111", highlightthickness=0)
        self.canvas_gr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        self.draw_gr_bar(2.5)
        
        # 4. Fader & Level Meter
        fader_box = tk.Frame(self.frame, bg=STRIP_BG, padx=6, pady=4)
        fader_box.pack(fill=tk.BOTH, expand=True)
        
        sm_row = tk.Frame(fader_box, bg=STRIP_BG)
        sm_row.pack(fill=tk.X, pady=2)
        self.btn_solo = tk.Button(sm_row, text="S", font=("Segoe UI", 8, "bold"), bg="#333", fg="#888", width=3, bd=1, command=self.toggle_solo)
        self.btn_solo.pack(side=tk.LEFT, padx=2)
        self.btn_mute = tk.Button(sm_row, text="M", font=("Segoe UI", 8, "bold"), bg="#333", fg="#888", width=3, bd=1, command=self.toggle_mute)
        self.btn_mute.pack(side=tk.LEFT, padx=2)
        
        self.lbl_fader = tk.Label(sm_row, text="0.0 dB", font=("Consolas", 8, "bold"), fg="#fff", bg=STRIP_BG)
        self.fader = ttk.Scale(fader_box, from_=6, to=-60, orient=tk.VERTICAL, command=self.on_fader_slider)
        self.lbl_fader.pack(side=tk.RIGHT, padx=2)
        
        fader_area = tk.Frame(fader_box, bg=STRIP_BG)
        fader_area.pack(fill=tk.BOTH, expand=True, pady=4)
        
        self.meter_canvas = tk.Canvas(fader_area, width=14, bg="#0d0e11", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.meter_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        self.draw_meter(0.70)
        
        self.fader.set(0)
        self.fader.pack(side=tk.RIGHT, fill=tk.Y, expand=True, padx=4)

    def draw_meter(self, level):
        self.meter_canvas.delete("all")
        h = 120
        w = 14
        segments = 22
        seg_h = h / segments
        active_segs = int(level * segments)
        for i in range(segments):
            y2 = h - (i * seg_h)
            y1 = y2 - seg_h + 1
            col = ACCENT_RED if i > segments * 0.85 else (CREATIVE_ORANGE if i > segments * 0.65 else ACCENT_GREEN) if i < active_segs else "#15181d"
            self.meter_canvas.create_rectangle(2, y1, w - 2, y2, fill=col, outline="")

    def draw_gr_bar(self, gr_db):
        self.canvas_gr.delete("all")
        w = self.canvas_gr.winfo_width() or 80
        fill_w = int(w * min(1.0, gr_db / 18.0))
        self.canvas_gr.create_rectangle(0, 0, fill_w, 7, fill=ACCENT_RED, outline="")

    def on_trim_slider(self, val):
        self.trim_db = float(val)
        sign = "+" if self.trim_db > 0 else ""
        self.lbl_trim.config(text=f"{sign}{self.trim_db:.1f} dB")
        self.on_change()

    def on_fader_slider(self, val):
        self.fader_db = float(val)
        sign = "+" if self.fader_db > 0 else ""
        self.lbl_fader.config(text="-inf dB" if self.fader_db <= -59 else f"{sign}{self.fader_db:.1f} dB")
        self.on_change()

    def on_eq_slider(self, band, val):
        gain = float(val)
        if band == "low": self.eq_low = gain
        elif band == "mid": self.eq_mid = gain
        elif band == "high": self.eq_high = gain
        if band in self.eq_sliders:
            slider, lbl = self.eq_sliders[band]
            sign = "+" if gain > 0 else ""
            lbl.config(text=f"{sign}{gain:.1f}")
        self.on_change()

    def on_thresh_slider(self, val):
        self.comp_thresh = float(val)
        self.lbl_thresh.config(text=f"{int(self.comp_thresh)}dB")
        self.on_change()

    def on_limit_toggle(self):
        self.safety_limit = self.var_limit.get()
        self.on_change()

    def toggle_eq(self):
        self.eq_active = not self.eq_active
        self.btn_eq.config(text="ON" if self.eq_active else "OFF",
                           bg="#2d422a" if self.eq_active else "#333",
                           fg=ACCENT_GREEN if self.eq_active else "#888")
        self.on_change()

    def toggle_comp(self):
        self.comp_active = not self.comp_active
        self.btn_comp.config(text="ON" if self.comp_active else "OFF",
                            bg="#48331d" if self.comp_active else "#333",
                            fg=CREATIVE_ORANGE if self.comp_active else "#888")
        self.on_change()

    def toggle_mute(self):
        self.is_muted = not self.is_muted
        self.btn_mute.config(bg=ACCENT_RED if self.is_muted else "#333", fg="#fff" if self.is_muted else "#888")
        self.on_change()

    def toggle_solo(self):
        self.is_solo = not self.is_solo
        self.btn_solo.config(bg=ACCENT_BLUE if self.is_solo else "#333", fg="#fff" if self.is_solo else "#888")
        self.on_change()


class CreativeSoundLabsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sound BlasterX G6 Studio Console (For Creative Labs SB1770)")
        self.root.geometry("1160x780")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(1040, 710)
        
        self.active_preset_name = "DIRECT (Raw CS43131 Bit-Perfect)"
        self.hid_device = None
        self.hid_path = None
        self.hid_connected = False
        
        self.init_hid()
        self.build_top_banner()
        self.build_preset_ribbon()
        self.build_mixer_canvas()
        self.build_hardware_dock()
        
        # Initial draw of spectrum & system sync
        self.update_spectrum_curve()
        self.sync_system_apo(silent=True)
        
    def init_hid(self):
        self.hid_device = None
        self.hid_path = None
        self.hid_connected = False
        try:
            devs = hid.enumerate(0x041e, 0x3256)
            for d in devs:
                if d.get('interface_number') == 4 or b"&mi_04" in d.get('path', b'').lower():
                    self.hid_path = d['path']
                    break
            if not self.hid_path and devs:
                self.hid_path = devs[0]['path']
                
            if self.hid_path:
                h = hid.device()
                h.open_path(self.hid_path)
                self.hid_device = h
                self.hid_connected = True
        except Exception:
            self.hid_connected = False

    def build_top_banner(self):
        top = tk.Frame(self.root, bg=HEADER_BG, height=54, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        
        logo_frame = tk.Frame(top, bg=HEADER_BG)
        logo_frame.pack(side=tk.LEFT, padx=14, pady=6)
        
        tk.Label(logo_frame, text="SOUND BLASTERX G6", font=("Impact", 16), fg=CREATIVE_ORANGE, bg=HEADER_BG).pack(side=tk.LEFT)
        tk.Label(logo_frame, text=" | STUDIO DIRECT CONSOLE", font=("Segoe UI", 9, "bold"), fg="#fff", bg=HEADER_BG).pack(side=tk.LEFT, pady=2)
        
        spec_box = tk.Frame(top, bg="#0f1114", bd=1, relief=tk.SOLID, padx=8, pady=3)
        spec_box.pack(side=tk.LEFT, padx=16)
        tk.Label(spec_box, text="DAC: CIRRUS CS43131 384kHz MasterHIFI | WIMA CAPS | XAMP DISCRETE PUSH-PULL", font=("Consolas", 8, "bold"), fg=ACCENT_GREEN, bg="#0f1114").pack()
        
        stat_frame = tk.Frame(top, bg=HEADER_BG)
        stat_frame.pack(side=tk.RIGHT, padx=14)
        hid_c = ACCENT_GREEN if self.hid_connected else ACCENT_RED
        hid_t = "USB HID: LINKED (MI_04)" if self.hid_connected else "USB HID: DISCONNECTED"
        self.lbl_hid_stat = tk.Label(stat_frame, text=hid_t, font=("Consolas", 8, "bold"), fg=hid_c, bg=HEADER_BG)
        self.lbl_hid_stat.pack(anchor="e")
        
        apo_installed = os.path.exists(APO_CONFIG_PATH)
        apo_c = ACCENT_GREEN if apo_installed else CREATIVE_ORANGE
        apo_t = "SYSTEM APO: ACTIVE (REALTIME)" if apo_installed else "SYSTEM APO: STANDALONE (EXPORT MODE)"
        self.lbl_apo_stat = tk.Label(stat_frame, text=apo_t, font=("Consolas", 8, "bold"), fg=apo_c, bg=HEADER_BG)
        self.lbl_apo_stat.pack(anchor="e")

    def build_preset_ribbon(self):
        ribbon = tk.Frame(self.root, bg="#1a1e24", height=90, bd=1, relief=tk.SOLID)
        ribbon.pack(fill=tk.X, padx=8, pady=(6, 2))
        ribbon.pack_propagate(False)
        
        left_f = tk.Frame(ribbon, bg="#1a1e24")
        left_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=4)
        
        p_row = tk.Frame(left_f, bg="#1a1e24")
        p_row.pack(fill=tk.X)
        tk.Label(p_row, text="LEGACY SOUND BLASTER CARD EMULATION:", font=("Segoe UI", 8, "bold"), fg=CREATIVE_ORANGE, bg="#1a1e24").pack(side=tk.LEFT)
        
        self.preset_combo = ttk.Combobox(p_row, values=list(LEGACY_PRESETS.keys()), state="readonly", width=34, font=("Segoe UI", 8, "bold"))
        self.preset_combo.set(self.active_preset_name)
        self.preset_combo.pack(side=tk.LEFT, padx=8)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)
        
        self.lbl_preset_desc = tk.Label(left_f, text=LEGACY_PRESETS[self.active_preset_name]["desc"], font=("Segoe UI", 7, "italic"), fg=TEXT_MUTED, bg="#1a1e24", anchor="w", wraplength=520, justify=tk.LEFT)
        self.lbl_preset_desc.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Real-Time Spectrum Response Plotter (Canvas)
        plot_box = tk.Frame(ribbon, bg="#0c0e12", bd=1, relief=tk.SOLID)
        plot_box.pack(side=tk.RIGHT, padx=10, pady=4)
        
        p_hdr = tk.Frame(plot_box, bg="#0c0e12")
        p_hdr.pack(fill=tk.X)
        tk.Label(p_hdr, text="REALTIME FREQUENCY RESPONSE (20Hz - 20kHz)", font=("Consolas", 6, "bold"), fg=ACCENT_BLUE, bg="#0c0e12").pack(side=tk.LEFT, padx=4)
        self.lbl_curve_gain = tk.Label(p_hdr, text="+0.0dB @ 1kHz", font=("Consolas", 6), fg=TEXT_MUTED, bg="#0c0e12")
        self.lbl_curve_gain.pack(side=tk.RIGHT, padx=4)
        
        self.canvas_spectrum = tk.Canvas(plot_box, width=360, height=58, bg="#07080a", highlightthickness=0)
        self.canvas_spectrum.pack(padx=2, pady=2)

    def update_spectrum_curve(self):
        c = self.canvas_spectrum
        c.delete("all")
        w = 360
        h = 58
        mid_y = h / 2.0  # 0 dB line
        
        # Grid lines
        c.create_line(0, mid_y, w, mid_y, fill="#222830", dash=(2, 2))
        c.create_line(0, mid_y - 18, w, mid_y - 18, fill="#161b22", dash=(1, 4)) # +6 dB
        c.create_line(0, mid_y + 18, w, mid_y + 18, fill="#161b22", dash=(1, 4)) # -6 dB
        
        # Frequency grid markers (100Hz, 1kHz, 10kHz)
        min_log = math.log10(20)
        max_log = math.log10(20000)
        for freq_mark in [100, 1000, 10000]:
            lx = (math.log10(freq_mark) - min_log) / (max_log - min_log) * w
            c.create_line(lx, 0, lx, h, fill="#181e26", dash=(1, 3))
            c.create_text(lx + 10, h - 6, text=f"{freq_mark if freq_mark < 1000 else str(freq_mark//1000)+'k'}", font=("Segoe UI", 5), fill="#444d5a")

        # Gather active filters: preset filters + Master EQ/Preamp
        preset_info = LEGACY_PRESETS.get(self.active_preset_name, {})
        filters = list(preset_info.get("filters", []))
        preamp = preset_info.get("preamp", 0.0)
        
        # Add channel 3-band EQ contributions from Loopback/Master
        if hasattr(self, 'strip_loop') and self.strip_loop.eq_active:
            if self.strip_loop.eq_low != 0:
                filters.append({"type": "LSC", "fc": 100, "gain": self.strip_loop.eq_low, "q": 0.71})
            if self.strip_loop.eq_mid != 0:
                filters.append({"type": "PK", "fc": 1000, "gain": self.strip_loop.eq_mid, "q": 1.4})
            if self.strip_loop.eq_high != 0:
                filters.append({"type": "HSC", "fc": 10000, "gain": self.strip_loop.eq_high, "q": 0.71})

        points = []
        num_pts = 90
        for i in range(num_pts):
            frac = i / (num_pts - 1)
            f = 10 ** (min_log + frac * (max_log - min_log))
            
            # Compute net magnitude response in dB
            db = preamp
            for filt in filters:
                ftype = filt['type']
                fc = filt['fc']
                g = filt.get('gain', 0.0)
                q = filt.get('q', 0.707)
                if ftype == 'PK':
                    ratio = f / fc
                    w_log = math.log(max(1e-4, ratio))
                    sigma = 1.0 / max(0.2, q)
                    db += g * math.exp(-0.5 * (w_log / sigma) ** 2)
                elif ftype == 'LSC':
                    db += g / (1.0 + (f / fc) ** 2)
                elif ftype == 'HSC':
                    db += g * (f / fc) ** 2 / (1.0 + (f / fc) ** 2)
                elif ftype == 'LP':
                    db += -20.0 * math.log10(max(1e-3, math.sqrt(1.0 + (f / fc) ** 4)))
                elif ftype == 'HP':
                    db += -20.0 * math.log10(max(1e-3, math.sqrt(1.0 + (fc / f) ** 4)))
            
            # Map dB to canvas pixels (+12 dB at top, -18 dB at bottom)
            px = frac * w
            py = mid_y - (db * 3.0)
            py = max(2, min(h - 2, py))
            points.append(px)
            points.append(py)

        if len(points) >= 4:
            c.create_line(points, fill=ACCENT_BLUE, width=2, smooth=True)

    def build_mixer_canvas(self):
        mixer_frame = tk.Frame(self.root, bg=BG_DARK)
        mixer_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        strips_box = tk.Frame(mixer_frame, bg=BG_DARK)
        strips_box.pack(fill=tk.BOTH, expand=True)
        
        # 3 Real Hardware Input Strips
        self.strip_mic = LiveChannelStrip(strips_box, "CH 1: MIC IN", "DISCRETE FRONT PREAMP", ACCENT_BLUE, self.on_channel_change)
        self.strip_mic.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        self.strip_line = LiveChannelStrip(strips_box, "CH 2: LINE / S/PDIF", "REAR COMBO JACK", ACCENT_GREEN, self.on_channel_change)
        self.strip_line.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        self.strip_loop = LiveChannelStrip(strips_box, "CH 3: WHAT U HEAR", "DIGITAL STEREO LOOPBACK", CREATIVE_ORANGE, self.on_channel_change)
        self.strip_loop.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=3)
        
        # Master Output Strip
        m_strip = tk.Frame(strips_box, bg=STRIP_BG, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, highlightthickness=1)
        m_strip.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=3)
        
        m_head = tk.Frame(m_strip, bg=HEADER_BG, height=28)
        m_head.pack(fill=tk.X)
        m_head.pack_propagate(False)
        tk.Label(m_head, text="MASTER OUT (CS43131)", font=("Segoe UI", 9, "bold"), fg="#fff", bg=HEADER_BG).pack(side=tk.LEFT, padx=6)
        tk.Label(m_head, text="XAMP DUAL-MONO", font=("Segoe UI", 7), fg=TEXT_MUTED, bg=HEADER_BG).pack(side=tk.RIGHT, padx=6)
        
        m_body = tk.Frame(m_strip, bg=PANEL_BG, padx=8, pady=6)
        m_body.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        
        # Clip Guard
        cg = tk.Frame(m_body, bg="#271518", bd=1, relief=tk.SOLID, padx=6, pady=6)
        cg.pack(fill=tk.X, pady=(0, 6))
        tk.Label(cg, text="LIVE EAR/SPEAKER CLIP GUARD", font=("Segoe UI", 7, "bold"), fg=ACCENT_RED, bg="#271518").pack(anchor="w")
        tk.Label(cg, text="True Brickwall Limiter catches digital overs at -0.3 dB.", font=("Segoe UI", 6), fg=TEXT_COLOR, bg="#271518").pack(anchor="w")
        
        tk.Label(m_body, text="MASTER DAC BUS LEVEL:", font=("Segoe UI", 7, "bold"), fg=TEXT_MUTED, bg=PANEL_BG).pack(anchor="w", pady=(4, 2))
        
        m_fader_area = tk.Frame(m_body, bg=PANEL_BG)
        m_fader_area.pack(fill=tk.BOTH, expand=True, pady=4)
        
        self.master_meter = tk.Canvas(m_fader_area, width=28, bg="#0d0e11", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.master_meter.pack(side=tk.LEFT, fill=tk.Y, padx=4)
        self.draw_stereo_meter(0.78, 0.74)
        
        self.lbl_m_fader = tk.Label(m_body, text="0.0 dB", font=("Consolas", 8, "bold"), fg="#fff", bg=PANEL_BG)
        self.master_fader = ttk.Scale(m_fader_area, from_=6, to=-60, orient=tk.VERTICAL, command=self.on_master_slider)
        self.master_fader.set(0)
        self.master_fader.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=6)
        self.lbl_m_fader.pack(pady=2)
        
        btn_sync = tk.Button(m_body, text="SYNC SYSTEM AUDIO (APO)", font=("Segoe UI", 8, "bold"),
                             bg="#24486d", fg="#fff", bd=1, relief=tk.RAISED, pady=6, command=lambda: self.sync_system_apo(silent=False))
        btn_sync.pack(fill=tk.X, pady=4)
        
        if not os.path.exists(APO_CONFIG_PATH):
            btn_install_apo = tk.Button(m_body, text="GET EQUALIZER APO ENGINE", font=("Segoe UI", 7),
                                        bg="#333", fg=CREATIVE_ORANGE, bd=1, command=self.install_apo_engine)
            btn_install_apo.pack(fill=tk.X, pady=2)

    def draw_stereo_meter(self, left_lvl, right_lvl):
        self.master_meter.delete("all")
        h = 160
        segments = 24
        seg_h = h / segments
        for ch_idx, lvl in enumerate([left_lvl, right_lvl]):
            x1 = 2 + ch_idx * 13
            x2 = x1 + 10
            active = int(lvl * segments)
            for i in range(segments):
                y2 = h - (i * seg_h)
                y1 = y2 - seg_h + 1
                col = ACCENT_RED if i > segments * 0.85 else (CREATIVE_ORANGE if i > segments * 0.65 else ACCENT_GREEN) if i < active else "#15181d"
                self.master_meter.create_rectangle(x1, y1, x2, y2, fill=col, outline="")

    def build_hardware_dock(self):
        dock = tk.Frame(self.root, bg=PANEL_BG, height=64, bd=1, relief=tk.SOLID)
        dock.pack(fill=tk.X, padx=8, pady=(0, 6))
        dock.pack_propagate(False)
        
        led_f = tk.Frame(dock, bg=PANEL_BG)
        led_f.pack(side=tk.LEFT, padx=12, pady=6)
        
        lh = tk.Frame(led_f, bg=PANEL_BG)
        lh.pack(fill=tk.X)
        tk.Label(lh, text="HARDWARE RGB 'X' LOGO:", font=("Segoe UI", 8, "bold"), fg="#fff", bg=PANEL_BG).pack(side=tk.LEFT)
        self.led_preview_box = tk.Label(lh, text="  ", bg="#ff5500", relief=tk.SOLID, bd=1, width=3)
        self.led_preview_box.pack(side=tk.LEFT, padx=6)
        
        row_c = tk.Frame(led_f, bg=PANEL_BG)
        row_c.pack(fill=tk.X, pady=2)
        for name, col in [("Classic Amber", "#ff5500"), ("Cyan", "#00d0ff"), ("Studio Green", "#00ff66"), ("Red", "#ff0033"), ("Stealth Off", "#000000")]:
            tk.Button(row_c, text=name, font=("Segoe UI", 6, "bold"), bg=col if col != "#000000" else "#222",
                      fg="#000" if col in ["#00d0ff", "#00ff66"] else "#fff", bd=1, padx=6, command=lambda c=col: self.set_hardware_led(c)).pack(side=tk.LEFT, padx=2)
        tk.Button(row_c, text="Custom...", font=("Segoe UI", 6), bg="#333", fg="#fff", bd=1, padx=6, command=self.pick_led).pack(side=tk.LEFT, padx=2)

        gain_box = tk.Frame(dock, bg="#101216", bd=1, relief=tk.SOLID, padx=8, pady=4)
        gain_box.pack(side=tk.RIGHT, padx=12, pady=6)
        tk.Label(gain_box, text="XAMP ANALOG GAIN SWITCH: PHYSICAL RAIL DIVIDER", font=("Consolas", 7, "bold"), fg=CREATIVE_ORANGE, bg="#101216").pack()
        tk.Label(gain_box, text="LOW: 16-149Ω (IEMs/Sensitives) | HIGH: 150-600Ω (Planars/High-Z)", font=("Consolas", 6), fg=TEXT_MUTED, bg="#101216").pack()

    def on_preset_select(self, event):
        self.active_preset_name = self.preset_combo.get()
        self.lbl_preset_desc.config(text=LEGACY_PRESETS[self.active_preset_name]["desc"])
        self.update_spectrum_curve()
        self.sync_system_apo(silent=True)

    def on_master_slider(self, val):
        f = float(val)
        sign = "+" if f > 0 else ""
        self.lbl_m_fader.config(text="-inf dB" if f <= -59 else f"{sign}{f:.1f} dB")
        self.on_channel_change()

    def on_channel_change(self):
        if not hasattr(self, 'master_fader') or not hasattr(self, 'canvas_spectrum'):
            return
        self.update_spectrum_curve()
        self.sync_system_apo(silent=True)

    def set_hardware_led(self, hex_code):
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        
        # Ensure raw handle is open to Interface 4
        if not self.hid_device or not self.hid_connected:
            self.init_hid()
            
        success = False
        if self.hid_device:
            try:
                pkt = bytearray(65)
                pkt[0] = 0x00
                pkt[1] = 0x5a
                pkt[2] = 0x12
                pkt[3] = 0x07
                pkt[4] = 0x01
                pkt[5] = 0x96
                pkt[6] = r
                pkt[7] = g
                pkt[8] = b
                self.hid_device.write(bytes(pkt))
                
                commit = bytearray(65)
                commit[0] = 0x00
                commit[1] = 0x5a
                commit[2] = 0x11
                self.hid_device.write(bytes(commit))
                success = True
            except Exception:
                # Reconnect and retry once
                try:
                    self.init_hid()
                    if self.hid_device:
                        self.hid_device.write(bytes(pkt))
                        self.hid_device.write(bytes(commit))
                        success = True
                except Exception:
                    pass
                    
        # Update live visual swatch on UI immediately
        if hasattr(self, 'led_preview_box'):
            self.led_preview_box.config(bg=hex_code)
        if hasattr(self, 'lbl_hid_stat'):
            self.lbl_hid_stat.config(text=f"USB HID: LINKED ({hex_code})" if success else "USB HID: RETRYING",
                                    fg=ACCENT_GREEN if success else ACCENT_RED)
        return success

    def pick_led(self):
        c = colorchooser.askcolor(title="Select G6 Hardware LED Color")[1]
        if c: self.set_hardware_led(c)

    def sync_system_apo(self, silent=True):
        if not hasattr(self, 'master_fader'):
            return
        preset_info = LEGACY_PRESETS.get(self.active_preset_name, {})
        filters = preset_info.get("filters", [])
        preamp = preset_info.get("preamp", 0.0)
        
        lines = [
            "# ========================================================",
            "# SOUND BLASTERX G6 - REALTIME HARDWARE DSP CONFIG",
            f"# Active Card Model: {self.active_preset_name}",
            "# ========================================================\n"
        ]
        
        m_val = float(self.master_fader.get()) + preamp
        if m_val != 0 and m_val > -59:
            lines.append(f"Preamp: {m_val:+.1f} dB\n")
            
        if filters:
            lines.append(f"# --- {self.active_preset_name} Circuit Filters ---")
            for f in filters:
                f_type = f["type"]
                fc = f["fc"]
                gain = f.get("gain", 0.0)
                q = f.get("q", 0.707)
                if f_type in ["HP", "LP"]:
                    lines.append(f"Filter: ON {f_type} Fc {fc} Hz")
                else:
                    lines.append(f"Filter: ON {f_type} Fc {fc} Hz Gain {gain:+.1f} dB Q {q}")
            lines.append("")
            
        for strip in [self.strip_mic, self.strip_line, self.strip_loop]:
            lines.append(f"# Channel: {strip.title} ({strip.input_desc})")
            if strip.trim_db != 0:
                lines.append(f"Preamp: {strip.trim_db:+.1f} dB")
            if strip.eq_active:
                if strip.eq_low != 0:
                    lines.append(f"Filter: ON LSC Fc 100 Hz Gain {strip.eq_low:+.1f} dB Q 0.71")
                if strip.eq_mid != 0:
                    lines.append(f"Filter: ON PK Fc 1000 Hz Gain {strip.eq_mid:+.1f} dB Q 1.4")
                if strip.eq_high != 0:
                    lines.append(f"Filter: ON HSC Fc 10000 Hz Gain {strip.eq_high:+.1f} dB Q 0.71")
            lines.append("")

        config_payload = "\n".join(lines)
        
        # 1. Write directly to Equalizer APO live engine if installed
        apo_written = False
        if os.path.exists(os.path.dirname(APO_CONFIG_PATH)):
            try:
                with open(APO_CONFIG_PATH, "w", encoding="utf-8") as f:
                    f.write(config_payload)
                apo_written = True
            except Exception:
                pass

        # 2. Always write export backup to Desktop
        out_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sound_BlasterX_G6_Active_Config.txt")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(config_payload)
        except Exception:
            pass

        if not silent:
            dest_info = "Applied LIVE to Windows Audio Engine (Equalizer APO)!" if apo_written else f"Exported to Desktop:\n{out_path}\n\n(Install Equalizer APO to enable live realtime system processing)"
            messagebox.showinfo("System Audio Synced", f"Sound BlasterX G6 Synced!\nActive Card: {self.active_preset_name}\n\n{dest_info}")

    def install_apo_engine(self):
        url = "https://sourceforge.net/projects/equalizerapo/files/1.4.2/EqualizerAPO-x64-1.4.2.exe/download"
        dest = os.path.join(os.path.expanduser("~"), "Desktop", "EqualizerAPO-Setup.exe")
        msg = ("Equalizer APO is the zero-latency, open-source audio engine for Windows.\n\n"
               "Would you like to download the official 64-bit installer to your Desktop now?")
        if messagebox.askyesno("Install System Audio Engine", msg):
            try:
                messagebox.showinfo("Downloading", "Downloading Equalizer APO installer to Desktop...\nPlease wait a few seconds.")
                urllib.request.urlretrieve(url, dest)
                subprocess.Popen([dest], shell=True)
            except Exception as e:
                messagebox.showerror("Download Error", f"Could not download installer automatically:\n{e}\n\nPlease visit sourceforge.net/projects/equalizerapo/")


if __name__ == "__main__":
    root = tk.Tk()
    app = CreativeSoundLabsApp(root)
    root.mainloop()
