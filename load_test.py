import requests, time, os, statistics, csv, random

URL = "http://192.168.49.2:30512/predict"
IMG_DIR = "imagenet-sample-images"

latencies_over_time = []
latencies = []
start_global = time.time()

files = [
    os.path.join(IMG_DIR, f)
    for f in os.listdir(IMG_DIR)
    if f.lower().endswith((".jpg", ".jpeg", ".png"))
]

workload = []
with open("workload.txt") as f:
    for line in f:
        line = line.strip()
        if line:
            workload.append(int(line))

for qps in workload:
    deadline = time.time() + 1.0          # send for 1 second at this QPS
    delay = 1.0 / qps if qps > 0 else 1.0
    while time.time() < deadline:
        img_path = random.choice(files)
        start = time.time()
        with open(img_path, "rb") as f:
            res = requests.post(URL, files={"file": f})
        latency = time.time() - start
        timestamp = time.time() - start_global
        latencies.append(latency)
        latencies_over_time.append((timestamp, latency))
        print(f"qps={qps} status={res.status_code} latency={latency:.3f}s")
        time.sleep(max(0, delay - latency))

print("\n--- RESULTS ---")
print(f"Requests: {len(latencies)}")
print(f"avg latency: {statistics.mean(latencies):.3f}s")
print(f"p99 latency: {sorted(latencies)[int(0.99*len(latencies))]:.3f}s")
print(f"max latency: {max(latencies):.3f}s")

with open("latency.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "latency"])
    writer.writerows(latencies_over_time)
