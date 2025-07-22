#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <malloc.h>
#include <arm_neon.h>

// 获取高精度时间（微秒）
static uint64_t get_current_time_us() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000000 + tv.tv_usec;
}

// 初始化随机数据
void init_random_data(uint16_t* data, int size) {
    for (int i = 0; i < size; i++) {
        data[i] = rand() % 65536; // 0-65535的随机数
    }
}

// 标量版本实现
void scalar_vaba_u16(uint16_t* dst, uint16_t* a, uint16_t* b, int size) {
    for (int i = 0; i < size; i++) {
        int32_t diff = a[i] - b[i];
        dst[i] += (uint16_t)(diff > 0 ? diff : -diff);
    }
}

// NEON intrinsic优化版本
void neon_vaba_u16(uint16_t* dst, uint16_t* a, uint16_t* b, int size) {
    int i = 0;
    for (; i <= size - 4; i += 4) { // 每次处理4个16位元素（64位）
        uint16x4_t va = vld1_u16(a + i);
        uint16x4_t vb = vld1_u16(b + i);
        uint16x4_t vdst = vld1_u16(dst + i);
        vdst = vaba_u16(vdst, va, vb);
        vst1_u16(dst + i, vdst);
    }
    // 处理剩余元素
    for (; i < size; i++) {
        int32_t diff = a[i] - b[i];
        dst[i] += (uint16_t)(diff > 0 ? diff : -diff);
    }
}

int main() {
    const int TEST_SIZE = 1024;
    const int ITERATIONS = 10000;
    
    // 分配对齐内存（16字节对齐）
    uint16_t* a = (uint16_t*)memalign(16, TEST_SIZE * sizeof(uint16_t));
    uint16_t* b = (uint16_t*)memalign(16, TEST_SIZE * sizeof(uint16_t));
    uint16_t* dst_scalar = (uint16_t*)memalign(16, TEST_SIZE * sizeof(uint16_t));
    uint16_t* dst_neon = (uint16_t*)memalign(16, TEST_SIZE * sizeof(uint16_t));
    uint16_t* dst_initial = (uint16_t*)memalign(16, TEST_SIZE * sizeof(uint16_t));

    // 初始化随机种子
    srand(time(NULL));

    // 初始化输入数据
    init_random_data(a, TEST_SIZE);
    init_random_data(b, TEST_SIZE);
    init_random_data(dst_initial, TEST_SIZE);

    // 测试标量版本
    uint64_t start = get_current_time_us();
    for (int i = 0; i < ITERATIONS; i++) {
        memcpy(dst_scalar, dst_initial, TEST_SIZE * sizeof(uint16_t));
        scalar_vaba_u16(dst_scalar, a, b, TEST_SIZE);
    }
    uint64_t scalar_time = get_current_time_us() - start;

    // 测试NEON版本
    start = get_current_time_us();
    for (int i = 0; i < ITERATIONS; i++) {
        memcpy(dst_neon, dst_initial, TEST_SIZE * sizeof(uint16_t));
        neon_vaba_u16(dst_neon, a, b, TEST_SIZE);
    }
    uint64_t neon_time = get_current_time_us() - start;

    // 验证结果
    int errors = 0;
    for (int i = 0; i < TEST_SIZE; i++) {
        if (dst_scalar[i] != dst_neon[i]) {
            if (errors < 5) {
                printf("Mismatch at %d: a=%u, b=%u, scalar=%u, neon=%u\n",
                       i, a[i], b[i], dst_scalar[i], dst_neon[i]);
            }
            errors++;
        }
    }

    if (errors > 0) {
        printf("Total errors: %d\n", errors);
    } else {
        printf("Results verified\n");
    }

    // 打印性能数据
    printf("Scalar avg time: %.2f us\n", (double)scalar_time / ITERATIONS);
    printf("NEON avg time: %.2f us\n", (double)neon_time / ITERATIONS);
    printf("Speedup: %.2fx\n", (double)scalar_time / neon_time);

    // 释放内存
    free(a);
    free(b);
    free(dst_scalar);
    free(dst_neon);
    free(dst_initial);

    return 0;
}