from django.utils.encoding import force_str


def format_validation_error(exc):
    """
    Normalize Django ValidationError objects into a single user-facing string.
    """
    message_dict = getattr(exc, "message_dict", None)
    if message_dict:
        for messages in message_dict.values():
            if messages:
                return force_str(messages[0])
    messages = getattr(exc, "messages", None)
    if messages:
        return force_str(messages[0])
    return force_str(exc)
