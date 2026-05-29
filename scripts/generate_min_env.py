#!/usr/bin/env python3
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN = ROOT / "environment.generated.yml"
OUT_MIN = ROOT / "environment.min.yml"
OUT_REQ = ROOT / "requirements-pip.txt"

if not GEN.exists():
    print(f"Missing {GEN}")
    sys.exit(1)

pip_lines = []
in_pip = False
with GEN.open() as f:
    for line in f:
        if line.strip().startswith("- pip:"):
            in_pip = True
            continue
        if in_pip:
            # pip entries are like '    - package==version'
            s = line.strip()
            if s.startswith("-"):
                pkg = s.lstrip("- ")
                pip_lines.append(pkg)

# write requirements
OUT_REQ.write_text("\n".join(pip_lines) + ("\n" if pip_lines else ""))

# minimal conda env: keep python, pip, numpy, scipy, scikit-learn, pandas
min_deps = [
    "name: asd_env",
    "channels:",
    "  - conda-forge",
    "  - defaults",
    "dependencies:",
    "  - python=3.11",
    "  - pip",
    "  - numpy",
    "  - scipy",
    "  - scikit-learn",
    "  - pandas",
    "  - python-dotenv",
]

OUT_MIN.write_text("\n".join(min_deps) + "\n")
print(f"Wrote {OUT_MIN} and {OUT_REQ}")
