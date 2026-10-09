#!/bin/bash
set -euo pipefail
RG=SmartHospital-IoT-RG
VM=hospital-room-vm
KEY="${SSH_KEY_PATH:-$HOME/Downloads/smart-hospital-key.pem}"
az vm start -g "$RG" -n "$VM" --only-show-errors
IP=$(az vm show -g "$RG" -n "$VM" -d --query publicIps -o tsv)
echo 'Dashboard: https://smartroom-dashboard-girish2517-e6f0bacpgwc8fqhy.centralindia-01.azurewebsites.net/'
ssh -i "$KEY" "azureuser@$IP" 'cd ~/smart-hospital-simulator && . ./.env && .venv/bin/python sensor_simulator.py --scenario cycle --count 60 --interval 5'
