---
title: "API Error 429: Rate Limit Exceeded"
category: troubleshooting
---
A 429 response means your API key has exceeded its requests-per-minute or tokens-per-minute limit. This is independent of your subscription plan's chat message limit.

Fixes:
- Implement exponential backoff and retry (recommended: start at 1s, double up to 5 retries).
- Check Developer Console → API Keys → Usage to see your current tier's RPM/TPM caps.
- If you're consistently hitting limits under normal usage, your account may be eligible for a rate-limit tier increase — this requires a usage history review, requested from Developer Console → Request Limit Increase.

429s do not indicate a billing problem or a suspended account — no action is needed on your subscription to resolve this.
