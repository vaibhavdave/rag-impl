---
title: "Understanding Rate Limits"
category: usage
---
Each plan has a message cap that resets on a rolling daily window:

- Free: 20 messages/day
- Pro: 500 messages/day
- Team: 500 messages/day per seat, pooled across the org with a 20% shared buffer
- Enterprise: custom, set per contract

"Rate limit exceeded" means you've hit your plan's cap for the current window — it is not an error or account problem. The limit resets 24 hours after your first message in the current window, shown as a countdown in the app.

API usage has separate rate limits measured in requests-per-minute and tokens-per-minute, unrelated to your consumer subscription's message cap — see "API Usage vs. Subscription Usage."
