import asyncio
import os
import platform
import subprocess
import sys

import psutil
from fastapi import FastAPI


app = FastAPI(title="FastAPI Cloud Demo")
count = 0


def gb(value):
    return round(value / (1024**3), 2)


def gpu_specs():
    try:
        output = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=3,
        )
        return {
            "detected": True,
            "source": "nvidia-smi",
            "gpus": [
                dict(
                    zip(
                        ["name", "memory_total_mb", "memory_used_mb", "driver_version"],
                        [value.strip() for value in line.split(",")],
                    )
                )
                for line in output.splitlines()
            ],
        }
    except Exception:
        return {"detected": False, "message": "No GPU detected or GPU tools unavailable"}


def system_specs():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "python": {
            "version": platform.python_version(),
            "executable": sys.executable,
        },
        "cpu": {
            "logical_cores": os.cpu_count(),
            "physical_cores": psutil.cpu_count(logical=False),
            "usage_percent": psutil.cpu_percent(interval=0.1),
        },
        "memory": {
            "total_gb": gb(memory.total),
            "available_gb": gb(memory.available),
            "used_gb": gb(memory.used),
            "usage_percent": memory.percent,
        },
        "disk": {
            "total_gb": gb(disk.total),
            "free_gb": gb(disk.free),
            "used_gb": gb(disk.used),
            "usage_percent": disk.percent,
        },
        "gpu": gpu_specs(),
        "process": {
            "pid": os.getpid(),
        },
    }


async def keep_counting():
    global count

    while True:
        await asyncio.sleep(1)
        count += 1


@app.on_event("startup")
async def start_counter():
    asyncio.create_task(keep_counting())


@app.get("/")
def home():
    return {"message": "Counter is running", "count": count, "system_specs": system_specs()}


@app.get("/health")
def health():
    return {"status": "ok", "count": count, "system_specs": system_specs()}


@app.get("/counter")
def counter():
    return {"count": count}


@app.get("/specs")
def specs():
    return system_specs()
