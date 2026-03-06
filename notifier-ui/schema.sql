CREATE TABLE IF NOT EXISTS messages (
    message_id SERIAL PRIMARY KEY,
    message_uuid UUID NOT NULL UNIQUE,
    status INTEGER NOT NULL DEFAULT 0 CHECK (status IN (0, 1, 2)),
    text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_uuid ON messages(message_uuid);
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);