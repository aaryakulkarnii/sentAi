#!/bin/bash
# Run after Kafka is up (internal Docker listener)
set -e
BOOTSTRAP="${KAFKA_BOOTSTRAP_SERVERS:-kafka:29092}"
TOPICS=(
  "sentinelai.sysmon"
  "sentinelai.auditd"
  "sentinelai.cloudtrail"
  "sentinelai.network"
  "sentinelai.alerts"
)
for topic in "${TOPICS[@]}"; do
  kafka-topics.sh --create \
    --bootstrap-server $BOOTSTRAP \
    --replication-factor 1 \
    --partitions 4 \
    --topic "$topic" \
    --if-not-exists
  echo "Created: $topic"
done
