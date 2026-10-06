#!/usr/bin/env python3
"""Apply the frozen paired-seed decision rules to Qwen evaluation metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def compare_pair(seed: int, token: dict, example: dict) -> dict:
    token_short = token["generation"]["short"]["exact_match"]
    token_long = token["generation"]["long"]["exact_match"]
    example_short = example["generation"]["short"]["exact_match"]
    example_long = example["generation"]["long"]["exact_match"]
    return {
        "seed": seed,
        "short_exact_difference": example_short - token_short,
        "long_exact_difference": example_long - token_long,
        "balance_shift": (example_short - example_long) - (token_short - token_long),
        "balanced_exact_difference": example["summary"]["balanced_exact_match"]
        - token["summary"]["balanced_exact_match"],
        "worst_skill_exact_difference": example["summary"]["worst_skill_exact_match"]
        - token["summary"]["worst_skill_exact_match"],
        "balanced_nll_difference": example["summary"]["balanced_example_nll"]
        - token["summary"]["balanced_example_nll"],
        "balanced_target_accuracy_difference": example["summary"][
            "balanced_target_token_accuracy"
        ]
        - token["summary"]["balanced_target_token_accuracy"],
        "exact_rates": [token_short, token_long, example_short, example_long],
    }


def classify(pairs: list[dict]) -> tuple[str, dict]:
    diagnostics = {
        "valid_pair_count": len(pairs),
        "mean_balance_shift": mean([pair["balance_shift"] for pair in pairs]),
        "mean_worst_skill_exact_difference": mean(
            [pair["worst_skill_exact_difference"] for pair in pairs]
        ),
        "mean_balanced_exact_difference": mean(
            [pair["balanced_exact_difference"] for pair in pairs]
        ),
    }
    if len(pairs) != 2:
        return "INCONCLUSIVE_OR_MIXED", diagnostics
    headroom = any(0.05 < rate < 0.95 for pair in pairs for rate in pair["exact_rates"])
    mechanism = all(pair["balance_shift"] >= 0.10 for pair in pairs)
    beneficial = (
        mechanism
        and diagnostics["mean_worst_skill_exact_difference"] >= 0.05
        and all(pair["balanced_exact_difference"] >= -0.05 for pair in pairs)
        and diagnostics["mean_balanced_exact_difference"] >= -0.02
        and headroom
    )
    bounded_negative = headroom and all(
        abs(pair["short_exact_difference"]) < 0.05
        and abs(pair["long_exact_difference"]) < 0.05
        and abs(pair["balance_shift"]) < 0.05
        and abs(pair["balanced_nll_difference"]) < 0.05
        and abs(pair["balanced_target_accuracy_difference"]) < 0.03
        for pair in pairs
    )
    diagnostics["exact_headroom"] = headroom
    if beneficial:
        return "BENEFICIAL_POSITIVE", diagnostics
    if mechanism:
        return "MECHANISM_ONLY_TRADEOFF", diagnostics
    if bounded_negative:
        return "BOUNDED_NEGATIVE", diagnostics
    return "INCONCLUSIVE_OR_MIXED", diagnostics


def fixture(short: float, long: float, balanced_nll: float = 1.0, accuracy: float = 0.5):
    return {
        "generation": {
            "short": {"exact_match": short},
            "long": {"exact_match": long},
        },
        "summary": {
            "balanced_exact_match": (short + long) / 2,
            "worst_skill_exact_match": min(short, long),
            "balanced_example_nll": balanced_nll,
            "balanced_target_token_accuracy": accuracy,
        },
    }


def self_test() -> None:
    positive = [
        compare_pair(1, fixture(0.4, 0.6), fixture(0.6, 0.6)),
        compare_pair(2, fixture(0.3, 0.5), fixture(0.5, 0.5)),
    ]
    assert classify(positive)[0] == "BENEFICIAL_POSITIVE"
    negative = [
        compare_pair(1, fixture(0.4, 0.5), fixture(0.41, 0.49, 1.01, 0.51)),
        compare_pair(2, fixture(0.5, 0.4), fixture(0.49, 0.41, 0.99, 0.49)),
    ]
    assert classify(negative)[0] == "BOUNDED_NEGATIVE"
    floor = [
        compare_pair(1, fixture(0.0, 0.0), fixture(0.0, 0.0)),
        compare_pair(2, fixture(0.0, 0.0), fixture(0.0, 0.0)),
    ]
    assert classify(floor)[0] == "INCONCLUSIVE_OR_MIXED"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", nargs=3, action="append", metavar=("SEED", "TOKEN", "EXAMPLE"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print(json.dumps({"status": "PASS", "tests": 3}, indent=2))
        return
    if not args.pair or args.output is None:
        parser.error("--pair and --output are required unless --self-test is used")
    pairs = []
    for seed, token_path, example_path in args.pair:
        token = json.loads(Path(token_path).read_text())
        example = json.loads(Path(example_path).read_text())
        if token["fingerprints"]["data_manifest.json"] != example["fingerprints"]["data_manifest.json"]:
            raise ValueError(f"Data fingerprint mismatch for seed {seed}")
        if token["fingerprints"]["model.safetensors"] != example["fingerprints"]["model.safetensors"]:
            raise ValueError(f"Model fingerprint mismatch for seed {seed}")
        pairs.append(compare_pair(int(seed), token, example))
    classification, diagnostics = classify(pairs)
    report = {
        "classification": classification,
        "diagnostics": diagnostics,
        "pairs": pairs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite: {args.output}")
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
