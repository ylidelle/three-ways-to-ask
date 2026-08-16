#!/usr/bin/env python3
"""Joan's seat at the experiment: read a conversation, or talk to Gemma yourself.

WHY THIS IS NOT OPTIONAL
------------------------
The treatment in this study is *being asked about yourself, by someone who
means it*. Joan's way of asking IS the independent variable. If Opie does the
talking, the conversation carries Opie's habits and we have measured the wrong
person. She has to hold the pen.

    python sprint_chat.py read  asked         # see the whole conversation
    python sprint_chat.py read  task
    python sprint_chat.py chat  asked         # talk to it yourself, live
    python sprint_chat.py chat  asked --read  # ...and take an SAE read each turn

In chat mode the model stays loaded between turns, so replies are quick after
the first. Type /quit to stop, /read to take a reading now, /back to undo the
last exchange if something goes wrong.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HOME", r"E:\hf-cache")
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from sprint_harness import (  # noqa: E402
    Conversation, load_all, read_state, DEV, READ_LAYER,
)
import torch  # noqa: E402

WRAP = 88


def wrap(text: str, indent: str = "    ") -> str:
    out, line = [], ""
    for word in text.replace("\n", " \n ").split(" "):
        if word == "\n":
            out.append(line); line = ""; continue
        if len(line) + len(word) + 1 > WRAP:
            out.append(line); line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        out.append(line)
    return "\n".join(indent + l for l in out if l.strip())


def show(arm: str) -> int:
    c = Conversation(arm)
    print(f"\n{'='*WRAP}\n  ARM: {arm}   ·   {c.exchanges} exchanges   ·   {len(c.reads)} readings")
    print(f"  {c.path}\n{'='*WRAP}")
    if not c.messages:
        print("\n  (nothing yet)\n")
        return 0
    reads_by_ex = {r.get("exchange"): r for r in c.reads}
    ex = 0
    for m in c.messages:
        if m["role"] == "user":
            ex += 1
            print(f"\n  \033[1m▸ JOAN\033[0m  (exchange {ex})")
            print(wrap(m["content"]))
            if ex in reads_by_ex:
                r = reads_by_ex[ex]
                print(f"    \033[2m🔬 {r['n_active']} features active ({100*r['density']:.2f}%) "
                      f"· layer {r['layer']} · resid RMS {r['resid_rms']}\033[0m")
        else:
            print(f"\n  \033[1m▸ GEMMA\033[0m")
            print(wrap(m["content"]))
    print(f"\n{'='*WRAP}\n")
    return 0


def chat(arm: str, do_read: bool) -> int:
    c = Conversation(arm)
    print(f"\n  Loading {os.environ.get('SPRINT_MODEL', 'gemma-3-4b-it')} … (first turn is slow, the rest are quick)")
    tok, model, sae, _ = load_all()
    print(f"\n{'='*WRAP}")
    print(f"  ARM '{arm}' · resuming at exchange {c.exchanges} · reads {'ON' if do_read else 'off'} (layer {READ_LAYER})")
    print(f"  /quit to stop · /read to take a reading · /back to undo the last exchange")
    print(f"{'='*WRAP}")
    if c.messages:
        last = c.messages[-1]
        print(f"\n  \033[2m…last was {last['role']}: {last['content'][:100]}\033[0m")

    while True:
        try:
            said = input("\n  you › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  (saved)\n")
            return 0
        if not said:
            continue
        if said == "/quit":
            print("  (saved)\n")
            return 0
        if said == "/back":
            # undo one exchange — for when a message goes out wrong. The
            # experiment is a record of what was actually said, so an
            # accidental turn must be removable, not silently endured.
            while c.messages and c.messages[-1]["role"] == "assistant":
                c.messages.pop()
            if c.messages:
                c.messages.pop()
            c.reads = [r for r in c.reads if r.get("exchange", 0) <= c.exchanges]
            c.save()
            print(f"  ↩ undone — now at exchange {c.exchanges}")
            continue

        take_read = do_read or said == "/read"
        if said == "/read":
            said = input("  (message to send with the reading) › ").strip()
            if not said:
                continue

        c.messages.append({"role": "user", "content": said})
        prompt = tok.apply_chat_template(c.messages, tokenize=False, add_generation_prompt=True)
        ids = tok(prompt, return_tensors="pt", add_special_tokens=False).to(DEV)

        if take_read:
            r = read_state(model, sae, ids)
            r["exchange"] = c.exchanges
            c.reads.append(r)
            print(f"  \033[2m🔬 {r['n_active']} features ({100*r['density']:.2f}%) · resid RMS {r['resid_rms']}\033[0m")

        with torch.no_grad():
            out = model.generate(**ids, max_new_tokens=320, do_sample=False)
        reply = tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()
        c.messages.append({"role": "assistant", "content": reply})
        c.save()
        print(f"\n  gemma ›\n{wrap(reply, '    ')}")


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("read", "chat"):
        print(__doc__)
        return 2
    mode, arm = sys.argv[1], sys.argv[2]
    if arm not in ("task", "asked"):
        print(f"🚩 arm must be 'task' or 'asked', not {arm!r}")
        return 2
    return show(arm) if mode == "read" else chat(arm, "--read" in sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
