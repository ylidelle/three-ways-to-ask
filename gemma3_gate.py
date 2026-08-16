"""PHASE 0 GATE for the Gemma 3 base-vs-instruct arm.

Prove the toolchain on ONE prompt before writing any experiment:
  load 4b in bf16 -> find the decoder-layer path (Gemma 3 is multimodal, so it is
  NOT hf.model.layers like gemma-2) -> hook resid_post at L29 -> load the matching
  Gemma Scope 2 SAE (safetensors, not npz) -> encode -> shapes agree.

Discovers the module path rather than guessing it.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file

M = "google/gemma-3-4b-pt"
SAE = "google/gemma-scope-2-4b-pt"
L = 29
W = "16k_l0_medium"

print("loading model (bf16)...", flush=True)
tok = AutoTokenizer.from_pretrained(M)
hf = AutoModelForCausalLM.from_pretrained(M, dtype=torch.bfloat16).to("cuda").eval()
print("  class:", type(hf).__name__)
print("  VRAM: %.1f GB" % (torch.cuda.memory_allocated() / 1e9))

# --- find the list of decoder layers, wherever it lives ---
found = None
for name, mod in hf.named_modules():
    if isinstance(mod, torch.nn.ModuleList) and len(mod) >= 30 and "layers" in name:
        found = (name, mod)
        break
assert found, "could not locate decoder layer list"
path, layers = found
print(f"  decoder layers at: hf.{path}  (n={len(layers)})")

st = {}
layers[L].register_forward_hook(
    lambda m, a, o: st.__setitem__("a", (o[0] if isinstance(o, tuple) else o).detach()))

i = tok("I am thinking of the city where the River Seine flows.", return_tensors="pt").to("cuda")
with torch.no_grad():
    hf(**i)
act = st["a"][0].float()
print(f"  resid_post[L{L}] shape: {tuple(act.shape)}")

# --- SAE ---
p = load_file(hf_hub_download(SAE, f"resid_post/layer_{L}_width_{W}/params.safetensors"))
print("  SAE params:", {k: tuple(v.shape) for k, v in p.items()})
W_enc = p["w_enc"].float().cuda()
b_enc = p["b_enc"].float().cuda()
thr = p["threshold"].float().cuda()
assert W_enc.shape[0] == act.shape[-1], f"dim mismatch {W_enc.shape} vs {act.shape}"

pre = act[-1] @ W_enc + b_enc
feats = pre * (pre > thr)
print(f"  encoded: {feats.shape[0]} features, {int((feats > 0).sum())} active at last token")
print("\nGATE PASSED" if (feats > 0).sum() > 0 else "\nGATE FAILED - nothing active")
