# Vercel Integration for Test Reports

This document explains how to set up Vercel integration for automatically deploying Allure test reports.

## Required Secrets

You need to configure the following GitHub repository secrets:

### 1. VERCEL_TOKEN
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your profile → Settings → Tokens
3. Create a new token with appropriate scope
4. Copy the token and add it as `VERCEL_TOKEN` in GitHub repository secrets

### 2. VERCEL_PROJECT_ID
1. Create a new project on Vercel (can be empty initially)
2. Go to the project settings
3. Copy the Project ID from the General tab
4. Add it as `VERCEL_PROJECT_ID` in GitHub repository secrets

### 3. VERCEL_ORG_ID
1. Go to your Vercel team/organization settings
2. Copy the Team ID or Organization ID
3. Add it as `VERCEL_ORG_ID` in GitHub repository secrets

## How it works

1. **Test Execution**: All test matrix jobs run and generate Allure results
2. **Artifact Upload**: Each job uploads its Allure results as artifacts
3. **Report Generation**: After all tests complete, a separate job:
   - Downloads all artifacts
   - Merges them into a single allure-results directory  
   - Generates HTML report using Allure CLI
   - Deploys the report to Vercel

## Accessing Reports

Once deployed, the reports will be available at:
```
https://your-project-name.vercel.app
```

Each pull request will get its own deployment with a unique URL that will be shown in the GitHub Actions logs.

## Local Testing

To test the Allure integration locally:

```bash
# Install allure-pytest
pip install allure-pytest

# Run tests with allure
pytest --alluredir=allure-results tests/

# Generate HTML report (requires Allure CLI)
allure generate allure-results/ --clean -o allure-report/

# Serve the report locally
allure open allure-report/
```

## Troubleshooting

### Missing artifacts
- Check that the test jobs completed successfully
- Verify the `allure-results/` directory contains JSON files
- Ensure `--alluredir` path matches the artifact upload path

### Deployment failures
- Verify all three Vercel secrets are correctly set
- Check that the Vercel project exists and is accessible
- Review the GitHub Actions logs for detailed error messages

### Empty reports
- Ensure tests are actually running and generating results
- Check that allure-pytest is installed via tox deps
- Verify the allure-results directory structure