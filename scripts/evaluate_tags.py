import os
import subprocess
import csv
import shutil
from pathlib import Path

# =====================================================================
# 评委配置区：在这里填入所有参赛队伍的 Git 仓库克隆链接
# =====================================================================
REPOS = [
    # "https://github.com/username/team1-repo.git",
    # "https://gitlab.com/username/team2-repo.git",
]

CLONE_DIR = "./temp_eval_repos"
RESULTS_CSV = "leaderboard_results.csv"

def run_cmd(cmd, cwd=None):
    """执行 Shell 命令并返回输出结果"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None

def evaluate_repo(repo_url):
    """克隆仓库并评估时间和交付物"""
    team_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = os.path.join(CLONE_DIR, team_name)
    
    print(f"\n📦 正在拉取队伍仓库: {team_name} ...")
    
    # 清理历史残留
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path, ignore_errors=True)
    
    clone_out = run_cmd(["git", "clone", "--quiet", repo_url, repo_path])
    if not os.path.exists(repo_path):
        print(f"  ❌ 拉取失败，请检查链接或网络权限: {repo_url}")
        return {
            "Team": team_name, "RepoURL": repo_url,
            "Basic Time": "Error", "Advanced Time": "Error",
            "Has App": False, "Has Logs": False
        }

    # 获取 Tag 对应的时间戳（%cI 返回严格的 ISO 8601 格式时间）
    basic_time = run_cmd(["git", "log", "-1", "--format=%cI", "basic-done"], cwd=repo_path)
    advanced_time = run_cmd(["git", "log", "-1", "--format=%cI", "advanced-done"], cwd=repo_path)

    # 检查核心交付物文件是否存在
    has_app = os.path.exists(os.path.join(repo_path, "app.py"))
    
    # AI 交互日志可能是 markdown 或者是其他形式附件
    has_logs = False
    for file in os.listdir(repo_path):
        if "PROMPT" in file.upper() or "LOG" in file.upper() or "AGENT" in file.upper():
            has_logs = True
            break

    print(f"  ✅ 基础完赛: {basic_time if basic_time else '未找到 Tag'}")
    print(f"  ✅ 进阶完赛: {advanced_time if advanced_time else '未找到 Tag'}")
    
    return {
        "Team": team_name,
        "RepoURL": repo_url,
        "Basic Time": basic_time if basic_time else "N/A",
        "Advanced Time": advanced_time if advanced_time else "N/A",
        "Has App": has_app,
        "Has Logs": has_logs
    }

def main():
    if not REPOS:
        print("⚠️ 请先在脚本顶部 REPOS 列表中添加参赛队伍的仓库链接！")
        return

    print("🚀 开始执行“Code with AI” 竞赛自动评估脚本...")
    
    if not os.path.exists(CLONE_DIR):
        os.makedirs(CLONE_DIR)

    results = []
    for url in REPOS:
        res = evaluate_repo(url)
        results.append(res)
        
    # 按“基础关卡”完成时间排序（N/A 或 Error 放最后）
    results.sort(key=lambda x: x['Basic Time'] if x['Basic Time'] not in ("N/A", "Error") else "9999-12-31")

    # 写入 CSV 结果表
    with open(RESULTS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["Team", "Basic Time", "Advanced Time", "Has App", "Has Logs", "RepoURL"])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"\n🎉 评估完成！排行榜已导出至当前目录下的: {RESULTS_CSV}")

if __name__ == "__main__":
    main()
