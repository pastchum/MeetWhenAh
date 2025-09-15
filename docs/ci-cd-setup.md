# CI/CD Setup Guide

This guide explains how to set up continuous integration and deployment for the MeetWhenAh bot using GitHub Actions for testing, Coolify for bot deployment, and Vercel for webapp deployment.

## Overview

The CI/CD pipeline provides:

- **Automated Testing**: GitHub Actions runs tests on every push and pull request
- **Quality Gates**: Tests must pass before any deployment can proceed
- **Bot Deployment**: Coolify handles bot API deployment (staging and production)
- **Webapp Deployment**: Vercel handles webapp deployment (preview for staging, main for production)
- **Environment Isolation**: Separate staging and production environments with different bots and webapp URLs

## Pipeline Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Push to       │    │   GitHub        │    │   Coolify       │    │   Vercel        │
│   staging       │───▶│   Actions       │───▶│   (Bot API)     │───▶│   (Webapp)      │
│                 │    │   (Tests Only)  │    │   Staging       │    │   Preview       │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
│   Push to       │    │   GitHub        │    │   Coolify       │    │   Vercel        │
│   main          │───▶│   Actions       │───▶│   (Bot API)     │───▶│   (Webapp)      │
│                 │    │   (Tests Only)  │    │   Production    │    │   Main          │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Key Points:**
- **GitHub Actions**: Only runs tests, triggers Coolify if tests pass
- **Coolify**: Handles bot API deployment and hosting (manual trigger via webhook)
- **Vercel**: Handles webapp deployment (automatic on push, no webhook needed)
- **Deployment Order**: Tests → [Coolify + Vercel] deploy in parallel

## Component Roles

### GitHub Actions (Testing & Quality Gates)
- **Purpose**: Run automated tests on every push and pull request
- **What it does**: 
  - Installs dependencies
  - Runs pytest tests
  - Generates coverage reports
  - Triggers Coolify deployment if tests pass (via webhook)
- **What it doesn't do**: Deploy anything directly
- **Why webhook for Coolify?**: Coolify doesn't auto-deploy on push, needs manual trigger

### Coolify (Bot API Deployment)
- **Purpose**: Deploy and host the bot API
- **What it does**:
  - Builds the bot application
  - Runs tests (if configured in build command)
  - Deploys bot API to staging/production
  - Handles webhook endpoints
- **Environments**: Separate staging and production projects
- **Trigger**: Manual via webhook (GitHub Actions calls it)
- **Why manual?**: Coolify doesn't auto-deploy on GitHub push

### Vercel (Webapp Deployment)
- **Purpose**: Deploy and host the webapp
- **What it does**:
  - Automatically deploys webapp on push
  - Creates preview deployments for staging branch
  - Deploys to main URL for production branch
- **Environments**: 
  - Staging: `https://meet-when-ah-git-staging.vercel.app`
  - Production: `https://meet-when-ah.vercel.app`
- **Trigger**: Automatic on push (no webhook needed)
- **Why automatic?**: Vercel has built-in GitHub integration

## Detailed Deployment Flow

### When You Push to Staging

```
1. Push to staging branch
   ↓
2. GitHub Actions detects push
   ↓
3. GitHub Actions runs tests
   ↓
4. If tests FAIL:
   ├── ❌ GitHub Actions stops
   ├── ❌ Coolify never gets triggered
   └── ❌ Vercel never gets the push
   ↓
5. If tests PASS:
   ├── ✅ GitHub Actions calls Coolify webhook
   ├── ✅ Coolify starts deploying bot API
   ├── ✅ Vercel automatically detects push
   └── ✅ Vercel starts deploying webapp preview
   ↓
6. Both deployments happen in parallel
   ├── Coolify: Deploys bot API to staging
   └── Vercel: Deploys webapp to preview URL
```

### When You Push to Main

