---
title: "Setting Up SSO/SAML (Enterprise)"
category: admin
---
SSO is available on Enterprise plans and supports any SAML 2.0-compliant identity provider (Okta, Azure AD, OneLogin, Google Workspace, etc.).

Setup steps:
1. Admin Console → Security → SSO → "Configure SAML."
2. Copy the provided ACS URL and Entity ID into your identity provider's app configuration.
3. Upload your IdP's metadata XML (or enter the SSO URL and certificate manually) back into Nimbus AI.
4. Test with a single user in "SSO test mode" before enforcing it org-wide.
5. Enable "Require SSO" to disable password-based login for all org members.

Once enforced, existing members' passwords are deactivated — they must log in through the IdP. This does not affect API keys, which authenticate separately. SSO configuration changes can take up to 15 minutes to propagate.
