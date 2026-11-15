"""Multi-page DOM-Delta compaction benchmark script for agent-browser-mesh."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from agent_browser_mesh.tools import BenchmarkMatrix


def main() -> None:
    bm = BenchmarkMatrix()
    rows = bm.run(reps=3)
    print(bm.format_table(rows))


if __name__ == "__main__":
    main()
