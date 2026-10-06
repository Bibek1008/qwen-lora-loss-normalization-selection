# Result

## Supported result

Final validation loss prospectively selected the better of token-mean and
example-mean Qwen3-0.6B LoRA training on all three untouched confirmation
seeds.

| Seed | Selected | Selected exact | Other exact | Selected NLL | Other NLL |
| --- | --- | ---: | ---: | ---: | ---: |
| 20260817 | Example | 86.46% | 4.17% | 0.0631 | 0.7599 |
| 20260818 | Token | 79.17% | 27.08% | 0.1345 | 0.5479 |
| 20260819 | Token | 87.50% | 53.12% | 0.0911 | 0.2177 |

The validation-selected policy averaged 84.38% exact match. Always-token
averaged 56.94%, and always-example averaged 55.56%. Its worst seed was 79.17%,
versus 4.17% and 27.08% for the fixed policies. Every frozen success gate
passed.

Each decision was sealed before test evaluation and included validation losses
plus hashes of the protocol, trainer, data, logs, receipts, and adapters.

## Negative result preserved

A fixed 50/50 mixture of token-mean and example-mean loss did not stabilize
training. It reversed from 91.67% exact match on seed 20260815 to 6.25% on seed
20260816. This rules out the simple fixed midpoint under this protocol.

## Practical meaning

When LoRA outcomes are seed-sensitive, a small validation set can be used to
choose the loss normalization instead of assuming one normalization is always
best. This trades approximately twice the training compute for much better
reliability in this experiment.

## Boundary

This is a three-seed prospective result on one synthetic variable-length
associative-recall task, Qwen3-0.6B 3-bit MLX, one optimizer, and one LoRA
configuration. Prompt templates are held out, but facts are not. It does not
establish universal transfer to natural data, larger models, other optimizers,
or other adapter settings.
