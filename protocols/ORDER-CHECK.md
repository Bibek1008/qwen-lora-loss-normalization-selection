# Reversed-order determinism check

Frozen after the independent reviewer identified that seed and launch order
were aliased in protocol 2.0 and before either replay began.

Replay seed 20260812 in reversed order: example first, then token. Preserve the
same code, model, data, seed, 576 updates, batch size, LoRA settings, learning
rate, and output evaluator. Write to new directories and do not overwrite the
confirmation artifacts.

Primary decision:

- If each replay adapter SHA-256 exactly matches its original same-seed,
  same-condition adapter, training is reproducible despite launch order and
  execution order is ruled out for this block. No reevaluation is needed.
- If either adapter hash differs, evaluate both replays. The result remains an
  endpoint-instability finding, but must not be attributed specifically to
  seed without further evidence.

This check does not alter or replace the frozen protocol 2.0 classification.

## Outcome

**Pass.** Replaying seed 20260812 in reversed order produced byte-identical
final adapters for both conditions:

- example original and replay:
  `e53d1c0c670f65f37f5a06a4ed44c5adcacaede8d9f6fd47e824d10ca6ee4428`
- token original and replay:
  `e9b6a9d63aacf914e3f9976970ccebf4ea43e9d8a7d565a73924074062917ad8`

This rules out execution order and run-to-run nondeterminism for the replayed
block. Because identical adapter bytes imply identical evaluation outputs,
reevaluation was unnecessary under the frozen decision rule. The observed
cross-block winner reversal can therefore be attributed to the changed seed
within this implementation, while the broader generalization limits remain.
