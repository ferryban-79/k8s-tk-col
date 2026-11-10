import os
import subprocess
import sys
from pathlib import Path

# Zaroori files jo GitHub par sync karni hain
TARGET_FILES = ["links.txt", "session_mapping.json", "rclone.conf.enc"]

def main():
    print("=" * 55)
    print("🚀 TikTok Scraper — Local SSH Multi-File Sync Tool")
    print("=" * 55)

    # Check ki kya hum sahi git repository ke andar hain
    if not Path(".git").exists():
        print("❌ Error: Local .git folder nahi mila! Sahi repository me run karein.")
        sys.exit(1)

    # Files check karein aur stage karein
    files_to_add = []
    for filename in TARGET_FILES:
        local_path = Path(__file__).parent / filename
        if local_path.exists():
            files_to_add.append(filename)
            print(f"📦 Staging: {filename}")
        else:
            print(f"⚠️  Skipping: {filename} (Local file nahi mili)")

    if not files_to_add:
        print("❌ Sync karne ke liye koi target file maujood nahi hai.")
        return

    try:
        # 1. Files ko git add karein
        subprocess.run(["git", "add"] + files_to_add, check=True)
        
        # 2. Check karein ki kya koi actual changes hain commit karne ke liye
        status_check = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=True)
        if not status_check.stdout.strip():
            print("✅ All files are already up-to-date on GitHub. No changes to push.")
            print("=" * 55)
            return

        # 3. Changes ko locally commit karein
        commit_msg = "🔄 Auto-sync: Updated configuration, links, and map via SSH"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        print("📝 Changes committed locally.")

        # 4. SSH ke zariye GitHub par push karein
        print("⬆️  Pushing changes to GitHub via SSH Tunnel...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("🎉 Success! All configuration files synced to GitHub via SSH!")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git Operation Failed: {e}")

    print("=" * 55)

if __name__ == "__main__":
    main()