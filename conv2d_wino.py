from typing import Tuple
from tinygrad.runtime.ops_metal import RawMetalBuffer, MetalProgram
from tinygrad.helpers import dtypes
import numpy as np
from string import Template
import functools

LID = 1

_src_tmpl = Template(open("conv2d_wino_2x2_3x3.metal", "r").read()) 

@functools.lru_cache(maxsize=None)
def _prgs(N, HW, C, F):
  src = _src_tmpl.substitute(N=N,HW=HW,C=C,F=F)
  return MetalProgram("filter_transform", src), MetalProgram("conv", src)

def conv2d_wino(ims:RawMetalBuffer, fs:RawMetalBuffer, size:Tuple[int,int,int,int]) -> RawMetalBuffer:
  N, HW, C, F = size
  tfs = RawMetalBuffer(F*C*4*4, dtypes.float32)
  out = RawMetalBuffer(N*F*(HW-2)*(HW-2), dtypes.float32)
  ft_prg, conv_prg = _prgs(N, HW, C, F)
  ft_prg([F,1,1], [C,1,1], tfs, fs, wait=True)
  conv_prg([HW//16, HW//(16*LID), 1], [1, LID, 1], out, ims, tfs, wait=True)
  return out
