# Simulator code guide

The simulator lives at `source/simulator/sensor_simulator.py` locally and `~/smart-hospital-simulator/sensor_simulator.py` on the Azure VM.

## What each part does

1. `SCENARIOS` maps each named case to three values: temperature in °C, humidity in %, and occupancy. For example, `critical` is `(28, 75, 4)`.
2. `argparse` reads the command options. `--scenario cycle` walks through normal, boundary, warning, critical and recovery; `--count` controls the number of readings; `--interval` controls the seconds between them. `random` creates varying values.
3. The `for` loop selects values, gives each reading `ROOM-01` and a fresh UTC timestamp, then builds a JSON object.
4. `requests.post` sends that JSON to the Azure Function over HTTPS. The Function URL and key come from the private VM environment, so the script does not contain secrets.
5. The script prints the sent reading, HTTP code, request time, and Function result. The result contains the room status and the stored Table Storage record ID. The last `time.sleep` pauses between readings, but not after the final reading.

## Presentation command

Inside the VM, after changing to `~/smart-hospital-simulator` and running `. ./.env`:

```bash
.venv/bin/python sensor_simulator.py --scenario cycle --count 10 --interval 5
```

This repeats the five scenarios twice. To hold each status on screen longer, run the five individual scenario commands with `--count 6 --interval 5`.

## What to say

> The VM chooses simulated sensor values, adds a timestamp and sends JSON to the Function. The Function validates and classifies the values, writes a table entity, and returns its status and record ID. The dashboard reads that stored entity.

`HTTP 200` means the cloud request succeeded. `CRITICAL` describes the room condition, not an HTTP failure. `stored: true` means the Function confirmed a successful table write. The `RowKey` connects the terminal response to the dashboard and Azure Storage browser.
