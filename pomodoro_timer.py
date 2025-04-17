import tkinter as tk
from tkinter import messagebox
import time
import threading

POMODORO_DURATION = 25 * 60  # 25 minutes
BREAK_DURATION = 15 * 60    # 15 minutes
POMODOROS_BEFORE_BREAK = 4

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.configure(bg="#111111")

        self.pomodoros_completed = 0
        self.is_break = False
        self.timer_running = False
        self.time_left = POMODORO_DURATION
        self.timer_thread = None
        self.paused = False  # Track paused state

        label_fg = "#FFA500"
        btn_fg = "#FFA500"
        btn_bg = "#222222"

        # Custom title bar
        self.title_bar = tk.Frame(root, bg="#111111", relief="raised", bd=0, highlightthickness=0)
        self.title_bar.pack(fill=tk.X, side=tk.TOP)
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.do_move)

        self.title_label = tk.Label(self.title_bar, text="Pomodoro Timer", bg="#111111", fg="#FFA500", font=("Helvetica", 12, "bold"))
        self.title_label.pack(side=tk.LEFT, padx=10)
        self.title_label.bind('<Button-1>', self.start_move)
        self.title_label.bind('<B1-Motion>', self.do_move)

        self.min_button = tk.Button(self.title_bar, text="_", command=self.minimize_window, bg="#111111", fg="#FFA500", borderwidth=0, font=("Helvetica", 12, "bold"), activebackground="#444444", activeforeground="#FFA500")
        self.min_button.pack(side=tk.RIGHT, padx=(0,0))

        self.close_button = tk.Button(self.title_bar, text="✕", command=root.destroy, bg="#111111", fg="#FFA500", borderwidth=0, font=("Helvetica", 12, "bold"), activebackground="#444444", activeforeground="#FFA500")
        self.close_button.pack(side=tk.RIGHT, padx=10)

        # Window dragging
        self._offsetx = 0
        self._offsety = 0

        self.label_timer = tk.Label(root, text=self.format_time(self.time_left), font=("Helvetica", 36), fg=label_fg, bg="#111111")
        self.label_timer.pack(pady=20)

        self.label_pomodoros = tk.Label(root, text=f"Completed Pomodoros: {self.pomodoros_completed}", font=("Helvetica", 16), fg=label_fg, bg="#111111")
        self.label_pomodoros.pack(pady=10)

        self.label_message = tk.Label(root, text="Ready to start!", font=("Helvetica", 14), fg=label_fg, bg="#111111")
        self.label_message.pack(pady=10)

        self.button_start = tk.Button(root, text="Start Next Phase", command=self.start_next_phase, font=("Helvetica", 14), fg=btn_fg, bg="#222222", activeforeground=btn_fg, activebackground="#444444")
        self.button_start.pack(pady=10)

        self.button_pause = tk.Button(root, text="Pause", command=self.pause_or_resume, font=("Helvetica", 14), fg=btn_fg, bg="#222222", activeforeground=btn_fg, activebackground="#444444")
        self.button_pause.pack(pady=10)

        self.button_reset = tk.Button(root, text="Reset Pomodoros", command=self.reset_pomodoros, font=("Helvetica", 14), fg=btn_fg, bg="#222222", activeforeground=btn_fg, activebackground="#444444")
        self.button_reset.pack(pady=10)

        self.update_ui()

    def format_time(self, seconds):
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def update_ui(self):
        self.label_timer.config(text=self.format_time(self.time_left))
        self.label_pomodoros.config(text=f"Completed Pomodoros: {self.pomodoros_completed}")
        if self.is_break:
            self.label_message.config(text="Break Period")
            self.button_start.config(text="Resume")
        else:
            self.label_message.config(text="Ready to start!")
            self.button_start.config(text="Start Next Phase")
        if self.timer_running:
            self.button_start.config(state=tk.DISABLED)
            self.button_pause.config(state=tk.NORMAL, text="Pause")
        elif self.paused:
            self.button_start.config(state=tk.DISABLED)
            self.button_pause.config(state=tk.NORMAL, text="Resume")
        else:
            self.button_start.config(state=tk.NORMAL)
            self.button_pause.config(state=tk.DISABLED, text="Pause")

    def timer_tick(self):
        while self.time_left > 0 and self.timer_running:
            time.sleep(1)
            self.time_left -= 1
            self.root.after(0, self.update_ui)
        if self.timer_running:
            self.root.after(0, self.timer_end)

    def start_timer(self):
        self.timer_running = True
        self.update_ui()
        self.timer_thread = threading.Thread(target=self.timer_tick, daemon=True)
        self.timer_thread.start()

    def stop_timer(self):
        self.timer_running = False
        self.update_ui()

    def pause_or_resume(self):
        if self.timer_running:
            self.paused = True
            self.stop_timer()
        elif self.paused:
            self.paused = False
            self.start_timer()

    def timer_end(self):
        self.timer_running = False
        if not self.is_break:
            self.pomodoros_completed += 1
            messagebox.showinfo("Pomodoro Complete!", "Time for a break!")
            if self.pomodoros_completed % POMODOROS_BEFORE_BREAK == 0:
                self.is_break = True
                self.time_left = BREAK_DURATION
            else:
                self.is_break = False
                self.time_left = POMODORO_DURATION
        else:
            messagebox.showinfo("Break Over!", "Resume your Pomodoro sessions!")
            self.is_break = False
            self.time_left = POMODORO_DURATION
        self.update_ui()

    def start_next_phase(self):
        if not self.timer_running:
            self.start_timer()

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def do_move(self, event):
        x = event.x_root - self._offsetx
        y = event.y_root - self._offsety
        self.root.geometry(f'+{x}+{y}')

    def minimize_window(self):
        self.root.update_idletasks()
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(200, lambda: self.root.overrideredirect(True))

    def reset_pomodoros(self):
        self.pomodoros_completed = 0
        self.update_ui()


def main():
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
