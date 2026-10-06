#!/usr/bin/env python3
"""Seal a token-vs-example choice from final validation loss only."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def final_loss(path: Path) -> float:
    matches = re.findall(
        r"Iter 576: Val loss ([0-9]+(?:\.[0-9]+)?)", path.read_text()
    )
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one update-576 validation loss: {path}")
    return float(matches[0])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--token-log", type=Path, required=True)
    parser.add_argument("--example-log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite sealed selection: {args.output}")
    losses = {
        "token": final_loss(args.token_log),
        "example": final_loss(args.example_log),
    }
    selected = "token" if losses["token"] <= losses["example"] else "example"
    record = {
        "seed": args.seed,
        "rule": "lower final validation loss at update 576; ties choose token",
        "final_validation_loss": losses,
        "selected_condition": selected,
        "test_evaluation_status_at_seal": "NOT_STARTED",
        "fingerprints": {
            "token_log": sha256(args.token_log),
            "example_log": sha256(args.example_log),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(record, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
