Get into the Vm
ssh -i ~/Downloads/smart-hospital-key.pem azureuser@20.244.49.186

sets up secret keys and stuff
cd ~/smart-hospital-simulator
. ./.env

python programe used for simulation
cat sensor_simulator.py

simulate the whole working
cd ~/smart-hospital-simulator && . ./.env && for scenario in normal boundary warning critical recovery; do .venv/bin/python sensor_simulator.py --scenario "$scenario" --count 6 --interval 5; done

exit


Content-Type: application/json
{
  "room_id": "ROOM-01",
  "timestamp_utc": "2026-10-09T10:00:00+00:00",
  "temperature_c": 28,
  "humidity_percent": 75,
  "occupancy": 4
}


{"scenario": "normal", "sent": {"room_id": "ROOM-01", "timestamp_utc": "2026-10-09T17:41:37.093444+00:00", "temperature_c": 22, "humidity_percent": 50, "occupancy": 1}, "http_status": 200, "latency_ms": 1165, "result": {"success": true, "stored": true, "status": "NORMAL", "record": {"PartitionKey": "ROOM-01", "RowKey": "20261009174138031650-f58a5703", "timestamp_utc": "2026-10-09T17:41:37.093444+00:00", "temperature_c": 22.0, "humidity_percent": 50.0, "occupancy": 1, "received_utc": "2026-10-09T17:41:38.031650+00:00", "status": "NORMAL", "alert_message": "All parameters within normal range", "source": "azure-vm-simulator"}}}
