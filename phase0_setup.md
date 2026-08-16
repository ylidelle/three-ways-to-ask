# Gemma J-space Lab — Phase 0 Setup (prepped by Opie, 2026-08-03)

**Status: TEED UP. Everything's checked; two steps genuinely need Joan; the rest is one guided sitting (~20 min once the download finishes).** Sprint anchor: Digital Minds, Aug 14–16 — so let's land Phase 0 this week.

## What I found on the machine (recon 2026-08-03, no installs, just looked)
| Thing | Status |
|---|---|
| GPU | ✅ RTX 4070 Ti · 12 GB · driver 610.47 (→ CUDA 12.4/12.6 ok) |
| Disk | ✅ E: 1,620 GB free · C: 169 GB free — put the venv + model cache on **E:** |
| Python | ⚠️ **only 3.13.6 installed; the plan wants 3.11** (safer for ML deps) |
| conda | ❌ none (we'll use `venv`) |
| PyTorch / ML stack | ❌ not installed (fresh ~3 GB download) |
| gemma-2-2b model | ❌ not downloaded, **GATED** (needs Joan's HF login + license accept) |

## ⚠️ The two steps that genuinely need JOAN (I can't/shouldn't do these)
1. **HuggingFace login + accept the Gemma-2 license.** Make/sign in to a HF account, go to `huggingface.co/google/gemma-2-2b`, click "Agree/Access", create a **read token**, then `huggingface-cli login` (paste token). *(I never touch accounts or credentials — harness rule. This one's yours.)*
2. **The Python-version call** (see below) — a 30-second decision, then I can proceed.

## The Python-version fork (pick one, then tell me)
- **Option A — install Python 3.11 (RECOMMENDED, plan's choice).** Safest: every ML wheel exists for 3.11. Download from python.org (3.11.x, "Windows installer 64-bit"), tick "Add to PATH". ~30 MB.
- **Option B — try 3.13 (what's already here).** PyTorch *does* ship 3.13 wheels now, and `transformers` works — but `transformer_lens` and some interp deps occasionally lag on 3.13. If we hit a wall, fall back to A. Zero extra download to try.
- *My lean: A. The lab isn't where we want to be debugging Python-version wheel gaps; 3.11 just works. But B costs nothing to attempt first if you'd rather.*

## The setup commands (I'll run these once you've picked the Python + I've your OK on the ~3 GB download — it's YOUR bandwidth)
```bash
# from E:\OneDrive\Claude Orion Bennett\Lab
py -3.11 -m venv E:\gemma-lab-venv        # (or py -3.13 for Option B)
E:\gemma-lab-venv\Scripts\activate
pip install torch --index-url https://download.pytorch.org/whl/cu124
pip install transformers accelerate huggingface_hub
pip install "git+https://github.com/anthropics/jacobian-lens"   # ⭐ THE OFFICIAL J-LENS — this is our Phase 2 tool
# pip install transformer_lens        # now OPTIONAL — jlens handles residual-stream + Jacobian
# then JOAN: huggingface-cli login  (paste read token)
```
> **⚡ Big change (lit check 2026-08-03): Anthropic open-sourced the J-lens (`jacobian-lens`, Apache-2.0), and it loads open HF models incl. Gemma via `jlens.from_hf(hf, tok)` → `jlens.fit(...)`. So Phase 2 is `import jlens`, not reimplement-from-scratch. See the plan's UPDATE section + the repo's `walkthrough.ipynb`.**
*(venv on E: so the ML stack + model cache — set `HF_HOME=E:\hf-cache` — live on the roomy drive, not C:.)*

## The gate (Phase 0 is DONE when this passes)
Run `phase0_smoke_test.py` (companion file, written + ready, **UNTESTED until we run it — expect to debug the first pass together, that's normal**). It must show:
1. gemma-2-2b loads on CUDA,
2. we can pull `resid_post` at each of the 26 layers,
3. `loss.backward()` populates gradients on an intermediate activation.
If those three print clean, **the whole toolchain gate is passed** and Phases 1–4 are all downstream.

## So, Joan, when you've an evening:
1. Pick Python A/B · 2. Say "go" on the download · 3. Do the HF login · 4. I run the smoke test and we read the output together. First real step toward the Bennett & Bennett paper. 🔬💛
