import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk
import subprocess
import threading
import json
import os

class FileDecisionDialog:
    def __init__(self, parent, changes_data):
        self.result = {}
        self.changes_data = changes_data
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("File Decision Manager")
        self.dialog.geometry("900x700")
        self.dialog.grab_set()  # Make modal
        self.dialog.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with scrollbar
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Individual File Decisions", 
                              font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = tk.Label(main_frame, 
                               text="Choose what to do with each file. Your workspace will be updated based on these decisions.",
                               font=("Arial", 10), wraplength=800)
        instructions.pack(pady=(0, 10))
        
        # Create notebook for different change types
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, 10))
        
        self.file_vars = {}
        
        # Added Files Tab
        if self.changes_data.get('added'):
            self.create_added_files_tab()
        
        # Modified Files Tab  
        if self.changes_data.get('modified'):
            self.create_modified_files_tab()
            
        # Deleted Files Tab
        if self.changes_data.get('deleted'):
            self.create_deleted_files_tab()
        
        # Buttons frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Bulk action buttons
        bulk_frame = tk.Frame(button_frame)
        bulk_frame.pack(pady=(0, 10))
        
        tk.Button(bulk_frame, text="Keep All Changes", command=self.keep_all_changes,
                 bg="lightgreen", width=15).pack(side='left', padx=5)
        tk.Button(bulk_frame, text="Revert All Changes", command=self.revert_all_changes,
                 bg="lightcoral", width=15).pack(side='left', padx=5)
        
        # Action buttons
        action_frame = tk.Frame(button_frame)
        action_frame.pack()
        
        tk.Button(action_frame, text="Apply Decisions", command=self.apply_decisions,
                 bg="lightblue", width=15, font=("Arial", 10, "bold")).pack(side='left', padx=5)
        tk.Button(action_frame, text="Cancel", command=self.cancel,
                 width=15).pack(side='left', padx=5)
    
    def create_added_files_tab(self):
        """Create tab for added files"""
        added_frame = ttk.Frame(self.notebook)
        self.notebook.add(added_frame, text=f"Added Files ({len(self.changes_data['added'])})")
        
        # Create scrollable frame
        canvas = tk.Canvas(added_frame)
        scrollbar = ttk.Scrollbar(added_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions for added files
        info_label = tk.Label(scrollable_frame, 
                             text="These files were created during your session:",
                             font=("Arial", 10, "bold"), fg="green")
        info_label.pack(anchor='w', pady=(5, 10))
        
        self.file_vars['added'] = {}
        
        for file_path in self.changes_data['added']:
            file_frame = tk.Frame(scrollable_frame, relief='ridge', bd=1)
            file_frame.pack(fill='x', padx=5, pady=2)
            
            # File path label
            path_label = tk.Label(file_frame, text=file_path, font=("Courier", 9), anchor='w')
            path_label.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            
            # Decision variable
            var = tk.StringVar(value="keep")
            self.file_vars['added'][file_path] = var
            
            # Radio buttons
            radio_frame = tk.Frame(file_frame)
            radio_frame.pack(side='right', padx=5)
            
            tk.Radiobutton(radio_frame, text="Keep", variable=var, value="keep",
                          fg="green").pack(side='left')
            tk.Radiobutton(radio_frame, text="Delete", variable=var, value="delete",
                          fg="red").pack(side='left')
    
    def create_modified_files_tab(self):
        """Create tab for modified files"""
        modified_frame = ttk.Frame(self.notebook)
        self.notebook.add(modified_frame, text=f"Modified Files ({len(self.changes_data['modified'])})")
        
        # Create scrollable frame
        canvas = tk.Canvas(modified_frame)
        scrollbar = ttk.Scrollbar(modified_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions for modified files
        info_label = tk.Label(scrollable_frame, 
                             text="These files were changed during your session:",
                             font=("Arial", 10, "bold"), fg="orange")
        info_label.pack(anchor='w', pady=(5, 10))
        
        self.file_vars['modified'] = {}
        
        for file_path in self.changes_data['modified']:
            file_frame = tk.Frame(scrollable_frame, relief='ridge', bd=1)
            file_frame.pack(fill='x', padx=5, pady=2)
            
            # File path label
            path_label = tk.Label(file_frame, text=file_path, font=("Courier", 9), anchor='w')
            path_label.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            
            # Decision variable
            var = tk.StringVar(value="keep")
            self.file_vars['modified'][file_path] = var
            
            # Radio buttons
            radio_frame = tk.Frame(file_frame)
            radio_frame.pack(side='right', padx=5)
            
            tk.Radiobutton(radio_frame, text="Keep Changes", variable=var, value="keep",
                          fg="green").pack(side='left')
            tk.Radiobutton(radio_frame, text="Revert to Original", variable=var, value="revert",
                          fg="red").pack(side='left')
    
    def create_deleted_files_tab(self):
        """Create tab for deleted files"""
        deleted_frame = ttk.Frame(self.notebook)
        self.notebook.add(deleted_frame, text=f"Deleted Files ({len(self.changes_data['deleted'])})")
        
        # Create scrollable frame
        canvas = tk.Canvas(deleted_frame)
        scrollbar = ttk.Scrollbar(deleted_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Instructions for deleted files
        info_label = tk.Label(scrollable_frame, 
                             text="These files were deleted during your session:",
                             font=("Arial", 10, "bold"), fg="red")
        info_label.pack(anchor='w', pady=(5, 10))
        
        self.file_vars['deleted'] = {}
        
        for file_path in self.changes_data['deleted']:
            file_frame = tk.Frame(scrollable_frame, relief='ridge', bd=1)
            file_frame.pack(fill='x', padx=5, pady=2)
            
            # File path label
            path_label = tk.Label(file_frame, text=file_path, font=("Courier", 9), anchor='w')
            path_label.pack(side='left', fill='x', expand=True, padx=5, pady=5)
            
            # Decision variable
            var = tk.StringVar(value="restore")
            self.file_vars['deleted'][file_path] = var
            
            # Radio buttons
            radio_frame = tk.Frame(file_frame)
            radio_frame.pack(side='right', padx=5)
            
            tk.Radiobutton(radio_frame, text="Restore File", variable=var, value="restore",
                          fg="green").pack(side='left')
            tk.Radiobutton(radio_frame, text="Keep Deleted", variable=var, value="keep_deleted",
                          fg="red").pack(side='left')
    
    def keep_all_changes(self):
        """Set all files to keep current state"""
        for category in self.file_vars:
            for file_path, var in self.file_vars[category].items():
                if category == 'added':
                    var.set("keep")
                elif category == 'modified':
                    var.set("keep")
                elif category == 'deleted':
                    var.set("keep_deleted")
    
    def revert_all_changes(self):
        """Set all files to revert to original state"""
        for category in self.file_vars:
            for file_path, var in self.file_vars[category].items():
                if category == 'added':
                    var.set("delete")
                elif category == 'modified':
                    var.set("revert")
                elif category == 'deleted':
                    var.set("restore")
    
    def apply_decisions(self):
        """Apply the user's decisions"""
        decisions = {}
        
        for category in self.file_vars:
            decisions[category] = {}
            for file_path, var in self.file_vars[category].items():
                decisions[category][file_path] = var.get()
        
        self.result = decisions
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel without making changes"""
        self.result = {}
        self.dialog.destroy()

class SecureWorkspaceUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Workspace - Enhanced File Control")
        self.root.geometry("900x700")

        self.status_label = tk.Label(root, text="Status: Idle", fg="blue", font=("Arial", 12))
        self.status_label.pack(pady=5)

        # Button frame for better organization
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.timer_button = tk.Button(button_frame, text="Set Session Timer (minutes)", 
                                     command=self.set_timer, width=25)
        self.timer_button.pack(pady=2)

        self.start_button = tk.Button(button_frame, text="Start Session", 
                                     command=self.run_start, width=25, bg="lightgreen")
        self.start_button.pack(pady=2)

        self.stop_button = tk.Button(button_frame, text="Stop Session", 
                                    command=self.run_stop, width=25, bg="lightcoral")
        self.stop_button.pack(pady=2)

        # Log area with frame and label
        log_frame = tk.Frame(root)
        log_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        log_label = tk.Label(log_frame, text="Session Log:", font=("Arial", 10, "bold"))
        log_label.pack(anchor='w')

        self.log = scrolledtext.ScrolledText(log_frame, height=25, width=110, 
                                           state='disabled', font=("Consolas", 9))
        self.log.pack(fill='both', expand=True)

        self.session_timer = None
        self.session_active = False
        self.pending_changes = None
        
        # Update button states
        self.update_button_states()

    def append_log(self, text):
        self.log.configure(state='normal')
        self.log.insert(tk.END, text + '\n')
        self.log.configure(state='disabled')
        self.log.see(tk.END)
        self.root.update_idletasks()

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        if "Started" in status:
            self.session_active = True
        elif "Stopped" in status or "Idle" in status:
            self.session_active = False
        self.update_button_states()

    def update_button_states(self):
        if self.session_active:
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
        else:
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')

    def run_command(self, script):
        try:
            # Get the directory of the current script (all files are in same folder)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(script_dir, script)
            
            process = subprocess.Popen(
                ["python3", script_path], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                cwd=script_dir
            )
            
            # Read output in real-time
            output_buffer = ""
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    self.append_log(line)
                    output_buffer += line + "\n"
                    
                    # Check for changes detection
                    if "CHANGES_DETECTED_START" in line:
                        self.capture_changes_data(process)
            
            # Get any remaining output
            remaining_output, error = process.communicate()
            if remaining_output:
                self.append_log(remaining_output.strip())
            if error:
                self.append_log("Error:\n" + error.strip())

        except Exception as e:
            self.append_log(f"Exception: {str(e)}")

    def capture_changes_data(self, process):
        """Capture the changes data from the process output"""
        changes_json = ""
        capturing = True
        
        while capturing:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            self.append_log(line)
            
            if "CHANGES_DETECTED_END" in line:
                capturing = False
            elif "CHANGES_DETECTED_START" not in line:
                changes_json += line + "\n"
        
        try:
            changes_data = json.loads(changes_json)
            if any(changes_data.values()):  # If there are any changes
                self.root.after(500, lambda: self.show_file_decision_dialog(changes_data))
        except json.JSONDecodeError:
            self.append_log("Error: Could not parse changes data")

    def show_file_decision_dialog(self, changes_data):
        """Show the file decision dialog"""
        dialog = FileDecisionDialog(self.root, changes_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # Save decisions to file
            with open("user_choices.json", "w") as f:
                json.dump(dialog.result, f, indent=2)
            self.append_log("\nFile decisions saved. Processing changes...")
        else:
            # User cancelled - create empty choices file
            with open("user_choices.json", "w") as f:
                json.dump({}, f)
            self.append_log("\nNo decisions made. Keeping all changes by default...")

    def run_start(self):
        self.update_status("Starting session...")
        self.append_log("=" * 60)
        self.append_log("STARTING SECURE WORKSPACE SESSION")
        self.append_log("=" * 60)
        threading.Thread(target=self._run_and_log, args=("start_session.py", "Session Started"), daemon=True).start()

    def run_stop(self):
        self.update_status("Stopping session...")
        self.append_log("\n" + "=" * 60)
        self.append_log("STOPPING SECURE WORKSPACE SESSION")
        self.append_log("=" * 60)
        if self.session_timer:
            self.root.after_cancel(self.session_timer)
            self.session_timer = None
            self.append_log("Session timer cancelled.")
        threading.Thread(target=self._run_and_log, args=("stop_session.py", "Session Stopped"), daemon=True).start()

    def _run_and_log(self, script, done_status):
        self.run_command(script)
        self.update_status(done_status)

    def set_timer(self):
        minutes = simpledialog.askinteger("Session Timer", 
                                        "Enter session duration in minutes:", 
                                        minvalue=1, maxvalue=480)
        if minutes:
            if self.session_timer:
                self.root.after_cancel(self.session_timer)
            self.session_timer = self.root.after(minutes * 60 * 1000, self.auto_stop_session)
            self.append_log(f"Session timer set for {minutes} minute(s)")

    def auto_stop_session(self):
        self.append_log("\n*** SESSION TIMER EXPIRED - AUTO STOPPING ***")
        self.run_stop()

    def on_closing(self):
        if self.session_active:
            if messagebox.askokcancel("Quit", "A session is active. Stop session before quitting?"):
                self.run_stop()
                # Give time for session to stop before closing
                self.root.after(3000, self.root.destroy)
            else:
                return
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SecureWorkspaceUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
