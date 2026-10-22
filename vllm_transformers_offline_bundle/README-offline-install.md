# vLLM + Transformers 离线安装包（Linux x86_64 / CPython 3.10）

本目录共 **204 个 `.whl` 文件，约 3.7 GB**，用于在**无外网**的 Linux 机器上安装 vLLM 与 Transformers。

## 1. 关键版本

| 包 | 版本 | 说明 |
| --- | --- | --- |
| vllm | **0.31.0** | 支持 Python 3.10 的最新 vLLM（满足“0.17.0 以上”） |
| transformers | **5.17.0** | 满足 `>=5.10.4`，且落在 vLLM 0.31 的 `<5.18.0` 约束内 |
| tokenizers | 0.23.3 | 匹配 transformers 5.17 |
| huggingface-hub | 1.33.0 | 匹配 transformers 5.17 |
| torch / torchaudio / torchvision | 2.13.0 / 2.11.0 / 0.28.0 | vLLM 0.31 的硬性 pin |
| triton | 3.7.1 | torch 2.13 对应版本 |
| numpy | 2.2.6 | 3.10 可用的最新 numpy 2.x |

> **为什么不是 vllm 0.32.0**：PyPI 上 `vllm-0.32.0` 的元数据是 `Requires-Python >=3.11,<3.15`，
> 在 Python 3.10 上 `pip` 会直接判定为“无匹配版本”（即使它的轮子是 `cp38-abi3`）。
> 目标机若是 3.10，唯一能装的最高版本就是 **0.31.0**；要上 0.32.0 必须先把目标机升到 3.11/3.12。

> **glibc 要求 ≥ 2.31**（Ubuntu 20.04+ / Debian 11+ / RHEL 9+）。
> 原因：`llguidance 1.7.6` 只提供 `manylinux_2_31` 的 abi3 轮子，且它是 vLLM 的硬依赖。
> 若目标机是 glibc 2.28–2.30（Debian 10 / RHEL 8），需要单独处理该包（见第 5 节）。

## 2. 传到离线机

把整个 `vllm_transformers_offline_bundle` 目录拷到离线机，例如 `/opt/vllm_transformers_offline_bundle`。

传输后建议先校验完整性：

```bash
cd /opt/vllm_transformers_offline_bundle
sha256sum -c SHA256SUMS.txt --quiet && echo "ALL OK"
```

## 3. 安装

```bash
python3.10 -m pip install \
  --no-index \
  --find-links=/opt/vllm_transformers_offline_bundle \
  -r /opt/vllm_transformers_offline_bundle/requirements-linux-cp310.txt
```

- `--no-index` 保证完全不碰网络（连索引都不查）。
- `--find-links` 指向本目录，pip 只从这里取轮子。
- `requirements-linux-cp310.txt` 是**完整锁定清单**（202 个包，含全部传递依赖），
  版本与本目录中的轮子一一对应，可保证可复现安装。

只装 vLLM + Transformers（依赖手动管）时可用：

```bash
python3.10 -m pip install --no-index --find-links=. \
  vllm==0.31.0 transformers==5.17.0
```

## 4. 验证

```bash
python3.10 -c "import vllm, transformers, torch; \
print('vllm        ', vllm.__version__); \
print('transformers', transformers.__version__); \
print('torch       ', torch.__version__); \
print('cuda avail  ', torch.cuda.is_available())"
```

期望输出含 `vllm 0.31.0`、`transformers 5.17.0`、`torch 2.13.0+cu130`（CUDA 版号以实际轮子为准）。

## 5. 可能遇到的问题

**a) 目标机没有 pip**
本目录已附带 `pip-26.2.2-py3-none-any.whl` 和 `wheel-0.48.0-py3-none-any.whl`：

```bash
python3.10 -m ensurepip --upgrade          # 或用下面两条
python3.10 -m zipfile -e pip-26.2.2-py3-none-any.whl /tmp/pipx
python3.10 /tmp/pipx/pip install --no-index --find-links=. pip wheel
```

**b) glibc < 2.31**
`llguidance` 无可用轮子。两个选择：
- 目标机装 Rust 工具链后从 sdist 编译（`llguidance-1.7.6.tar.gz`，需自行下载并带过去）；
- 或改用不需要 `llguidance` 的旧版 vLLM（0.17.x–0.2x 系列），但那会牵动一堆版本约束，需重新出包。

**c) 安装时报 `No matching distribution found for xxx`**
说明清单里有包在本目录缺失（传输损坏/漏拷）。先跑第 2 节的 `sha256sum -c` 定位。

**d) 显存/驱动的 CUDA 版本**
本包内的 `nvidia-*` 轮子为 **CUDA 13.x** 运行时库（`cu13` 系列）。
目标机驱动需支持 CUDA 13（NVIDIA 驱动 ≥ 580 左右）；否则请告知，可改出 cu12 版本。

## 6. 目录内容来源

全部来自 PyPI 官方源，目标平台标签：
`cp310` / `manylinux_2_31`（并向下兼容 2_28、2_27、2_24、2014 等全部低阶标签）。
解析方式：`uv pip compile --python-platform x86_64-manylinux_2_31 --python-version 3.10`，
下载方式：`pip download --no-deps -r` + 多 `--platform` 标签。
