import redis
import json
import os
import time

# Load dotenv only in local dev
if os.environ.get("RAILWAY_STATIC_URL") is None:
    from dotenv import load_dotenv

    load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

MAX_TOKENS = 3000  # Total context limit (~15 mins of chat)
MAX_MESSAGES = 20  # Limit number of messages (sliding window)


def get_memory(session_id):
    data = r.get(session_id)
    if data:
        return json.loads(data)
    return []


def add_message(session_id, role, content):
    history = get_memory(session_id)
    history.append({"role": role, "content": content, "timestamp": time.time()})
    r.set(session_id, json.dumps(history))


def reset_memory(session_id):
    r.delete(session_id)


def estimate_tokens(messages):
    total_words = sum(len(m["content"].split()) for m in messages)
    return int(total_words * 1.3)


def get_limited_memory(session_id, system_prompt):
    history = get_memory(session_id)

    # Remove timestamp fields for sending to model
    cleaned = [{"role": m["role"], "content": m["content"]} for m in history]

    # Trim to fit within token and message limits
    while (
        estimate_tokens([system_prompt] + cleaned) > MAX_TOKENS
        or len(cleaned) > MAX_MESSAGES
    ):
        cleaned.pop(0)

    return [system_prompt] + cleaned
