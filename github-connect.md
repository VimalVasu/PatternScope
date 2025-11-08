# Connect Local Repository to GitHub

Follow these commands to connect your local PatternScope repository to GitHub.

## Step 0: Remove Existing Remote (if any)

If you need to start from scratch, first check if a remote exists:

```bash
git remote -v
```

If you see an existing `origin`, remove it:

```bash
git remote remove origin
```

Verify it's removed:

```bash
git remote -v
```

(Should show nothing)

## Step 1: Create GitHub Repository (if not already created)

Go to [github.com](https://github.com) and create a new repository named `PatternScope`.
- Do NOT initialize it with README, .gitignore, or license (since you already have a local repo)

## Step 2: Add Remote Origin

Replace `YOUR_USERNAME` with your actual GitHub username:

```bash
git remote add origin https://github.com/VimalVasu/PatternScope.git
```

Or if you prefer SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/PatternScope.git
```

## Step 3: Verify Remote

Check that the remote was added correctly:

```bash
git remote -v
```

You should see:
```
origin  https://github.com/YOUR_USERNAME/PatternScope.git (fetch)
origin  https://github.com/YOUR_USERNAME/PatternScope.git (push)
```

## Step 4: Pull Existing Files from GitHub

Since the GitHub repo already has files, pull them first:

```bash
git pull origin main --allow-unrelated-histories --no-rebase
```

The flags mean:
- `--allow-unrelated-histories`: Allows merging repos with different histories
- `--no-rebase`: Uses merge strategy (instead of rebase) to combine the branches

### If you get merge conflicts:
1. Git will tell you which files have conflicts
2. Open those files and resolve conflicts (look for `<<<<<<<`, `=======`, `>>>>>>>` markers)
3. After resolving:
```bash
git add .
git commit -m "Merge remote repository"
```

## Step 5: Push to GitHub

Now push your local changes to GitHub:

```bash
git push -u origin main
```

The `-u` flag sets up tracking so future pushes can be done with just `git push`.

## Troubleshooting

### If you get a "repository already exists" error:
The remote might already be configured. Check with:
```bash
git remote -v
```

Remove existing remote if needed:
```bash
git remote remove origin
```

Then re-add it with Step 2.

### If you have uncommitted changes:
First commit or stash your changes:
```bash
git status
git add .
git commit -m "Your commit message"
```

Then proceed with push.

### Authentication Issues:
- For HTTPS: You'll need a Personal Access Token (not password)
  - Generate at: GitHub Settings → Developer settings → Personal access tokens
- For SSH: Set up SSH keys first
  - Guide: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
