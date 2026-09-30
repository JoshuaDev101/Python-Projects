import tkinter as tk
import time
import random

LYRICS = [
    (0,   "Oh i don't care if you're insincere"),
    (7,   "just tell me what i wanna hear"),
    (13,   "you know where to find me"),
    (15,  "the place where we lived all the years, oh"),
    (23,  "and tell me you love me"),
    (26,  "that's all that i need to hear"),

]

BOX_W, BOX_H = 300, 250
FONT = ("Helvetica", 22, "bold")
BG_COLOR = "#ffffff"
FG_COLOR = "#000000"
RISE_SPEED = 65


class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        self.full_text = text

        self.label = tk.Label(
            self.win, text="", font=FONT, bg=BG_COLOR, fg=FG_COLOR,
            wraplength=BOX_W - 25, justify="center"
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        self.x = x
        self.y = float(y)

        self.typewriter_index = 0
        self.typewriter()

    def rise(self, dy):
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[:self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(100, self.typewriter)


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.last_slot = None
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None

        self.start()

    def random_position(self):
        """Spawn sa gitna; random left/middle/right pero di pwedeng same slot
        sa kaka-spawn lang, at iwas sa slot na may box pa sa spawn area."""
        spawn_y = (self.screen_h - BOX_H) // 2

        center_x = (self.screen_w - BOX_W) // 2
        gap = 60
        slots = [
            center_x - BOX_W - gap,   # left
            center_x,                 # middle
            center_x + BOX_W + gap,   # right
        ]

        def blocked(slot_x):
            return any(
                abs(b.x - slot_x) < BOX_W and abs(b.y - spawn_y) < BOX_H
                for b in self.boxes
            )

        def lowest_box_y(slot_x):
            ys = [b.y for b in self.boxes if abs(b.x - slot_x) < BOX_W]
            return max(ys) if ys else float("-inf")

        candidates = [s for s in slots if s != self.last_slot and not blocked(s)]

        if not candidates:
            others = [s for s in slots if s != self.last_slot]
            candidates = [min(others, key=lowest_box_y)]

        x = random.choice(candidates)
        self.last_slot = x
        return x, spawn_y

    def start(self):
        self.root.iconify()
        self.start_time = time.time()
        self.last_frame_time = self.start_time
        self.tick()

    def tick(self):
        now = time.time()
        elapsed = now - self.start_time
        dt = now - self.last_frame_time
        self.last_frame_time = now

        # Spawn lyrics on their original timing, at random positions
        while (self.next_lyric_idx < len(LYRICS)
               and LYRICS[self.next_lyric_idx][0] <= elapsed):
            _, text = LYRICS[self.next_lyric_idx]
            x, y = self.random_position()
            self.boxes.append(LyricCard(self.root, text, x, y))
            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt
        for box in self.boxes:
            box.rise(dy)

        still_visible = []
        for box in self.boxes:
            if box.is_offscreen():
                try:
                    box.win.destroy()
                except tk.TclError:
                    pass
            else:
                still_visible.append(box)
        self.boxes = still_visible

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
