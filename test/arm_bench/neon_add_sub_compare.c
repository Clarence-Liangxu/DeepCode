#include <arm_neon.h>
#include <stdio.h>
#include "timer.h"

#define LOOP_COUNT 100
#define VECTOR_LEN 4

typedef struct {
    float val[VECTOR_LEN];
} float32x4_wrap_t;

// 原始伪码实现
float32x4_wrap_t neon_add_sub_manual(float32x4_wrap_t Vn, float32x4_wrap_t Vm, int sub_op) {
    float32x4_wrap_t result;
    for (int e = 0; e < VECTOR_LEN; ++e) {
        float element1 = Vn.val[e];
        float element2 = Vm.val[e];
        result.val[e] = sub_op ? (element1 - element2) : (element1 + element2);
    }
    return result;
}

// NEON intrinsic 实现
float32x4_t neon_add_sub_intrinsic(float32x4_t Vn, float32x4_t Vm, int sub_op) {
    return sub_op ? vsubq_f32(Vn, Vm) : vaddq_f32(Vn, Vm);
}

int main() {
    // 初始化输入向量
    float32x4_wrap_t Vn_wrap = {{1.0f, 2.0f, 3.0f, 4.0f}};
    float32x4_wrap_t Vm_wrap = {{0.5f, 1.5f, 2.5f, 3.5f}};

    float32x4_wrap_t result_manual;
    float32x4_wrap_t result_intrinsic_wrap;

    float32x4_t Vn = vld1q_f32(Vn_wrap.val);
    float32x4_t Vm = vld1q_f32(Vm_wrap.val);
    float32x4_t result_intrinsic;

    // Manual 实现计时
    {
      SCOPED_TIMER(t, "manual");
      for (int i = 0; i < LOOP_COUNT; ++i)
        result_manual = neon_add_sub_manual(Vn_wrap, Vm_wrap, 0);
    }

    {
      SCOPED_TIMER(t, "intrinsic");

      for (int i = 0; i < LOOP_COUNT; ++i)
        result_intrinsic = neon_add_sub_intrinsic(Vn, Vm, 0);
    }
    // Intrinsic 实现计时

    vst1q_f32(result_intrinsic_wrap.val, result_intrinsic);

    // 打印加法结果
    printf("Manual result:     ");
    for (int i = 0; i < VECTOR_LEN; ++i)
        printf("%.2f ", result_manual.val[i]);
    printf("\n");

    printf("Intrinsic result:  ");
    for (int i = 0; i < VECTOR_LEN; ++i)
        printf("%.2f ", result_intrinsic_wrap.val[i]);
    printf("\n");

    return 0;
}
