# build-megablocks

Pre-built Linux wheels for [MegaBlocks](https://github.com/databricks/megablocks), across Python,
PyTorch, CUDA, and CPU architectures.

## Installation

Following the PyTorch convention, artifacts are published to a separate index for each CUDA
version. Each wheel has a local version suffix that identifies the CUDA and PyTorch versions it
was built against, such as `megablocks==0.10.0+cu.12.8.torch.2.7`, and requires the
matching PyTorch release.

Pre-built wheels are available on [Astral's GPU indexes](https://wheels.astral.sh/index.html).
For example, to install a CUDA 12.8 build:

```console
$ uv add megablocks --index astral-cu128=https://wheels.astral.sh/simple/cu128/
```

This configures the index and uses it as the source for `megablocks`:

```toml
[tool.uv.sources]
megablocks = { index = "astral-cu128" }

[[tool.uv.index]]
name = "astral-cu128"
url = "https://wheels.astral.sh/simple/cu128/"
```

Or, with `uv pip`:

```console
$ uv pip install --index https://wheels.astral.sh/simple/cu128/ megablocks
```

## Supported versions

Wheels are available for the following `megablocks` version:

- [`0.10.0`](https://github.com/astral-sh-build/build-megablocks/releases/tag/v0.10.0-r4)

The latest release, MegaBlocks 0.10.0, supports the following combinations:

| PyTorch | Python   | `x86_64` CUDA | `aarch64` CUDA |
| ------- | -------- | ------------- | -------------- |
| 2.7.1   | 3.9-3.13 | 12.6, 12.8    | 12.8           |

## License

build-megablocks is licensed under the [Apache License, Version 2.0](LICENSE).

<div align="center">
  <a target="_blank" href="https://astral.sh" style="background:none">
    <img src="https://raw.githubusercontent.com/astral-sh/ruff/main/assets/svg/Astral.svg" alt="Made by Astral">
  </a>
</div>
