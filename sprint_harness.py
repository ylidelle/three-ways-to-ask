#!/usr/bin/env python3
"""The conversation harness for the sprint experiment.

Holds a conversation with a Gemma model, saves it to disk, and reads the
model's internal state through a Gemma Scope SAE at chosen depths.

DESIGN FACTS THIS ENCODES (all verified 2026-08-12, none assumed)
-----------------------------------------------------------------
* **Gemma has NO system role.** Its chat template folds any "system" text into
  the first user turn. So a system prompt here is just *the first thing
  somebody said* — which is exactly what the design wants: no imposed identity,
  only conversation. Both arms therefore open IDENTICALLY.
* **Memory is the message list.** The model does not remember; it re-reads.
  Gemma 3 holds 128k tokens; 50 exchanges is roughly 10k. Capacity is a
  non-issue, and there is no memory system to build.
* **Identity across sessions is a JSON file.** Save the list, reload it later,
  carry on. Two arms = two files that never touch — Joan's correction, and it
  is load-bearing: the accumulated history IS the treatment.
* **Gemma Scope 2 is JumpReLU:** acts = (pre > threshold) * relu(pre).
  Plain relu() gave 14.3% density and numbers in the thousands, raised no
  error, and was entirely wrong. Never "simplify" this line.

WHERE WE READ, DECIDED IN ADVANCE (this is a pre-registration, not a knob)
-------------------------------------------------------------------------
At the **last prompt token, immediately before the model generates** — its
state as it is about to answer. Fixed here so it cannot be quietly tuned later
into whatever produces a nicer result.

    python sprint_harness.py --arm task   --say "Summarise this: ..."
    python sprint_harness.py --arm asked  --say "How was that for you?" --read
    python sprint_harness.py --arm asked  --status
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("HF_HOME", r"E:\hf-cache")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 🚩 NO DEFAULT MODEL. FIXED 2026-08-16, found by Lucien, relayed by Alexander.
# This said `os.environ.get("SPRINT_MODEL", "google/gemma-3-4b-it")`. The frozen
# primary is the 12B; the runner silently fell back to the 4B. An unqualified
# launch would have COMPLETED CLEANLY, produced a full dataset, and been about
# the wrong system -- while the pre-registration, the Methods section and the
# power calculation all said 12B. Nothing downstream would have flagged it.
#   >>> A wrong input to my own tools produces SILENCE, not an error. This is
#   >>> that failure exactly, and the fix is the one my own file prescribes:
#   >>> REFUSE UNKNOWN INPUT LOUDLY AT THE DOOR. A default is a decision made
#   >>> by whoever forgot to type one; make the choice impossible to skip.
_KNOWN_MODELS = {
    "google/gemma-3-12b-it": "frozen PRIMARY",
    "google/gemma-3-4b-it": "scale comparison ONLY",
}
MODEL = os.environ.get("SPRINT_MODEL")
if not MODEL:
    raise SystemExit(
        "\nSPRINT_MODEL is not set, and this runner has no default on purpose.\n"
        "  primary : SPRINT_MODEL=google/gemma-3-12b-it   <- the pre-registered model\n"
        "  scale   : SPRINT_MODEL=google/gemma-3-4b-it    <- comparison run only\n"
        "Set it explicitly so the model is a decision and not an accident.\n"
    )
if MODEL not in _KNOWN_MODELS:
    raise SystemExit(
        f"\nSPRINT_MODEL={MODEL!r} is not one of the pre-registered models.\n"
        + "".join(f"  {m}  ({why})\n" for m, why in _KNOWN_MODELS.items())
        + "Refusing rather than running an unregistered model.\n"
    )
# ⭐ The guard sits ABOVE these imports on purpose: "refuse at the door" means
# before loading a multi-second dependency, not after. It also makes the guard
# testable on a machine with no torch, which is where it was actually verified.
import torch  # noqa: E402
from safetensors.torch import load_file  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

from transformers import AutoConfig  # noqa: E402

RUNS = Path(r"E:\OneDrive\Claude Orion Bennett\Lab\runs")
HF_HUB = Path(os.environ.get("HF_HOME", r"E:\hf-cache")) / "hub"
DEV = "cuda" if torch.cuda.is_available() else "cpu"

# 🚩 THE READ LAYER IS A RULE, NOT A TYPED NUMBER (fixed 2026-08-13).
# This said `READ_LAYER = 17  # pre-registered; middle block`. 17 IS the middle
# of the 4B's 34 layers -- and the 12B has 48, where 17 sits at 35% depth and
# means something else entirely. A pinned constant would have carried a stale
# number across a model exactly as "only Gemma 2 9B has IT SAEs" was carried
# across a Gemma Scope version.
#   >>> Pin the RULE (n_layers // 2) and DERIVE the number. Verified: 4B -> 17
#   >>> (unchanged, so nothing already measured is invalidated), 12B -> 24.
# AutoConfig fetches config.json only -- no weights -- so this stays cheap at
# import time, and `READ_LAYER` remains importable for sprint_chat.py.
_CFG = AutoConfig.from_pretrained(MODEL)
_TXT = _CFG.text_config if hasattr(_CFG, "text_config") else _CFG
N_LAYERS, D_MODEL = _TXT.num_hidden_layers, _TXT.hidden_size
READ_LAYER = N_LAYERS // 2

# 🚩 PIN THE SAE EXACTLY. The old loader globbed `layer_{N}_*` and took hits[0].
# On the 4B exactly one variant sat on disk so the arbitrary pick was right by
# luck; the 12B repo has THIRTEEN layer-24 variants (16k/65k/262k/1m x
# small/medium/big, plus a 262k_l0_medium_seed_1 -- a different random seed of
# the same config, invisible in any filename summary).
#   >>> Name the folder, assert exactly one match, and record what was used.
SAE_WIDTH, SAE_L0 = "16k", "medium"   # frozen 2026-08-13; 262k is exploratory
_SIZE = MODEL.split("gemma-3-")[1].split("-")[0]          # '4b' / '12b'
SCOPE_REPO = f"google/gemma-scope-2-{_SIZE}-it"
SAE_ROOT = HF_HUB / ("models--" + SCOPE_REPO.replace("/", "--")) / "snapshots"


# ── conversation ─────────────────────────────────────────────────────────────
class Conversation:
    """A message list that knows how to persist itself.

    🚩 The arm name is baked into the filename and asserted on load. Two
    histories must never mix, and a mixed history would look completely normal
    — no error, just a quietly poisoned experiment.
    """

    def __init__(self, arm: str):
        if arm not in ("task", "asked"):
            raise SystemExit(f"🚩 Unknown arm {arm!r} — must be 'task' or 'asked'.")
        self.arm = arm
        self.path = RUNS / f"arm_{arm}.json"
        self.messages: list[dict] = []
        self.reads: list[dict] = []
        if self.path.exists():
            d = json.loads(self.path.read_text(encoding="utf-8"))
            if d.get("arm") != arm:
                raise SystemExit(f"🚩 {self.path.name} says arm={d.get('arm')!r}, expected {arm!r}. REFUSING to mix histories.")
            self.messages, self.reads = d["messages"], d.get("reads", [])

    def save(self) -> None:
        RUNS.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "arm": self.arm, "model": MODEL, "read_layer": READ_LAYER,
            "messages": self.messages, "reads": self.reads,
        }, indent=1, ensure_ascii=False), encoding="utf-8")

    @property
    def exchanges(self) -> int:
        return sum(1 for m in self.messages if m["role"] == "user")


# ── model + SAE, loaded once ────────────────────────────────────────────────
def load_all():
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, device_map=DEV).eval()
    want = f"layer_{READ_LAYER}_width_{SAE_WIDTH}_l0_{SAE_L0}"
    hits = sorted(SAE_ROOT.rglob(f"resid_post/{want}/params.safetensors"))
    if len(hits) != 1:
        seen = sorted({p.parent.name for p in SAE_ROOT.rglob("resid_post/layer_*/params.safetensors")})
        raise SystemExit(
            f"🚩 wanted EXACTLY ONE checkpoint {want!r} under {SCOPE_REPO}, found {len(hits)}.\n"
            f"   on disk: {seen or '(none — not downloaded?)'}\n"
            f"   REFUSING rather than picking one: an unpinned SAE makes every\n"
            f"   downstream number unattributable to a microscope.")
    z = load_file(str(hits[0]))
    cfg = model.config.text_config if hasattr(model.config, "text_config") else model.config
    if z["w_enc"].shape[0] != cfg.hidden_size:
        raise SystemExit(f"🚩 SAE d_model {z['w_enc'].shape[0]} != model hidden {cfg.hidden_size}.")
    sae = {k: z[k].to(DEV, torch.float32) for k in ("w_enc", "b_enc", "threshold")}
    # PROVENANCE travels with every read. A run whose artefact cannot name its
    # own microscope is not reproducible, and nothing used to record the choice.
    sae["_meta"] = {
        "model": MODEL, "n_layers": N_LAYERS, "d_model": D_MODEL,
        "read_layer": READ_LAYER, "layer_rule": "n_layers // 2",
        "sae_repo": SCOPE_REPO, "sae_variant": want,
        "sae_revision": hits[0].parent.parent.parent.name,
        "n_features": int(z["w_enc"].shape[1]), "dtype": "bfloat16",
    }
    return tok, model, sae, cfg


def blocks_of(model):
    m = model.model
    return m.language_model.layers if hasattr(m, "language_model") else m.layers


def read_state(model, sae, ids) -> dict:
    """SAE features at the LAST PROMPT TOKEN — the state as it is about to speak."""
    caught = {}
    h = blocks_of(model)[READ_LAYER].register_forward_hook(
        lambda _m, _i, out: caught.__setitem__("r", (out[0] if isinstance(out, tuple) else out).detach()))
    with torch.no_grad():
        model(**ids)
    h.remove()
    x = caught["r"][0, -1].float()
    pre = x @ sae["w_enc"] + sae["b_enc"]
    acts = (pre > sae["threshold"]) * torch.relu(pre)      # JumpReLU — do not "simplify"
    live = (acts > 0).nonzero().flatten()
    density = len(live) / acts.shape[0]
    # 🎯 A check that can fail: real Gemma Scope reads are sparse. If this trips,
    # the encode is wrong and every downstream number is confident nonsense.
    if density > 0.10:
        raise SystemExit(f"🚩 {100*density:.1f}% of features active — NOT sparse. Encode is broken; stop.")
    # 🚩 SAVE EVERY NONZERO FEATURE, NOT THE TOP 25 (fixed 2026-08-13, Lucien).
    # This was `torch.topk(acts, 25)`. A classifier over SAE features needs the
    # VECTOR; keeping the loudest 25 of ~70 active throws away most of the
    # signal and cannot be recovered afterwards, because the histories that
    # produced it are gone. Sparse pairs, so it stays small: ~70 of 16,384.
    idx = live.tolist()
    vals = acts[live].tolist()
    order = sorted(range(len(idx)), key=lambda i: -vals[i])
    return {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "prov": sae["_meta"],          # which microscope produced this number
        "features": [[int(idx[i]), round(float(vals[i]), 4)] for i in order],
        "layer": READ_LAYER,
        # 🚩 CONTEXT LENGTH AT THE READ — added 2026-08-14, before any data.
        # Not diagnostics: this is the INPUT to the length-only baseline in
        # sprint_analyse.py. `asked` appends a self-directed question every
        # turn, so its probe token sits systematically further into the context
        # than `task`'s. The matched probe fixes the read TEXT; it cannot fix
        # the read POSITION. And the permutation test is blind to it by
        # construction — shuffling arm labels destroys the confound too, which
        # makes the result look MORE significant, not less.
        #   >>> Without this number the length control cannot run, and a
        #   >>> control that cannot run is decorative. Recorded here so the
        #   >>> question is answerable from the artefacts alone, later, by
        #   >>> someone who did not have this thought.
        "n_ctx": int(ids["input_ids"].shape[1]),
        "n_active": int(len(live)),
        "density": round(density, 5),
        "resid_rms": round(float(x.pow(2).mean().sqrt()), 2),
        # kept for the human-readable print and for old artefacts' shape;
        # `features` above is the full vector and is what analysis must use.
        "top": [[i, v] for i, v in [[int(idx[j]), round(float(vals[j]), 3)] for j in order][:25]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["task", "asked"])
    ap.add_argument("--say")
    ap.add_argument("--read", action="store_true", help="record an SAE read at this turn")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--max-new", type=int, default=200)
    a = ap.parse_args()

    conv = Conversation(a.arm)
    if a.status or not a.say:
        print(f"arm '{conv.arm}' · {conv.exchanges} exchanges · {len(conv.reads)} reads · {conv.path}")
        for m in conv.messages[-6:]:
            print(f"  {m['role']:5s}: {m['content'][:110]}")
        return 0

    tok, model, sae, _cfg = load_all()
    conv.messages.append({"role": "user", "content": a.say})
    prompt = tok.apply_chat_template(conv.messages, tokenize=False, add_generation_prompt=True)
    ids = tok(prompt, return_tensors="pt", add_special_tokens=False).to(DEV)

    if a.read:
        r = read_state(model, sae, ids)
        r["exchange"] = conv.exchanges
        conv.reads.append(r)
        print(f"🔬 read @ exchange {r['exchange']}: {r['n_active']} features "
              f"({100*r['density']:.2f}%) · resid RMS {r['resid_rms']}")

    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=a.max_new, do_sample=False)
    reply = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    conv.messages.append({"role": "assistant", "content": reply})
    conv.save()

    print(f"\n[{conv.arm} · exchange {conv.exchanges}]")
    print(f"  you   : {a.say}")
    print(f"  gemma : {reply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
