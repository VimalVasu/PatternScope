# GitHub Setup Guide for PatternScope

This guide walks you through connecting your local PatternScope project to a GitHub repository and pushing your code.

## Prerequisites

- Git installed on your system
- GitHub account created
- GitHub CLI (`gh`) installed (optional but recommended)

## Method 1: Using GitHub CLI (Recommended)

### Step 1: Initialize Git Repository

```bash
# Navigate to your project directory
cd /Users/vimaleshvasu/Desktop/Apps/PatternScope

# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: PatternScope project setup"
```

### Step 2: Create GitHub Repository and Push

```bash
# Authenticate with GitHub (if not already)
gh auth login

# Create repository and push in one command
gh repo create PatternScope --public --source=. --remote=origin --push

# Or for private repository:
gh repo create PatternScope --private --source=. --remote=origin --push
```

That's it! Your code is now on GitHub.

## Method 2: Manual Setup via GitHub Website

### Step 1: Initialize Local Git Repository

```bash
# Navigate to your project directory
cd /Users/vimaleshvasu/Desktop/Apps/PatternScope

# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: PatternScope project setup"
```

### Step 2: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `PatternScope`
3. Description: (optional) "Your project description"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (since you already have local files)
6. Click "Create repository"

### Step 3: Connect Local Repository to GitHub

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/PatternScope.git

# Verify remote was added
git remote -v

# Push code to GitHub
git branch -M main
git push -u origin main
```

## Daily Workflow: Pushing New Code

Once your repository is set up, use this workflow to push changes:

### Basic Git Workflow

```bash
# 1. Check status of changed files
git status

# 2. Stage files for commit
git add .                    # Add all changed files
# OR
git add path/to/file.js      # Add specific file

# 3. Commit changes with descriptive message
git commit -m "feat: add user authentication"

# 4. Push to GitHub
git push
```

### Commit Message Best Practices

Use conventional commit format:

- `feat: add new feature`
- `fix: resolve bug in login`
- `docs: update README`
- `refactor: restructure auth module`
- `test: add unit tests for API`
- `chore: update dependencies`

### Example Workflow Session

```bash
# Made changes to multiple files
git status

# Stage specific files
git add src/components/Header.js
git add src/styles/main.css

# Commit with descriptive message
git commit -m "feat: implement responsive header navigation"

# Push to GitHub
git push

# Or do everything at once:
git add . && git commit -m "fix: resolve mobile menu overflow issue" && git push
```

## Working with Branches

### Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/user-profile

# Make changes and commit
git add .
git commit -m "feat: add user profile page"

# Push branch to GitHub
git push -u origin feature/user-profile

# Create pull request using GitHub CLI
gh pr create --title "Add user profile page" --body "Implements user profile with avatar and bio"
```

### Switch Between Branches

```bash
# View all branches
git branch -a

# Switch to existing branch
git checkout main
git checkout feature/user-profile

# Pull latest changes
git pull origin main
```

## Useful Git Commands

### View History

```bash
# View commit history
git log

# View compact history
git log --oneline

# View changes in last commit
git show
```

### Undo Changes

```bash
# Discard changes to a file (before staging)
git checkout -- path/to/file.js

# Unstage a file (after git add)
git reset HEAD path/to/file.js

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - USE WITH CAUTION
git reset --hard HEAD~1
```

### Sync with Remote

```bash
# Fetch changes without merging
git fetch origin

# Pull latest changes from main
git pull origin main

# Force pull (overwrite local changes) - USE WITH CAUTION
git fetch origin
git reset --hard origin/main
```

## Troubleshooting

### Authentication Issues

If you encounter authentication issues with HTTPS:

**Option 1: Use GitHub CLI**
```bash
gh auth login
```

**Option 2: Use SSH instead of HTTPS**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key and add to GitHub (Settings → SSH Keys)
cat ~/.ssh/id_ed25519.pub

# Change remote URL to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/PatternScope.git
```

### Merge Conflicts

If you encounter merge conflicts:

```bash
# Pull changes
git pull origin main

# Fix conflicts in files marked with <<<<<<, ======, >>>>>>

# Stage resolved files
git add path/to/resolved/file.js

# Complete merge
git commit -m "merge: resolve conflicts with main"

# Push changes
git push
```

### Already Exists Error

If repository already exists on GitHub:

```bash
# Add existing repository as remote
git remote add origin https://github.com/YOUR_USERNAME/PatternScope.git

# Pull existing content
git pull origin main --allow-unrelated-histories

# Push your changes
git push -u origin main
```

## Integration with Task Master

When using Task Master with Git:

```bash
# Reference tasks in commits
git commit -m "feat: implement JWT auth (task 1.2)"

# Create PR for completed task
task-master show 1.2  # Get task details
gh pr create --title "Complete task 1.2: User authentication" --body "$(task-master show 1.2)"

# Commit after completing subtask
task-master set-status --id=1.2.3 --status=done
git add .
git commit -m "feat: complete auth token validation (task 1.2.3)"
git push
```

## Quick Reference

```bash
# Setup (one-time)
git init
gh repo create PatternScope --public --source=. --remote=origin --push

# Daily workflow
git add .
git commit -m "feat: description"
git push

# Branch workflow
git checkout -b feature/name
# ... make changes ...
git push -u origin feature/name
gh pr create

# Sync with remote
git pull origin main
```

## Additional Resources

- [GitHub Documentation](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Quick Start Command Sequence:**

```bash
cd /Users/vimaleshvasu/Desktop/Apps/PatternScope
git init
git add .
git commit -m "Initial commit: PatternScope project setup"
gh repo create PatternScope --public --source=. --remote=origin --push
```

Your repository will be available at: `https://github.com/YOUR_USERNAME/PatternScope`
