# CI/CD Setup Guide

This guide explains how to set up continuous integration and deployment for the MeetWhenAh bot using GitHub Actions and Coolify.

## Overview

The CI/CD pipeline provides:

- **Automated Testing**: Runs tests on every push and pull request
- **Environment-Specific Deployments**: Staging and production deployments
- **Quality Gates**: Tests must pass before deployment
- **Automated Deployment**: Deploys to Coolify on successful tests

## Pipeline Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Push to       │    │   Push to       │    │   Push to       │
│   develop       │    │   main          │    │   any branch    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Run Tests     │    │   Run Tests     │    │   Run Tests     │
│   + Deploy to   │    │   + Deploy to   │    │   Only          │
│   Staging       │    │   Production    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Prerequisites

### 1. GitHub Repository
- Repository with the bot code
- GitHub Actions enabled
- Appropriate branch protection rules

### 2. Coolify Setup
- Coolify instance running
- Two projects: staging and production
- Webhook URLs for each project

### 3. Bot Configuration
- Development bot for local testing
- Staging bot (`meeting_the_stage_bot`)
- Production bot (`MeetWhenAhBot`)

### 4. Environment Setup
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
- **Branch**: `develop`
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
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

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
    if: github.ref == 'refs/heads/develop' && github.event_name == 'push'
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

1. **Push to `develop` branch**:
   - Runs tests
   - Deploys to staging (if tests pass)

2. **Push to `main` branch**:
   - Runs tests
   - Deploys to production (if tests pass)

3. **Pull Request to `main` or `develop`**:
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
feature/your-feature → develop → main
     ↓                   ↓        ↓
   Tests Only        Staging   Production
```

### Branch Protection

Recommended branch protection rules:

- **`main` branch**:
  - Require pull request reviews
  - Require status checks (tests must pass)
  - Require up-to-date branches

- **`develop` branch**:
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

2. **Deployment Failing**:
   - Verify Coolify webhook URLs
   - Check Coolify project configuration
   - Verify environment variables
   - Ensure environment files are properly configured

3. **Bot Not Responding**:
   - Check bot token validity
   - Verify webhook configuration
   - Check environment variables
   - See [Environment Configuration Guide](./environment-configuration.md) for setup help

4. **Environment Issues**:
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
