from secure_workspace import SecureWorkspace
import time

def main():
    print("Initializing Secure Workspace (Optimized)...")
    start_time = time.time()
    
    sw = SecureWorkspace(max_depth=3, max_workers=4)
    
    print("Creating snapshot...")
    sw.save_snapshot()
    
    print("Creating backup...")
    sw.backup_files()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Secure session started successfully in {duration:.2f} seconds!")
    print("You may now work freely in your workspace.")
    print("\nPerformance settings:")
    print(f"- Scanning depth: {sw.max_depth} levels from home directory")
    print(f"- Parallel threads: {sw.max_workers}")
    print("- Large files (>100MB) are automatically skipped")
    print("- System directories are excluded for speed")

if __name__ == "__main__":
    main()
