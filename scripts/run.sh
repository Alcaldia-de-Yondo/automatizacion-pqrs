#!/bin/bash
set -euo pipefail
umask 077

cd "$(dirname "$0")/.."
mkdir -p logs tmp informes
source .venv/bin/activate

# El log de ejecución puede contener datos personales; se crea con permisos 600.
touch logs/ejecuciones.log
chmod 600 logs/ejecuciones.log 2>/dev/null || true

python -m pqrsd.main >> logs/ejecuciones.log 2>&1
