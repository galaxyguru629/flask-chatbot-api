# memory.py
from collections import defaultdict

# session_id => list of messages
sessions = defaultdict(list)

def get_memory(session_id):
    return sessions[session_id]

def add_message(session_id, role, content):
    sessions[session_id].append({"role": role, "content": content})

def reset_memory(session_id):
    sessions[session_id].clear()
