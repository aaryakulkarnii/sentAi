#!/usr/bin/env python3
"""Generate synthetic security events and publish to Kafka."""

import argparse
import asyncio
import json
import random
from datetime import datetime

HOSTS = ["dc01.corp.local", "ws-alice", "ws-bob", "srv-web01", "srv-db01"]
USERS = ["alice", "bob", "charlie", "svc-backup", "SYSTEM"]
IPS   = ["10.0.1.5", "10.0.2.10", "192.168.1.100", "203.0.113.42", "185.220.101.5"]


def make_sysmon_event(severity: str = "low") -> dict:
    return {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "winlog": {"event_id": random.choice([1, 3, 7, 11, 13])},
        "host": {"name": random.choice(HOSTS)},
        "user": {"name": random.choice(USERS)},
        "process": {
            "name": random.choice(["powershell.exe", "cmd.exe", "mimikatz.exe", "notepad.exe"]),
            "pid": random.randint(1000, 65535),
            "command_line": random.choice(["whoami", "net user /domain", "powershell -enc AAAAA"]),
        },
        "source": {"ip": random.choice(IPS)},
        "_severity": severity,
    }


async def publish(count: int) -> None:
    from aiokafka import AIOKafkaProducer
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        for _ in range(count):
            sev = random.choices(["low", "medium", "high", "critical"], weights=[50, 30, 15, 5])[0]
            event = make_sysmon_event(sev)
            await producer.send_and_wait("sentinelai.sysmon", json.dumps(event).encode())
        print(f"Published {count} events to sentinelai.sysmon")
    finally:
        await producer.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    asyncio.run(publish(args.count))