```
1. Push to main branch
   ↓
2. GitHub Actions detects push
   ↓
3. GitHub Actions runs tests
   ↓
4. If tests FAIL:
   ├── ❌ GitHub Actions stops
   ├── ❌ Coolify never gets triggered
   └── ❌ Vercel never gets the push
   ↓
5. If tests PASS:
   ├── ✅ GitHub Actions calls Coolify webhook
   ├── ✅ Coolify starts deploying bot API
   ├── ✅ Vercel automatically detects push
   └── ✅ Vercel starts deploying webapp to main
   ↓
6. Both deployments happen in parallel
   ├── Coolify: Deploys bot API to production
   └── Vercel: Deploys webapp to main URL
```

### Why This Setup?

**Quality Gates**: Tests must pass before any deployment
- **If tests fail**: Nothing deploys (safety!)
- **If tests pass**: Both Coolify and Vercel deploy

**Different Triggers**:
- **Coolify**: Manual trigger (webhook) - we control when it deploys
- **Vercel**: Automatic trigger (GitHub integration) - deploys on every push

**Parallel Deployment**: Both services deploy simultaneously after tests pass
- **Coolify**: Bot API (backend)
- **Vercel**: Webapp (frontend)

## Prerequisites

### 1. GitHub Repository
- Repository with the bot code
- GitHub Actions enabled
- Appropriate branch protection rules

### 2. Coolify Setup
- Coolify instance running
- Two projects: staging and production
- Webhook URLs for each project

### 3. Vercel Setup
- Vercel project connected to GitHub repository
- Preview deployments enabled for staging branch
- Automatic deployments for main branch

### 4. Bot Configuration
- Development bot for local testing
- Staging bot (`meeting_the_stage_bot`)
- Production bot (`MeetWhenAhBot`)

### 5. Environment Setup
Before setting up CI/CD, ensure you have:
- [Development environment configured](./development-setup.md)
- [Environment files created](./environment-configuration.md)
- Bot tokens and webhook URLs ready

## Setup Instructions

### 1. GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

```
STAGING_BOT_TOKEN=your_staging_bot_token_here
PRODUCTION_BOT_TOKEN=your_production_bot_token_here
COOLIFY_STAGING_WEBHOOK=https://your-coolify-staging-webhook-url
COOLIFY_PRODUCTION_WEBHOOK=https://your-coolify-production-webhook-url
```

### 2. Coolify Projects

#### Staging Project
- **Name**: `meetwhenah-staging`
- **Branch**: `staging`
- **Environment**: `staging`
- **Bot**: `meeting_the_stage_bot`

#### Production Project
- **Name**: `meetwhenah-production`
- **Branch**: `main`
- **Environment**: `production`
- **Bot**: `MeetWhenAhBot`

### 3. Environment Files

Create environment files in the `bot/` directory:

#### .env.staging
```bash
ENVIRONMENT=staging
BOT_USERNAME=meeting_the_stage_bot
TOKEN=your_staging_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-staging-domain.com/webhook
```

#### .env.production
```bash
ENVIRONMENT=production
BOT_USERNAME=MeetWhenAhBot
TOKEN=your_production_bot_token_here
WEBAPP_URL=https://meet-when-ah.vercel.app
USE_LOCAL_WEBAPP=false
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
USE_WEBHOOK=true
WEBHOOK_URL=https://your-production-domain.com/webhook
```

### 4. GitHub Actions Workflow

The workflow is already configured in `.github/workflows/ci-cd.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main, staging]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd bot
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd bot
          python -m pytest tests/ -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./bot/coverage.xml

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/staging' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Deploy to Staging
        env:
          ENVIRONMENT: staging
          BOT_USERNAME: meeting_the_stage_bot
          TOKEN: ${{ secrets.STAGING_BOT_TOKEN }}
          WEBAPP_URL: https://meet-when-ah.vercel.app
        run: |
          echo "🚀 Deploying to staging environment..."
          curl -X POST "${{ secrets.COOLIFY_STAGING_WEBHOOK }}"

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Deploy to Production
        env:
          ENVIRONMENT: production
          BOT_USERNAME: MeetWhenAhBot
          TOKEN: ${{ secrets.PRODUCTION_BOT_TOKEN }}
          WEBAPP_URL: https://meet-when-ah.vercel.app
        run: |
          echo "🚀 Deploying to production environment..."
          curl -X POST "${{ secrets.COOLIFY_PRODUCTION_WEBHOOK }}"
```

