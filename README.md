# Notification Webhooks System

A real-time webhook notification demo built with FastAPI, PostgreSQL, and WebSockets.
The project is organized in module-based service packages (`app/...`) for clean
separation of API routes, schemas, services, and infrastructure.

## Architecture

The repo contains three cooperating components:

- **notifier-ui**: Main FastAPI app. Hosts the web UI, provides REST APIs,
	stores messages in PostgreSQL, and broadcasts updates over WebSockets.
- **provider-sim**: External provider simulator. Accepts outbound requests,
	waits 2–5 seconds, then calls back the notifier webhook with success/failure.
- **postgres**: PostgreSQL database storing messages and delivery status.

## Key Features

- Send messages from a web interface
- Real-time status updates via WebSockets (PENDING → DELIVERED / ERROR)
- Asynchronous webhook flow between services
- Message persistence in PostgreSQL
- Container-ready with Docker Compose

## Quick Start (Docker)

1. Build and start all services:

```bash
docker-compose up --build
```

2. Open the UI: http://localhost:8000

3. Provider simulator API: http://localhost:8001

4. PostgreSQL is available on Docker network host `postgres:5432`.

## Message Flow

1. User submits message → `notifier-ui` creates DB record (status: PENDING)
2. Background task calls `provider-sim` `/api/send`
3. `provider-sim` waits 2–5s, decides success/failure, then calls the
	 `notifier-ui` callback `/api/provider-callback`
4. `notifier-ui` updates the DB and broadcasts the new status to WebSocket clients

## How to Use

1. Open http://localhost:8000
2. Type a message and click **Send Message**
3. Message is stored as `PENDING`
4. Status updates in real-time to `DELIVERED` or `ERROR`

## API Endpoints

**notifier-ui** (default port 8000)

- `GET /` — Web interface
- `GET /api/messages?limit=N` — Fetch latest messages
- `POST /api/messages` — Create new message
- `POST /api/provider-callback` — Webhook endpoint for provider responses
- `WS /ws` — WebSocket for real-time updates

**provider-sim** (default port 8001)

- `POST /api/send` — Simulates processing a message (2–5s delay; success rate ~85%)

## API Examples

Run these after `docker-compose up --build`.

Create a message in `notifier-ui`:

```bash
curl -X POST http://localhost:8000/api/messages \
	-H "Content-Type: application/json" \
	-d '{"text":"Hello from API"}'
```

Fetch latest messages:

```bash
curl "http://localhost:8000/api/messages?limit=10"
```

Send directly to `provider-sim` (which will callback to notifier):

```bash
curl -X POST http://localhost:8001/api/send \
	-H "Content-Type: application/json" \
	-d '{
		"message_id": "11111111-1111-1111-1111-111111111111",
		"text": "Provider direct test",
		"callback_url": "http://localhost:8000/api/provider-callback"
	}'
```

Simulate provider callback success manually:

```bash
curl -X POST http://localhost:8000/api/provider-callback \
	-H "Content-Type: application/json" \
	-d '{
		"message_id": "11111111-1111-1111-1111-111111111111",
		"status": "completed",
		"provider_job_id": "demo-job-123"
	}'
```

Simulate provider callback error manually:

```bash
curl -X POST http://localhost:8000/api/provider-callback \
	-H "Content-Type: application/json" \
	-d '{
		"message_id": "11111111-1111-1111-1111-111111111111",
		"status": "error",
		"error": "Simulated failure"
	}'
```

## Message Status Codes

- `0` — PENDING (created and awaiting processing)
- `1` — DELIVERED (provider succeeded)
- `2` — ERROR (provider failed)

## Schema Modules

Schemas are organized by domain and service:

- **notifier-ui**
	- `app/schemas/message.py` → API request/response and message models
	- `app/schemas/events.py` → WebSocket event envelope model
- **provider-sim**
	- `app/schemas/message.py` → provider send request/response models
	- `app/schemas/callback.py` → provider callback payload models

## Project Layout

```
webhook-notification/
├── docker-compose.yml
├── notifier-ui/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── realtime/
│   │   ├── schemas/
│   │   └── services/
│   ├── static/index.html
│   ├── schema.sql
│   ├── requirements.txt
│   └── Dockerfile
├── provider-sim/
│   ├── app/
│   │   ├── main.py
│   │   ├── schemas/
│   │   └── services/
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

Run each service from its own folder:

- `notifier-ui`
	- install: `pip install -r requirements.txt`
	- run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `provider-sim`
	- install: `pip install -r requirements.txt`
	- run: `uvicorn app.main:app --host 0.0.0.0 --port 8001`

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
- `CALLBACK_URL` — Callback endpoint sent to provider simulator
- `NOTIFIER_UI_URL` — Notifier base URL used by provider-sim configuration

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
