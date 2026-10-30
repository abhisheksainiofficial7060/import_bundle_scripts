#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从 repos.txt 读取 repo 列表，对每个 repo 执行 git pull
让所有 repo 保持最新
"""

import subprocess
from pathlib import Path

def git_pull(repo_dir):
    """执行 git pull，直接输出详细信息到控制台"""
    try:
        # 直接输出到控制台，不捕获输出
        # 这样可以看到 git pull 的详细信息（拉取的文件、更新内容等）
        result = subprocess.run(
            ['git', 'pull'],
            cwd=repo_dir,
            stdout=None,  # 直接输出到控制台
            stderr=None,  # 直接输出到控制台（包括进度信息）
            text=True
        )
        
        if result.returncode == 0:
            return True, ""
        else:
            return False, "git pull failed"
    except Exception as e:
        return False, str(e)

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    
    # repos.txt 文件路径
    repos_file = script_dir / "repos.txt"
    
    # 检查 repos.txt 是否存在
    if not repos_file.exists():
        print(f"Error: File not found: {repos_file}")
        return
    
    # 读取 repos.txt
    try:
        with open(repos_file, 'r', encoding='utf-8') as f:
            repos = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error: Failed to read {repos_file}: {e}")
        return
    
    if not repos:
        print("repos.txt is empty")
        return
    
    print(f"Found {len(repos)} repo(s), starting pull...\n")
    
    # 统计
    success_count = 0
    skip_count = 0
    error_count = 0
    
    # 处理每个 repo
    for repo in repos:
        repo_dir = script_dir / repo
        
        if not repo_dir.exists():
            print(f"{repo}: Error (directory not found)")
            error_count += 1
            continue
        
        # 检查是否是 git 仓库
        git_dir = repo_dir / ".git"
        if not git_dir.exists():
            print(f"{repo}: Skipped (not a git repository)")
            skip_count += 1
            continue
        
        print(f"{repo}:")
        print()  # 空行，让输出更清晰
        
        # 执行 pull（详细信息会直接显示在控制台）
        success, message = git_pull(repo_dir)
        
        print()  # 空行
        
        if success:
            success_count += 1
        else:
            # 检查是否是正常的错误（比如没有远程分支）
            if "no tracking information" in message.lower() or "no upstream branch" in message.lower():
                print(f"  Skipped (no remote tracking branch)")
                skip_count += 1
            else:
                print(f"  Error: {message}")
                error_count += 1
    
    print(f"\nDone! Successfully pulled: {success_count}, Skipped: {skip_count}, Errors: {error_count}")

if __name__ == "__main__":
    main()


