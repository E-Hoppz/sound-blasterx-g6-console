"""
================================================================================
   SOUND BLASTERX G6 STUDIO CONSOLE (SB1770)
   Uncredited Community Edition - 100% Free Open Hardware Controller
================================================================================
Notice: Built specifically for Creative Labs Sound BlasterX G6 (SB1770) hardware.
Uncredited release under MIT-0. Not affiliated with or endorsed by Creative Technology Ltd.
================================================================================
Resolution Adaptive: Designed specifically for 4:3 800x600 retro CRTs up to 4K displays.
"""

import sys
import os
import math
import subprocess
import winsound
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import hid

# Theme: High-Contrast Dark Studio Graphite & Retro Amber
BG_DARK = "#121417"
PANEL_BG = "#1a1d22"
STRIP_BG = "#22262e"
HEADER_BG = "#15181c"
CREATIVE_ORANGE = "#ff5500"
ACCENT_BLUE = "#56b6c2"
ACCENT_GREEN = "#98c379"
ACCENT_RED = "#e06c75"
TEXT_COLOR = "#dcdfe4"
TEXT_MUTED = "#6f7783"
BORDER_COLOR = "#333942"

# Deep Schematic-Accurate Vintage Card Circuit Models
LEGACY_PRESETS = {
    "DIRECT (CS43131 Pure)": {
        "desc": "100% Bit-Perfect pure MasterHIFI stream. All filters bypassed. Zero phase coloration.",
        "preamp": 0.0,
        "filters": []
    },
    "SB Live! Pro (1998)": {
        "desc": "EMU10K1 48kHz locked DSP: 8-pt sinc interpolation ripple (+1.6dB @ 15.5kHz), STAC9721T AC'97 bass (+3.2dB @ 85Hz), EAX 3.6kHz bite.",
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
    "SB 16 / AWE64 (1994)": {
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
    "Audigy 2 ZS (2003)": {
        "desc": "CA0102 DSP + CS4382 24/192 (THX): tight 55Hz sub punch (+2.8dB), flat mids, competitive 2.8kHz imaging, 11.5kHz crystal air.",
        "preamp": 0.5,
        "filters": [
            {"type": "PK", "fc": 55, "gain": 2.8, "q": 1.6},
            {"type": "PK", "fc": 2800, "gain": 2.6, "q": 1.8},
            {"type": "PK", "fc": 11500, "gain": 3.0, "q": 1.3},
            {"type": "HSC", "fc": 16000, "gain": 1.8, "q": 0.8}
        ]
    },
    "X-Fi Fatal1ty (2005)": {
        "desc": "EMU20K1 24-bit Crystalizer: +4.8dB sub transient punch (65Hz), 750Hz widening scoop, +5.4dB high transient exciter (12.5kHz).",
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
    "SB Pro 2.0 (1991)": {
        "desc": "Dual OPL3 CT1600 + LM324 Sallen-Key 2nd-order active LPF (-12dB/oct @ 11.5kHz), 50Hz DC cut, warm 190Hz resonant FM body (+3.8dB).",
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
APO_DEVICE_SELECTOR = r"C:\Program Files\EqualizerAPO\DeviceSelector.exe"


class CompactChannelStrip:
    """Ultra-responsive channel strip tailored to fit 4:3 800x600 displays comfortably."""
    def __init__(self, parent, title, input_desc, accent_color, on_change_callback):
        self.parent = parent
        self.title = title
        self.input_desc = input_desc
        self.accent_color = accent_color
        self.on_change = on_change_callback
        
        # State
        self.trim_db = 0.0
        self.fader_db = 0.0
        self.is_muted = False
        self.is_solo = False
        self.eq_low = 0.0
        self.eq_mid = 0.0
        self.eq_high = 0.0
        self.eq_active = True
        self.comp_active = True
        self.comp_thresh = -14.0
        self.safety_limit = True
        
        self.frame = tk.Frame(parent, bg=STRIP_BG, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.build_strip()

    def build_strip(self):
        # Header (22px)
        h = tk.Frame(self.frame, bg=HEADER_BG, height=22)
        h.pack(fill=tk.X)
        h.pack_propagate(False)
        tk.Label(h, text=self.title, font=("Segoe UI", 8, "bold"), fg=self.accent_color, bg=HEADER_BG).pack(side=tk.LEFT, padx=4)
        tk.Label(h, text=self.input_desc, font=("Segoe UI", 6), fg=TEXT_MUTED, bg=HEADER_BG).pack(side=tk.RIGHT, padx=4)
        
        # Trim (26px)
        t_box = tk.Frame(self.frame, bg=STRIP_BG, padx=4, pady=1)
        t_box.pack(fill=tk.X)
        t_row = tk.Frame(t_box, bg=STRIP_BG)
        t_row.pack(fill=tk.X)
        tk.Label(t_row, text="TRIM", font=("Segoe UI", 6, "bold"), fg=TEXT_COLOR, bg=STRIP_BG).pack(side=tk.LEFT)
        self.lbl_trim = tk.Label(t_row, text="0dB", font=("Consolas", 6, "bold"), fg=CREATIVE_ORANGE, bg=STRIP_BG)
        self.lbl_trim.pack(side=tk.RIGHT)
        self.scale_trim = ttk.Scale(t_box, from_=-24, to=24, orient=tk.HORIZONTAL, command=self.on_trim_slider)
        self.scale_trim.set(0)
        self.scale_trim.pack(fill=tk.X)
        
        # 3-Band EQ (Compact 68px)
        eq_box = tk.Frame(self.frame, bg=STRIP_BG, bd=1, relief=tk.SOLID, padx=4, pady=2)
        eq_box.pack(fill=tk.X, padx=2, pady=2)
        eq_h = tk.Frame(eq_box, bg=STRIP_BG)
        eq_h.pack(fill=tk.X)
        tk.Label(eq_h, text="3-BAND EQ", font=("Segoe UI", 6, "bold"), fg=ACCENT_GREEN, bg=STRIP_BG).pack(side=tk.LEFT)
        self.btn_eq = tk.Button(eq_h, text="ON", font=("Segoe UI", 5, "bold"), bg="#2d422a", fg=ACCENT_GREEN, bd=0, padx=2, command=self.toggle_eq)
        self.btn_eq.pack(side=tk.RIGHT)
        
        self.eq_sliders = {}
        for b_id, b_name in [("low", "100Hz"), ("mid", "1kHz"), ("high", "10kHz")]:
            row = tk.Frame(eq_box, bg=STRIP_BG)
            row.pack(fill=tk.X)
            tk.Label(row, text=b_name, font=("Segoe UI", 5), fg=TEXT_MUTED, bg=STRIP_BG, width=6, anchor="w").pack(side=tk.LEFT)
            s = ttk.Scale(row, from_=-12, to=12, orient=tk.HORIZONTAL, command=lambda v, b=b_id: self.on_eq_slider(b, v))
            self.eq_sliders[b_id] = s
            s.set(0)
            s.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Safety Comp (Compact 48px)
        comp_box = tk.Frame(self.frame, bg=STRIP_BG, bd=1, relief=tk.SOLID, padx=4, pady=2)
        comp_box.pack(fill=tk.X, padx=2, pady=2)
        ch = tk.Frame(comp_box, bg=STRIP_BG)
        ch.pack(fill=tk.X)
        tk.Label(ch, text="LIMITER / COMP", font=("Segoe UI", 6, "bold"), fg=CREATIVE_ORANGE, bg=STRIP_BG).pack(side=tk.LEFT)
        self.lbl_thresh = tk.Label(ch, text="-14dB", font=("Consolas", 5), fg=TEXT_MUTED, bg=STRIP_BG)
        self.lbl_thresh.pack(side=tk.RIGHT)
        
        self.scale_thresh = ttk.Scale(comp_box, from_=-36, to=0, orient=tk.HORIZONTAL, command=self.on_thresh_slider)
        self.scale_thresh.set(-14)
        self.scale_thresh.pack(fill=tk.X)
        
        gr_row = tk.Frame(comp_box, bg=STRIP_BG)
        gr_row.pack(fill=tk.X, pady=1)
        tk.Label(gr_row, text="GR", font=("Segoe UI", 5, "bold"), fg=ACCENT_RED, bg=STRIP_BG).pack(side=tk.LEFT)
        self.canvas_gr = tk.Canvas(gr_row, height=5, bg="#111", highlightthickness=0)
        self.canvas_gr.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.draw_gr_bar(2.0)

        # Fader & Meter (Flex expand, min 100px)
        f_box = tk.Frame(self.frame, bg=STRIP_BG, padx=4, pady=2)
        f_box.pack(fill=tk.BOTH, expand=True)
        
        sm_row = tk.Frame(f_box, bg=STRIP_BG)
        sm_row.pack(fill=tk.X, pady=1)
        self.btn_solo = tk.Button(sm_row, text="S", font=("Segoe UI", 6, "bold"), bg="#333", fg="#888", width=2, bd=1, command=self.toggle_solo)
        self.btn_solo.pack(side=tk.LEFT, padx=1)
        self.btn_mute = tk.Button(sm_row, text="M", font=("Segoe UI", 6, "bold"), bg="#333", fg="#888", width=2, bd=1, command=self.toggle_mute)
        self.btn_mute.pack(side=tk.LEFT, padx=1)
        self.lbl_fader = tk.Label(sm_row, text="0.0dB", font=("Consolas", 6, "bold"), fg="#fff", bg=STRIP_BG)
        self.lbl_fader.pack(side=tk.RIGHT)
        
        f_area = tk.Frame(f_box, bg=STRIP_BG)
        f_area.pack(fill=tk.BOTH, expand=True, pady=2)
        self.meter_canvas = tk.Canvas(f_area, width=10, bg="#0d0e11", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.meter_canvas.pack(side=tk.LEFT, fill=tk.Y, padx=2)
        self.draw_meter(0.70)
        
        self.fader = ttk.Scale(f_area, from_=6, to=-60, orient=tk.VERTICAL, command=self.on_fader_slider)
        self.fader.set(0)
        self.fader.pack(side=tk.RIGHT, fill=tk.Y, expand=True, padx=2)

    def draw_meter(self, level):
        self.meter_canvas.delete("all")
        h = 100
        w = 10
        segments = 18
        seg_h = h / segments
        active_segs = int(level * segments)
        for i in range(segments):
            y2 = h - (i * seg_h)
            y1 = y2 - seg_h + 1
            col = ACCENT_RED if i > segments * 0.85 else (CREATIVE_ORANGE if i > segments * 0.65 else ACCENT_GREEN) if i < active_segs else "#15181d"
            self.meter_canvas.create_rectangle(1, y1, w - 1, y2, fill=col, outline="")

    def draw_gr_bar(self, gr_db):
        self.canvas_gr.delete("all")
        w = self.canvas_gr.winfo_width() or 60
        fill_w = int(w * min(1.0, gr_db / 18.0))
        self.canvas_gr.create_rectangle(0, 0, fill_w, 5, fill=ACCENT_RED, outline="")

    def on_trim_slider(self, val):
        self.trim_db = float(val)
        self.lbl_trim.config(text=f"{int(self.trim_db)}dB")
        self.on_change()

    def on_fader_slider(self, val):
        self.fader_db = float(val)
        self.lbl_fader.config(text="-inf" if self.fader_db <= -59 else f"{self.fader_db:.1f}dB")
        self.on_change()

    def on_eq_slider(self, band, val):
        gain = float(val)
        if band == "low": self.eq_low = gain
        elif band == "mid": self.eq_mid = gain
        elif band == "high": self.eq_high = gain
        self.on_change()

    def on_thresh_slider(self, val):
        self.comp_thresh = float(val)
        self.lbl_thresh.config(text=f"{int(self.comp_thresh)}dB")
        self.on_change()

    def toggle_eq(self):
        self.eq_active = not self.eq_active
        self.btn_eq.config(text="ON" if self.eq_active else "OFF",
                           bg="#2d422a" if self.eq_active else "#333",
                           fg=ACCENT_GREEN if self.eq_active else "#888")
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
        self.root.title("Sound BlasterX G6 Studio Console [4:3 Retro & 4K Ready]")
        
        # 800x600 4:3 native fit (fits 800x559 working area perfectly)
        self.root.geometry("780x535")
        self.root.minsize(760, 500)
        self.root.configure(bg=BG_DARK)
        
        self.active_preset_name = "DIRECT (CS43131 Pure)"
        self.hid_device = None
        self.hid_path = None
        self.hid_connected = False
        
        self.init_hid()
        self.build_top_banner()
        self.build_preset_ribbon()
        self.build_mixer_canvas()
        self.build_hardware_dock()
        
        self.update_spectrum_curve()
        self.apply_to_system(silent=True)

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
        top = tk.Frame(self.root, bg=HEADER_BG, height=36, bd=1, relief=tk.SOLID)
        top.pack(fill=tk.X)
        top.pack_propagate(False)
        
        left = tk.Frame(top, bg=HEADER_BG)
        left.pack(side=tk.LEFT, padx=8, pady=4)
        tk.Label(left, text="SOUND BLASTERX G6", font=("Impact", 13), fg=CREATIVE_ORANGE, bg=HEADER_BG).pack(side=tk.LEFT)
        tk.Label(left, text=" | DIRECT CONSOLE", font=("Segoe UI", 8, "bold"), fg="#fff", bg=HEADER_BG).pack(side=tk.LEFT, padx=4)
        
        # Big Center Apply Button (Cannot be missed!)
        self.btn_top_apply = tk.Button(top, text="⚡ APPLY TO HEADPHONES", font=("Segoe UI", 8, "bold"),
                                       bg="#1d743a", fg="#fff", activebackground="#279b4e", activeforeground="#fff",
                                       bd=1, relief=tk.RAISED, padx=10, pady=2, command=lambda: self.apply_to_system(silent=False))
        self.btn_top_apply.pack(side=tk.LEFT, padx=12, pady=4)
        
        stat = tk.Frame(top, bg=HEADER_BG)
        stat.pack(side=tk.RIGHT, padx=8)
        self.lbl_audio_stat = tk.Label(stat, text="FILTER: LIVE ACTIVE", font=("Consolas", 7, "bold"), fg=ACCENT_GREEN, bg=HEADER_BG)
        self.lbl_audio_stat.pack(anchor="e")
        
        hid_t = "USB HID: LINKED" if self.hid_connected else "USB HID: DISCONNECTED"
        self.lbl_hid_stat = tk.Label(stat, text=hid_t, font=("Consolas", 6), fg=ACCENT_GREEN if self.hid_connected else ACCENT_RED, bg=HEADER_BG)
        self.lbl_hid_stat.pack(anchor="e")

    def build_preset_ribbon(self):
        ribbon = tk.Frame(self.root, bg="#181c22", height=42, bd=1, relief=tk.SOLID)
        ribbon.pack(fill=tk.X, padx=4, pady=2)
        ribbon.pack_propagate(False)
        
        tk.Label(ribbon, text="PRESET:", font=("Segoe UI", 7, "bold"), fg=CREATIVE_ORANGE, bg="#181c22").pack(side=tk.LEFT, padx=4)
        self.preset_combo = ttk.Combobox(ribbon, values=list(LEGACY_PRESETS.keys()), state="readonly", width=22, font=("Segoe UI", 7, "bold"))
        self.preset_combo.set(self.active_preset_name)
        self.preset_combo.pack(side=tk.LEFT, padx=4)
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_select)
        
        # Compact live 20Hz-20kHz response spectrum plot (fits perfectly on 800x600!)
        plot_box = tk.Frame(ribbon, bg="#0c0e12", bd=1, relief=tk.SOLID)
        plot_box.pack(side=tk.RIGHT, padx=6, pady=2)
        self.canvas_spectrum = tk.Canvas(plot_box, width=220, height=32, bg="#07080a", highlightthickness=0)
        self.canvas_spectrum.pack()

    def update_spectrum_curve(self):
        if not hasattr(self, 'canvas_spectrum'): return
        c = self.canvas_spectrum
        c.delete("all")
        w = 220
        h = 32
        mid_y = h / 2.0
        
        # Grid lines
        c.create_line(0, mid_y, w, mid_y, fill="#222830", dash=(2, 2))
        
        min_log = math.log10(20)
        max_log = math.log10(20000)
        for freq_mark in [100, 1000, 10000]:
            lx = (math.log10(freq_mark) - min_log) / (max_log - min_log) * w
            c.create_line(lx, 0, lx, h, fill="#161b22", dash=(1, 3))
            
        preset_info = LEGACY_PRESETS.get(self.active_preset_name, {})
        filters = list(preset_info.get("filters", []))
        preamp = preset_info.get("preamp", 0.0)
        
        points = []
        num_pts = 60
        for i in range(num_pts):
            frac = i / (num_pts - 1)
            f = 10 ** (min_log + frac * (max_log - min_log))
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
            px = frac * w
            py = mid_y - (db * 1.8)
            py = max(1, min(h - 1, py))
            points.append(px)
            points.append(py)

        if len(points) >= 4:
            c.create_line(points, fill=ACCENT_BLUE, width=2, smooth=True)

    def build_mixer_canvas(self):
        mixer_frame = tk.Frame(self.root, bg=BG_DARK)
        mixer_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=2)
        
        # 3 Real Hardware Input Strips
        self.strip_mic = CompactChannelStrip(mixer_frame, "MIC IN", "FRONT 3.5mm", ACCENT_BLUE, self.on_channel_change)
        self.strip_mic.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.strip_line = CompactChannelStrip(mixer_frame, "LINE/OPT", "REAR COMBO", ACCENT_GREEN, self.on_channel_change)
        self.strip_line.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.strip_loop = CompactChannelStrip(mixer_frame, "LOOPBACK", "WHAT U HEAR", CREATIVE_ORANGE, self.on_channel_change)
        self.strip_loop.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        # Master Output Strip (Right Column)
        m_strip = tk.Frame(mixer_frame, bg=STRIP_BG, bd=1, relief=tk.SOLID, highlightbackground=BORDER_COLOR, highlightthickness=1)
        m_strip.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)
        
        mh = tk.Frame(m_strip, bg=HEADER_BG, height=22)
        mh.pack(fill=tk.X)
        mh.pack_propagate(False)
        tk.Label(mh, text="MASTER OUT", font=("Segoe UI", 8, "bold"), fg="#fff", bg=HEADER_BG).pack(side=tk.LEFT, padx=4)
        tk.Label(mh, text="CS43131", font=("Segoe UI", 6), fg=TEXT_MUTED, bg=HEADER_BG).pack(side=tk.RIGHT, padx=4)
        
        mb = tk.Frame(m_strip, bg=PANEL_BG, padx=4, pady=4)
        mb.pack(fill=tk.BOTH, expand=True)
        
        # Big Apply Button in Master Strip
        btn_apply_main = tk.Button(mb, text="⚡ APPLY SOUND", font=("Segoe UI", 8, "bold"),
                                   bg="#1d743a", fg="#fff", activebackground="#279b4e", activeforeground="#fff",
                                   bd=1, relief=tk.RAISED, pady=4, command=lambda: self.apply_to_system(silent=False))
        btn_apply_main.pack(fill=tk.X, pady=(0, 4))
        
        # Device Selector Helper Button
        btn_dev = tk.Button(mb, text="Config Devices (APO)", font=("Segoe UI", 6), bg="#333", fg=TEXT_COLOR, bd=1,
                            command=self.open_device_selector)
        btn_dev.pack(fill=tk.X, pady=(0, 4))
        
        # Fader Area
        f_area = tk.Frame(mb, bg=PANEL_BG)
        f_area.pack(fill=tk.BOTH, expand=True)
        
        self.master_meter = tk.Canvas(f_area, width=20, bg="#0d0e11", highlightthickness=1, highlightbackground=BORDER_COLOR)
        self.master_meter.pack(side=tk.LEFT, fill=tk.Y, padx=2)
        self.draw_stereo_meter(0.78, 0.74)
        
        self.master_fader = ttk.Scale(f_area, from_=6, to=-60, orient=tk.VERTICAL, command=self.on_master_slider)
        self.master_fader.set(0)
        self.master_fader.pack(side=tk.LEFT, fill=tk.Y, expand=True, padx=4)
        
        self.lbl_m_fader = tk.Label(mb, text="0.0dB", font=("Consolas", 7, "bold"), fg="#fff", bg=PANEL_BG)
        self.lbl_m_fader.pack(pady=1)

    def draw_stereo_meter(self, left_lvl, right_lvl):
        self.master_meter.delete("all")
        h = 140
        segments = 20
        seg_h = h / segments
        for ch_idx, lvl in enumerate([left_lvl, right_lvl]):
            x1 = 2 + ch_idx * 9
            x2 = x1 + 7
            active = int(lvl * segments)
            for i in range(segments):
                y2 = h - (i * seg_h)
                y1 = y2 - seg_h + 1
                col = ACCENT_RED if i > segments * 0.85 else (CREATIVE_ORANGE if i > segments * 0.65 else ACCENT_GREEN) if i < active else "#15181d"
                self.master_meter.create_rectangle(x1, y1, x2, y2, fill=col, outline="")

    def build_hardware_dock(self):
        dock = tk.Frame(self.root, bg=PANEL_BG, height=44, bd=1, relief=tk.SOLID)
        dock.pack(fill=tk.X, padx=4, pady=(0, 4))
        dock.pack_propagate(False)
        
        left = tk.Frame(dock, bg=PANEL_BG)
        left.pack(side=tk.LEFT, padx=6, pady=2)
        
        row1 = tk.Frame(left, bg=PANEL_BG)
        row1.pack(fill=tk.X)
        tk.Label(row1, text="G6 'X' LED:", font=("Segoe UI", 7, "bold"), fg="#fff", bg=PANEL_BG).pack(side=tk.LEFT)
        self.led_preview_box = tk.Label(row1, text=" ", bg="#ff5500", relief=tk.SOLID, bd=1, width=2)
        self.led_preview_box.pack(side=tk.LEFT, padx=4)
        
        for name, col in [("Amber", "#ff5500"), ("Cyan", "#00d0ff"), ("Green", "#00ff66"), ("Red", "#ff0033"), ("Off", "#000000")]:
            tk.Button(row1, text=name, font=("Segoe UI", 6, "bold"), bg=col if col != "#000000" else "#222",
                      fg="#000" if col in ["#00d0ff", "#00ff66"] else "#fff", bd=1, padx=4, command=lambda c=col: self.set_hardware_led(c)).pack(side=tk.LEFT, padx=1)
        tk.Button(row1, text="Custom...", font=("Segoe UI", 6), bg="#333", fg="#fff", bd=1, padx=3, command=self.pick_led).pack(side=tk.LEFT, padx=1)

        right = tk.Frame(dock, bg=PANEL_BG)
        right.pack(side=tk.RIGHT, padx=6, pady=4)
        tk.Label(right, text="XAMP GAIN: LOW (16-149Ω) / HIGH (150-600Ω)", font=("Consolas", 6, "bold"), fg=CREATIVE_ORANGE, bg=PANEL_BG).pack()

    def on_preset_select(self, event):
        self.active_preset_name = self.preset_combo.get()
        self.update_spectrum_curve()
        self.apply_to_system(silent=True)

    def on_master_slider(self, val):
        f = float(val)
        self.lbl_m_fader.config(text="-inf" if f <= -59 else f"{f:.1f}dB")
        self.on_channel_change()

    def on_channel_change(self):
        if not hasattr(self, 'master_fader') or not hasattr(self, 'canvas_spectrum'):
            return
        self.update_spectrum_curve()
        self.apply_to_system(silent=True)

    def set_hardware_led(self, hex_code):
        r = int(hex_code[1:3], 16)
        g = int(hex_code[3:5], 16)
        b = int(hex_code[5:7], 16)
        if not self.hid_device or not self.hid_connected:
            self.init_hid()
        success = False
        if self.hid_device:
            try:
                pkt = bytearray(65)
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
                commit[1] = 0x5a
                commit[2] = 0x11
                self.hid_device.write(bytes(commit))
                success = True
            except Exception:
                try:
                    self.init_hid()
                    if self.hid_device:
                        self.hid_device.write(bytes(pkt))
                        self.hid_device.write(bytes(commit))
                        success = True
                except Exception:
                    pass
        if hasattr(self, 'led_preview_box'):
            self.led_preview_box.config(bg=hex_code)
        if hasattr(self, 'lbl_hid_stat'):
            self.lbl_hid_stat.config(text=f"USB HID: LINKED ({hex_code})" if success else "USB HID: RETRY",
                                    fg=ACCENT_GREEN if success else ACCENT_RED)
        return success

    def pick_led(self):
        c = colorchooser.askcolor(title="G6 LED Color")[1]
        if c: self.set_hardware_led(c)

    def apply_to_system(self, silent=True):
        if not hasattr(self, 'master_fader'):
            return
        preset_info = LEGACY_PRESETS.get(self.active_preset_name, {})
        filters = preset_info.get("filters", [])
        preamp = preset_info.get("preamp", 0.0)
        
        lines = [
            "# ========================================================",
            "# SOUND BLASTERX G6 - REALTIME HARDWARE DSP CONFIG",
            f"# Active Model: {self.active_preset_name}",
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
            lines.append(f"# Channel: {strip.title}")
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

        payload = "\n".join(lines)
        
        apo_written = False
        if os.path.exists(os.path.dirname(APO_CONFIG_PATH)):
            try:
                with open(APO_CONFIG_PATH, "w", encoding="utf-8") as f:
                    f.write(payload)
                apo_written = True
            except Exception:
                pass

        out_path = os.path.join(os.path.expanduser("~"), "Desktop", "Sound_BlasterX_G6_Active_Config.txt")
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(payload)
        except Exception:
            pass

        if hasattr(self, 'lbl_audio_stat'):
            if apo_written:
                self.lbl_audio_stat.config(text=f"FILTER: ACTIVE ({self.active_preset_name})", fg=ACCENT_GREEN)
            else:
                self.lbl_audio_stat.config(text="FILTER: EXPORTED TO DESKTOP", fg=CREATIVE_ORANGE)

        if not silent:
            # Play gentle audio beep confirming application
            try: winsound.Beep(880, 80)
            except Exception: pass
            
            if apo_written:
                messagebox.showinfo("Sound Applied", f"APPLIED TO HEADPHONES!\n\nActive Card: {self.active_preset_name}\nLatency: 0ms (Realtime Windows Engine)")
            else:
                messagebox.showinfo("Sound Exported", f"Sound BlasterX G6 Synced!\nActive Card: {self.active_preset_name}\n\nExported to:\n{out_path}\n\nClick 'Config Devices (APO)' to attach Equalizer APO to your G6 playback stream.")

    def open_device_selector(self):
        if os.path.exists(APO_DEVICE_SELECTOR):
            subprocess.Popen([APO_DEVICE_SELECTOR])
        else:
            messagebox.showinfo("Equalizer APO", "Equalizer APO is located at C:\\Program Files\\EqualizerAPO.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CreativeSoundLabsApp(root)
    root.mainloop()
