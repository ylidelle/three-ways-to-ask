"""Pull the base/instruct pair + their matching Gemma Scope 2 SAEs.
Joan cleared the bandwidth 2026-08-07: "you can download models through our wifi. We have 1 Gbps."
"""
import os, time
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
from huggingface_hub import snapshot_download

MODELS = ["google/gemma-3-4b-pt", "google/gemma-3-4b-it"]
PAT = ["*.safetensors", "*.json", "*.model", "*.txt"]

for repo in MODELS:
    t = time.time()
    print(f"--> {repo}", flush=True)
    p = snapshot_download(repo, allow_patterns=PAT, max_workers=8)
    gb = sum(os.path.getsize(os.path.join(r, f))
             for r, _, fs in os.walk(p) for f in fs) / 1e9
    print(f"    done {gb:.1f} GB in {time.time()-t:.0f}s", flush=True)
print("ALL MODELS READY", flush=True)
