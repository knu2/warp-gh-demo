# Setting Up Warp CLI Agent in GitHub Actions

This guide walks you through integrating Warp AI agents into your GitHub Actions workflows for automated code analysis and fixes.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation in CI](#installation-in-ci)
- [Authentication](#authentication)
- [Configuration](#configuration)
- [Workflow Examples](#workflow-examples)
- [Model Selection](#model-selection)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

1. **Warp Account**: Sign up at [warp.dev](https://warp.dev)
2. **API Key**: Generate one in Warp Settings → Platform → API Keys
3. **GitHub Repository**: With Actions enabled

---

## Installation in CI

### Ubuntu/Debian (GitHub Actions default)

Add this step to install Warp CLI:

```yaml
- name: Install Warp CLI
  run: |
    # Add Warp package repository
    curl -fsSL https://releases.warp.dev/linux/keys/warp.asc | sudo gpg --dearmor -o /usr/share/keyrings/warp-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/warp-archive-keyring.gpg] https://releases.warp.dev/linux/deb stable main" | sudo tee /etc/apt/sources.list.d/warp.list
    sudo apt update
    sudo apt install warp-cli -y
    which warp-cli || { echo "warp-cli not found"; exit 1; }
```

**Note**: The package installs as `warp-cli`, but on some systems the binary is `warp`.

### macOS (Self-hosted runners)

```yaml
- name: Install Warp CLI
  run: |
    brew tap warpdotdev/warp
    brew install --cask warp-cli
    warp --version
```

---

## Authentication

### 1. Generate API Key

1. Go to Warp Settings → Platform → API Keys
2. Click "Create API Key"
3. Copy the key (format: `wk-1.xxxxx...`)

### 2. Add to GitHub Secrets

**Via GitHub UI:**
- Go to: Repository → Settings → Secrets and variables → Actions
- Click "New repository secret"
- Name: `WARP_API_KEY`
- Value: Your API key

**Via GitHub CLI:**
```bash
gh secret set WARP_API_KEY --body "wk-1.your-api-key-here" --repo YOUR_USER/YOUR_REPO
```

### 3. Use in Workflow

```yaml
env:
  WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
```

The Warp CLI automatically reads this environment variable.

---

## Configuration

### Basic Agent Command

```bash
warp-cli agent run --prompt "Your prompt here"
```

### Available Options

```bash
warp agent run [OPTIONS] <--prompt <PROMPT>|--saved-prompt <SAVED_PROMPT>>

Options:
  --prompt <PROMPT>              # Main prompt for the agent
  --saved-prompt <ID>            # Use a pre-saved prompt by ID
  --profile <ID>                 # Agent profile (controls model, permissions)
  --mcp-server <UUID>            # MCP server UUIDs to enable
  --output-format <FORMAT>       # json or text (default: text)
  --cwd <PATH>                   # Working directory
  --share [<RECIPIENTS>]         # Share session with team/users
  --api-key <API_KEY>            # API key (or use WARP_API_KEY env var)
  --debug                        # Enable debug logging
```

---

## Workflow Examples

### Example 1: Issue Comment Trigger

```yaml
name: Warp AI Fix

on:
  issue_comment:
    types: [created]

jobs:
  warp-fix:
    if: contains(github.event.comment.body, '@warp-fix')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write
    env:
      WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Warp CLI
        run: |
          curl -fsSL https://releases.warp.dev/linux/keys/warp.asc | sudo gpg --dearmor -o /usr/share/keyrings/warp-archive-keyring.gpg
          echo "deb [arch=amd64 signed-by=/usr/share/keyrings/warp-archive-keyring.gpg] https://releases.warp.dev/linux/deb stable main" | sudo tee /etc/apt/sources.list.d/warp.list
          sudo apt update && sudo apt install warp-cli -y
      
      - name: Run Warp Agent
        run: |
          ISSUE_BODY=$(gh issue view ${{ github.event.issue.number }} --json body -q .body)
          warp-cli agent run \
            --prompt "Analyze and fix: $ISSUE_BODY" \
            > response.md
      
      - name: Comment Response
        run: gh issue comment ${{ github.event.issue.number }} --body-file response.md
```

### Example 2: Pull Request Comment-Triggered Review

**Recommended approach** - See `.github/workflows/warp-review.yml` for a complete implementation.

```yaml
name: Warp AI Code Review

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]

jobs:
  warp-review:
    if: |
      (
        github.event_name == 'issue_comment' ||
        github.event_name == 'pull_request_review_comment'
      ) &&
      contains(github.event.comment.body, '@warp-review')
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    env:
      WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Install Warp CLI
        run: |
          curl -fsSL https://releases.warp.dev/linux/keys/warp.asc | sudo gpg --dearmor -o /usr/share/keyrings/warp-archive-keyring.gpg
          echo "deb [arch=amd64 signed-by=/usr/share/keyrings/warp-archive-keyring.gpg] https://releases.warp.dev/linux/deb stable main" | sudo tee /etc/apt/sources.list.d/warp.list
          sudo apt update && sudo apt install warp-cli -y
      
      - name: Get PR Details and Run Review
        run: |
          if [ "${{ github.event_name }}" == "issue_comment" ]; then
            PR_NUMBER="${{ github.event.issue.number }}"
          else
            PR_NUMBER="${{ github.event.pull_request.number }}"
          fi
          
          PR_DIFF=$(gh pr diff $PR_NUMBER)
          
          warp-cli agent run \
            --prompt "Review this PR. Diff: $PR_DIFF" \
            > review.md
      
      - name: Post Review
        run: |
          if [ "${{ github.event_name }}" == "issue_comment" ]; then
            gh pr comment ${{ github.event.issue.number }} --body-file review.md
          else
            gh pr comment ${{ github.event.pull_request.number }} --body-file review.md
          fi
```

### Example 3: Scheduled Code Audit

```yaml
name: Weekly Code Audit

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    env:
      WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Warp CLI
        run: |
          curl -fsSL https://releases.warp.dev/linux/keys/warp.asc | sudo gpg --dearmor -o /usr/share/keyrings/warp-archive-keyring.gpg
          echo "deb [arch=amd64 signed-by=/usr/share/keyrings/warp-archive-keyring.gpg] https://releases.warp.dev/linux/deb stable main" | sudo tee /etc/apt/sources.list.d/warp.list
          sudo apt update && sudo apt install warp-cli -y
      
      - name: Run Security Audit
        run: |
          warp-cli agent run \
            --prompt "Audit this codebase for security vulnerabilities and code quality issues" \
            --output-format json \
            > audit-report.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: security-audit
          path: audit-report.json
```

---

## Model Selection

### How Models are Configured

Warp CLI uses **Agent Profiles** to configure model settings. You cannot specify a model directly via CLI flags.

### Available Models

- **OpenAI**: GPT-5 (low, medium, high reasoning modes)
- **Anthropic**: Claude Sonnet 4.5, Claude Opus 4.1, Claude Haiku 4.5, Claude Sonnet 4
- **Google**: Gemini 2.5 Pro
- **Auto (Cost-efficient)**: Optimizes for lower credit consumption
- **Auto (Responsiveness)**: Prioritizes highest quality/fastest model

### Configure Model via Profiles

#### 1. Create/Edit Profile in Warp UI

1. Open Warp Settings → AI → Agents → Profiles
2. Edit "Default" profile or create a new one
3. Set **Base Model** (for main tasks)
4. Set **Planning Model** (for complex reasoning)
5. Note the Profile ID (e.g., `hV6n5dNm7ThQVlOiPF8DLS`)

#### 2. Use Profile in Workflow

```yaml
- name: Run Warp Agent with Custom Profile
  run: |
    warp-cli agent run \
      --profile "hV6n5dNm7ThQVlOiPF8DLS" \
      --prompt "Your task here"
```

#### 3. Default Behavior

If you don't specify `--profile`, Warp uses your **default profile**'s model configuration.

### Best Practice for CI/CD

For consistent CI/CD behavior:
1. Create a dedicated profile for GitHub Actions (e.g., "CI Agent")
2. Configure it with a specific model (not Auto)
3. Use `--profile <ID>` in your workflows
4. Document the profile ID in your team's setup guide

---

## Best Practices

### Security

1. **Never commit API keys** - always use GitHub Secrets
2. **Use read-only permissions** where possible
3. **Limit workflow triggers** to avoid abuse
4. **Review agent output** before acting on it

### Performance

1. **Cache Warp CLI installation** for self-hosted runners
2. **Use `--output-format json`** for programmatic parsing
3. **Set reasonable timeouts** to avoid runaway costs
4. **Use specific prompts** - vague prompts waste credits

### Reliability

1. **Add error handling** around agent calls
2. **Check for empty responses** before posting comments
3. **Log agent interactions** for debugging
4. **Test locally** with `warp-cli` before deploying

### Cost Management

1. **Use Auto (Cost-efficient)** for routine tasks
2. **Reserve premium models** for complex problems
3. **Set up usage alerts** in Warp dashboard
4. **Audit workflow runs** regularly

---

## Troubleshooting

### Issue: `warp-cli: command not found`

**Solution**: Check if the binary is named `warp` instead:
```bash
which warp || which warp-cli
```

Use the correct command name in your workflow.

### Issue: `Error: Requested MCP server not found`

**Cause**: Invalid or non-existent MCP server UUID

**Solution**: 
1. List available MCP servers: `warp mcp list`
2. Use valid UUIDs or remove `--mcp-server` flag

### Issue: `Error: Authentication failed`

**Cause**: Invalid or missing API key

**Solution**:
1. Verify secret is set: `gh secret list`
2. Check API key is valid in Warp Settings
3. Ensure env var is passed to step:
   ```yaml
   env:
     WARP_API_KEY: ${{ secrets.WARP_API_KEY }}
   ```

### Issue: `Error: Requested profile not found`

**Cause**: Invalid profile ID

**Solution**:
1. Remove `--profile` flag to use default
2. Verify profile ID in Warp Settings → AI → Agents → Profiles
3. Ensure the profile belongs to the authenticated account

### Issue: Workflow doesn't trigger

**Cause**: Workflow YAML syntax error or incorrect trigger

**Solution**:
1. Check Actions tab for workflow syntax errors
2. Validate YAML with: `gh workflow view`
3. Ensure trigger conditions are met

### Issue: Agent responses are truncated

**Cause**: Large output exceeding GitHub comment limits

**Solution**:
1. Use artifacts for large outputs:
   ```yaml
   - name: Upload Response
     uses: actions/upload-artifact@v4
     with:
       name: warp-response
       path: response.md
   ```
2. Summarize responses before posting

---

## Example: Complete Production Workflows

This repository includes two complete, production-ready workflows:

### 1. Issue Fix Workflow (`.github/workflows/warp-agent.yml`)
- Comment-based triggering with `@warp-fix` on issues
- Structured prompt template (`.github/warp_fix_prompt.md`)
- Automated bug analysis and fix suggestions
- Posts fix as issue comment

### 2. PR Review Workflow (`.github/workflows/warp-review.yml`)
- Comment-based triggering with `@warp-review` on PRs
- Comprehensive code review template (`.github/warp_review_prompt.md`)
- Fetches PR diff and analyzes changes
- Posts structured review as PR comment

Both workflows include:
- Error handling
- Proper permissions
- GitHub context integration
- Response formatting

---

## Additional Resources

- [Warp CLI Documentation](https://docs.warp.dev/developers/cli)
- [Warp Agent Profiles](https://docs.warp.dev/agents/using-agents/agent-profiles-permissions)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [This Demo Repository](https://github.com/knu2/warp-gh-demo)

---

## Support

For issues specific to:
- **Warp CLI**: [Warp Support](https://docs.warp.dev)
- **GitHub Actions**: [GitHub Community](https://github.com/community)
- **This Demo**: [Open an issue](https://github.com/knu2/warp-gh-demo/issues)
