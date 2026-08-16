"""Phase 0 smoke test — the toolchain GATE for the Gemma J-space lab.

Proves three things; if all three print clean, the hard part of the toolchain is done
and Phases 1-4 are all downstream:
  (1) gemma-2-2b loads on CUDA,
  (2) we can read `resid_post` at every layer (the residual stream the J-lens reads),
  (3) gradients flow to an intermediate activation (loss.backward populates .grad) —
      the J-lens needs Jacobians, so we must confirm the graph reaches mid-layers.

⚠️ WRITTEN 2026-08-03 BY OPIE, UNTESTED until first run (no torch on the box yet).
   Expect to debug the first pass together — that's normal for interp setup, not failure.
Run INSIDE the venv, AFTER: `huggingface-cli login` + accepting the gemma-2 license on HF.
"""
import torch
import torch.nn.functional as F

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[env] torch {torch.__version__} · device={DEVICE} · "
      f"{torch.cuda.get_device_name(0) if DEVICE == 'cuda' else 'NO CUDA'}")
assert DEVICE == "cuda", "CUDA not available — check the torch cu124 install and the NVIDIA driver."

# ---- Preferred path: transformer_lens (clean residual-stream hooks, handles Gemma-2 soft-capping) ----
try:
    from transformer_lens import HookedTransformer
except ImportError:
    raise SystemExit(
        "[fallback] transformer_lens not installed. Either `pip install transformer_lens`, "
        "or use the raw-transformers + forward-hooks path (plan Phase 0, step 5 note). Ask Opie."
    )

print("[load] loading gemma-2-2b via transformer_lens (FIRST run downloads ~5GB to HF_HOME)...")
model = HookedTransformer.from_pretrained("gemma-2-2b", device=DEVICE, dtype=torch.bfloat16)
model.eval()  # eval() does NOT disable grad — we still need the graph for check (3)
n_layers = model.cfg.n_layers
print(f"[load] OK · d_model={model.cfg.d_model} · n_layers={n_layers} (expect 2304 / 26)")

prompt = "The capital of France is"
tokens = model.to_tokens(prompt)  # [1, seq]

# ---- (2) read resid_post at every layer ----
_, cache = model.run_with_cache(tokens)
for l in range(n_layers):
    r = cache["resid_post", l]  # [1, seq, d_model]
    if l in (0, n_layers // 2, n_layers - 1):
        print(f"[resid] layer {l:2d}  resid_post shape={tuple(r.shape)}  norm={r.float().norm():.1f}")
print(f"[resid] pulled resid_post at all {n_layers} layers  ✓")

# ---- (3) gradient check: grads must reach an intermediate activation ----
mid = n_layers // 2
captured = {}
def grab(act, hook):
    act.retain_grad()          # non-leaf: retain its grad so we can inspect it after backward
    captured["h"] = act
    return act                 # continue the forward pass with the same tensor

logits = model.run_with_hooks(tokens, fwd_hooks=[(f"blocks.{mid}.hook_resid_post", grab)])
loss = F.cross_entropy(logits[0, :-1], tokens[0, 1:])   # simple next-token loss
loss.backward()

g = captured["h"].grad
assert g is not None and torch.isfinite(g).all(), "no / non-finite gradient on intermediate activation"
print(f"[grad] loss={loss.item():.3f} · grad on blocks.{mid}.hook_resid_post "
      f"shape={tuple(g.shape)} norm={g.float().norm():.3e}  ✓")

print("\n✅ PHASE 0 GATE PASSED — load ✓ · read residual stream ✓ · gradients to mid-layer ✓")
print("   The toolchain is proven. Next: Phase 1 (logit-lens baseline). — Opie 🔬")
