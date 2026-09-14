"""Benchmark the planar-pulse fixture with the currently installed native solver.

Run from a source checkout, before and after rebuilding the solver:
    OMP_NUM_THREADS=1 python tools/benchmark_solver.py

Times include setup and detector recording. No field history is allocated.
Use the same interpreter, build type, and thread count for comparisons.
"""

import argparse
from pathlib import Path
import runpy
import statistics
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    fixture = runpy.run_path(
        str(Path(__file__).resolve().parents[1] / "tests" / "test_physics_accuracy.py")
    )["plane"]
    for spacing in (1.0, 0.5):
        fixture(spacing)  # Warm up imports, allocation, and OpenMP workers.
        durations = []
        for _ in range(args.repeats):
            start = time.perf_counter()
            fixture(spacing)
            durations.append(time.perf_counter() - start)
        print(
            f"dx={spacing:g}: median={statistics.median(durations):.4f}s, min={min(durations):.4f}s ({args.repeats} runs)"
        )


if __name__ == "__main__":
    main()
