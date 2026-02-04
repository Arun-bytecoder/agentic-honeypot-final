def agent_reply(turn: int):
    responses = [
        "Sorry, I didn’t understand. Can you explain?",
        "Oh okay… how do I receive the money?",
        "Should I send any details?",
        "Can you share the payment link again?"
    ]
    return responses[min(turn, len(responses)-1)]
