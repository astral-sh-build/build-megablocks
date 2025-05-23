#!/bin/bash
# Script to prepare the build environment for Megablocks.
#
# Example usage:
#   ./prepare_for_build.sh v0.9.0

set -euxo pipefail

export ROOT=`pwd`

if [ $# -ne 1 ]; then
    echo "Usage: $0 <megablocks_version>"
    echo "Example: $0 v0.9.0"
    exit 1
fi

MEGABLOCKS_VERSION=$1

# Ensure that the Megablocks version is supported.
if [ ! -d "${ROOT}/build_scripts/patches/${MEGABLOCKS_VERSION}" ]; then
    echo "Error: patches/${MEGABLOCKS_VERSION} directory does not exist"
    exit 1
fi

# Apply patches.
for patch in "${ROOT}/build_scripts/patches/${MEGABLOCKS_VERSION}"/*.patch; do
    patch -p1 -d ${ROOT} -i ${patch}
done
