"""Send simulated room readings from the Azure VM to the HTTP Function."""

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone

import requests


# Each scenario contains (temperature in C, humidity in %, occupancy).
SCENARIOS = {
    "normal": (22, 50, 1),
    "boundary": (24, 60, 2),
    "warning": (25, 65, 3),
    "critical": (28, 75, 4),
    "recovery": (22, 50, 1),
}


def main():
    parser = argparse.ArgumentParser(description="Simulate a hospital room")
    parser.add_argument("--scenario", choices=[*SCENARIOS, "cycle", "random"], default="cycle")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()

    if args.count < 1 or args.interval < 1:
        parser.error("count and interval must each be at least 1")

    # The private .env file on the VM provides these values.
    function_url = os.environ["FUNCTION_URL"]
    function_key = os.environ["FUNCTION_KEY"]
    scenario_names = list(SCENARIOS)

    print("Azure VM sensor simulator | ROOM-01 | JSON over HTTPS", flush=True)
    for number in range(args.count):
        scenario = scenario_names[number % len(scenario_names)] if args.scenario == "cycle" else args.scenario

        if scenario == "random":
            temperature = round(random.uniform(19, 28), 1)
            humidity = round(random.uniform(35, 75), 1)
            occupancy = random.randint(0, 4)
        else:
            temperature, humidity, occupancy = SCENARIOS[scenario]

        reading = {
            "room_id": "ROOM-01",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "temperature_c": temperature,
            "humidity_percent": humidity,
            "occupancy": occupancy,
        }

        started = time.monotonic()
        try:
            response = requests.post(
                function_url,
                headers={"x-functions-key": function_key},
                json=reading,
                timeout=30,
            )
            print(json.dumps({
                "scenario": scenario,
                "sent": reading,
                "http_status": response.status_code,
                "latency_ms": round((time.monotonic() - started) * 1000),
                "result": response.json(),
            }), flush=True)
            response.raise_for_status()
        except (requests.RequestException, ValueError):
            # Do not print the request URL, key, or private environment values.
            print(json.dumps({"error": "Reading not confirmed; check connectivity and credentials"}), flush=True)

        if number + 1 < args.count:
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
