# Telegram CLI 🛩️

A tiny CLI for your own Telegram account (logs in over MTProto, sees what your
app sees). It currently does two things:

- **Look up IDs** — chat & user IDs for your groups, channels, and DMs.
- **Download history** — export a chat's full message history (and media) to disk.

## Setup

1. Get `api_id` + `api_hash` at https://my.telegram.org → **API development tools**.
2. Install and configure:
   ```bash
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt
   cp .env.example .env      # paste api_id + api_hash
   chmod +x tg
   ```
3. Log in once (needs a real terminal):
   ```bash
   ./tg whoami               # prompts for phone + code (+ 2FA)
   ```
   Cached in `tg.session` — a full-account credential, gitignored. Keep it private.

## Look up IDs

```bash
./tg whoami                          # your own account id
./tg list                            # every chat: id, type, @username, name
./tg list --type group supergroup    # filter by type
./tg resolve @somebody               # id/@username/title -> id + type + name
./tg members <id|@username|title>    # list a group's members
```

IDs use the Bot API "marked" form: users positive, groups `-<id>`,
supergroups/channels `-100<id>`.

## Download history

```bash
./tg history <id|@username|title>    # full history -> export/<id>/messages.jsonl
./tg history <id> --media            # also download photos/videos/docs
./tg history <id> --limit 500        # only the most recent 500
```

One JSON object per message (id, date, sender_id, text, reply/forward/media
markers), sorted by id (chronological); media goes to `export/<id>/media/`.
Re-running is idempotent — it skips saved messages, appends new ones, resumes
interrupted runs, and waits out rate limits. `export/` is gitignored.

## Notes

- Member lists are complete for basic groups and supergroups you admin; otherwise
  Telegram returns a partial list.
- `.env` and `tg.session` are secrets — never commit them.
