#!/bin/bash
# Script to prepare the build environment for DeepSpeed.
#
# Example usage:
#   ./prepare_for_build.sh v0.16.7

set -euxo pipefail

export ROOT=`pwd`

if [ $# -ne 1 ]; then
    echo "Usage: $0 <deepspeed_version>"
    echo "Example: $0 v0.16.7"
    exit 1
fi

DEEPSPEED_VERSION=$1

# # Ensure that the DeepSped version is supported.
# if [ ! -d "${ROOT}/build_scripts/patches/${DEEPSPEED_VERSION}" ]; then
#     echo "Error: patches/${DEEPSPEED_VERSION} directory does not exist"
#     exit 1
# fi

python -c "import torch; print(torch._C._GLIBCXX_USE_CXX11_ABI)"

# # Apply patches.
# for patch in "${ROOT}/build_scripts/patches/${DEEPSPEED_VERSION}"/*.patch; do
#     patch -p1 -d ${ROOT} -i ${patch}
# done
