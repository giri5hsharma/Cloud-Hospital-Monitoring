#!/bin/bash
set -euo pipefail
az vm deallocate -g SmartHospital-IoT-RG -n hospital-room-vm --only-show-errors
az vm get-instance-view -g SmartHospital-IoT-RG -n hospital-room-vm --query 'instanceView.statuses[].displayStatus' -o table
echo 'VM compute stopped. Disk, public IP, storage and the B1 App Service plan may still incur charges.'
