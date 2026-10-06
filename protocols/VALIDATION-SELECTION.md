# Prospective validation-selection protocol

Frozen before training seeds 20260817, 20260818, and 20260819.

The archived selection records hash the original frozen lab copy. This public
copy removes machine-local paths, so it is intentionally not byte-identical.

For each seed, train token-mean and example-mean LoRA arms with identical model,
data, minibatch order, optimizer, 576-update budget, and LoRA configuration.
Select the arm with lower final validation loss at update 576; a numerical tie
selects token mean. Write the selection and relevant hashes before evaluating
either arm on the test split.

The method succeeds only if all six train/evaluation pairs are valid and:

1. the selected arm has lower balanced test NLL on every seed;
2. selected exact match is never more than five percentage points below the
   unselected arm;
3. selected mean NLL is lower and selected mean exact match is higher than both
   always-token and always-example policies;
4. selected worst-seed NLL is lower and selected worst-seed exact match is
   higher than both fixed policies.

No seed replacement, extra seed, arm removal, tie-rule change, checkpoint
selection, hyperparameter change, test-based selection, metric substitution,
or post-hoc threshold change is allowed.

The test split contains 96 held-out prompt templates over training facts. This
protocol does not test factual generalization.
