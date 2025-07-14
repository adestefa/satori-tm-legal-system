# Apple App-Specific Password Analysis - Official Requirements

Based on Apple Support Document: https://support.apple.com/en-us/102654

## 🔍 CRITICAL REQUIREMENTS FOR iCloud AUTHENTICATION

### Two-Factor Authentication Prerequisite
**REQUIREMENT**: Apple Account **must be protected with two-factor authentication**
- This is a **hard requirement** - no app-specific passwords without 2FA
- If 2FA is not enabled, app-specific passwords cannot be generated
- All authentication attempts will fail without proper 2FA setup

### App-Specific Password Limitations
- **Maximum**: 25 active app-specific passwords at a time
- **Usage**: Specifically for "apps made by non-Apple developers"
- **Security**: Prevents apps from storing primary Apple Account password

## 🚨 AUTOMATIC REVOCATION TRIGGERS

### When App-Specific Passwords Are Automatically Invalidated
1. **Primary Apple Account password is changed**
   - ALL existing app-specific passwords become invalid immediately
   - Must regenerate all app-specific passwords after password change
2. **Manual revocation** through account.apple.com

### Individual Password Management
- Can revoke individual passwords without affecting others
- Can revoke all passwords at once
- No notification when passwords are revoked

## 📋 CORRECT GENERATION PROCEDURE

### Official Steps from Apple
1. **Sign in to account.apple.com** (not appleid.apple.com as previously referenced)
2. **Navigate to**: "Sign-In and Security" section
3. **Select**: "App-Specific Passwords"
4. **Choose**: "Generate an app-specific password"
5. **Label**: Give it a descriptive name (e.g., "TM iCloud Sync")

### Authentication Usage
- **Method**: "Enter or paste the app-specific password into the password field"
- **Format**: Use exactly as generated (no modifications)
- **Field**: Replace normal password with app-specific password in authentication

## 🔧 TROUBLESHOOTING OUR SPECIFIC ISSUE

### Why Both Passwords May Be Invalid

#### Scenario 1: 2FA Not Properly Configured
- If 2FA was disabled/reconfigured, all app-specific passwords become invalid
- Need to verify 2FA status on Apple Account

#### Scenario 2: Primary Password Changed
- If the main Apple Account password was changed recently
- ALL app-specific passwords automatically revoked
- Both `zpcc-qsrx-saut-khph` and `gqlv-uvis-tvze-ofhg` would be invalid

#### Scenario 3: Manual Revocation
- Passwords were manually revoked for security reasons
- Individual passwords can be revoked without notification

#### Scenario 4: Account Security Review
- Apple may automatically revoke passwords during security reviews
- Common after suspicious activity or security incidents

## ✅ RESOLUTION STEPS

### 1. Verify 2FA Status
- Log into **account.apple.com** (not appleid.apple.com)
- Confirm two-factor authentication is active and properly configured
- If 2FA is disabled, enable it first

### 2. Check Existing App-Specific Passwords
- Navigate to "Sign-In and Security" → "App-Specific Passwords"
- See if any passwords are still listed as active
- Revoke any old/unused passwords to clean up the list

### 3. Generate Fresh Password
- Use the official procedure: "Generate an app-specific password"
- Label it clearly: "TM Legal Document Sync" or similar
- Copy the password exactly as provided (usually format: xxxx-xxxx-xxxx-xxxx)

### 4. Update Configuration
- Replace password in `/dashboard/config/settings.json`
- Use exact password format provided by Apple
- Do not modify or truncate the password

### 5. Test Authentication
- Wait 5-10 minutes after generation (Apple propagation time)
- Test through dashboard settings page
- Monitor for any 2FA prompts that may appear

## 🎯 LIKELY ROOT CAUSE ANALYSIS

### Based on Apple Error Code -20101
The error "Check the account information you entered and try again" combined with our findings suggests:

1. **Primary Apple Account password was changed** → All app-specific passwords invalidated
2. **2FA configuration changed** → Existing passwords no longer valid
3. **Security review** → Apple automatically revoked passwords

### Why Both Passwords Fail
Since both passwords show similar failure patterns, it's likely a **global invalidation event** (like primary password change) rather than individual password expiration.

## 📞 ADDITIONAL SUPPORT OPTIONS

### If Problems Persist
- **Apple Support**: Contact directly for account-specific issues
- **Account Recovery**: May be needed if 2FA is misconfigured
- **Security Review**: Check for any account security flags

### Verification Steps
1. **Can you log into account.apple.com with primary credentials?**
2. **Is 2FA properly configured and working?**
3. **Are there any security alerts or notifications?**
4. **When was the primary Apple Account password last changed?**

---

**CONCLUSION**: The authentication failure is consistent with Apple's automatic app-specific password revocation, likely triggered by a primary password change or security review. Following Apple's official regeneration procedure should resolve the issue.