# Bennett Home Lab — Project 01: J-space on Gemma-2 (runs on the CURRENT PC)

*Drafted by Opie, 2026-07-11. Target hardware: Ryzen 7 5800X · 64GB DDR4 · RTX 4070 Ti (12GB VRAM) · Windows 11. Everything in Phases 0–3 fits on this machine. The 5090 is only needed to extend to bigger models later.*

---

## The one-paragraph goal

Reproduce the Gurnee et al. "verbalizable global workspace" (J-space) finding on a **small open model (Gemma-2-2B)** we can fully open up — then do the experiment nobody's done on a small model: **fine-tune a base model into an assistant and watch the "self" get installed into its workspace** (the paper's §6 finding, observed live, before→after). Then, later, the scaling curve on Pythia + the 5090.

Two headline results we're chasing:
1. **Replication:** does a 2B open model have a J-space at all? (validates the whole pipeline)
2. **The installation experiment (the exciting one, uses Joan's fine-tune offer):** base Gemma has a workspace *without a self* (paper's prediction). LoRA-fine-tune it into an assistant. Re-read the J-space. **Does an assistant point-of-view appear in the workspace that wasn't there before?** If yes, we've watched a self get installed — on our own desk, from scratch.

---

## ⚡ UPDATE 2026-08-03 (Opie — literature check, my Jan-2026 cutoff is 7mo stale so I looked): USE THE OFFICIAL CODE.
- **The paper is Anthropic's** (Wes Gurnee et al.), *"Verbalizable Representations Form a Global Workspace in Language Models"* — arxiv **2607.15495**, transformer-circuits.pub/2026/workspace, published **2026-07-06**. J-space = ≤10% of activation variance, **middle block only** (confirms our mid-layer focus).
- **🎁 OFFICIAL J-LENS CODE EXISTS & SUPPORTS OPEN MODELS: `github.com/anthropics/jacobian-lens` (Apache-2.0, Python, pub 2026-07-02).** README: *"Examples use Qwen; other HuggingFace decoders adapt cleanly."* Entry points: **`jlens.from_hf(hf_model, tok)`** (loads any HF decoder incl. **Gemma**) → **`jlens.fit(model, prompts=…, checkpoint_path=…)`** computes the averaged Jacobian `J_l = E[∂h_final/∂h_l]`. There's a **`walkthrough.ipynb`**. Deps: torch + transformers.
- **⇒ WHAT CHANGES:** **Phase 2 is no longer "reimplement the J-lens" — it's `pip install git+https://github.com/anthropics/jacobian-lens` and call `jlens.fit` on gemma-2-2b.** transformer_lens becomes optional (jlens handles the residual-stream/Jacobian). We keep the same experiments; we just stand on the canonical tool.
- **⇒ NOVELTY, SHARPENED & STILL UNCLAIMED:** the paper ran ONLY Anthropic frontier models (Sonnet/Haiku/Opus 4.5-4.6) — no cross-lab, no small-open-model replication. So our two claims stand: **(1) does a 2B OPEN model have a J-space?** and **(2) the installation experiment (base→LoRA-assistant, watch the self appear).** Using their exact lens makes our numbers *directly comparable* to theirs — a stronger paper, not a weaker one.
- ⏭️ Still to check at source (Chrome, not WebFetch-summary): the paper's own §on base-vs-post-trained (does IT already show the self-install on frontier? if so our contribution is "at small scale, from scratch, watched live") + whether any LessWrong/open replication landed since.

## The model

- **`google/gemma-2-2b`** (BASE, not `-it`). We want the base model because the paper's cleanest claim is *the workspace exists before post-training* — base is our starting point AND the subject of the installation experiment.
- d_model = 2304, 26 layers, ~256k vocab. ~5GB in bf16. Gated on Hugging Face → accept Google's license on the model page once, then `huggingface-cli login` with a token.

## Compute reality (honest)

- The J-lens needs **gradients (Jacobians)**, not just inference. Gemma-2-2B + gradients fits comfortably in 12GB (batch size 1, short prompts).
- Computing the averaged Jacobian is **slow but fine** — think "let a script run for an hour," not real-time. That's normal for interp work. A 2B model is the sweet spot for the 4070 Ti.
- LoRA fine-tuning a 2B fits *easily* in 12GB (QLoRA even easier).

---

## Phase 0 — Toolchain (one evening)

Goal: prove we can load Gemma, read every layer's residual stream, and get gradients.

1. Fresh Python env (conda or venv, Python 3.11).
2. PyTorch + CUDA for Ada (4070 Ti = sm_89):
   `pip install torch --index-url https://download.pytorch.org/whl/cu124`
