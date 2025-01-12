// Copyright (c) 2023, DeepLink.
#include <ATen/ATen.h>

#include "csrc_dipu/aten/RegisterDIPU.hpp"
#include "csrc_dipu/aten/ops/DIPUCopy.hpp"

namespace dipu {
namespace native {

at::Tensor& custom_fallback_dipu_copy_(at::Tensor& self, const at::Tensor& src,
                                       bool non_blocking) {
  DIPU_OP_LOG_WARNING_ONCE("custom fallback to dipu copy, name=copy_"
                           << std::endl);
  static DIPUCopyInpOnCPU onCpuCopy;

  dipu::profile::RecordBlockCreator dipu_recorder(__FUNCTION__);
  onCpuCopy.run(self, src, non_blocking);
  return self;
}

}  // namespace native
}  // namespace dipu
