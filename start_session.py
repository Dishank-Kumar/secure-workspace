from secure_workspace import SecureWorkspace

def main():
    print("Initializing Secure Workspace...")
    sw = SecureWorkspace()
    sw.save_snapshot()
    sw.backup_files()
    print("Secure session started. You may now work freely.")

if __name__ == "__main__":
    main()
