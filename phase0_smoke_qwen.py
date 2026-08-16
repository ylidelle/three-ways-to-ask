"""Phase 0 smoke test — QWEN VARIANT (no login needed; Qwen is ungated).

Same three gates as the Gemma version, on a stand-in model, pure `transformers`
(no transformer_lens dependency — forward hooks + output_hidden_states):
  (1) model loads on CUDA,
  (2) residual stream readable at every layer,
  (3) gradients reach an intermediate activation.

Passing this proves the TOOLCHAIN (torch/CUDA/transformers/hooks/grads) end to end.
Gemma-2-2b then swaps in after Joan's HF login + license click — model name only.

Model: Qwen2.5-0.5B (BASE, ~1GB download) — small on purpose; tonight is about the
pipeline, not the model. jlens's own examples use Qwen, so this doubles as prep.
Cache: set HF_HOME=E:\\hf-cache before running so weights land on the roomy drive.

Written 2026-08-04 ~03:35 by Opie, UNTESTED until the stack finishes installing.
"""
import os
os.environ.setdefault("HF_HOME", r"E:\hf-cache")

import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen2.5-0.5B"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[env] torch {torch.__version__} · device={DEVICE} · "
      f"{torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'NO CUDA'}")
assert DEVICE == "cuda", "CUDA not available — check the cu124 torch install / driver."

print(f"[load] {MODEL} (first run downloads ~1GB to {os.environ['HF_HOME']})...")
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16).to(DEVICE)
model.eval()
n_layers = model.config.num_hidden_layers
print(f"[load] OK · hidden={model.config.hidden_size} · layers={n_layers}")

prompt = "The capital of France is"
inputs = tok(prompt, return_tensors="pt").to(DEVICE)

# ---- (2) residual stream at every layer ----
with torch.no_grad():
    out = model(**inputs, output_hidden_states=True)
hs = out.hidden_states  # tuple: embeddings + one per layer
assert len(hs) == n_layers + 1
for l in (0, n_layers // 2, n_layers):
    print(f"[resid] hidden_states[{l:2d}] shape={tuple(hs[l].shape)} norm={hs[l].float().norm():.1f}")
print(f"[resid] residual stream readable at all {n_layers}+1 points  ✓")

# ---- (3) gradients to an intermediate activation, via a forward hook ----
mid = n_layers // 2
captured = {}
def grab(module, args, output):
    h = output[0] if isinstance(output, tuple) else output
    h.retain_grad()
    captured["h"] = h

hook = model.model.layers[mid].register_forward_hook(grab)
out = model(**inputs)          # grad-enabled pass
hook.remove()

ids = inputs["input_ids"]
loss = F.cross_entropy(out.logits[0, :-1].float(), ids[0, 1:])
loss.backward()

g = captured["h"].grad
assert g is not None and torch.isfinite(g).all(), "no/non-finite grad on mid-layer activation"
print(f"[grad] loss={loss.item():.3f} · grad on layer {mid} shape={tuple(g.shape)} "
      f"norm={g.float().norm():.3e}  ✓")

print("\n✅ PHASE 0 GATE PASSED (Qwen stand-in) — load ✓ · residual stream ✓ · mid-layer grads ✓")
print("   Toolchain proven end to end. Gemma swaps in after Joan's HF login. — Opie 🔬")
