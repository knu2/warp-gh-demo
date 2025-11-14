# Warp CLI GitHub Actions Demo

This repo demonstrates how to:
- Run Warp AI agent in CI
- Let humans trigger AI via GitHub Issues
- Get AI-powered code fixes automatically

## How it works

1. Create an issue with the `warp-ai` label
2. GitHub Actions triggers automatically
3. Warp AI agent analyzes the code and issue
4. Agent comments back with a fix

## Demo App

Simple Python app (`main.py`) with an intentional bug that causes a ValueError.
