# KeyCRM Telegram Bot

This project replaces the exported n8n workflow `KeyCRM Get Order + Buyer`.

Flow implemented in Python:

1. Wait for the Telegram command `/spisok`
2. Fetch orders from KeyCRM with `filter[status_id]=2`
3. Aggregate product quantities by `sku`
4. Insert an empty line when the SKU prefix before `_` changes
5. Send the formatted report back to Telegram

## Configuration

Copy `.env.example` to `.env` and fill in the secrets:

```env
TELEGRAM_BOT_TOKEN=...
KEYCRM_API_TOKEN=...
TELEGRAM_TARGET_CHAT_ID=
```

If `TELEGRAM_TARGET_CHAT_ID` is empty, the bot replies to the chat that triggered `/spisok`.

## Local run

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

## Docker

Build and run:

```bash
docker compose up --build -d
```

## Deploy On Hostinger VPS

This bot does not need Traefik because it uses Telegram long polling and does not expose an HTTP port.

If your VPS already runs a shared `docker-compose.yml` with `traefik`, `n8n`, and `n8n_test`, add one more service:

```yaml
  keycrm_bot:
    build: /opt/keycrm-bot
    container_name: keycrm_bot
    restart: always
    env_file:
      - /opt/keycrm-bot/.env
```

Example full flow on the server:

```bash
sudo mkdir -p /opt/keycrm-bot
cd /opt/keycrm-bot
```

Copy the project files there, create `.env`, then run:

```bash
docker compose up -d --build keycrm_bot
```

Useful commands:

```bash
docker compose logs -f keycrm_bot
docker compose ps
docker compose restart keycrm_bot
```

If you keep the bot in a separate folder with its own compose file, deployment is even simpler:

```bash
cd /opt/keycrm-bot
cp .env.example .env
docker compose up -d --build
```

## Notes

- The app reads credentials only from environment variables and does not hardcode the values from the n8n export.
- Pagination is handled across multiple KeyCRM pages instead of being limited to page 1 only.
- Telegram messages are split into chunks if the report exceeds Telegram message limits.
- The KeyCRM bearer token from the exported n8n workflow should be rotated because it was embedded in the JSON export.
