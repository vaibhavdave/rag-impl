---
title: "Slack Integration Keeps Disconnecting"
category: troubleshooting
---
The Slack integration (Team/Enterprise only) uses an OAuth token that Slack workspace admins can revoke, and which expires automatically after 90 days of inactivity.

To reconnect: Admin Console → Integrations → Slack → Reconnect, then re-authorize in the Slack OAuth prompt. This does not affect message history already posted.

If it disconnects repeatedly (multiple times per week), the most common cause is a Slack workspace-level app-approval policy re-revoking third-party app tokens on a schedule — check with your Slack workspace admin whether Nimbus AI is on an allowlist, since this is a Slack-side workspace policy rather than a Nimbus AI issue.
