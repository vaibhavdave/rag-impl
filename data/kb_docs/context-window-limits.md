---
title: "Context Window Limits by Plan"
category: usage
---
The context window is how much conversation history and uploaded file content the assistant can consider at once:

- Free: 30K tokens (~20 pages of text)
- Pro / Team / Enterprise: 200K tokens (~150 pages of text)

If a conversation exceeds the context window, the oldest messages are dropped from what the model can see (they remain visible in your chat history, just not "remembered" by the assistant). Uploading a file larger than the remaining context budget will cause the assistant to only read part of it — for large documents, splitting into sections or asking targeted questions performs better than pasting the entire document at once.
