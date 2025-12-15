import subprocess

GIT_PATH = r"C:\Users\User\anaconda3\pkgs\git-2.40.1-haa95532_1\Library\bin\git.exe"

def run_git_command(cmd, cwd=None):
    result = subprocess.run(
        [GIT_PATH] + cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print("Error:", result.stderr.strip())
    return result

def get_current_branch(cwd=None):
    """取得目前分支名稱"""
    result = subprocess.run(
        [GIT_PATH, "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout.strip()

def has_changes(cwd=None):
    """檢查是否有檔案變更"""
    result = subprocess.run(
        [GIT_PATH, "status", "--porcelain"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    return bool(result.stdout.strip())

def auto_push(remote_url=None, cwd=None):
    """自動 push 到 GitHub，偵測目前分支"""
    branch = get_current_branch(cwd)
    if not branch:
        print("⚠️ 尚未建立分支，請先 commit 一次再推送。")
        return

    remotes = subprocess.run(
        [GIT_PATH, "remote", "-v"],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    ).stdout.strip()

    if not remotes:
        if remote_url:
            print("🔗 設定遠端 origin...")
            run_git_command(["remote", "add", "origin", remote_url], cwd=cwd)
        else:
            print("⚠️ 尚未設定遠端，請提供 remote_url")
            return

    print(f"🚀 推送到 GitHub ({branch})...")
    run_git_command(["push", "-u", "origin", branch], cwd=cwd)

# 專案路徑
PROJECT_PATH = r"D:/Code/Project/Python Project/Side Project"

# ---------------- 使用範例 ----------------
if __name__ == "__main__":
    # 初始化（只需第一次）
    run_git_command(["init"], cwd=PROJECT_PATH)

    # 設定使用者資訊（只需一次）
    run_git_command(["config", "user.name", "徐政賢"], cwd=PROJECT_PATH)
    run_git_command(["config", "user.email", "weary898@gmail.com"], cwd=PROJECT_PATH)
        
    # ✅ 檢查是否有變更
    if has_changes(cwd=PROJECT_PATH):
        print("🔍 偵測到檔案有變更，開始 commit...")
        run_git_command(["add", "."], cwd=PROJECT_PATH)
        run_git_command(["commit", "-m", "更新專案內容"], cwd=PROJECT_PATH)
        auto_push(
            remote_url="https://github.com/UsernameJasonHsu/RAG-Agent.git",
            cwd=PROJECT_PATH
        )
    else:
        print("✅ 沒有檔案變更，跳過 commit 與 push。")