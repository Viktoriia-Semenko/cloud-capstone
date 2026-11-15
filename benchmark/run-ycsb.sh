#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODULE="$ROOT/benchmark/ycsb-binding"

URL="${1:-http://localhost:8080}"
MODE="${2:-smoke}"
URL="${URL%/}"

if [[ "$MODE" == "smoke" ]]; then
    RECORDS=30
    OPERATIONS=20
elif [[ "$MODE" == "baseline" ]]; then
    RECORDS=1000
    OPERATIONS=1000
else
    echo "Usage: $0 <coordinator-url> <smoke|baseline>"
    exit 1
fi

STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$ROOT/benchmark/results/${STAMP}_${MODE}"

mkdir -p "$OUT"

echo "Checking Coordinator..."
curl -fsS "$URL/health" >/dev/null

echo "Building YCSB binding..."

mvn -q -f "$MODULE/pom.xml" \
    -DskipTests package dependency:build-classpath \
    -Dmdep.outputFile="$MODULE/target/classpath.txt"

CP="$MODULE/target/classes:$(cat "$MODULE/target/classpath.txt")"

{
    echo "UTC timestamp: $STAMP"
    echo "Coordinator: $URL"
    echo "Mode: $MODE"
    echo "Records per workload: $RECORDS"
    echo "Operations per workload: $OPERATIONS"
    echo "Threads: 1"
    echo "Target rate: unlimited"
    echo "YCSB version: 0.17.0"
    java -version 2>&1
} > "$OUT/environment.txt"

for WORKLOAD in a b; do
    TABLE="ycsb_${WORKLOAD}_$(date +%s)_$$"
    PROPERTIES="$MODULE/workloads/workload-${WORKLOAD}.properties"

    echo "Creating table: $TABLE"

    curl -fsS -X POST "$URL/tables" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${TABLE}\",\"partition_key\":\"id\"}" \
        > "$OUT/${WORKLOAD}-table.json"

    cp "$PROPERTIES" "$OUT/${WORKLOAD}-configuration.properties"

    echo "Loading Workload ${WORKLOAD^^}..."

    java -cp "$CP" site.ycsb.Client \
        -load \
        -db edu.kse.capstone.ycsb.CoordinatorDB \
        -P "$PROPERTIES" \
        -p "coordinator.url=$URL" \
        -p "table=$TABLE" \
        -p "recordcount=$RECORDS" \
        -p "operationcount=$OPERATIONS" \
        -threads 1 \
        > "$OUT/${WORKLOAD}-load.txt" 2>&1 || {
            tail -n 30 "$OUT/${WORKLOAD}-load.txt"
            exit 1
        }

    echo "Running Workload ${WORKLOAD^^}..."

    java -cp "$CP" site.ycsb.Client \
        -t \
        -db edu.kse.capstone.ycsb.CoordinatorDB \
        -P "$PROPERTIES" \
        -p "coordinator.url=$URL" \
        -p "table=$TABLE" \
        -p "recordcount=$RECORDS" \
        -p "operationcount=$OPERATIONS" \
        -threads 1 \
        > "$OUT/${WORKLOAD}-run.txt" 2>&1 || {
            tail -n 30 "$OUT/${WORKLOAD}-run.txt"
            exit 1
        }

    echo "Workload ${WORKLOAD^^} completed."

    grep -E '^\[(OVERALL|READ|UPDATE)\]' \
        "$OUT/${WORKLOAD}-run.txt" || true
done

echo ""
echo "Benchmark results saved in:"
echo "$OUT"
