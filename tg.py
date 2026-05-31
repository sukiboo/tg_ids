import os
import sys
import argparse

from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel

HERE = os.path.dirname(os.path.abspath(__file__))
SESSION = os.path.join(HERE, "tg.session")


def load_env():
    path = os.path.join(HERE, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def make_client():
    api_id = os.environ.get("TG_API_ID")
    api_hash = os.environ.get("TG_API_HASH")
    if not api_id or not api_hash:
        sys.exit("Missing TG_API_ID / TG_API_HASH. Copy .env.example to .env and fill them in.")
    return TelegramClient(SESSION, int(api_id), api_hash)


def entity_type(ent):
    if isinstance(ent, User):
        if ent.deleted:
            return "deleted"
        return "bot" if ent.bot else "user"
    if isinstance(ent, Chat):
        return "group"
    if isinstance(ent, Channel):
        return "supergroup" if ent.megagroup else "channel"
    return type(ent).__name__.lower()


def display_name(ent):
    if isinstance(ent, User):
        return " ".join(x for x in (ent.first_name, ent.last_name) if x) or ""
    return getattr(ent, "title", "") or ""


def resolve_target(client, target):
    target = target.strip()
    if target.startswith("@"):
        return client.get_entity(target)
    as_int = None
    try:
        as_int = int(target)
    except ValueError:
        pass
    if as_int is not None:
        try:
            return client.get_entity(as_int)
        except (ValueError, TypeError):
            pass
    matches = []
    for d in client.iter_dialogs():
        if as_int is not None:
            if d.id == as_int or getattr(d.entity, "id", None) == abs(as_int):
                return d.entity
        elif target.lower() in (d.name or "").lower():
            matches.append(d)
    if as_int is not None:
        sys.exit(f"No chat with id {target} found in your dialogs.")
    if not matches:
        sys.exit(f"No chat found matching id/username/title: {target!r}")
    if len(matches) > 1:
        print(f"Ambiguous — {len(matches)} matches for {target!r}:")
        for d in matches:
            print(f"  {d.id:>15}  {entity_type(d.entity):<11}  {d.name}")
        sys.exit("Re-run with the exact id.")
    return matches[0].entity


def cmd_whoami(client, args):
    me = client.get_me()
    print(f"id:        {me.id}")
    print(f"username:  @{me.username}" if me.username else "username:  (none)")
    print(f"name:      {display_name(me)}")
    print(f"phone:     +{me.phone}" if me.phone else "phone:     (hidden)")


def cmd_list(client, args):
    rows = []
    for d in client.iter_dialogs():
        ent = d.entity
        t = entity_type(ent)
        if args.type and t not in args.type:
            continue
        rows.append({
            "id": d.id,
            "type": t,
            "username": getattr(ent, "username", None) or "",
            "name": d.name or "",
        })
    print(f"\n{len(rows)} chats\n")
    print(f"{'id':>15}  {'type':<11}  {'username':<22}  name")
    print("-" * 80)
    for r in rows:
        uname = ("@" + r["username"]) if r["username"] else ""
        print(f"{r['id']:>15}  {r['type']:<11}  {uname:<22}  {r['name']}")


def cmd_members(client, args):
    entity = resolve_target(client, args.chat)
    title = display_name(entity)
    cid = getattr(entity, "id", "")
    users = client.get_participants(entity)
    rows = []
    for u in users:
        rows.append({
            "id": u.id,
            "username": u.username or "",
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "bot": bool(getattr(u, "bot", False)),
            "deleted": bool(getattr(u, "deleted", False)),
        })
    rows.sort(key=lambda r: (r["bot"], r["first_name"].lower(), r["id"]))
    print(f"\n{title}  (id {cid}) — {len(rows)} participants\n")
    print(f"{'id':>12}  {'username':<22}  name")
    print("-" * 60)
    for r in rows:
        name = (r["first_name"] + " " + r["last_name"]).strip()
        uname = ("@" + r["username"]) if r["username"] else ""
        tag = " [bot]" if r["bot"] else (" [deleted]" if r["deleted"] else "")
        print(f"{r['id']:>12}  {uname:<22}  {name}{tag}")


def cmd_resolve(client, args):
    ent = resolve_target(client, args.target)
    print(f"id:        {getattr(ent, 'id', '')}")
    print(f"type:      {entity_type(ent)}")
    uname = getattr(ent, "username", None)
    print(f"username:  @{uname}" if uname else "username:  (none)")
    print(f"name:      {display_name(ent)}")


def build_parser():
    p = argparse.ArgumentParser(prog="tg", description="Look up Telegram chat and user IDs.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami", help="show your own account id").set_defaults(func=cmd_whoami)

    pl = sub.add_parser("list", help="list all chats (DMs, groups, channels) with ids")
    pl.add_argument("--type", nargs="+",
                    choices=["user", "bot", "group", "supergroup", "channel", "deleted"],
                    help="filter by chat type")
    pl.set_defaults(func=cmd_list)

    pm = sub.add_parser("members", help="list members of a group by id/@username/title")
    pm.add_argument("chat", help="chat id, @username, or part of the title")
    pm.set_defaults(func=cmd_members)

    pr = sub.add_parser("resolve", help="resolve an id/@username/title to id+type+name")
    pr.add_argument("target", help="chat/user id, @username, or part of a title")
    pr.set_defaults(func=cmd_resolve)

    return p


def main():
    load_env()
    args = build_parser().parse_args()
    with make_client() as client:
        args.func(client, args)


if __name__ == "__main__":
    main()
