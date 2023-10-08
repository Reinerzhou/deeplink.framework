import torch
from common.utils import *
import torch_dipu
import pytest
import torch._dynamo as dynamo

class OpModule(torch.nn.Module):
    def forward(self, a, b):
        res_default = torch.ops.aten.bmm.default(a, b)
        return res_default

model = OpModule()
args = parse_args()
compiled_model = compile_model(model, args.backend, args.dynamic)


class TestBmm():
    @pytest.mark.parametrize("dtype", [torch.float32])
    @pytest.mark.parametrize("sizes", [Size(((5, 3, 4), (5, 4, 3)), ((5, 3, 4), (5, 4, 3))), Size(((3, 5, 2), (3, 2, 5)), ((3, 5, 2), (3, 2, 5)))])
    @pytest.mark.parametrize("compiled_model", compiled_model)
    def test_torch_bmm(self, sizes, dtype, compiled_model):
        device = get_device()
        size = sizes.dynamic if compiled_model.dynamic else sizes.static
        input1 = torch.randn(size[0], dtype=dtype)
        input2 = torch.randn(size[1], dtype=dtype)

        dicp_input1 = input1.to(device)
        dicp_input2 = input2.to(device)

        output = model(input1, input2)
        dynamo.reset()
        update_dynamo_config(compiled_model.dynamic)
        dicp_output = compiled_model.model(dicp_input1, dicp_input2)

        assert torch.allclose(output, dicp_output.cpu(), equal_nan=True)
