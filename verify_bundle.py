"""Verify the offline wheel bundle against the pinned lock file."""
import sys, zipfile
from pathlib import Path
from packaging.utils import parse_wheel_filename, canonicalize_name

root = Path(r"C:\Users\CSK\Desktop\Something\Code Dynasty\杂七杂八")
bundle = root / "vllm_transformers_offline_bundle"
lock = root / "requirements.lock"

wanted = {}
for line in lock.read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if "==" in line:
        n, v = line.split("==", 1)
        wanted[canonicalize_name(n)] = v

found, problems, corrupt = {}, [], []
for whl in sorted(bundle.glob("*.whl")):
    try:
        name, ver, _build, tags = parse_wheel_filename(whl.name)
    except Exception as e:                      # noqa: BLE001
        problems.append(f"UNPARSABLE {whl.name}: {e}")
        continue
    found[canonicalize_name(name)] = (str(ver), whl.name, tags)
    try:
        with zipfile.ZipFile(whl) as zf:
            bad = zf.testzip()
            if bad is not None:
                corrupt.append(f"{whl.name}: bad member {bad}")
    except Exception as e:                      # noqa: BLE001
        corrupt.append(f"{whl.name}: {e}")

missing = sorted(set(wanted) - set(found))
extra = sorted(set(found) - set(wanted))
version_mismatch = [
    f"{n}: lock={wanted[n]} wheel={found[n][0]}"
    for n in sorted(set(wanted) & set(found))
    if wanted[n] != found[n][0]
]

print(f"lock entries : {len(wanted)}")
print(f"wheel files  : {len(found)}")
print(f"total size   : {sum(p.stat().st_size for p in bundle.glob('*.whl')) / 2**30:.2f} GiB")
print(f"missing      : {missing or 'none'}")
print(f"extra        : {extra or 'none'}")
print(f"version diff : {version_mismatch or 'none'}")
print(f"corrupt      : {corrupt or 'none'}")
print(f"problems     : {problems or 'none'}")

# Sanity: nothing in the bundle should need a newer glibc than 2.31,
# and every wheel must be importable by CPython 3.10 on x86_64 Linux.
too_new = [n for n, (_, _, tags) in found.items()
           if not any(t.platform == "any"
                      or t.platform.startswith(("manylinux", "linux"))
                      for t in tags)]
print(f"non-linux/pure wheels: {too_new or 'none'}")

bad_py = []
for n, (_, fname, tags) in found.items():
    if not any(t.interpreter in ("py3", "py2.py3") or t.interpreter.startswith(("cp310", "cp39", "cp38", "cp37", "cp36"))
               and t.abi in ("none", "abi3")
               or t.interpreter == "cp310"
               for t in tags):
        bad_py.append(f"{fname}")
print(f"python-tag check failed: {bad_py or 'none'}")
sys.exit(1 if (missing or extra or version_mismatch or corrupt or problems) else 0)
