"""
Shared state module to manage global variables across different command modules
"""

# Shared context messages list for AI conversations
context_messages = []  # Список словарей вида {"role": "user", "content": "..."} или {"role": "assistant", "content": "..."}

# Current model ID
MODEL_ID = "tngtech/deepseek-r1t2-chimera:free"

MODEL_IMG = "magic"


def set_model_id(new_model_id):
    """Update the global MODEL_ID"""
    global MODEL_ID
    MODEL_ID = new_model_id


def get_model_id():
    """Get the current MODEL_ID"""
    global MODEL_ID
    return MODEL_ID

def set_model_img(new_model_id):
    """Update the global MODEL_ID"""
    global MODEL_IMG
    MODEL_IMG = new_model_id


def get_model_img():
    """Get the current MODEL_ID"""
    global MODEL_IMG
    return MODEL_IMG

def clear_context():
    """Clear the context messages"""
    global context_messages
    context_messages.clear()