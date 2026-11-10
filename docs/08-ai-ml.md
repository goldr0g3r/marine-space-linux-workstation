# AI/ML on a 4 GB RTX 3050

## A useful, realistic scope

This laptop is suitable for Python/data science, classical ML, small vision models, inference and carefully sized training exercises. Four gigabytes of VRAM is a hard constraint shared with any graphics workload using that GPU. Large models, high-resolution vision batches and heavy GPU simulation will exceed it quickly. Start with CPU baselines, small batches, modest input resolution and one GPU workload at a time.

Use remote compute when a project requires more memory; do not make the workstation setup depend on running large models locally. If you upgrade system RAM later, GPU VRAM remains unchanged.

## Python projects

Use a separate environment and lockfile for each project. Python 3.12 is a conservative starting point; verify the current framework's supported versions before changing it. [uv project documentation](https://docs.astral.sh/uv/guides/projects/).

```bash
mkdir -p "$HOME/Projects/robotics-ml"
cd "$HOME/Projects/robotics-ml"
uv init --python 3.12
uv add numpy scipy pandas matplotlib scikit-learn jupyterlab
uv run python -c 'import numpy; print(numpy.__version__)'
uv run jupyter lab --ip=127.0.0.1 --no-browser
```

Keep the generated access token private; do not bind a notebook to all network interfaces as a convenience. Commit `pyproject.toml` and `uv.lock`. Exclude datasets, trained weights, caches and secrets.

## PyTorch and CUDA

First verify the **host driver** with `nvidia-smi`. Its displayed CUDA version is the driver's supported CUDA ceiling, not proof that a toolkit or PyTorch runtime is installed.

Use PyTorch's current Linux/Pip/Python installation selector to choose a CUDA wheel supported by your driver. Translate the package/index choice into the documented uv PyTorch integration so it is recorded in the project. Do not copy an old hardcoded CUDA wheel URL from a blog. [PyTorch selector](https://pytorch.org/get-started/locally/), [uv PyTorch guide](https://docs.astral.sh/uv/guides/integration/pytorch/).

For a first CPU-only learning environment, add the packages with a named index:

```bash
uv add torch torchvision --index pytorch=https://download.pytorch.org/whl/cpu
```

That command binds `torch` and `torchvision` to the `pytorch` index under `[tool.uv.sources]`, but it does not mark the index explicit. Checked with uv 0.13.1: without that flag, other packages such as NumPy and Pillow were also locked from the PyTorch index instead of PyPI. Edit the generated entry in `pyproject.toml` to match the uv guide's pattern:

```toml
[[tool.uv.index]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cpu"
explicit = true
```

An existing lockfile keeps its recorded sources, so remove `uv.lock` and run `uv lock` again after the edit. Then confirm in `uv.lock` that only the torch packages list the PyTorch index as their source.

For GPU work, replace the index with the **current selector-compatible CUDA index** and resolve the lockfile again. Review `pyproject.toml` to confirm torch packages are bound to that index. Wheel availability depends on Python version and platform.

After installing a CUDA build, run a numerical smoke test:

```bash
uv run python - <<'PY'
import torch
print('torch:', torch.__version__, 'wheel CUDA:', torch.version.cuda)
assert torch.cuda.is_available(), 'CUDA unavailable: check wheel, driver, device access'
print('GPU:', torch.cuda.get_device_name(0))
a = torch.ones((512, 512), device='cuda')
b = a @ a
torch.cuda.synchronize()
assert torch.allclose(b, torch.full_like(b, 512))
print('CUDA tensor test passed')
PY
```

Do not install the full host CUDA toolkit unless compiling CUDA code/extensions requires it. Framework runtime, toolkit and host driver versions are related but different components. The tensor test was not run during document preparation because PyTorch/CUDA setup was not installed for this task.

## Memory habits

- Start batch size at 1–4 for vision, then measure. Mixed precision helps compatible workloads but does not guarantee a model fits.
- Use small input images first; keep DataLoader worker counts modest on 16 GB RAM.
- Close the simulator before training. Monitor GPU memory with `nvidia-smi` during the workload.
- Do not fix out-of-memory errors by repeatedly changing distro. Reduce the model/batch or move the workload.
- Keep only active models/datasets on the internal SSD; log dataset versions and download sources.

## Robotics-oriented progression

Start with a sensor dataset: clean units/timestamps, split by recording session to prevent leakage, train a simple baseline, and evaluate on held-out sessions. Then try a small image classifier or detector. Measure inference latency, memory and failure cases before integrating it into a ROS node.

For GPU containers, validate CDI using [the container guide](06-containers-and-ros.md), then run a numerical test inside a framework image compatible with the host driver. A successful container `nvidia-smi` alone does not establish that training or GUI rendering works.
