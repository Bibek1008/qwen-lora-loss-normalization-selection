# Protocol 2.0 paired confirmation

Frozen after pilot seed 20260811 passed headroom and before either confirmation
seed was trained.

## Fixed design

Use the same model, tokenizer, data, masks, balanced batches, LoRA settings,
optimizer, evaluator, and token/example loss definitions as protocol 1.0.
Change only the predeclared budget from 288 to 576 updates.

Paired seeds and order:

1. 20260812: token, then example;
2. 20260813: example, then token.

The pilot seed is excluded. Every process runs alone, preserves receipts and
raw logs, and must evaluate all 96 test records.

## Decision rules

Differences are `example - token` within each seed.

- Beneficial positive: both balance shifts are at least +0.10; mean worst-skill
  exact match improves by at least +0.05; neither balanced exact match drops by
  more than 0.05; mean balanced exact drops by no more than 0.02.
- Mechanism-only tradeoff: both balance shifts are at least +0.10 but a
  beneficial gate fails.
- Bounded negative: in both seeds, each skill exact difference and balance
  shift has magnitude below 0.05, balanced NLL differs by less than 0.05, and
  balanced target-token accuracy differs by less than 0.03.
- Inconclusive or mixed: every other outcome.

At least one arm/skill exact rate must remain strictly between 5% and 95% for
positive or bounded-negative interpretation. Thresholds, seeds, budget, and
metrics cannot change after outcomes are observed.
