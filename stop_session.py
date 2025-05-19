from secure_workspace import SecureWorkspace
import os

CHOICE_FILE = "user_choices.txt"

def load_user_choices():
    if not os.path.exists(CHOICE_FILE):
        return set()
    with open(CHOICE_FILE, "r") as f:
        content = f.read().strip()
    if content.lower() == "all":
        return "all"
    elif content.lower() == "none":
        return set()
    else:
        try:
            indices = [int(x.strip()) - 1 for x in content.split(",") if x.strip().isdigit()]
            return set(indices)
        except:
            return set()

def apply_decision(files, keep_indices):
    keep = set()
    if keep_indices == "all":
        return set(files)
    for i in keep_indices:
        if 0 <= i < len(files):
            keep.add(files[i])
    return keep

def main():
    print("Stopping Secure Workspace...")
    sw = SecureWorkspace()
    sw.load_snapshot()

    added, modified, deleted = sw.detect_changes()

    keep_added = apply_decision(added, load_user_choices()) if added else set()
    keep_modified = apply_decision(modified, load_user_choices()) if modified else set()
    skip_deleted = apply_decision(deleted, load_user_choices()) if deleted else set()

    for f in added:
        if f not in keep_added:
            sw.remove_file(f)

    for f in modified:
        if f not in keep_modified:
            sw.restore_file(f)

    for f in deleted:
        if f not in skip_deleted:
            sw.restore_file(f)

    # Cleanup
    if os.path.exists(CHOICE_FILE):
        os.remove(CHOICE_FILE)

    print("\nSession cleaned up. Goodbye!")

if __name__ == "__main__":
    main()
