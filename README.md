# **Secure Workspace Manager**  
*A Safe Sandbox Environment for File Modifications*

## **Overview**  
This tool creates a **secure workspace** that:  
✅ **Tracks changes** to files during a session  
✅ **Backs up original files** for easy restoration  
✅ **Allows selective preservation** of modifications  
✅ **Provides a GUI** for easy control  

Ideal for **testing scripts, experimenting with files, or temporary work** without risking permanent changes.  

---

## **Key Features**  

### **1. Session Management**  
- **Start Session**: Takes a snapshot of all files in the workspace  
- **Stop Session**: Restores files to their original state (with user choice)  

### **2. Change Detection**  
- Detects **added, modified, and deleted files**  
- Uses **SHA-256 hashing** to verify file integrity  

### **3. User Control**  
- **Choose which changes to keep** (all, none, or specific files)  
- **Set a timer** for automatic session termination  

### **4. Exclusion System**  
- Automatically ignores common directories (`.git`, `node_modules`, etc.)  
- Customizable exclusion patterns  

---

## **Installation**  

### **1. Clone the Repository**  
```bash
git clone https://github.com/Dishank-Kumar/secure-workspace.git
cd secure-workspace
```

### **2. Install Dependencies**  
```bash
pip install tkinter
```

*(No additional dependencies needed for basic functionality.)*  

---

## **Usage**  

### **1. Run the GUI**  
```bash
python app.py
```

### **2. Start a Session**  
- Click **"Start Session"** to begin tracking changes.  
- Optionally set a **timer** for auto-shutdown.  

### **3. Work Normally**  
- Modify, add, or delete files as needed.  

### **4. Stop the Session**  
- Click **"Stop Session"** to review changes.  
- Choose which files to **keep or discard**.  

---

## **Example Workflow**  

### **Starting a Session**  
```python
from secure_workspace import SecureWorkspace

sw = SecureWorkspace()  
sw.save_snapshot()  # Records current file states  
sw.backup_files()   # Creates backups  
```

### **Stopping a Session**  
```python
added, modified, deleted = sw.detect_changes()  

# Restore all changes (optional)  
for file in modified:  
    sw.restore_file(file)  

# Keep specific files (via GUI or manual input)  
```

---

## **Command-Line Tools**  

| Script | Purpose |  
|--------|---------|  
| `start_session.py` | Initialize a secure session |  
| `stop_session.py` | End session and clean up |  

Run them directly:  
```bash
python start_session.py
python stop_session.py
```

---

## **Configuration**  

### **Custom Exclusions**  
Modify `DEFAULT_EXCLUDE` in `secure_workspace.py` to ignore specific files/dirs:  
```python
DEFAULT_EXCLUDE = [
    ".git", "__pycache__", "temp/*"  # Add your own patterns
]
```

### **Changing Workspace Directory**  
```python
sw = SecureWorkspace(home_dir="/path/to/your/workspace")
```

---

## **Security Notes**  
🔒 **Backups are stored in a temp directory** (automatically cleaned).  
⚠ **No encryption** – avoid storing sensitive data in the workspace.  

---

## **License**  
MIT License – Free for personal and commercial use.  

---
  

🚀 **Happy Safe Coding!** 🚀
