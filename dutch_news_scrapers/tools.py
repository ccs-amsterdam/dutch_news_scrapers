
def serialize(obj):
    """JSON serializer that accepts datetime & date"""
    from datetime import datetime, date, time
    if isinstance(obj, date) and not isinstance(obj, datetime):
        obj = datetime.combine(obj, time.min)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, set):
        return sorted(obj)


def get_chunks(sequence, batch_size):
    # TODO can be made more efficient by not creating a new list every time
    buffer = []
    for a in sequence:
        buffer.append(a)
        if len(buffer) >= batch_size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer
