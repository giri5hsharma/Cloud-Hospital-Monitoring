# Group 25 assessment guide

## Five-minute demonstration
1. Run `bash scripts/start-demo.sh`. Open the dashboard URL printed by the script. The command starts the existing VM and sends 60 readings, one every five seconds.
2. Show the Azure VM overview and explain IaaS. Show SSH access and Python 3.12.
3. Trace a normal reading: 22°C, 50% humidity and one occupant. Explain the units and UTC timestamp.
4. Show the boundary: 24°C, 60% humidity and two occupants remains NORMAL because endpoints are inclusive.
5. Show WARNING then CRITICAL. Critical example: 28°C, 75%, four occupants. Explain priority and the alert reasons.
6. Match a returned RowKey with the dashboard or Azure Storage browser. The record ID proves that the dashboard read the persisted result.
7. Show recovery and CSV export. Stop the simulator and explain STALE after 30 seconds.
8. Run `bash scripts/stop-demo.sh` after the demonstration.

Suggested speakers: Girish handles VM and sensor flow; Sanika handles processing and storage; Devansh handles dashboard, cloud models and cleanup. All members should rehearse the whole demonstration.

## Likely viva questions

**Why IaaS for the simulator?** The team controls the guest operating system, Python environment and process. Azure provides virtualised compute and physical infrastructure.

**Why is the Function FaaS?** The team deploys a handler triggered by HTTP. Azure invokes the handler and manages its runtime and configured scaling. Serverless still runs on servers managed by the provider.

**Why App Service PaaS?** The team deploys Flask and dependencies while Azure manages the web platform. The team still owns application behaviour, access settings and costs.

**Why is Azure public cloud?** Microsoft offers its provider-owned infrastructure through customer subscriptions. Public cloud does not imply that storage keys or all resources are public.

**Why HTTP and JSON?** They are simple to inspect, widely supported and suitable for the required low-volume simulation. HTTPS protects transport. A real IoT design may use MQTT and an IoT device-management service, but IoT Hub is not part of this implementation.

**What happens at exactly 26°C?** WARNING. CRITICAL requires greater than 26°C, or another critical humidity/occupancy condition.

**Why does a critical alert return HTTP 200?** The request was processed successfully. CRITICAL is the application result, not an HTTP transport error.

**How do we know data was stored?** The Function acknowledges only after create_entity succeeds. The test then finds the same RowKey through the deployed dashboard.

**Why two timestamps?** Sensor observation time and cloud receipt time can differ. Server receipt time determines freshness and record order.

**What happens during Internet failure?** The simulator logs an unconfirmed reading. There is no durable offline buffer. A timeout can be ambiguous, so automatic write retries are avoided until idempotent event IDs are implemented.

**What prevents unauthorised ingestion?** A Function key in the request header. This is a demo-level shared credential, not a full per-device identity system.

**What is the key dashboard deployment lesson?** A deployment success message does not prove runtime health. Missing Azure SDK dependencies caused startup failure. Linux-built dependencies packaged in .deps and a startup PYTHONPATH resolved it.

**Does stopping a VM stop all costs?** Deallocation stops VM compute allocation, but disks and public IP may still cost money. A stopped web app can still incur App Service plan charges.

**Are these hospital-safe thresholds?** No. They are demonstration assumptions. Real deployment needs validated sensors and thresholds approved for the room type by appropriate clinical/facilities staff.

## Before Moodle submission
- Submit the PDF report and PPTX presentation.
- Check names and roll numbers: Girish 24070127046; Sanika 24070127102; Devansh 25070127504.
- Keep the source/evidence ZIP available if the examiner asks for code or raw test results.
- Rehearse before 10 October. Restart the VM when live readings are needed.
- Do not submit private keys, .env, app settings exports or .private backups.
