[![Lang](https://img.shields.io/badge/Lang-English-2ea043?style=for-the-badge)](README.md)
[![Lang](https://img.shields.io/badge/Lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-6e7781?style=for-the-badge)](README.zh-CN.md)

# vLLM + Transformers Offline Bundle

**A ready-to-carry wheel set for installing vLLM on an air-gapped Linux machine.**

204 wheels · 3.67 GB · Linux x86_64 · CPython 3.10

Because GitHub rejects any file over 100 MB (10 of these wheels exceed that — `torch` alone is 502 MB),
the wheels are **not** stored in Git. They ship as **4 split archive volumes attached to a Release**:

> **[Download the bundle →](https://github.com/ChenSK23/vllm/releases/tag/v0.31.0-cp310)**

---

## What's inside

| Package | Version |
| --- | --- |
| **vllm** | **0.31.0** |
| **transformers** | **5.17.0** |
| tokenizers | 0.23.3 |
| huggingface-hub | 1.33.0 |
| torch / torchaudio / torchvision | 2.13.0 / 2.11.0 / 0.28.0 |
| triton | 3.7.1 |
| numpy | 2.2.6 |
| CUDA runtime | 13.x (`nvidia-*` cu13 series) |

The bundle pins the **full transitive closure** — 202 packages — in
[`requirements-linux-cp310.txt`](vllm_transformers_offline_bundle/requirements-linux-cp310.txt).
Two extra wheels (`pip`, `wheel`) are included so a bare interpreter can bootstrap itself offline.

---

## Two constraints you must know

### 1. Why vLLM 0.31.0 and not 0.32.0

`vllm 0.32.0` declares `Requires-Python >=3.11,<3.15` on PyPI. On Python 3.10 `pip` refuses to
install it — even though the wheel filename says `cp38-abi3`. **0.31.0 is the newest vLLM that
supports Python 3.10.** Moving to 0.32.0 requires upgrading the target machine to 3.11 / 3.12 first.

### 2. glibc ≥ 2.31 on the target machine

`llguidance 1.7.6` — a hard dependency of vLLM — only publishes a `manylinux_2_31` abi3 wheel.
That makes 2.31 the floor for the whole bundle (Ubuntu 20.04+, Debian 11+, RHEL 9+).
On glibc 2.28–2.30 (Debian 10, RHEL 8) that single package has no usable binary wheel.

The bundled `nvidia-*` wheels are the **CUDA 13** runtime, so the NVIDIA driver must support CUDA 13.

---

## Reassemble the archive

Download all four volumes into one directory:

```bash
# recommended: let unzip read the volumes directly
unzip vllm-cp310-bundle.zip -d wheels

# alternative: concatenate into one file first
cat vllm-cp310-bundle.z01 vllm-cp310-bundle.z02 vllm-cp310-bundle.z03 \
    vllm-cp310-bundle.zip > vllm-cp310-bundle-full.zip
```

The extracted directory already contains `requirements-linux-cp310.txt` and `SHA256SUMS.txt`,
so it is self-contained.

---

## Install

```bash
cd wheels
sha256sum -c SHA256SUMS.txt --quiet && echo "ALL OK"

python3.10 -m pip install \
  --no-index \
  --find-links=. \
  -r requirements-linux-cp310.txt
```

`--no-index` guarantees pip never touches the network — it will not even query an index.

To install only the two top-level packages:

```bash
python3.10 -m pip install --no-index --find-links=. \
  vllm==0.31.0 transformers==5.17.0
```

---

## Verify

```bash
python3.10 -c "import vllm, transformers, torch; \
print(vllm.__version__, transformers.__version__, torch.__version__, torch.cuda.is_available())"

# expected: 0.31.0 5.17.0 2.13.0+cu130 True
```

---

## Repository layout

```
.
├── README.md                                  # this file (English)
├── README.zh-CN.md                            # 简体中文
├── download_bundle.ps1                        # script that built the bundle (Windows)
├── verify_bundle.py                           # verifies completeness + platform tags
├── requirements.in                            # vllm==0.31.0, transformers>=5.10.4
├── requirements.lock                          # 202 pinned packages
└── vllm_transformers_offline_bundle/
    ├── README-offline-install.md              # detailed install / troubleshooting notes
    ├── requirements-linux-cp310.txt           # same lock file, used for install
    └── SHA256SUMS.txt                         # SHA256 of every wheel
```

`*.whl` is git-ignored; the binaries live in the Release.

---

## How the bundle was built

1. **Resolve for the target platform.** `uv pip compile --python-platform x86_64-manylinux_2_31
   --python-version 3.10` evaluates environment markers against *Linux*, not the machine doing the
   download. Plain `pip download` on Windows deadlocks on `mcp → pywin32` (`sys_platform == "win32"`).
2. **Fetch wheels, not sdists.** `pip download --no-deps -r requirements.lock` with every
   `manylinux` level from `2_31` down to `2_5` listed explicitly — pip's `--platform` matching is
   literal and does not expand downward, so `manylinux_2_28` alone misses `numpy`'s `2_17` wheel
   and `nvidia-cuda-cupti`'s `2_25` wheel.
3. **Verify.** `verify_bundle.py` checks that all 202 wheels are present, that every zip passes a
   CRC test, and that every wheel tag intersects the cp310/manylinux tag set.

---

## License

This repository contains only packaging scripts and manifests. The wheels remain under the licenses
of their upstream projects (Apache-2.0 for vLLM, Apache-2.0 for Transformers, BSD-3-Clause for
PyTorch, and so on). No license file has been added to this repository yet.
