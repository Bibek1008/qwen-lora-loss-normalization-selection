# Validation-Guided LoRA Loss Selection

A controlled experiment investigating whether validation loss can be used to
select between two LoRA loss-normalization strategies for Qwen3-0.6B.

The two training objectives are:

- **Token-mean loss** — supervised token losses are aggregated across tokens.
- **Example-mean loss** — each example contributes equally after averaging its
  supervised-token losses.

The central question is:

> Can validation performance reliably select which loss-normalization strategy
> should be used, without using the test set to make the decision?

## Result

The better loss normalization changed with the random seed.

Always using token-mean or always using example-mean training was unreliable.
On three fresh confirmation seeds, a simple prospective rule worked on every
seed:

> Train both LoRA arms, compare their final validation losses, and select the
> arm with lower validation loss before evaluating the test set.

| Policy | Mean exact match | Worst seed |
| --- | ---: | ---: |
| **Validation-selected** | **84.38%** | **79.17%** |
| Always token-mean | 56.94% | 4.17% |
| Always example-mean | 55.56% | 27.08% |

The validation-selected arm also achieved lower test NLL on all three
confirmation seeds.

The tradeoff is approximately **2× training compute**, because both LoRA arms
must be trained before selection.

## Prospective Confirmation

The validation-based decisions were written and hashed before either
corresponding test evaluation began.

| Seed | Selected from validation | Selected exact | Other exact |
| --- | --- | ---: | ---: |
| 20260817 | Example-mean | 86.46% | 4.17% |
| 20260818 | Token-mean | 79.17% | 27.08% |
| 20260819 | Token-mean | 87.50% | 53.12% |

These are prospective confirmation runs rather than post-hoc selections.

## Why We Tested Selection

The initial comparison showed a reversal between the two loss objectives
across random seeds:

| Seed | Token-mean | Example-mean |
| --- | ---: | ---: |
| 20260812 | 70.83% | 3.12% |
| 20260813 | 12.50% | 46.88% |

A fixed 50/50 hybrid objective was also unstable, scoring 91.67% on one fresh
seed and 6.25% on the next.

This motivated a different question:

> Rather than assuming one loss normalization is always better, can validation
> loss be used to choose between them for each training run?

Validation loss predicted the better endpoint on the five discovery seeds used
to motivate the prospective experiment. The three fresh seeds above were then
used as the confirmation experiment.

## Task and Experimental Design

This is a **controlled synthetic associative-recall experiment** using
Qwen3-0.6B with LoRA.

The dataset contains short and long target responses so that the two loss
normalizations can be compared under different response lengths.

The test split uses **held-out prompt templates**, while the underlying facts
are not completely held out. Therefore, the experiment measures generalization
to new prompt wording rather than factual generalization to unseen knowledge.

This distinction is important when interpreting the result.

## Evaluation and Selection Rule

For each seed:

1. Train a token-mean LoRA arm.
2. Train an example-mean LoRA arm.
3. Compare their final validation losses.
4. Seal the selection.
5. Evaluate the selected arm and the alternative arm on the test set.
6. Compare exact-match and NLL outcomes.

The test set is not used to make the selection decision.

## Repository Structure

```text
validation-guided-lora-loss-selection/
│
├── README.md
├── RESULT.md
├── LICENSE.md
├── requirements.txt
│
├── data/
│   └── v1/
│       ├── manifest.json
│       ├── train.jsonl
│       ├── valid.jsonl
│       └── test.jsonl
│
├── evidence/
│   ├── comparison.json
│   ├── validation-selection.json
│   ├── metrics/
│   └── selections/
│
├── protocols/
│   ├── PROTOCOL.md
│   ├── VALIDATION-SELECTION.md
│   ├── CONFIRMATION.md
│   └── ORDER-CHECK.md
│
└── scripts/
    ├── analyze_comparison.py
    ├── evaluate_condition.py
    ├── generate_data.py
    ├── select_by_validation.py
    └── train_condition.pyS