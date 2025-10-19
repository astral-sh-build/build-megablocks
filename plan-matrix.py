# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "packaging",
# ]
# ///

import json

from packaging.version import Version

# NOTE(ww): Megablocks doesn't support PyTorch 2.8 or 2.9 yet.
# Once it does, we can add them here to widen the matrix below,
# or just remove this filter entirely.
MEGABLOCKS_SUPPORTED_TORCH_VERSIONS = [
    "2.7.1",
]

ARCH_TORCH_PAIRS = {
    "x86_64": ["2.7.1", "2.8.0", "2.9.0"],
    "aarch64": ["2.7.1", "2.8.0", "2.9.0"],
}

# Supported Python versions for each PyTorch version.
# We use these to filter out the matrix.
TORCH_PYTHON_SUPPORT = {
    "2.7.1": ["3.9", "3.10", "3.11", "3.12", "3.13"],
    "2.8.0": ["3.9", "3.10", "3.11", "3.12", "3.13"],
    "2.9.0": ["3.10", "3.11", "3.12", "3.13", "3.14"],
}

# Minimum and maximum CUDA versions for each PyTorch version.
PYTORCH_CUDA_RANGES: dict[str, tuple[str, str]] = {
    "2.7": ("11.8", "12.8"),
    "2.8": ("11.8", "12.8"),
    "2.9": ("12.6", "13.0"),
}

# Actual CUDA versions to build against for each PyTorch version.
PYTORCH_CUDA_VERSIONS: dict[str, list[str]] = {
    "2.7": ["12.8.0"],
    "2.8": ["12.9.0"],
    "2.9": ["12.9.0", "13.0.0"],
}

# CUDA architectures to build against for each PyTorch version.
TORCH_CUDA_ARCH_LIST = {
    # https://github.com/pytorch/pytorch/blob/134179474539648ba7dee1317959529fbd0e7f89/.ci/manywheel/build_cuda.sh#L55
    "2.7": "7.5;8.0;8.6;9.0;10.0;12.0+PTX",
    # https://github.com/pytorch/pytorch/blob/ba56102387ef21a3b04b357e5b183d48f0afefc7/.ci/manywheel/build_cuda.sh#L56
    "2.8": "7.5;8.0;8.6;9.0;10.0;12.0+PTX",
    # https://github.com/pytorch/pytorch/blob/0fabc3ba44823f257e70ce397d989c8de5e362c1/.ci/manywheel/build_cuda.sh#L56
    "2.9": "7.5;8.0;8.6;9.0;10.0;12.0+PTX",
}

# The glibc version to use for each PyTorch version, for manylinux builds.
TORCH_GLIBC_VERSION: dict[str, str] = {
    "2.4": "2_17",
    "2.5": "2_17",
    "2.6": "2_24",
    "2.7": "2_24",
    "2.8": "2_28",
    "2.9": "2_28",
}

AUDITWHEEL_BLANKET_EXCLUDES = [
    "libcuda.so",
    "libcuda.so.1",
    "libc10.so",
    "libc10_cuda.so",
    "libtorch.so",
    "libtorch_python.so",
    "libtorch_cpu.so",
    "libtorch_cuda.so",
    "libtorch_cuda_cpp.so",
    "libtorch_cuda_cu.so",
    "libcufile_rdma.so",
    "libcufile_rdma.so.1",
    "libcufile.so.1",
    "libcufile.so.0",
    "libcufile.so",
    "libcurand.so.10",
]

AUDITWHEEL_CUDA_VERSION_EXCLUDES = {
    "11": [
        "libcudart.so.11",
        "libcudart.so.11.0",
    ],
    "12": [
        "libcudart.so.12",
        "libcudart.so.12.0",
    ],
    "13": [
        "libcudart.so.13",
        "libcudart.so.13.0",
    ],
}

# Matrix exclusions.
EXCLUSIONS = [
    # No exclusions yet.
]


