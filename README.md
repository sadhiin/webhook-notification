# Notification Webhooks System

A simple real-time notification demo using FastAPI, PostgreSQL and WebSockets. The
project demonstrates a webhook-based integration where a main app forwards
messages to a provider simulator, which then calls back via a webhook to update
message status. The UI receives live updates over a WebSocket connection.

## Architecture

The repo contains three cooperating components:

- **notifier-ui**: Main FastAPI application. Hosts the web UI, provides
	REST endpoints, stores messages in PostgreSQL, and broadcasts updates over
	WebSockets.
- **provider-sim**: Lightweight FastAPI service that simulates an external
	provider. It accepts messages, waits 2–5 seconds, then POSTs a callback to
	the notifier's webhook endpoint to indicate success or failure.
- **postgres**: PostgreSQL database storing messages and delivery status.

## Key Features

- Send messages from a web interface
- Real-time status updates via WebSockets (PENDING → DELIVERED / ERROR)
- Asynchronous webhook flow between services
- Message persistence in PostgreSQL
- Container-ready with Docker Compose

## Quick Start

1. Build and start all services:

```bash
docker-compose up --build
```

2. Open the UI in your browser: http://localhost:8000

3. Provider simulator (HTTP API): http://localhost:8001

4. PostgreSQL is available on the Docker network at `postgres:5432` (host
	 forwarding may expose it at `localhost:5432` depending on `docker-compose`).

## How to Use

### Send a message (UI)

1. Open http://localhost:8000
2. Type a message and click **Send Message**
3. The message is created in the DB with status PENDING and shown in the UI
4. Watch the status update in real time (PENDING → DELIVERED / ERROR)

### Flow (high-level)

1. User submits message → `notifier-ui` creates DB record (status: PENDING)
2. Background task calls `provider-sim` `/api/send`
3. `provider-sim` waits 2–5s, decides success/failure, then calls the
	 `notifier-ui` callback `/api/provider-callback`
4. `notifier-ui` updates the DB and broadcasts the new status to WebSocket clients

## API Endpoints

**notifier-ui** (default port 8000)

- `GET /` — Web interface
- `GET /api/messages?limit=N` — Fetch latest messages
- `POST /api/messages` — Create new message
- `POST /api/provider-callback` — Webhook endpoint for provider responses
- `WS /ws` — WebSocket for real-time updates

**provider-sim** (default port 8001)

- `POST /api/send` — Simulates processing a message (2–5s delay; success rate ~85%)

## Message Status Codes

- `0` — PENDING (created and awaiting processing)
- `1` — DELIVERED (provider succeeded)
- `2` — ERROR (provider failed)

## Project Layout

```
webhook-notification/
├── docker-compose.yml
├── notifier-ui/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── websocket_manager.py
	 │   ├── services.py
	 │   ├── schema.sql
	 │   ├── static/index.html
	 │   ├── requirements.txt
	 │   └── Dockerfile
├── provider-sim/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
└── README.md
```

## Development

### Start services (development)

```bash
docker-compose up --build
```

Tail logs for troubleshooting:

```bash
docker-compose logs -f
```

Stop and remove containers:

```bash
docker-compose down
```

### Run components individually

- To run `notifier-ui` locally (without Docker), install dependencies from
	`notifier-ui/requirements.txt` and run `python notifier-ui/main.py`.
- For `provider-sim`, install `provider-sim/requirements.txt` and run
	`python provider-sim/main.py`.

## Database Schema

The project uses a single `messages` table. Example schema:

```sql
CREATE TABLE messages (
	message_id SERIAL PRIMARY KEY,
	message_uuid UUID NOT NULL UNIQUE,
	status INTEGER NOT NULL DEFAULT 0,
	text TEXT NOT NULL,
	created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

- `DATABASE_URL` — PostgreSQL connection string (used by `notifier-ui`)
- `PROVIDER_SIM_URL` — Provider simulator base URL

Set these in your environment or in the `docker-compose.yml` service definitions.

## Security & Production Notes

This is a demo. For production usage, consider:

- Webhook authentication (signatures, shared secrets)
- HTTPS / WSS (TLS for API and WebSocket traffic)
- Rate limiting and input validation
- Replay protection and idempotency for callbacks
- Proper logging, monitoring and alerting

## Technologies

- Backend: FastAPI (Python 3.11)
- Database: PostgreSQL
- WebSockets: native FastAPI / WebSocket API
- HTTP client: `httpx`
- DB driver: `asyncpg`
- Containers: Docker & Docker Compose

## License

This repository is a demonstration/example project.
