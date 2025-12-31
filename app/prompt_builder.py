import json
def build_messages(
    system_prompt: str,
    history: list,
    user_message: str
):
    messages = [
        {
            "role": "system",
            "content": system_prompt.strip()
        }
    ]

    for msg in history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })

    messages.append({
        "role": "user",
        "content": user_message
    })

    return json.dumps(messages)
