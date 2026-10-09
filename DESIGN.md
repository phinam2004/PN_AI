---
name: maya-ai-design-system
description: |
  Official Google Labs Stitch compliant design contract for Maya AI Next-Gen Voice Assistant.
  Defines atmospheric tokens, dark glassmorphism palette, kinetic soundwave interactions,
  and anti-slop guidelines.
category: design-systems
surface: desktop-web-hud
platform: cross-platform
---

# Design System: Maya AI Core HUD & Next-Gen Interface

> Single Source of Truth (Hợp đồng thiết kế duy nhất) tuân thủ tiêu chuẩn Google Labs & Stitch.

---

## 1. Visual Theme & Atmosphere

Maya AI interface is an **Airy Cyber-Minimalist Cockpit (Density: 5, Variance: 6, Motion: 7)**.
- **Mood:** High-agency, surgical, restrained intelligence. Like a mission-control HUD stripped of cinematic clutter.
- **Philosophy:** No cheesy 80s neon purple/pink grids, no cartoon robot avatars, no fake spinning sci-fi rings with zero data.
- **Materiality:** Deep OLED charcoal slate (`#0B0D11`) with subtle optical blur backdrop (`backdrop-filter: blur(20px)`), razor-thin semi-transparent borders (`rgba(255, 255, 255, 0.08)`), and a living, organic reactive audio core that pulses with speech amplitude.

---

## 2. Calibrated Color Palette & Roles

Strict rule: Maximum 1 primary energetic accent. Neutrals strictly calibrated to cold slate.

| Token Name | Hex / RGBA Code | Functional Role |
| :--- | :--- | :--- |
| **Deep Void Canvas** | `#090A0F` | Main application background (OLED off-black) |
| **Surface Slate 900** | `#12151D` | Panel, card, and modular container background |
| **Surface Elevated** | `rgba(26, 31, 44, 0.65)` | Glassmorphism cards, modal overlay |
| **Glass Border** | `rgba(255, 255, 255, 0.08)` | 1px precision dividers and containment borders |
| **Glass Border Active** | `rgba(0, 229, 255, 0.35)` | Active state indicator for listening/active card |
| **Cyber Cyan (Accent)** | `#00E5FF` | Sole energetic accent: audio wave, primary CTA, active badge |
| **Signal Amber (Alert)** | `#F59E0B` | Thinking state, processing query |
| **Signal Emerald (Success)** | `#10B981` | Command executed, connected, microphone ready |
| **Signal Crimson (Error)** | `#EF4444` | Fallback warning, microphone disconnected |
| **Text Primary** | `#F8FAFC` | Main speech transcripts, headers (Zinc-50) |
| **Text Muted** | `#94A3B8` | Subtitles, telemetry labels, timestamps (Zinc-400) |
| **Text Dim** | `#475569` | Inactive status, placeholder hints (Zinc-600) |

---

## 3. Typographic Architecture

Typography is engineered for maximum legibility in low-light environments, using weight-driven hierarchy rather than gigantic scale.

- **Display & Headings:** `Outfit`, `Cabinet Grotesk`, or `Geist` — track-tight (`letter-spacing: -0.03em`), bold or semibold.
- **Body & Speech Stream:** `Geist`, `Satoshi`, or modern system UI (`-apple-system`, `Segoe UI`, `Roboto`) — relaxed leading (`1.6`), max line width `65ch`.
- **Telemetry & Audio Metrics:** `Geist Mono` or `JetBrains Mono` — for CPU/RAM percentages, latency indicators (e.g. `24ms`), timestamps, and command debug tokens.
- **Forbidden Typography:**
  - ❌ `Inter` (banned for high-end creative identity).
  - ❌ Generic serifs (`Times New Roman`, `Georgia`).
  - ❌ Comic/Gimmicky futuristic fonts (`Orbitron`, `Papyrus`).

---

## 4. Component Stylings & Interaction States

### 4.1 The Core Kinetic Orb / Waveform
- An SVG or Canvas-driven organic soundwave that transitions through 4 distinct states:
  1. **IDLE:** Restrained breathing cycle (subtle slow pulse, opacity `0.4`, accent Cyan `#00E5FF`).
  2. **LISTENING:** Expansive amplitude modulation reflecting incoming mic decibels in real-time.
  3. **THINKING:** Twin orbital light trails revolving at `1.2s` frequency (Amber `#F59E0B`).
  4. **SPEAKING:** Multi-frequency harmonic wave bouncing with TTS audio output.

### 4.2 Status Badge
- Pill-shaped container (`border-radius: 9999px`), padding `4px 12px`, background `rgba(255, 255, 255, 0.05)`, border `1px solid rgba(255, 255, 255, 0.1)`.
- Features an 8px pulsing status dot indicating system readiness.

### 4.3 Interactive Command Cards
- Flat slate cards (`#12151D`), `border-radius: 16px`, `padding: 20px`.
- Hover state: `-2px` subtle Y-translate, border accent opacity rises from `0.08` to `0.25`. No blurry drop shadows.
- Active feedback: `-1px` scale push down.

### 4.4 Live Transcript Feed
- Waterfall chat stream with distinct message bubbles:
  - User: Right-aligned, semi-translucent dark slate with cyan left-border accent.
  - Maya: Left-aligned, crisp off-white text with markdown formatting support for code snippets, lists, and tables.

---

## 5. Layout & Responsive Principles

- **Desktop (Primary):** Asymmetric 2-column or 3-column cockpit:
  - Left Sidebar / Telemetry: System health (CPU, RAM, Mic level, active LLM model indicator).
  - Center Stage: Kinetic Audio Visualizer + Main Speech Transcript Stream.
  - Right Drawer / Quick Commands: Frequent action triggers, automation quick-toggles, settings.
- **Compact HUD / Floating Mini-Window:** 400x550px floating overlay mode that docks to screen corner with always-on-top toggle.
- **Mobile / Web Collapse (< 768px):** Strict single column cascade with bottom-docked audio orb.

---

## 6. Motion Philosophy & Micro-Interactions

- **Spring Dynamics:** `stiffness: 120, damping: 18` for natural physical weight.
- **Hardware Acceleration:** All animations strictly confined to `transform` (GPU composite) and `opacity`.
- **Fluid Stagger:** Messages in the transcript stream cascade with `60ms` stagger delay.
- **Zero Layout Thrashing:** No animated heights or margins that trigger browser reflows.

---

## 7. Anti-Patterns (Banned AI Clichés)

- 🚫 **NO Neon Purple / Magenta Gradients:** Avoid generic "cyberpunk AI" tropes.
- 🚫 **NO Fake Tech Gimmicks:** No meaningless random binary code streams, no fake percentage bars that don't reflect actual metrics.
- 🚫 **NO Overlapping Text/Visuals:** Every element holds its own dedicated spatial boundary.
- 🚫 **NO Emojis in Core System Data:** Use clean SVG icons or monospace text for badges.
- 🚫 **NO Pure Black `#000000`:** Use calibrated `#090A0F` to prevent harsh OLED clipping.
