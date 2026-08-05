---
title: "Trouble Logging In"
category: troubleshooting
---
If you can't log in:

- **"Invalid credentials"**: double-check for extra whitespace or autofill errors; use "Forgot Password" rather than retrying repeatedly, as repeated failed attempts temporarily lock the account for 15 minutes after 5 failures.
- **Locked out after failed attempts**: wait 15 minutes, or use "Forgot Password" to reset immediately regardless of lock state.
- **SSO users (Enterprise)**: if your identity provider session expired, log out of the IdP and back in; a Nimbus-specific password reset does nothing for SSO-managed accounts since Nimbus never stores the password.
- **"Account not found"**: confirm you're using the email your organization registered — some users have both a personal Free account and a work Enterprise account under different emails.

Persistent login failures after a password reset should be escalated with the account email and approximate time of the failed attempts.
