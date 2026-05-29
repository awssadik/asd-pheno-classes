#!/usr/bin/env python3
import pathlib
from collections import OrderedDict

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQ = ROOT / "conda_requirements.txt"
OUT = ROOT / "environment.generated.yml"

conda_pkgs = []
pip_pkgs = []
name_version = {}

with REQ.open() as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("platform:"):
            continue
        # split on '='; entries are like name=version=build or name=version or name=version=pypi_0
        parts = line.split("=")
        name = parts[0]
        # ignore bizarre internal package markers
        if name.startswith("_"):
            continue
        if len(parts) >= 3 and parts[-1].lower().startswith("pypi"):
            # pip package; reconstruct name==version if version present
            version = parts[1] if len(parts) >= 2 else None
            if version:
                pip_pkgs.append(f"{name}=={version}")
            else:
                pip_pkgs.append(name)
        else:
            # conda package: use name=version (drop build string if present)
            version = parts[1] if len(parts) >= 2 else None
            if version:
                conda_pkgs.append(f"{name}={version}")
            else:
                conda_pkgs.append(name)

# Deduplicate while preserving order
def dedup(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

conda_pkgs = dedup(conda_pkgs)
pip_pkgs = dedup(pip_pkgs)

# ensure python is specified (prefer existing python line)
py = None
for entry in conda_pkgs:
    if entry.startswith("python="):
        py = entry
        break
if not py:
    py = "python=3.11"
    conda_pkgs.insert(0, py)

yml_lines = []
yml_lines.append("name: asd_env")
yml_lines.append("channels:")
yml_lines.append("  - conda-forge")
yml_lines.append("  - defaults")
yml_lines.append("dependencies:")
for p in conda_pkgs:
    yml_lines.append(f"  - {p}")
if pip_pkgs:
    yml_lines.append("  - pip:")
    for p in pip_pkgs:
        yml_lines.append(f"    - {p}")

OUT.write_text("\n".join(yml_lines))
print(f"Wrote {OUT}")
