# Build Action Failure Analysis & Solutions

## Problem Summary

The GitHub Actions build is failing during the `npm run sources` step with the error:
```
Error connecting to datasource spoti: The incoming JSON object does not contain a client_email field
```

## Root Cause Analysis

### 1. **Primary Issue: Invalid GCP Credentials Format**
The `GCP_CREDENTIALS` secret in GitHub repository secrets is not properly formatted as a valid Google Cloud service account JSON key.

### 2. **Evidence of the Problem**
From the action logs, we can see:
- Google auth step succeeds: `Created credentials file at "/home/runner/work/evidence_test/evidence_test/gha-creds-2bb8adfb498f8356.json"`
- Service account is identified: `dreamlike@dreamlike-459719.iam.gserviceaccount.com`
- But Evidence BigQuery connector fails to parse the credentials

### 3. **Configuration Analysis**
- **Data Source**: BigQuery (`spoti` source)
- **Project**: `dreamlike-459719`
- **Dataset**: `test.spoti`
- **Authentication**: Service account (correct method)
- **Location**: EU (correct)

## Solutions

### Solution 1: Fix GCP_CREDENTIALS Secret (Recommended)

The `GCP_CREDENTIALS` secret must contain a complete, valid service account JSON key with the following structure:

```json
{
  "type": "service_account",
  "project_id": "dreamlike-459719",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "dreamlike@dreamlike-459719.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dreamlike%40dreamlike-459719.iam.gserviceaccount.com"
}
```

**Steps to fix:**
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Find the `dreamlike@dreamlike-459719.iam.gserviceaccount.com` service account
3. Create a new JSON key or download the existing one
4. Copy the **entire JSON content** (not just parts of it)
5. In GitHub repository → Settings → Secrets → Actions
6. Update the `GCP_CREDENTIALS` secret with the complete JSON

### Solution 2: Verify Service Account Permissions

Ensure the service account has the necessary permissions:
- **BigQuery Data Viewer** (to read data)
- **BigQuery Job User** (to run queries)
- **BigQuery User** (for dataset access)

### Solution 3: Alternative Authentication Method

If service account JSON continues to cause issues, consider using Workload Identity Federation:

```yaml
- id: 'auth'
  uses: 'google-github-actions/auth@v2'
  with:
    workload_identity_provider: 'projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/providers/PROVIDER_ID'
    service_account: 'dreamlike@dreamlike-459719.iam.gserviceaccount.com'
```

### Solution 4: Test Locally First

Before pushing changes, test the credentials locally:

```bash
# Set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Test the connection
npm run sources
```

## Verification Steps

After implementing Solution 1:

1. **Local Testing:**
   ```bash
   # Set environment variables to match GitHub Actions
   export EVIDENCE_SOURCE__spoti__authenticator=service-account
   export EVIDENCE_SOURCE__spoti__location=EU
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
   
   # Test sources
   npm run sources
   
   # Test build
   npm run build
   ```

2. **GitHub Actions Testing:**
   - Push a small change to trigger the action
   - Monitor the "Build Evidence Project" step
   - Look for successful completion of `npm run sources`

## Current Configuration Status

✅ **Correct Configuration:**
- Evidence config: `evidence.config.yaml` properly configured
- Package.json: Dependencies and build scripts correct
- Deploy workflow: Environment variables properly set
- Service account: Exists and appears to be accessible

❌ **Issue:**
- GCP_CREDENTIALS secret: Invalid or incomplete JSON format

## Expected Behavior After Fix

After implementing the solution, the build should:
1. ✅ Install dependencies
2. ✅ Authenticate with Google Cloud
3. ✅ Connect to BigQuery datasource
4. ✅ Execute `npm run sources` successfully
5. ✅ Execute `npm run build` successfully
6. ✅ Upload artifacts for deployment

## Additional Recommendations

1. **Add Error Handling**: Consider adding a fallback or more descriptive error handling in the workflow
2. **Environment Separation**: Use different service accounts for development and production
3. **Monitoring**: Set up alerts for build failures
4. **Documentation**: Document the credential setup process for team members

## Files Involved

- `.github/workflows/deploy.yaml` - GitHub Actions workflow
- `sources/spoti/connection.yaml` - BigQuery connection config
- `evidence.config.yaml` - Evidence configuration
- `package.json` - Build scripts and dependencies

The primary fix needed is updating the `GCP_CREDENTIALS` secret with a complete, valid service account JSON key.