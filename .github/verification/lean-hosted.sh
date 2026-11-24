#!/usr/bin/env bash
set -euo pipefail
mkdir -p engine-evidence DockerData/market-hours DockerData/symbol-properties
root="$PWD"
docker pull "$LEAN" >engine-evidence/image.log &
pull_pid=$!
python -m pip install pandas==2.3.3 exchange-calendars==4.13.3
curl -fsSL "https://raw.githubusercontent.com/koreainvestment/open-trading-api/$KIS_COMMIT/backtester/kis_backtest/lean/data_converter.py" -o "$RUNNER_TEMP/kis_converter.py"
python -m tradingagents.execution.kis_lean_crosscheck --converter "$RUNNER_TEMP/kis_converter.py" --converter-sha256 "$CONVERTER_SHA" --output engine-evidence/reference
awk -F, '{print $1 "0900," $2; print $1 "1530," $5}' engine-evidence/reference/000001.csv >DockerData/events.csv
# The launcher image already has its version-matched venue and symbol database.
wait "$pull_pid"
docker image inspect "$LEAN" --format '{{json .RepoDigests}} {{json .Config.Labels}}' >>engine-evidence/image.log
for scenario in gross_fixture transaction_costs transaction_costs_and_tax_reserve; do
  mkdir -p "engine-evidence/$scenario"
  docker run --rm --network none --user "$(id -u):$(id -g)" -e HOME=/tmp -e SCENARIO="$scenario" \
    -v "$root/.github/verification:/Algorithm:ro" \
    -v "$root/DockerData/events.csv:/Fixture/events.csv:ro" \
    -v "$root/engine-evidence/$scenario:/Results" \
    -v "$root/.github/verification/lean-config.json:/Lean/Launcher/bin/Debug/config.json:ro" \
    "$LEAN" >"engine-evidence/$scenario/launcher.log" 2>&1 || { tail -40 "engine-evidence/$scenario/launcher.log"; exit 1; }
done
python .github/verification/check-lean.py
