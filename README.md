# vLLM 离线安装包（Linux x86_64 / CPython 3.10）

为**无外网**的 Linux 机器准备的 vLLM + Transformers 离线安装包，共 **204 个 wheel，3.67 GB**。

因为 GitHub 有 **单文件 100 MB 硬限制**（本包中 `torch` 502 MB、`nvidia-cublas` 403 MB 等 10 个文件超限），
wheel 不放在 Git 仓库里，而是以 **4 个分卷 zip** 的形式挂在 Release 上：

> **Releases → `vllm-cp310-bundle` → 下载全部 4 个分卷**

## 版本

| 包 | 版本 |
| --- | --- |
| **vllm** | **0.31.0** |
| **transformers** | **5.17.0** |
| tokenizers | 0.23.3 |
| huggingface-hub | 1.33.0 |
| torch / torchaudio / torchvision | 2.13.0 / 2.11.0 / 0.28.0 |
| triton | 3.7.1 |
| numpy | 2.2.6 |

## 两个必须知道的约束

**1) 为什么是 vLLM 0.31.0 而不是 0.32.0**

`vllm 0.32.0` 的 PyPI 元数据是 `Requires-Python >=3.11,<3.15`，在 Python 3.10 上 pip 会直接判定
「无匹配版本」——即使它的轮子文件名是 `cp38-abi3`。目标机是 3.10 时，能装的最高版本就是 **0.31.0**。
要上 0.32.0，需先把目标机升到 Python 3.11 / 3.12。

**2) 目标机 glibc 必须 ≥ 2.31**（Ubuntu 20.04+ / Debian 11+ / RHEL 9+）

`llguidance 1.7.6`（vLLM 的硬依赖）只提供 `manylinux_2_31` 的 abi3 轮子。若目标机是 glibc 2.28–2.30
（Debian 10 / RHEL 8），这个包没有可用二进制轮子，需要改走源码编译或降级 vLLM。

另外包内 `nvidia-*` 为 **CUDA 13** 运行时（`cu13` 系列），目标机 NVIDIA 驱动需支持 CUDA 13。

## 离线机安装步骤

**① 取回并合并分卷**（4 个文件放在同一目录）

```bash
cat vllm-cp310-bundle.z01 vllm-cp310-bundle.z02 vllm-cp310-bundle.z03 \
    vllm-cp310-bundle.zip > vllm-cp310-bundle-full.zip

# 或者直接用 unzip 读取分卷（要求 4 个分卷都在同一目录）
unzip vllm-cp310-bundle.zip -d wheels
```

> 注：分卷是标准 Info-ZIP 拆分归档，`unzip` 会自动按 `.z01/.z02/.z03/.zip` 顺序拼接。

**② 校验**

```bash
cd wheels
sha256sum -c SHA256SUMS.txt --quiet && echo "ALL OK"
```

**③ 安装**

```bash
python3.10 -m pip install --no-index --find-links=. -r requirements-linux-cp310.txt
```

`--no-index` 保证完全不访问网络。锁定清单是 202 个包的完整传递依赖闭包，版本与包内轮子一一对应。

**④ 验证**

```bash
python3.10 -c "import vllm, transformers, torch; \
print(vllm.__version__, transformers.__version__, torch.__version__, torch.cuda.is_available())"
# 期望：0.31.0 5.17.0 2.13.0+cu130 True
```

## 仓库结构

```
.
├── README.md                                  # 本文件
├── download_bundle.ps1                        # 生成该离线包的脚本（Windows）
├── verify_bundle.py                           # 校验包完整性与平台标签
├── requirements.in                            # 顶层需求：vllm==0.31.0, transformers>=5.10.4
├── requirements.lock                          # 202 个包的锁定清单
└── vllm_transformers_offline_bundle/
    ├── README-offline-install.md              # 更详细的安装/排错说明
    ├── requirements-linux-cp310.txt           # 同上锁定清单（安装用）
    └── SHA256SUMS.txt                         # 204 个轮子的 SHA256
```

`*.whl` 已在 `.gitignore` 中忽略，实体文件通过 Release 分发。

## 这个包是怎么生成的

1. `uv pip compile --python-platform x86_64-manylinux_2_31 --python-version 3.10` 做**面向目标平台**的解析
   （绕开 pip 在 Windows 上把 `sys_platform == "win32"` 标记按宿主机求值导致的死锁，例如 `mcp → pywin32`）。
2. `pip download --no-deps -r requirements.lock` 逐包抓取，并把 `manylinux_2_31` 到 `manylinux_2_5`
   **每一档 glibc 标签都显式列出**——pip 的 `--platform` 只做字面匹配，不会向下兼容展开。
3. `verify_bundle.py` 校验：202 个轮子齐全、zip 未损坏、每个轮子的 tag 都能在 cp310/linux 上命中。
