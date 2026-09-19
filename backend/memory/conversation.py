from collections import defaultdict

_sessions = defaultdict(list)

def add_message(session_id, role, content):
    _sessions[session_id].append({"role": role, "content": content})

def get_messages(session_id):
    return _sessions.get(session_id, [])

def build_context(session_id):
    return "\n".join(f"{m['role']}: {m['content']}" for m in get_messages(session_id)[-10:])
