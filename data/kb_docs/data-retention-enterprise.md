---
title: "Data Retention Policy (Enterprise)"
category: admin
---
Standard retention (Free/Pro/Team): deleted conversations and files are purged from active systems within 30 days; backups are purged within 90 days.

Enterprise supports custom retention, configured under Admin Console → Security → Data Retention:
- **Zero-retention mode**: conversation content is not stored beyond the active session at all, used only to generate the response.
- **Custom window**: retain conversations for a specified period (e.g., 1 year) for compliance/audit purposes, after which they're auto-purged.

Retention settings apply org-wide and take effect for new conversations going forward — they are not applied retroactively to content already stored under the previous policy. Changing retention settings requires Owner or admin role and is logged in the org's audit trail.
