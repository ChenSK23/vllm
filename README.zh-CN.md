[![Lang](https://img.shields.io/badge/Lang-English-6e7781?style=for-the-badge)](README.md)
[![Lang](https://img.shields.io/badge/Lang-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-2ea043?style=for-the-badge)](README.zh-CN.md)

# vLLM + Transformers 离线安装包

**给内网 / 无外网 Linux 机器准备的 vLLM 轮子合集。**

204 个 wheel · 3.67 GB · Linux x86_64 · CPython 3.10

GitHub 有 **单文件 100 MB 硬限制**（本包有 10 个文件超限，`torch` 一个就 502 MB），
所以 wheel **不放在 Git 仓库里**，而是以 **4 个分卷 zip** 挂在 Release 上：

> **[→ 下载安装包](https://github.com/ChenSK23/vllm/releases/tag/v0.31.0-cp310)**

---

## 包里有什么

| 包 | 版本 |
| --- | --- |
| **vllm** | **0.31.0** |
| **transformers** | **5.17.0** |
| tokenizers | 0.23.3 |
| huggingface-hub | 1.33.0 |
| torch / torchaudio / torchvision | 2.13.0 / 2.11.0 / 0.28.0 |
| triton | 3.7.1 |
| numpy | 2.2.6 |
| CUDA 运行时 | 13.x（`nvidia-*` cu13 系列） |

依赖是**完整闭包**——202 个包全部锁定在
[`requirements-linux-cp310.txt`](vllm_transformers_offline_bundle/requirements-linux-cp310.txt)。
另外附了 `pip` 和 `wheel` 两个轮子，这样裸解释器也能离线自举。

---

## 两个必须知道的约束

### 1. 为什么是 vLLM 0.31.0，不是 0.32.0

PyPI 上 `vllm 0.32.0` 的元数据是 `Requires-Python >=3.11,<3.15`。在 Python 3.10 上 `pip`
会直接判定「无匹配版本」——哪怕它的轮子文件名写着 `cp38-abi3`。**0.31.0 是最后一个支持
Python 3.10 的 vLLM**。要上 0.32.0，得先把目标机升到 3.11 / 3.12。

### 2. 目标机 glibc ≥ 2.31

`llguidance 1.7.6` 是 vLLM 的硬依赖，而它只提供 `manylinux_2_31` 的 abi3 轮子。
这一个包就把整个安装包的地板钉在了 2.31（Ubuntu 20.04+ / Debian 11+ / RHEL 9+）。
在 glibc 2.28–2.30（Debian 10、RHEL 8）上，这个包没有可用的二进制轮子。

包内的 `nvidia-*` 是 **CUDA 13** 运行时，因此 NVIDIA 驱动需支持 CUDA 13。

---

## 合并分卷

把 4 个分卷下载到同一个目录：

```bash
# 推荐：让 unzip 直接读分卷
unzip vllm-cp310-bundle.zip -d wheels

# 或者先拼接成一个文件
cat vllm-cp310-bundle.z01 vllm-cp310-bundle.z02 vllm-cp310-bundle.z03 \
    vllm-cp310-bundle.zip > vllm-cp310-bundle-full.zip
```

解压出来的目录里已经带好了 `requirements-linux-cp310.txt` 和 `SHA256SUMS.txt`，可以直接用。

---

## 安装

```bash
cd wheels
sha256sum -c SHA256SUMS.txt --quiet && echo "ALL OK"

python3.10 -m pip install \
  --no-index \
  --find-links=. \
  -r requirements-linux-cp310.txt
```

`--no-index` 保证 pip 完全不联网——连索引都不会查。

如果只想装两个顶层包：

```bash
python3.10 -m pip install --no-index --find-links=. \
  vllm==0.31.0 transformers==5.17.0
```

---

## 验证

```bash
python3.10 -c "import vllm, transformers, torch; \
print(vllm.__version__, transformers.__version__, torch.__version__, torch.cuda.is_available())"

# 期望：0.31.0 5.17.0 2.13.0+cu130 True
```

---

## 仓库结构

```
.
├── README.md                                  # 英文说明（默认）
├── README.zh-CN.md                            # 本文件
├── download_bundle.ps1                        # 生成该安装包的脚本（Windows）
├── verify_bundle.py                           # 校验完整性与平台标签
├── requirements.in                            # vllm==0.31.0, transformers>=5.10.4
├── requirements.lock                          # 202 个包的锁定清单
└── vllm_transformers_offline_bundle/
    ├── README-offline-install.md              # 更详细的安装 / 排错说明
    ├── requirements-linux-cp310.txt           # 同一份锁定清单（安装用）
    └── SHA256SUMS.txt                         # 每个 wheel 的 SHA256
```

`*.whl` 已在 `.gitignore` 里忽略，二进制走 Release。

---

## 这个包是怎么生成的

1. **面向目标平台做解析。** `uv pip compile --python-platform x86_64-manylinux_2_31
   --python-version 3.10` 会把环境标记按 **Linux** 求值，而不是按执行下载的机器。
   在 Windows 上直接 `pip download` 会死在 `mcp → pywin32`（`sys_platform == "win32"`）上。
2. **只取轮子，不取 sdist。** `pip download --no-deps -r requirements.lock`，并把
   `manylinux` 从 `2_31` 到 `2_5` 每一档都显式列出来——pip 的 `--platform` 只做字面匹配、
   不会向下展开，只写 `manylinux_2_28` 会漏掉 `numpy` 的 `2_17` 轮子和
   `nvidia-cuda-cupti` 的 `2_25` 轮子。
3. **校验。** `verify_bundle.py` 检查 202 个轮子齐全、每个 zip 通过 CRC 校验、
   每个轮子的 tag 都能在 cp310/manylinux 标签集中命中。

---

## 许可

本仓库只包含打包脚本和清单文件。wheel 本身遵循各自上游项目的许可证
（vLLM 为 Apache-2.0，Transformers 为 Apache-2.0，PyTorch 为 BSD-3-Clause 等）。
本仓库目前尚未添加 LICENSE 文件。
