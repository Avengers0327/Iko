import tkinter as tk
from tkinter import scrolledtext
import threading
import math
import queue
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from main import Iko


# ── palette ──────────────────────────────────────────────────────────────────
BG         = "#05050f"
PANEL      = "#0a0a1a"
VIOLET     = "#a855f7"
VIOLET_DIM = "#4c1d95"
CYAN       = "#06b6d4"
CYAN_DIM   = "#164e63"
WHITE      = "#f1f5f9"
MUTED      = "#475569"
FONT_MONO  = ("Space Mono", 14)
FONT_SMALL = ("Space Mono", 12)
FONT_TITLE = ("Space Mono", 16, "bold")


class IkoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Iko 🤖")
        self.root.configure(bg=BG)
        self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.iko = Iko()
        self.state = "idle"
        self.msg_queue = queue.Queue()

        self._build_ui()
        self._start_animation()
        self._poll_queue()

        threading.Thread(target=self._voice_loop, daemon=True).start()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        tk.Label(self.root, text="I  K  O", font=("Space Mono", 36, "bold"),
                 fg=VIOLET, bg=BG).pack(pady=(40, 4))
        tk.Label(self.root, text="android · escaped from a YA novel · your best friend",
                 font=("Space Mono", 14), fg=MUTED, bg=BG).pack(pady=(0, 24))

        self.canvas = tk.Canvas(self.root, width=480, height=480,
                                bg=BG, highlightthickness=0)
        self.canvas.pack(pady=8)
        self._init_chip()

        self.state_var = tk.StringVar(value="● idle")
        self.state_label = tk.Label(self.root, textvariable=self.state_var,
                                     font=("Space Mono", 14), fg=MUTED, bg=BG)
        self.state_label.pack(pady=(8, 24))

        chat_frame = tk.Frame(self.root, bg=PANEL, bd=0)
        chat_frame.pack(fill="both", expand=True, padx=80, pady=(0, 16))

        self.chat = scrolledtext.ScrolledText(
            chat_frame, bg=PANEL, fg=WHITE, font=FONT_SMALL,
            relief="flat", bd=0, wrap="word", state="disabled",
            insertbackground=VIOLET
        )
        self.chat.pack(fill="both", expand=True, padx=16, pady=16)
        self.chat.tag_config("you", foreground=CYAN)
        self.chat.tag_config("iko", foreground=VIOLET)
        self.chat.tag_config("sys", foreground=MUTED)

        input_frame = tk.Frame(self.root, bg=PANEL)
        input_frame.pack(fill="x", padx=80, pady=(0, 40))

        self.entry = tk.Entry(input_frame, bg="#0f0f1f", fg=WHITE,
                              font=FONT_MONO, relief="flat", bd=8,
                              insertbackground=VIOLET)
        self.entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 12))
        self.entry.bind("<Return>", self._on_text_send)

        send_btn = tk.Button(input_frame, text="→", font=FONT_TITLE,
                             bg=VIOLET_DIM, fg=VIOLET, relief="flat",
                             activebackground=VIOLET, activeforeground=BG,
                             cursor="hand2", command=self._on_text_send)
        send_btn.pack(side="right", ipadx=20, ipady=8)

    # ── chip animation ────────────────────────────────────────────────────────

    def _init_chip(self):
        cx, cy, r = 240, 240, 180
        self.cx, self.cy = cx, cy
        self.rings = []
        self.ring_angles = []
        self.ring_radii = [r, r-32, r-64]

        for i, col in enumerate([VIOLET_DIM, CYAN_DIM, VIOLET_DIM]):
            ring = self.canvas.create_oval(cx-self.ring_radii[i], cy-self.ring_radii[i],
                                           cx+self.ring_radii[i], cy+self.ring_radii[i],
                                           outline=col, width=2)
            self.rings.append(ring)
            self.ring_angles.append(i * 40)

        self.dots = []
        for i in range(6):
            dot = self.canvas.create_oval(0, 0, 10, 10, fill=CYAN, outline="")
            self.dots.append((dot, i * 60, 158))

        self.core = self.canvas.create_oval(cx-50, cy-50, cx+50, cy+50,
                                            fill=VIOLET_DIM, outline=VIOLET, width=3)
        self.pulse = self.canvas.create_oval(cx-25, cy-25, cx+25, cy+25,
                                             fill=VIOLET, outline="")

        for i in range(12):
            angle = math.radians(i * 30)
            x1 = cx + (r+10) * math.cos(angle)
            y1 = cy + (r+10) * math.sin(angle)
            x2 = cx + (r+24) * math.cos(angle)
            y2 = cy + (r+24) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill=MUTED, width=2)

        self.anim_t = 0

    def _start_animation(self):
        self._animate()

    def _animate(self):
        t = self.anim_t
        cx, cy = self.cx, self.cy
        state = self.state

        speed   = {"idle": 0.3, "listening": 1.2, "thinking": 0.6, "speaking": 1.8}.get(state, 0.3)
        glow    = {"idle": VIOLET_DIM, "listening": CYAN, "thinking": VIOLET_DIM, "speaking": VIOLET}.get(state, VIOLET_DIM)
        core_c  = {"idle": VIOLET_DIM, "listening": CYAN_DIM, "thinking": VIOLET_DIM, "speaking": VIOLET_DIM}.get(state, VIOLET_DIM)
        pulse_c = {"idle": VIOLET, "listening": CYAN, "thinking": VIOLET, "speaking": "#e879f9"}.get(state, VIOLET)

        pulse_r = 25 + 12 * math.sin(t * speed * 3)
        self.canvas.coords(self.pulse,
                           cx - pulse_r, cy - pulse_r,
                           cx + pulse_r, cy + pulse_r)
        self.canvas.itemconfig(self.pulse, fill=pulse_c)
        self.canvas.itemconfig(self.core, fill=core_c, outline=glow)

        for i, ring in enumerate(self.rings):
            self.ring_angles[i] += speed * (0.4 + i * 0.2)
            r = self.ring_radii[i]
            wobble = 6 * math.sin(t * speed + i)
            self.canvas.coords(ring,
                               cx - r + wobble, cy - r,
                               cx + r + wobble, cy + r)

        new_dots = []
        for dot, angle, orbit_r in self.dots:
            new_angle = angle + speed * 1.5
            x = cx + orbit_r * math.cos(math.radians(new_angle))
            y = cy + orbit_r * math.sin(math.radians(new_angle))
            self.canvas.coords(dot, x-5, y-5, x+5, y+5)
            self.canvas.itemconfig(dot, fill=pulse_c)
            new_dots.append((dot, new_angle, orbit_r))
        self.dots = new_dots

        self.anim_t += 0.05
        self.root.after(33, self._animate)

    # ── state & chat helpers ──────────────────────────────────────────────────

    def set_state(self, state):
        self.state = state
        labels = {
            "idle":      ("● idle",      MUTED),
            "listening": ("◉ listening", CYAN),
            "thinking":  ("◌ thinking",  VIOLET),
            "speaking":  ("▶ speaking",  "#e879f9"),
        }
        text, color = labels.get(state, ("● idle", MUTED))
        self.state_var.set(text)
        self.state_label.config(fg=color)

    def log(self, who, text):
        self.chat.config(state="normal")
        tag = "you" if who == "You" else ("sys" if who == "—" else "iko")
        prefix = f"{who}: " if who != "—" else ""
        self.chat.insert("end", prefix, tag)
        self.chat.insert("end", text + "\n")
        self.chat.see("end")
        self.chat.config(state="disabled")

    def _poll_queue(self):
        while not self.msg_queue.empty():
            fn = self.msg_queue.get_nowait()
            fn()
        self.root.after(50, self._poll_queue)

    def _ui(self, fn):
        self.msg_queue.put(fn)

    # ── voice loop ────────────────────────────────────────────────────────────

    def _voice_loop(self):
        self._ui(lambda: self.log("—", "voice loop started — say something!"))
        while True:
            self._ui(lambda: self.set_state("listening"))
            prompt = self.iko.listen()
            if not prompt.strip():
                continue

            self._ui(lambda p=prompt: self.log("You", p))

            if prompt.lower().strip() in ["exit", "quit"]:
                self._ui(lambda: self.log("—", "goodbye!"))
                break

            self._ui(lambda: self.set_state("thinking"))
            response = self.iko.generate([
                {"role": "system", "content": self.iko.SYSTEM_PROMPT},
                *self.iko.history,
                {"role": "user", "content": prompt}
            ])

            self.iko.history.append({"role": "user", "content": prompt})
            self._save_message("user", prompt)
            self.iko.history.append({"role": "assistant", "content": response})
            self._save_message("assistant", response)

            self._ui(lambda r=response: self.log("Iko", r))
            self._ui(lambda: self.set_state("speaking"))
            self.iko.speak(response)

    def _save_message(self, role, content):
        conn = sqlite3.connect("history.db")
        conn.execute("INSERT INTO history (role, content) VALUES (?, ?)", (role, content))
        conn.commit()
        conn.close()

    # ── text fallback ─────────────────────────────────────────────────────────

    def _on_text_send(self, event=None):
        prompt = self.entry.get().strip()
        if not prompt:
            return
        self.entry.delete(0, "end")
        threading.Thread(target=self._text_respond, args=(prompt,), daemon=True).start()

    def _text_respond(self, prompt):
        self._ui(lambda p=prompt: self.log("You", p))
        self._ui(lambda: self.set_state("thinking"))
        response = self.iko.generate([
            {"role": "system", "content": self.iko.SYSTEM_PROMPT},
            *self.iko.history,
            {"role": "user", "content": prompt}
        ])
        self.iko.history.append({"role": "user", "content": prompt})
        self._save_message("user", prompt)
        self.iko.history.append({"role": "assistant", "content": response})
        self._save_message("assistant", response)
        self._ui(lambda r=response: self.log("Iko", r))
        self._ui(lambda: self.set_state("speaking"))
        self.iko.speak(response)
        self._ui(lambda: self.set_state("listening"))


if __name__ == "__main__":
    root = tk.Tk()
    app = IkoGUI(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
