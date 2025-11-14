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

## Quick Start

### Try it yourself:

1. **Fork this repository**
2. **Set up your Warp API key**:
   ```bash
   gh secret set WARP_API_KEY --body "wk-your-api-key" --repo YOUR_USER/warp-gh-demo
   ```
3. **Create an issue** and comment `@warp-fix` to trigger the agent!

## Documentation

- **[GitHub Actions Setup Guide](./GITHUB_ACTIONS_SETUP.md)** - Complete guide for integrating Warp CLI in your workflows
- **[Issue Fix Prompt Template](./.github/warp_fix_prompt.md)** - Customize how the AI agent analyzes issues
- **[Original Instructions](./instructions.md)** - Step-by-step demo creation walkthrough

## Demo App

Simple Python app (`main.py`) with an intentional bug that causes a ValueError.

## Features

- ✅ **Issue Fixes with PR Creation** - Comment `@warp-fix` on issues, agent creates a PR with the fix
- ✅ **PR Reviews** - Comment `@warp-review` on pull requests for AI code reviews
- ✅ **Write Access** - Agent can edit files, create branches, and open PRs
- ✅ Structured prompt templates for better AI responses
- ✅ Automatic code analysis and fix suggestions
- ✅ Works on any issue or PR in the repository
- ✅ Production-ready workflow examples
