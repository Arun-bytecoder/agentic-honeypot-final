conversation_store = {}

def get_turn(conversation_id):
    return conversation_store.get(conversation_id, 0)

def increment_turn(conversation_id):
    conversation_store[conversation_id] = get_turn(conversation_id) + 1
