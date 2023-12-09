#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>

#include "amx.h"
#include "util.h"

// mini matrix multiplication
#define N 4

int16_t A[N*N]; // assume that it is transposed
int16_t B[N*N];
int16_t C[N*N];

int main() {  
  rand_array(A,N*N);
  rand_array(B,N*N);

  print_mat(A,N,N);
  print_mat(B,N,N);

  AMX_SET();

  for (uint64_t i = 0; i < N; i++) {
    AMX_LDX(PMASK & (uint64_t)(B + 2*N*i) | (i << 56));
    AMX_LDY(PMASK & (uint64_t)(A + 2*N*i) | (i << 56));
  }

  for (uint64_t i = 0; i < N; i++) {
    for (uint64_t j = 0; j < N; j++)
      AMX_MAC16((j*64) | ((i*64) << 9));
  }

  for (uint64_t i = 0; i < N; i++)
    AMX_STZ((PMASK & ((uint64_t)C+2*N*i)) | (2*i << 56));

  AMX_CLR();

  print_mat(C,N,N);
}
