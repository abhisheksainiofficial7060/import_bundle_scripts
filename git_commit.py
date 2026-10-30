#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用的 git commit 脚本
读取 repos.txt，对每个 repo 提交指定类型的文件
"""

import subprocess
import sys
from pathlib import Path

# ========== 配置常量 ==========
# Commit message
COMMIT_MESSAGE = "submit translation"

# 要提交的文件扩展名列表（不包含点号）
FILE_EXTENSIONS = ['tbulic22']
# =============================

def git_add_files(repo_dir, extensions):
    """添加指定扩展名的文件到 git staging area"""
    try:
        # 查找所有匹配的文件
        files_to_add = []
        repo_path = Path(repo_dir)
        
        for ext in extensions:
            # 递归查找所有匹配的文件
            for file_path in repo_path.rglob(f'*.{ext}'):
                # 获取相对于 repo 目录的路径
                rel_path = file_path.relative_to(repo_path)
                files_to_add.append(str(rel_path))
        
        if not files_to_add:
            return True, []  # 没有文件需要添加
        
        # 添加所有找到的文件，检查每个命令的返回值
        added_files = []
        for file_path in files_to_add:
            result = subprocess.run(
                ['git', 'add', file_path],
                cwd=repo_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                added_files.append(file_path)
            else:
                print(f"  Warning: Failed to add {file_path}: {result.stderr.strip()}")
        
        return True, added_files
    except Exception as e:
        print(f"  Error: Failed to add files: {e}")
        return False, []

def git_commit(repo_dir, message):
    """执行 git commit"""
    try:
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, error_msg
    except Exception as e:
        return False, str(e)

def git_push(repo_dir):
    """执行 git push"""
    try:
        # 获取当前分支
        branch_result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if branch_result.returncode != 0:
            return False, "Failed to get current branch"
        
        current_branch = branch_result.stdout.strip()
        if not current_branch:
            return False, "No current branch"
        
        # 执行 push
        result = subprocess.run(
            ['git', 'push'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, error_msg
    except Exception as e:
        return False, str(e)

def check_unpushed_commits(repo_dir):
    """检查是否有未推送的提交"""
    try:
        # 尝试获取远程跟踪分支
        remote_branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if remote_branch_result.returncode != 0:
            # 没有远程跟踪分支，无法检查
            return False, []
        
        remote_branch = remote_branch_result.stdout.strip()
        
        # 检查本地是否有未推送的提交
        log_result = subprocess.run(
            ['git', 'log', f'{remote_branch}..HEAD', '--oneline'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if log_result.returncode == 0:
            commits = [line.strip() for line in log_result.stdout.strip().split('\n') if line.strip()]
            return len(commits) > 0, commits
        
        return False, []
    except:
        return False, []

def check_modified_files(repo_dir, extensions):
    """检查工作区是否有匹配扩展名的修改文件（包括未跟踪、已修改、已删除）"""
    try:
        # -uall：列出未跟踪目录下的每个文件，避免只出现父目录导致路径不以 .ext 结尾而无法匹配
        result = subprocess.run(
            ['git', 'status', '--porcelain', '-uall'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False, []
        
        # 解析状态输出
        # 格式: XY filename
        # X: staged状态, Y: working tree状态
        # ??: 未跟踪, M: 修改, D: 删除, A: 新增
        modified_files = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            
            status = line[:2]
            file_path = line[3:].strip()
            
            # 检查文件扩展名是否匹配
            if any(file_path.endswith(f'.{ext}') for ext in extensions):
                # 如果文件在工作区有变化（未跟踪、修改、删除）或已暂存
                if status[0] != ' ' or status[1] != ' ':  # 有变化
                    modified_files.append(file_path)
        
        return len(modified_files) > 0, modified_files
    except Exception as e:
        return False, []

def check_staged_files(repo_dir):
    """检查是否有 staged 的文件"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only'],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            staged_files = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            return len(staged_files) > 0, staged_files
        return False, []
    except Exception as e:
        return False, []

def main():
    value = input("Validate finished? [finished or n]:\n")
    if value.strip() != "finished":
        print("script stopped")
        sys.exit(0)

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
    
    print(f"Found {len(repos)} repo(s), starting commit...")
    print(f"Commit message: {COMMIT_MESSAGE}")
    print(f"File extensions: {', '.join(FILE_EXTENSIONS)}\n")
    
    # 处理每个 repo
    success_count = 0
    skip_count = 0
    error_count = 0
    
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
        
        # 先检查是否有匹配扩展名的修改文件
        has_modified, modified_files = check_modified_files(repo_dir, FILE_EXTENSIONS)
        if not has_modified:
            # 检查是否有未 push 的提交
            has_unpushed, unpushed_commits = check_unpushed_commits(repo_dir)
            if has_unpushed:
                print(f"  Found {len(unpushed_commits)} unpushed commit(s), pushing...")
                push_success, push_message = git_push(repo_dir)
                if push_success:
                    print(f"  Pushed successfully")
                    success_count += 1
                else:
                    print(f"  Error: Push failed - {push_message}")
                    error_count += 1
            else:
                print(f"  Skipped (no matching files to commit, no unpushed commits)")
                skip_count += 1
            continue
        
        # 显示找到的修改文件
        if modified_files:
            print(f"  Found {len(modified_files)} modified file(s)")
        
        # 添加指定类型的文件
        add_success, added_files = git_add_files(repo_dir, FILE_EXTENSIONS)
        if not add_success:
            print(f"  Error: Failed to add files")
            error_count += 1
            continue
        
        # 检查是否有文件被成功添加到 staging area
        has_staged, staged_files = check_staged_files(repo_dir)
        if not has_staged:
            print(f"  Warning: Files found but none were staged. This may indicate the files are already committed or ignored.")
            skip_count += 1
            continue
        
        # 执行 commit
        success, message = git_commit(repo_dir, COMMIT_MESSAGE)
        
        if success:
            print(f"  Committed successfully ({len(staged_files)} file(s))")
            # Commit 成功后，尝试 push
            has_unpushed, unpushed_commits = check_unpushed_commits(repo_dir)
            if has_unpushed:
                print(f"  Pushing {len(unpushed_commits)} commit(s)...")
                push_success, push_message = git_push(repo_dir)
                if push_success:
                    print(f"  Pushed successfully")
                    success_count += 1
                else:
                    print(f"  Warning: Commit succeeded but push failed - {push_message}")
                    error_count += 1
            else:
                success_count += 1
        else:
            # 检查是否是正常的跳过情况
            if "nothing to commit" in message.lower() or "no changes" in message.lower() or "nothing added" in message.lower():
                print(f"  Skipped (nothing to commit)")
                skip_count += 1
            else:
                print(f"  Error: Commit failed - {message}")
                error_count += 1
                # 如果 commit 失败，可以选择继续或停止
                # 这里选择继续，但会记录错误
    
    print(f"\nDone! Successfully committed: {success_count}, Skipped: {skip_count}, Errors: {error_count}")

if __name__ == "__main__":
    main()

