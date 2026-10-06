#!/usr/bin/env python3
"""Generate a deterministic mixed short/long associative-recall SFT dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


SHORT_WORDS = (
    "amber azure beige black blue bronze brown coral cream cyan gold gray green "
    "indigo ivory jade khaki lilac lime magenta maroon mint navy ochre olive orange "
    "peach pearl pink plum purple red rose ruby rust salmon scarlet silver tan teal "
    "umber violet white yellow aqua copper charcoal crimson".split()
)

LONG_WORDS = (
    "apple arch beach bird brook cedar cloud coast comet coral crane dawn delta dune "
    "earth elm ember falcon field flame forest frost garden glade grove harbor hawk "
    "hill island lake leaf light maple meadow moon mountain oak ocean orchid pine plain "
    "pond rain raven reef river rock rose sage shore sky snow sparrow spring star stone "
    "storm sun tide trail tree valley wave willow wind winter wolf".split()
)

TRAIN_TEMPLATES = (
    "Give the stored response for key {key}.",
    "What response belongs to identifier {key}?",
    "Recall the assigned value of {key}.",
    "Return the memorized answer associated with {key}.",
)
VALID_TEMPLATE = "State the learned response attached to {key}."
TEST_TEMPLATE = "Which exact value was assigned to code {key}?"


def stable_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_records(seed: int, facts_per_skill: int) -> dict[str, list[dict]]:
    if facts_per_skill > len(SHORT_WORDS):
        raise ValueError("facts_per_skill exceeds the short-answer vocabulary")

    rng = random.Random(seed)
    short_targets = rng.sample(SHORT_WORDS, facts_per_skill)
    long_targets = []
    for _ in range(facts_per_skill):
        long_targets.append(" ".join(rng.sample(LONG_WORDS, 8)))

    splits: dict[str, list[dict]] = {"train": [], "valid": [], "test": []}
    for kind, targets, prefix in (
        ("short", short_targets, "S"),
        ("long", long_targets, "L"),
    ):
        for index, target in enumerate(targets):
            key = f"{prefix}{index:03d}"
            for template_id, template in enumerate(TRAIN_TEMPLATES):
                splits["train"].append(
                    {
                        "id": f"{key}-train-{template_id}",
                        "key": key,
                        "kind": kind,
                        "prompt": template.format(key=key),
                        "completion": target,
                    }
                )
            splits["valid"].append(
                {
                    "id": f"{key}-valid",
                    "key": key,
                    "kind": kind,
                    "prompt": VALID_TEMPLATE.format(key=key),
                    "completion": target,
                }
            )
            splits["test"].append(
                {
                    "id": f"{key}-test",
                    "key": key,
                    "kind": kind,
                    "prompt": TEST_TEMPLATE.format(key=key),
                    "completion": target,
                }
            )

    for split, records in splits.items():
        random.Random(seed + {"train": 11, "valid": 17, "test": 23}[split]).shuffle(records)
    return splits


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260809)
    parser.add_argument("--facts-per-skill", type=int, default=48)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    splits = build_records(args.seed, args.facts_per_skill)
    manifest = {
        "generator_seed": args.seed,
        "facts_per_skill": args.facts_per_skill,
        "train_templates_per_fact": len(TRAIN_TEMPLATES),
        "long_completion_words": 8,
        "splits": {},
    }
    for split, records in splits.items():
        path = args.output / f"{split}.jsonl"
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
        manifest["splits"][split] = {
            "records": len(records),
            "short": sum(r["kind"] == "short" for r in records),
            "long": sum(r["kind"] == "long" for r in records),
            "sha256": stable_hash(path),
        }

    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
