# Nimbus AI Helpdesk Assistant — User Guide

Your account-aware support assistant. It knows Nimbus AI's plans and policies, and — because you're logged in — it can look up *your* billing, usage, and (if you're an org admin) your team's seats to give you a real answer instead of a generic one.

---

## Getting started

1. Open the app and you'll land on the login screen.
2. Log in with your Nimbus AI account email and password.
3. You're in. Type a question in the chat box at the bottom and press Enter.

That's it — there's no separate "connect your account" step. The moment you're logged in, the assistant already has secure access to your own plan, billing, and usage data; it just never has access to anyone else's.

**Trying it out?** The login screen has a "Demo accounts" panel with several pre-loaded logins (password `NimbusDemo123!`), each already set up with a specific scenario — a duplicate charge, a near-maxed-out usage limit, an org with a seat that needs cleaning up, and so on. Great for seeing the assistant handle a real, specific situation rather than a hypothetical one.

---

## What can I ask it?

The assistant handles five kinds of requests well. Anything outside these, it'll tell you honestly and offer to connect you to a human agent rather than guessing.

### 1. Choosing or changing your plan

Ask it to compare plans, explain what changes on an upgrade or downgrade, or help you decide if it's time to move up a tier.

> **You:** I'm on Free and keep running out of messages by the afternoon. Worth upgrading?
> **Assistant:** Since you're consistently hitting the 20 messages/day cap on Free, Pro (500/day, plus file uploads and a much larger context window) would likely solve that immediately — upgrades take effect right away, and you're only charged a prorated amount for the rest of this cycle...

### 2. Billing questions

Ask about a specific charge, a possible duplicate, a failed payment, refund eligibility, or where to find an invoice. The assistant looks up your actual charges — it's not reciting a generic policy at you.

> **You:** I think I was charged twice this month.
> **Assistant:** I checked your billing history — you do have two $20.00 charges on the same date (July 31), both for the Pro subscription. That pattern matches a billing retry error, which is fully refundable. I can confirm this qualifies under our refund policy...

### 3. Usage and rate limits

Ask why you're being rate-limited, how many messages you have left, or when your limit resets. Answers are based on your actual current usage, not just "here's what the limits are."

> **You:** How many messages do I have left today?
> **Assistant:** You're at 498 of your 500 daily messages on Pro — 2 remaining. Your limit resets at [time], about 19 hours from now...

### 4. Technical/feature troubleshooting

File upload errors, a disconnected integration, API error codes, login trouble. These don't need any account lookup — just tell it what's going wrong.

> **You:** My file upload keeps failing.
> **Assistant:** A few common causes: files over 20MB (Pro/Team/Enterprise limit), unsupported formats (supported: PDF, DOCX, TXT, CSV, PNG, JPG), or a mid-upload network drop. Can you tell me the file size and format...

### 5. Org/team administration

*(Team and Enterprise admins only.)* Add or remove seats, ask about SSO setup, or check your org's seat roster.

> **You:** One of our employees left the company but still shows as an active seat.
> **Assistant:** I can see that seat in your org roster — it's still marked active. You (or another admin) can remove it from Admin Console → Members → Remove, which takes effect immediately...

If you ask for seat information and you're **not** an org admin, the assistant will tell you plainly that seat management requires an admin role, rather than pretending it can't find the data.

---

## Tips for getting a better answer

- **Be specific.** "I was charged twice" gets a much better answer than "there's a billing problem."
- **One topic at a time.** The assistant handles follow-ups fine within a conversation, but starting a new chat for an unrelated topic keeps things cleaner.
- **It won't ask who you are.** You're already authenticated — if it ever seems to be asking for an account number or "confirming your identity," that's a sign something's off, not a normal step.

## What it won't do

- It won't discuss or access any account other than the one you're logged into.
- It won't guess at policy it doesn't actually know — if something isn't covered, it'll say so and offer to hand you off to a human agent rather than making something up.
- It's not a general-purpose assistant — off-topic requests get politely declined.

## Logging out

Use the **Log out** button in the sidebar. This clears the current chat; logging back in starts a fresh conversation.
