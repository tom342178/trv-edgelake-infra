"""Entry point for the EdgeLake Operator."""

import subprocess
import sys


def main():
    """Run the operator using kopf."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "kopf",
            "run",
            "--standalone",
            "--all-namespaces",
            "src/edgelake_operator/operator.py",
        ],
        check=True,
    )


if __name__ == "__main__":
    main()
