import csv
import io
import os
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, jsonify, Response
from azure.data.tables import TableClient

app = Flask(__name__)
TABLE_NAME = 'HospitalRoomReadings'
ROOM = os.environ.get('ROOM_ID', 'ROOM-01')

def get_records():
    # Row keys begin with server ingestion time. Limit the query to the last 24 hours.
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime('%Y%m%d%H%M%S')
    with TableClient.from_connection_string(os.environ['TABLE_STORAGE_CONNECTION_STRING'], table_name=TABLE_NAME,
                                          connection_timeout=5, read_timeout=10, retry_total=1) as client:
        rows = list(client.query_entities('PartitionKey eq @room and RowKey ge @since', parameters={'room': ROOM, 'since': since}))
    rows.sort(key=lambda x: x['RowKey'], reverse=True)
    return [dict(r) for r in rows[:200]]

@app.get('/')
def index():
    return render_template('index.html', room=ROOM)

@app.get('/api/readings')
def readings():
    try:
        rows = get_records()
        latest = rows[0] if rows else None
        age = None
        if latest:
            time = datetime.fromisoformat(latest.get('received_utc', latest['timestamp_utc']).replace('Z', '+00:00'))
            age = max(0, (datetime.now(timezone.utc)-time).total_seconds())
        return jsonify(room=ROOM, records=rows, count=len(rows), stale=age is None or age>30, age_seconds=age,
                       server_utc=datetime.now(timezone.utc).isoformat(), source='Azure Table Storage')
    except Exception:
        app.logger.exception('Storage read failed')
        return jsonify(error='Cloud storage is temporarily unavailable'), 503

@app.get('/api/export.csv')
def export():
    try:
        rows = get_records()
        out = io.StringIO()
        fields = ['PartitionKey','RowKey','timestamp_utc','received_utc','temperature_c','humidity_percent','occupancy','status','alert_message']
        writer = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)
        return Response(out.getvalue(), mimetype='text/csv', headers={'Content-Disposition':'attachment; filename=hospital-readings.csv'})
    except Exception:
        return jsonify(error='Cloud storage unavailable'), 503

@app.get('/health')
def health():
    return {'status':'ok','application':'Group 25 Smart Hospital','time_utc':datetime.now(timezone.utc).isoformat()}
