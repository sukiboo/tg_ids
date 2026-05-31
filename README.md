# Telegram ID lookup CLI 🛩️

A tiny CLI for looking up Telegram **chat IDs** and **user IDs** — for your own
groups, channels, and DMs. It logs in as your user account over MTProto, so it sees everything your Telegram app sees.

## Setup

1. Get API credentials at https://my.telegram.org → **API development tools** →
   create an app (any title/platform — the fields are cosmetic). Copy the
   `api_id` and `api_hash`.

2. Install dependencies and configure:

   ```bash
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt

   cp .env.example .env          # then edit .env: paste api_id + api_hash
   chmod +x tg
   ```

3. Log in (first run only, needs a real terminal):

   ```bash
   ./tg whoami                   # prompts for phone + login code (+ 2FA if set)
   ```

   The login is cached in `tg.session` — a full-account credential. Keep it
   private (it's gitignored). Revoke anytime in Telegram → Settings → Devices.

## Usage

```bash
./tg whoami                      # your own account id
./tg list                        # every chat: id, type, @username, name
./tg list --type group supergroup
./tg resolve @somebody           # id/@username/title -> id + type + name
./tg members <id|@username|title>
```

IDs are returned in the "marked" form the Bot API uses: users positive, basic
groups `-<id>`, supergroups/channels `-100<id>`.

## Using this with your own account

This tool ships with **no credentials** — register your own app and bring your
own. The `api_id`/`api_hash` identify the *application*, not a user: you log in
as yourself with `./tg whoami`, and the tool only ever sees *your* groups and
DMs. Just put your two values in `.env` (gitignored):

| Key           | Purpose                     |
| ------------- | --------------------------- |
| `TG_API_ID`   | API id from my.telegram.org |
| `TG_API_HASH` | API hash from my.telegram.org |

## Notes

- Member listing is complete for basic groups and for supergroups where you're
  an admin. For large supergroups where you're not an admin, Telegram returns a
  partial list.
- The `.session` file is a live credential and is gitignored — keep it private.
- Output is printed to stdout only; redirect it yourself if you want a file
  (e.g. `./tg members <id> > members.txt`).
