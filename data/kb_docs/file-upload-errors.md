---
title: "Troubleshooting File Upload Errors"
category: troubleshooting
---
Common causes of file upload failures:

- **File too large**: Pro/Team/Enterprise support up to 20MB per file; Free does not support uploads at all. Compress or split larger files.
- **Unsupported format**: supported types are PDF, DOCX, TXT, CSV, PNG, and JPG. Other formats (e.g., .pages, .zip) will fail silently or show a generic error.
- **Network interruption mid-upload**: shows as "upload failed, please retry" — this is a transient client-side issue, not an account problem; retrying usually resolves it.
- **Context budget exceeded**: if your conversation already has a lot of history, there may not be enough context budget left for the file — start a new conversation and retry.

If none of these apply and the error persists across a new conversation, a different browser, and a smaller test file, this indicates a service-side issue and should be escalated with the exact error message and timestamp.
