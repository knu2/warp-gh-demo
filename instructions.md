
# Warp CLI + GitHub Actions: Full End-to-End Demo (AI Agent Instructions)

> Goal: Create a complete, runnable demo — from repo to GitHub Actions — that lets you trigger a Warp AI agent directly from a GitHub Issue comment using only `gh` CLI and Warp CLI. The agent will read the issue, analyze code, suggest fixes, and comment back — all automated.

You (AI Agent) will do everything step-by-step.
I (human) will only:
- Run `gh` commands you tell me
- Trigger the workflow by commenting `@warp-fix` on an issue
- Watch the magic

---

## Step 1: Create Demo Repository (Run Locally)

```bash
# Initialize git repo (if not already done)
git init
```

### Add a buggy Python app
```bash
cat > main.py << 'EOF'
def main():
    print("Hello, Warp!")
    x = int("42")  # Fine
    y = int("abc")  # ValueError!
    print(f"Result: {x + y}")

if __name__ == "__main__":
    main()
EOF
```

### Add README
```bash
cat > README.md << 'EOF'
# Warp CLI GitHub Actions Demo

This repo demonstrates how to:
- Run Warp AI agent in CI
- Let humans trigger AI via GitHub Issue comments
- Get AI-powered code fixes automatically

## How it works

1. Create an issue describing a bug
2. Comment `@warp-fix` on the issue
3. GitHub Actions triggers automatically
4. Warp AI agent analyzes the code and issue
5. Agent comments back with a fix

## Demo App

Simple Python app (`main.py`) with an intentional bug that causes a ValueError.
EOF
```

### Commit
```bash
git add .
git commit -m "feat: initial buggy Python app"
```

---

## Step 2: Push to GitHub (You Tell Me the Repo Name)

```bash
# Replace with your username or org
gh repo create warp-gh-demo --public --source=. --remote=origin --push
```

> **I run this** → Repo is now on GitHub: `https://github.com/YOUR_USER/warp-gh-demo`

---

## Step 3: Add Warp CLI GitHub Actions Workflow

```bash
mkdir -p .github/workflows
```

### Create `.github/workflows/warp-agent.yml`
```bash
cat > .github/workflows/warp-agent.yml << 'EOF'
name: Warp AI Agent (@warp-fix trigger)

on:
  issue_comment:
    types: [created]

jobs:
  warp-fix:
    # Only trigger on @warp-fix command
    if: |
      github.event_name == 'issue_comment' &&
      contains(github.event.comment.body, '@warp-fix')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    env:
      WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Warp CLI
        run: |
          # Add Warp package repository and install
          curl -fsSL https://releases.warp.dev/linux/keys/warp.asc | sudo gpg --dearmor -o /usr/share/keyrings/warp-archive-keyring.gpg
          echo "deb [arch=amd64 signed-by=/usr/share/keyrings/warp-archive-keyring.gpg] https://releases.warp.dev/linux/deb stable main" | sudo tee /etc/apt/sources.list.d/warp.list
          sudo apt update
          sudo apt install warp-cli -y
          which warp-cli || { echo "warp-cli not found"; exit 1; }

      - name: Run Warp Agent on Issue
        run: |
          ISSUE_NUMBER=${{ github.event.issue.number }}
          ISSUE_BODY=$(gh issue view $ISSUE_NUMBER --json body -q .body)
          COMMENT_BODY="${{ github.event.comment.body }}"
          
          PROMPT="Fix the bug in this Python code.
          
          Issue description: $ISSUE_BODY
          
          User comment: $COMMENT_BODY
          
          Analyze the code in main.py and provide a complete fixed version with proper exception handling."
          
          echo "Running Warp Agent..."
          warp-cli agent run \
            --prompt "$PROMPT" > warp-response.md
          
          cat warp-response.md

      - name: Comment Fix on Issue
        run: |
          gh issue comment ${{ github.event.issue.number }} --body-file warp-response.md
EOF
```

Key changes from original:
- Uses `issue_comment` trigger instead of labels
- Triggered by commenting `@warp-fix` on any issue
- Installs Warp CLI via official apt repository
- Uses `warp-cli` command (not `warp`)
- Removed MCP server/profile flags (use default agent)
- Adds `permissions: issues: write` for commenting
- Uses `GITHUB_TOKEN` (no need for custom PAT)

### Commit & Push
```bash
git add .github/workflows/warp-agent.yml
git commit -m "ci: add Warp AI agent on @warp-fix comment"
git push
```

---

## Step 4: Set Up Secrets

Go to: GitHub → Repo → Settings → Secrets and variables → Actions

Add this secret:

| Name | Value |
|------|-------|
| `WARP_API_KEY` | `wk-...` (from Warp Settings → Platform → API Keys) |

Note: No need for `GH_TOKEN` — the workflow uses the automatic `GITHUB_TOKEN`.

Or use `gh` CLI:
```bash
gh secret set WARP_API_KEY --body "wk-your-api-key-here" --repo YOUR_USER/warp-gh-demo
```

---

## Step 5: Create an Issue and Trigger the Agent

```bash
gh issue create \
  --title "Fix ValueError in main.py" \
  --body "The app crashes with: ValueError: invalid literal for int() with base 10: 'abc'. Please fix it with proper exception handling."
```

Then comment on the issue to trigger the agent:
```bash
gh issue comment 1 --body "@warp-fix"
```

> I run these → Issue created, then agent triggered by comment!

---

## Step 6: Watch GitHub Actions Run

1. Go to: GitHub → Actions tab
2. See job: Warp AI Agent (@warp-fix trigger)
3. Watch logs:
   - Warp CLI installs via apt
   - Agent reads issue + comment
   - Analyzes code
   - Generates fixed `main.py`
4. Agent comments back on the issue with the fix!

---

## Expected AI Comment on Issue

The agent will analyze the code and comment back with a fixed version, something like:

```python
def main():
    print("Hello, Warp!")
    x = int("42")
    try:
        y = int("abc")
    except ValueError:
        y = 0  # Default value on error
    print(f"Result: {x + y}")

if __name__ == "__main__":
    main()
```

> No human coding. Just comment `@warp-fix` → AI analyzes and fixes.

---

## Success! You Now Have:

| Feature | Done? |
|-------|-------|
| Demo repo with buggy code | Yes |
| Warp CLI in GitHub Actions | Yes |
| Trigger via `gh issue` + label | Yes |
| AI reads issue, fixes code | Yes |
| AI comments fix automatically | Yes |
| No manual coding | Yes |

---

## Next Steps (Tell Me Which to Do)

1. **Add PR creation** – AI opens PR with fix
2. **Support Python/JS** – multi-language detection
3. **Self-hosted runner** – pre-install Warp
4. **Warp Drive saved prompt** – reuse fix template
5. **Issue template** – `/fix` command in issue body

---

**Agent, your turn:**  
Run all the above **step-by-step**.  
Show me **each command** I need to run.  
When done, say:  
> **"Demo ready. Create the issue with `gh issue create --label warp-ai` to trigger AI fix."**

Let’s go.
