# Protocol 2.0: exact-match headroom pilot

Frozen before any protocol-2 Qwen training or evaluation.

## Purpose

Protocol 1.0 was inconclusive because strict exact match stayed at 2.08–4.17%.
This pilot tests whether a longer, otherwise unchanged run can create enough
headroom for a useful loss-normalization comparison. It does not reuse either
confirmation seed from protocol 1.0.

## Pilot

- Model, tokenizer, data, prompt templates, LoRA rank/layers/scale, batch size,
  optimizer, learning rate, mask, evaluator, and token-mean loss are identical
  to protocol 1.0.
- Pilot seed: 20260811.
- Condition: token mean only.
- Budget: 576 updates (six deterministic passes rather than three).
- The pilot chooses only whether 576 updates provide headroom; it cannot
  establish a token-versus-example result.

## Decision

Headroom passes only if:

- balanced strict exact match is strictly between 10% and 90%;
- short and long exact match are each above 5%;
- all 96 test records are evaluated, outputs are finite, and receipts exit 0.

If it passes, freeze two new paired confirmation seeds before either arm is
run. If it fails, do not tune thresholds or reuse this seed as confirmation;
the next redesign must change the task or evaluator while preserving protocol
1.0 as historical evidence.

## Authority and resources

One Qwen process at a time on the local M4 MacBook. No cloud, download,
publication, worktree, or mutation of the shared base model cache.
