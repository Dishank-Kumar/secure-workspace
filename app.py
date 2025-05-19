import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import subprocess
import threading
import json

class SecureWorkspaceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Workspace")

        self.status_label = tk.Label(root, text="Status: Idle", fg="blue")
        self.status_label.pack(pady=5)

        self.timer_button = tk.Button(root, text="Set Session Timer (minutes)", command=self.set_timer)
        self.timer_button.pack(pady=2)

        self.start_button = tk.Button(root, text="Start Session", command=self.run_start)
        self.start_button.pack(pady=2)

        self.stop_button = tk.Button(root, text="Stop Session", command=self.run_stop)
        self.stop_button.pack(pady=2)

        self.log = scrolledtext.ScrolledText(root, height=15, width=80, state='disabled')
        self.log.pack(padx=10, pady=10)

        self.session_timer = None

    def append_log(self, text):
        self.log.configure(state='normal')
        self.log.insert(tk.END, text + '\n')
        self.log.configure(state='disabled')
        self.log.see(tk.END)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def run_command(self, script):
        try:
            process = subprocess.Popen(["python3", f"../{script}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate()
            self.append_log(output.strip())
            if error:
                self.append_log("Error:\n" + error)

            # If file change lists are found, prompt for user input
            if any(key in output for key in ["Added Files:", "Modified Files:", "Deleted Files:"]):
                self.ask_user_choices()

        except Exception as e:
            self.append_log(f"Exception: {str(e)}")

    def ask_user_choices(self):
        user_input = simpledialog.askstring(
            "Preserve Changes",
            "Enter file numbers to keep (e.g., 2,3,4), or 'all', or 'none':"
        )
        if user_input is not None:
            with open("user_choices.txt", "w") as f:
                f.write(user_input)
            self.append_log(f"Your choice has been saved: {user_input}")

    def run_start(self):
        self.update_status("Starting session...")
        threading.Thread(target=self._run_and_log, args=("start_session.py", "Session Started")).start()

    def run_stop(self):
        self.update_status("Stopping session...")
        if self.session_timer:
            self.root.after_cancel(self.session_timer)
        threading.Thread(target=self._run_and_log, args=("stop_session.py", "Session Stopped")).start()

    def _run_and_log(self, script, done_status):
        self.run_command(script)
        self.update_status(done_status)

    def set_timer(self):
        minutes = simpledialog.askinteger("Session Timer", "Enter session duration in minutes:")
        if minutes:
            self.session_timer = self.root.after(minutes * 60 * 1000, self.run_stop)
            self.append_log(f"Session timer set: {minutes} minute(s)")

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureWorkspaceUI(root)
    root.mainloop()
