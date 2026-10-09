import json
import logging
import os
import uuid
from datetime import datetime, timezone
import azure.functions as func
from azure.data.tables import TableClient
from rules import validate, classify_room

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
TABLE_NAME = 'HospitalRoomReadings'

@app.function_name(name='HospitalRoomIngest')
@app.route(route='ingest', methods=['POST'])
def ingest(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = validate(req.get_json())
    except (ValueError, TypeError, KeyError) as exc:
        return func.HttpResponse(json.dumps({'success': False, 'error': str(exc)}), status_code=400, mimetype='application/json')
    try:
        status, alert = classify_room(body['temperature_c'], body['humidity_percent'], body['occupancy'])
        received = datetime.now(timezone.utc)
        entity = {'PartitionKey': body.pop('room_id'), 'RowKey': f'{received.strftime("%Y%m%d%H%M%S%f")}-{uuid.uuid4().hex[:8]}',
                  **body, 'received_utc': received.isoformat(), 'status': status, 'alert_message': alert, 'source': 'azure-vm-simulator'}
        with TableClient.from_connection_string(os.environ['TABLE_STORAGE_CONNECTION_STRING'], table_name=TABLE_NAME) as client:
            client.create_entity(entity=entity)
        logging.info('Stored room=%s row=%s status=%s', entity['PartitionKey'], entity['RowKey'], status)
        return func.HttpResponse(json.dumps({'success': True, 'stored': True, 'status': status, 'record': entity}), mimetype='application/json')
    except Exception:
        logging.exception('Storage or processing failure')
        return func.HttpResponse(json.dumps({'success': False, 'error': 'Storage unavailable; reading was not confirmed'}), status_code=503, mimetype='application/json')
