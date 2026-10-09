"""Demonstration thresholds, not clinical operating limits."""
import math
import re
from datetime import datetime, timezone

def validate(body):
    if not isinstance(body, dict):
        raise ValueError('JSON body must be an object')
    room = body.get('room_id', 'ROOM-01')
    if not isinstance(room, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,40}', room):
        raise ValueError('room_id must contain 1-40 letters, digits, underscores or hyphens')
    for field, low, high in [('temperature_c', -50, 100), ('humidity_percent', 0, 100), ('occupancy', 0, 20)]:
        value = body.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
            raise ValueError(f'{field} must be a finite number between {low} and {high}')
    if int(body['occupancy']) != body['occupancy']:
        raise ValueError('occupancy must be an integer')
    timestamp = body.get('timestamp_utc')
    if not isinstance(timestamp, str):
        raise ValueError('timestamp_utc is required as an ISO 8601 timestamp with timezone')
    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        raise ValueError('timestamp_utc must include a timezone')
    return {'room_id': room, 'timestamp_utc': dt.astimezone(timezone.utc).isoformat(),
            'temperature_c': float(body['temperature_c']), 'humidity_percent': float(body['humidity_percent']), 'occupancy': int(body['occupancy'])}

def classify_room(temperature_c, humidity_percent, occupancy):
    critical, warnings = [], []
    if temperature_c < 18 or temperature_c > 26:
        critical.append('Temperature outside demonstration critical limits (18-26 C)')
    elif temperature_c < 20 or temperature_c > 24:
        warnings.append('Temperature outside normal band (20-24 C)')
    if humidity_percent < 30 or humidity_percent > 70:
        critical.append('Humidity outside demonstration critical limits (30-70%)')
    elif humidity_percent < 40 or humidity_percent > 60:
        warnings.append('Humidity outside normal band (40-60%)')
    if occupancy > 3:
        critical.append('Occupancy exceeds demonstration capacity of 3')
    elif occupancy == 3:
        warnings.append('Occupancy at demonstration capacity')
    alerts = critical + warnings
    return ('CRITICAL' if critical else 'WARNING' if warnings else 'NORMAL', '; '.join(alerts) or 'All parameters within normal range')
