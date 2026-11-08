# Sound BlasterX G6 Studio Console
### Open Hardware Controller & Safety Mixer for Creative Labs SB1770

> **Dedicated to Creative Labs hardware. Uncredited. 100% Free for everyone.**

An ultra-lightweight, zero-bloat, open-source live mixer, safety limiter, and direct hardware controller engineered specifically for the **Creative Sound BlasterX G6 (SB1770)**.

---

## Legal Notice & Trademark Disclaimer

* This is an independent, uncredited open-source community tool developed exclusively for use with Creative Labs Sound BlasterX G6 hardware.
* This project is **not** affiliated with, endorsed by, or sponsored by Creative Technology Ltd.
* "Sound Blaster", "Sound BlasterX", and "Creative" are registered trademarks of Creative Technology Ltd.
* All trademarks, product names, and company names referenced herein are used solely for identification, compatibility, and nominative fair use purposes.
* No individual or third-party entity claims credit or ownership over this software. It is released under the **MIT-0 (No Attribution Required)** license.

---

## Why This Exists

Underneath Creative's 600MB consumer gaming software suite, the Sound BlasterX G6 is secretly a piece of brilliant pro-audio engineering:
* **DAC:** Cirrus Logic **CS43131** MasterHIFI (32-bit / 384kHz, 130 dB DNR, -115 dB THD+N).
* **Analog Reconstruction Filter:** Audiophile German **WIMA** film and foil capacitors.
* **Headphone Bi-Amp:** Discrete dual-mono **Xamp** push-pull bipolar transistor stage with **1.0 Ω output impedance** (powers 16 Ω IEMs up to 600 Ω planar cans without distortion).
* **ADC:** Cirrus Logic **CS5361** (24-bit / 192kHz multi-bit delta-sigma, 114 dB DNR).
* **Routing:** Real mechanical **Takamisawa telecom-grade relay** physically switching line and headphone paths.

**The Problem:**
Creative's official software (*Sound Blaster Command*) installs background telemetry (`Creative.Platform.Analytics.dll`), auto-updaters, and broken Audio Processing Objects (`cfSB1770.ini`) that memory-leak into the Windows kernel audio engine (`audiodg.exe`), causing the infamous **crunchy, robotic bit-crusher distortion bug**.

**The Solution:**
**G6 Studio Console.** 
Zero background services. Zero telemetry. Zero bloat. Just a clean, responsive studio mixer communicating directly with the G6's hardware.

---

## Features

### 1. Live 3-Channel Pro Mixer
Built specifically around the G6's physical and virtual signal paths:
* **CH 1: MIC IN** (Front discrete 3.5mm mic pre).
* **CH 2: LINE / OPTICAL IN** (Rear 3.5mm combo analog line & mini-Toslink optical receiver).
* **CH 3: WHAT U HEAR** (Internal zero-loss digital stereo loopback bus).

### 2. Live Gain Staging & Ear-Protection Clip Guard
* **Input Trim:** -24 dB to +24 dB gain staging.
* **Live 3-Band Parametric EQ:** Low shelf (100Hz), mid bell (1kHz), high shelf (10kHz).
* **Safety Compressor / Brickwall Limiter:** Protects your hearing and studio monitors from sudden volume spikes and harsh digital overs with an integrated true-peak limiter.

### 3. Schematic-Accurate Legacy Sound Blaster Emulations
Modeled directly after the component-level circuit schematics, reconstruction filters, and DSP architectures of Creative's most iconic soundcards:
* **Sound Blaster Live! Pro (1998 - EMU10K1):** CT4620/CT4760 path with 48kHz sinc interpolation ripple, STAC9721T AC'97 low-end punch (+3.2dB @ 85Hz), and classic EAX 3.6kHz presence bite.
* **Sound Blaster 16 / AWE64 Gold (1994 - CT1740):** Discrete ISA analog stage with 3rd-order Butterworth LPF cutoff at 15kHz, warm 100Hz tone shelf (+3.8dB), and 220Hz low-mid saturation.
* **Sound Blaster Audigy 2 ZS (2003 - CA0102 / CS4382):** 24-bit/192kHz clean path with tight 60Hz sub-bass, transparent mids, and competitive 11.5kHz crystal treble.
* **Sound Blaster X-Fi Fatal1ty (2005 - 24-bit Crystalizer):** EMU20K1 DSP multi-band transient expander curve with explosive 65Hz punch and 12kHz high-frequency excitation.
* **Sound Blaster Pro 2.0 (1991 - CT1600 Dual OPL3):** Classic DOS Sallen-Key analog filter stage with 60Hz rumble cut, warm 200Hz FM body, and steep 11.5kHz low-pass filter.

### 4. Hardware RGB "X" Logo Controller
Direct USB HID packet engine (Interface 4, `VID 0x041e / PID 0x3256`). Change the RGB color, set presets (Classic Amber, Cyan, Green, Red), or engage **Stealth OFF** for a dark studio environment.

### 5. 1-Click System Sync via Equalizer APO
Click one button to instantly export and link your mixer channel strips and legacy soundcard curves into Windows via Equalizer APO with **sub-millisecond latency and zero CPU load**.

---

## Installation

### Option A: 1-Click Installer (Recommended)
Double-click `Install-Creative-Sound-Labs.bat`. 
It will automatically set up the application, configure shortcuts, and have you up and running in 5 seconds.

### Option B: Portable / Manual Run
Requires Python 3.10+:
```bash
pip install -r requirements.txt
python creative_sound_labs_g6.py
```

---

## License
Released under the **MIT-0 (MIT No Attribution)** License. 
Free for all users and developers. No credit, attribution, or fees required.
