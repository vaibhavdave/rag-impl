---
title: "API Error 500: Internal Server Error"
category: troubleshooting
---
A 500 response indicates a transient service-side issue, not a problem with your request. Recommended handling:

- Retry with exponential backoff — most 500s resolve on retry within seconds.
- Check the status page for any ongoing incident before assuming it's specific to your account.
- If 500s persist for more than a few minutes across multiple requests, capture the `request-id` response header and the exact timestamp — this is required for support to investigate further.

500 errors are never caused by rate limits, billing status, or account configuration — those produce 429 or 403 responses respectively.
