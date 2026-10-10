import sys
import os
import dulwich.porcelain as dp
from dulwich.repo import Repo

REPO_URL = "github.com/modimust5669-art/imsanalysis.git"

def main():
    print("=" * 60)
    print("LIPTIS USA SALs App — GitHub Publisher")
    print(f"Target Repository: https://{REPO_URL}")
    print("=" * 60)

    token = None
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    
    if not token:
        print("\nGitHub requires a Personal Access Token (PAT) to authorize pushes.")
        print("To generate one:")
        print("  1. Go to: https://github.com/settings/tokens")
        print("  2. Click 'Generate new token (classic)'")
        print("  3. Give it a note (e.g. 'Liptis App') and check the [x] 'repo' scope")
        print("  4. Copy the generated token (starts with ghp_...)\n")
        try:
            token = input("Enter your GitHub Personal Access Token (or paste here): ").strip()
        except EOFError:
            pass

    if not token:
        print("Error: No GitHub token provided. Cannot proceed with push.")
        sys.exit(1)

    auth_url = f"https://{token}@{REPO_URL}"
    repo = Repo(".")

    # Ensure files are committed
    try:
        dp.add(repo)
        dp.commit(repo, message="Update LIPTIS USA SALs App".encode('utf-8'))
    except Exception:
        pass

    print("\nPushing code to GitHub repository...")
    try:
        # Push to main branch
        dp.push(repo, auth_url, "refs/heads/master:refs/heads/main", force=True)
        print("\n[SUCCESS] Successfully published to https://github.com/modimust5669-art/imsanalysis")
    except Exception as e:
        print(f"\n[PUSH FAILED] Error: {e}")
        print("Tip: Verify your token has 'repo' permissions and that your repository exists.")

if __name__ == "__main__":
    main()