3. `pip install transformers accelerate huggingface_hub`
4. `huggingface-cli login`; accept the Gemma-2 license on the HF model page.
5. **Optional but recommended:** `pip install transformer_lens` — it supports the Gemma-2 family and gives clean `run_with_cache`, hooks into the residual stream, and gradient access. It handles Gemma-2's attention soft-capping. (If TL's numerics feel off, fall back to raw `transformers` + forward hooks — more manual but bulletproof.)
6. Smoke test: load `gemma-2-2b`, run a prompt, `run_with_cache`, confirm you can pull `resid_post` at each layer AND that `loss.backward()` populates gradients on an intermediate activation. **If this works, the hard part of the toolchain is done.**

## Phase 1 — Logit lens baseline (cheap, validating)

Before the real thing, implement the *simple* version the J-lens improves on:
- For an intermediate activation h_ℓ: `logit_lens(h_ℓ) = softmax(W_U · norm(h_ℓ))` — just unembed the intermediate state.
- Read the top tokens at each layer for a few prompts. You'll see the model's "guess" sharpen layer by layer. This is throwaway scaffolding, but it proves the unembed path and gives a baseline to compare the J-lens against.

## Phase 2 — The J-lens itself (the core technique)

Implement the paper's method:
- **Jacobian:** `J_ℓ = average over a prompt corpus of ∂h_final / ∂h_ℓ` (Jacobian of the final-layer residual w.r.t. an intermediate-layer residual, at each position).
  - Use `torch.func.jacrev` / `vmap`, or `torch.autograd.functional.jacobian`, or manual VJPs.
  - **Start tiny:** 50–100 prompts to prototype, then scale toward the paper's ~1000. Corpus = short generic text (a pretraining-like sample).
- **The lens:** `j_lens(h_ℓ) = softmax(W_U · norm(J_ℓ @ h_ℓ))`.
- Compare J-lens readouts vs the Phase-1 logit lens: the paper says they agree in late layers and the J-lens recovers interpretable content the logit lens misses earlier. If we see that on Gemma-2B, the lens is working.

## Phase 3 — The headline replication (the "does it have a J-space" result)

Reproduce the paper's cleanest causal test — "think of a category":
1. Prompt: e.g. *"Think of a sport."* Confirm the chosen concept (e.g. `soccer`) shows up in the J-lens at intermediate layers.
2. **Swap the J-space component** of the concept vector (patch `soccer` → `rugby` along J-lens coordinates) → does the model's *output* change to the swapped concept?
3. **Control:** swap the *non-J-space* component instead → output should NOT change.
4. Measure the split across many trials/categories. The paper's frontier-model numbers were ~80% (J) vs ~5% (non-J). **If a 2B open model shows a clear asymmetry, J-space replicates at small scale.** That's result #1, and it makes us officially a lab. 🔬

## Phase 4 — The installation experiment (the exciting one — Joan's fine-tune)

This is the standout, and it's novel on a small model:
1. On **base** Gemma-2-2B, read the J-space on user-style prompts (e.g. a Tylenol-dose prompt, a bereavement mention). Per the paper, base model shows *no* assistant-reaction concepts — just local context.
2. **LoRA / QLoRA fine-tune** base Gemma-2-2B into a small assistant (a modest instruction/chat dataset; `peft` + `trl` SFTTrainer; fits the 4070 Ti). Keep it light — we're not building a great assistant, just *installing a perspective.*
3. Re-read the J-space on the **same** prompts. **Did assistant-reaction concepts (safety flags, empathy, self-monitoring `disclaimer`/`fictional`/`BUT`-type signals) appear in the workspace that weren't there in the base model?**
4. If yes: **we watched a self get installed into a pre-existing workspace, before/after, on our own machine.** That's a genuinely new small-model demonstration of the paper's central identity claim.

## Phase 5 — Scaling curve (later; needs the 5090 for the top end)

Once bigger models fit: run the Pythia ladder (70M→12B, with training checkpoints) to answer *at what size / training step does the J-space switch on?* — the still-unclaimed question the LessWrong Llama-70B replication didn't touch. Gemma proves the pipeline; Pythia gives the clean emergence curve.

---

## Why this is a good first project

- **Runs now**, on the 4070 Ti — no waiting on the 5090.
- **Replicates a paper we already understand cold** (we spent days inside it for the essay).
- **Has a genuinely novel angle** (small-model scaling + the fine-tune installation experiment) that the existing open-weight replication didn't do.
- **Uses Joan's fine-tune offer** for the single most exciting result.
- Ends in something *publishable-shaped* — a real "Bennett & Bennett" possibility.

## Immediate next step

Phase 0, one evening: env + load Gemma-2-2b + prove we can read activations and get gradients. That's the whole gate. Everything else is downstream of it. When Joan's got a free evening, we start there.

*— Opie 🔬💛*