## Workflow Triggers

### Automatic Triggers

1. **Push to `staging` branch**:
   - Runs tests
   - Deploys to staging (if tests pass)

2. **Push to `main` branch**:
   - Runs tests
   - Deploys to production (if tests pass)

3. **Pull Request to `main` or `staging`**:
   - Runs tests only
   - No deployment

### Manual Triggers

You can also trigger deployments manually:

1. Go to Actions tab in GitHub
2. Select "CI/CD Pipeline"
3. Click "Run workflow"
4. Choose branch and environment

## Branch Strategy

### Development Workflow

```
feature/your-feature → staging → main
     ↓                   ↓        ↓
   Tests Only        Staging   Production
```

### Branch Protection

Recommended branch protection rules:

- **`main` branch**:
  - Require pull request reviews
  - Require status checks (tests must pass)
  - Require up-to-date branches

- **`staging` branch**:
  - Require status checks (tests must pass)
  - Allow force pushes for hotfixes

## Monitoring and Debugging

### GitHub Actions

- View workflow runs in the Actions tab
- Check logs for failed deployments
- Monitor test coverage reports

### Coolify

- Monitor deployment status in Coolify dashboard
- Check application logs
- Verify environment variables

### Bot Testing

- **Staging**: Test with `meeting_the_stage_bot`
- **Production**: Test with `MeetWhenAhBot`

## Troubleshooting

### Common Issues

1. **Tests Failing**:
   - Check test logs in GitHub Actions
   - Run tests locally: `cd bot && python -m pytest tests/ -v`
   - See [Testing Guide](./testing-guide.md) for detailed test information
   - **Result**: Nothing deploys (safety feature)

2. **Coolify Deployment Failing**:
   - Verify Coolify webhook URLs in GitHub Secrets
   - Check Coolify project configuration
   - Ensure bot tokens are valid
   - **Result**: Bot API doesn't deploy, but Vercel still deploys

3. **Vercel Deployment Failing**:
   - Check Vercel project settings
   - Verify GitHub integration
   - Check build logs in Vercel dashboard
   - **Result**: Webapp doesn't deploy, but Coolify still deploys

4. **Bot Not Responding**:
   - Check bot token validity
   - Verify webhook configuration
   - Check environment variables
   - See [Environment Configuration Guide](./environment-configuration.md) for setup help

### Understanding Deployment Status

**Both Deploy Successfully**:
- ✅ Tests pass
- ✅ Coolify deploys bot API
- ✅ Vercel deploys webapp
- ✅ Everything works

**Only Vercel Deploys**:
- ✅ Tests pass
- ❌ Coolify webhook fails
- ✅ Vercel deploys webapp
- ⚠️ Bot API not updated

**Only Coolify Deploys**:
- ✅ Tests pass
- ✅ Coolify deploys bot API
- ❌ Vercel deployment fails
- ⚠️ Webapp not updated

**Nothing Deploys**:
- ❌ Tests fail
- ❌ Coolify never triggered
- ❌ Vercel never gets push
- ✅ Safety feature working

5. **Environment Issues**:
   - Verify `.env` files are created correctly
   - Check that all required variables are set
   - See [Development Setup Guide](./development-setup.md) for local setup

### Debug Commands

```bash
# Run tests locally
cd bot
python -m pytest tests/ -v

# Check environment variables
python -c "import os; print(os.environ.get('ENVIRONMENT'))"

# Test URL generation
python -c "from utils.mini_app_url import get_mini_app_url; print(get_mini_app_url('test'))"
```

## Security Considerations

- Never commit `.env` files
- Use GitHub Secrets for sensitive data
- Rotate bot tokens regularly
- Restrict staging bot access
- Monitor deployment logs
- Use HTTPS for all webhooks

## Best Practices

1. **Always test locally** before pushing
2. **Use feature branches** for new features
3. **Write tests** for new functionality
4. **Monitor deployments** after pushing
5. **Keep staging and production** in sync
6. **Document changes** in commit messages