def main() -> None:
    # Every matrix member is a primary 5-tuple of:
    # `torch-version`: the PyTorch version as "X.Y.Z", e.g. "2.7.0"
    # `python-version`: the Python version as "3.X", e.g. "3.10"
    # `cuda-version`: the CUDA version as "X.Y.Z", e.g. "11.8.0"
    # `cxx11-abi`: "TRUE" or "FALSE"
    # `target-arch`: the target architecture, e.g. "x86_64" or "aarch64"

    rows = []
    for target_arch, torch_versions in ARCH_TORCH_PAIRS.items():
        for torch_version in torch_versions:
            if torch_version not in MEGABLOCKS_SUPPORTED_TORCH_VERSIONS:
                continue

            for python_version in TORCH_PYTHON_SUPPORT[torch_version]:
                torch_version_parsed = Version(torch_version)
                torch_x_y = f"{torch_version_parsed.major}.{torch_version_parsed.minor}"
                cuda_versions = PYTORCH_CUDA_VERSIONS[torch_x_y]
                for cuda_version in cuda_versions:
                    row = {
                        "target-arch": target_arch,
                        "torch-version": str(torch_version_parsed),
                        "python-version": python_version,
                        "cuda-version": cuda_version,
                        # TODO(ww): Parametrize this? The original
                        # unrolled matrix had both TRUE and FALSE in ways
                        # that I couldn't discern a pattern for.
                        "cxx11-abi": "TRUE",
                    }

                    if row not in EXCLUSIONS:
                        rows.append(row)

    # Transform each row to add various nice-to-have representations of fields.
    for row in rows:
        # `CI_*` variables: same as the original ones.
        row["CI_CUDA_VERSION"] = row["cuda-version"]
        row["CI_TORCH_VERSION"] = row["torch-version"]
        row["CI_PYTHON_VERSION"] = row["python-version"]

        # `MATRIX_CUDA_VERSION`: XY instead of X.Y
        cuda_version = Version(row["cuda-version"])
        row["MATRIX_CUDA_VERSION"] = f"{cuda_version.major}{cuda_version.minor}"

        # `MATRIX_TORCH_VERSION`: `torch-version`, but only X.Y, no patch
        torch_version = Version(row["torch-version"])
        row["MATRIX_TORCH_VERSION"] = f"{torch_version.major}.{torch_version.minor}"

        # `MATRIX_PYTHON_VERSION`: same as `python-version`, but with the dot removed
        row["MATRIX_PYTHON_VERSION"] = row["python-version"].replace(".", "")

        # `MANYLINUX_CUDA_VERSION`: X.Y instead of X.Y.Z
        row["MANYLINUX_CUDA_VERSION"] = f"{cuda_version.major}.{cuda_version.minor}"

        # `MANYLINUX_CUDA_COMPAT_VERSION`: X-Y instead of X.Y.Z
        row["MANYLINUX_CUDA_COMPAT_VERSION"] = (
            f"{cuda_version.major}-{cuda_version.minor}"
        )

        # MANYLINUX_GLIBC_VERSION: the glibc version to use for manylinux builds.
        row["MANYLINUX_GLIBC_VERSION"] = TORCH_GLIBC_VERSION[
            row["MATRIX_TORCH_VERSION"]
        ]

        # `CI_AUDITWHEEL_EXCLUDES`: `--exclude {lib}` for each lib that should
        # be excluded when running `auditwheel repair`.
        cuda_major = str(cuda_version.major)
        auditwheel_excludes = (
            AUDITWHEEL_BLANKET_EXCLUDES
            + AUDITWHEEL_CUDA_VERSION_EXCLUDES.get(cuda_major, [])
        )
        row["CI_AUDITWHEEL_EXCLUDES"] = " ".join(
            f"--exclude {lib}" for lib in auditwheel_excludes
        )

        # TORCH_CUDA_VERSION: the CUDA version to download PyTorch for.
        # This is the CUDA version clamped to the min/max supported by the
        # given PyTorch version.
        # e.g. we can have system CUDA version being 11.7 but if torch==1.12 then we need to download the wheel from cu116
        # see https://github.com/pytorch/pytorch/blob/main/RELEASE.md#release-compatibility-matrix
        torch_x_y = f"{torch_version.major}.{torch_version.minor}"
        minv, maxv = PYTORCH_CUDA_RANGES[torch_x_y]
        torch_cuda_version = max(
            min(Version(row["cuda-version"]), Version(maxv)), Version(minv)
        )
        row["TORCH_CUDA_VERSION"] = (
            f"{torch_cuda_version.major}{torch_cuda_version.minor}"
        )

        row["TORCH_CUDA_ARCH_LIST"] = TORCH_CUDA_ARCH_LIST[torch_x_y]

        # RUNNER: the GitHub Actions runner to use.
        if row["target-arch"] == "x86_64":
            row["RUNNER"] = "depot-ubuntu-24.04-64"
        elif row["target-arch"] == "aarch64":
            row["RUNNER"] = "depot-ubuntu-24.04-arm-64"
        else:
            raise ValueError(f"Unknown target arch: {row['target-arch']}")

    print(json.dumps(rows))


if __name__ == "__main__":
    main()
