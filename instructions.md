
# Warp CLI + GitHub Actions: Full End-to-End Demo (AI Agent Instructions)

> **Goal:** Create a **complete, runnable demo** — from repo to GitHub Actions — that lets **you (the human)** trigger a **Warp AI agent** directly from a **GitHub Issue** using only `gh` CLI and Warp CLI.  
> The agent will **read the issue**, **analyze code**, **suggest fixes**, and **comment back** — all automated.

**You (AI Agent) will do everything step-by-step.**  
**I (human) will only:**  
- Run `gh` commands you tell me  
- Trigger the workflow from GitHub  
- Watch the magic

---

## Step 1: Create Demo Repository (Run Locally)

```bash
# Create and enter repo
mkdir warp-gh-demo && cd warp-gh-demo
git init

# Create a tiny Rust project (or use any language)
cargo init --bin --name demo-app
```

### Add a buggy `main.rs`
```bash
cat > src/main.rs << 'EOF'
fn main() {
    println!("Hello, Warp!");
    let x = "42".parse::<i32>().unwrap(); // Fine
    let y = "abc".parse::<i32>().unwrap(); // Panic!
    println!("Result: {}", x + y);
}
EOF
```

### Add README
```bash
cat > README.md << 'EOF'
# Warp CLI GitHub Actions Demo

This repo demonstrates how to:
- Run Warp AI agent in CI
- Let humans trigger AI via GitHub Issues
- Get AI-powered code fixes automatically
EOF
```

### Commit
```bash
git add .
git commit -m "feat: initial buggy Rust app"
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
name: Warp AI Agent (Issue Trigger)

on:
  issues:
    types: [opened, labeled]

jobs:
  run-warp-agent:
    if: contains(github.event.issue.labels.*.name, 'warp-ai')
    runs-on: ubuntu-latest
    env:
      WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
      GH_TOKEN: ${{ secrets.GH_TOKEN }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Warp CLI
        run: |
          curl -L https://releases.warp.dev/stable/linux-x86_64/warp-cli.tar.gz | tar -xz
          sudo mv warp-cli /usr/local/bin/warp
          warp --version

      - name: Install gh CLI
        run: |
          curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
          echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
          sudo apt update && sudo apt install gh -y

      - name: Run Warp Agent on Issue
        run: |
          ISSUE_BODY=$(gh issue view ${{ github.event.issue.number }} --json body -q .body)
          PROMPT="Fix the bug in this Rust code. Here's the error from CI and the issue: $ISSUE_BODY. Only edit src/main.rs. Return full fixed file."

          echo "Running Warp Agent..."
          warp agent run \
            --profile "hV6n5dNm7ThQVlOiPF8DLS" \
            --mcp-server "1deb1b14-b6e5-4996-ae99-233b7555d2d0" \
            --prompt "$PROMPT" > warp-response.md

          cat warp-response.md

      - name: Comment Fix on Issue
        run: |
          gh issue comment ${{ github.event.issue.number }} --body-file warp-response.md
EOF
```

### Commit & Push
```bash
git add .github/workflows/warp-agent.yml
git commit -m "ci: add Warp AI agent on labeled issues"
git push
```

---

## Step 4: Set Up Secrets (I Do This on GitHub)

Go to: **GitHub → Repo → Settings → Secrets and variables → Actions**

Add these secrets:

| Name | Value |
|------|-------|
| `WARP_API_KEY` | `wk-...` (from Warp Settings → API Keys) |
| `GH_TOKEN` | GitHub PAT with `repo` scope (or use default `GITHUB_TOKEN`) |

> **I do this manually** → Secrets are set.

---

## Step 5: Create a Trigger Issue (I Run This)

```bash
gh issue create \
  --title "Fix panic in main.rs" \
  --body "The app panics on startup with: thread 'main' panicked at 'called `Result::unwrap()` on an `Err` value'. Please fix it." \
  --label "warp-ai"
```

> **I run this** → Issue created with label `warp-ai`

---

## Step 6: Watch GitHub Actions Run

1. Go to: **GitHub → Actions tab**
2. See job: **Warp AI Agent (Issue Trigger)**
3. Watch logs:
   - Warp CLI installs
   - Agent reads issue
   - Analyzes code
   - Outputs fixed `main.rs`
4. **Agent comments back on the issue** with the fix!

---

## Expected AI Comment on Issue

```rust
// src/main.rs
fn main() {
    println!("Hello, Warp!");
    let x = "42".parse::<i32>().unwrap();
    let y = "abc".parse::<i32>().unwrap_or(0); // Fixed: use unwrap_or
    println!("Result: {}", x + y);
}
```

> **No human coding. Just label → AI fixes.**

---

## Bonus: One-Click Trigger (Reusable)

Save this alias:
```bash
alias warpfix='gh issue create --title "AI Fix" --body "Fix this bug with Warp AI" --label "warp-ai"'
```

Now just run:
```bash
warpfix
```
→ AI fixes code in CI → comments fix.

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
