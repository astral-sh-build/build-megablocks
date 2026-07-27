import importlib
from importlib.metadata import version

import pytest
import torch


@pytest.fixture(scope="module")
def device() -> torch.device:
    assert torch.cuda.is_available(), "The tests must run on a CUDA GPU"
    device = torch.device("cuda")
    return device


def test_published_cuda_wheel(device: torch.device) -> None:
    assert version("megablocks") == "0.10.0+cu.12.8.torch.2.7"
    assert torch.__version__ == "2.7.1+cu128"
    assert torch.version.cuda == "12.8"
    assert torch.cuda.get_device_name(device)


@pytest.mark.parametrize(
    "module_name", ["megablocks", "megablocks.ops", "megablocks_ops"]
)
def test_native_module(device: torch.device, module_name: str) -> None:
    assert importlib.import_module(module_name) is not None


@pytest.mark.parametrize("inclusive", [False, True])
def test_cuda_prefix_sum(device: torch.device, inclusive: bool) -> None:
    from megablocks import ops

    values = torch.tensor([2, 3, 5, 7], device=device, dtype=torch.int32)
    if inclusive:
        actual = ops.inclusive_cumsum(values, 0)
        expected = torch.tensor([2, 5, 10, 17], device=device, dtype=torch.int32)
    else:
        actual = ops.exclusive_cumsum(values, 0)
        expected = torch.tensor([0, 2, 5, 10], device=device, dtype=torch.int32)
    torch.testing.assert_close(actual, expected)


def test_cuda_histogram(device: torch.device) -> None:
    from megablocks import ops

    values = torch.tensor([[0, 2, 1, 2, 0, 3]], device=device, dtype=torch.int32)
    actual = ops.histogram(values, 4)
    expected = torch.tensor([[2, 1, 2, 1]], device=device, dtype=actual.dtype)
    torch.testing.assert_close(actual, expected)
