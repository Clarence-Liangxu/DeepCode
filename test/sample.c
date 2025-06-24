#include <stdio.h>

// 数组加法
void array_add(const float *a, const float *b, float *result, int n) {
    for (int i = 0; i < n; ++i) {
        result[i] = a[i] + b[i];
    }
}

// 数组减法
void array_sub(const float *a, const float *b, float *result, int n) {
    for (int i = 0; i < n; ++i) {
        result[i] = a[i] - b[i];
    }
}

// 数组乘法
void array_mul(const float *a, const float *b, float *result, int n) {
    for (int i = 0; i < n; ++i) {
        result[i] = a[i] * b[i];
    }
}

// 数组除法
void array_div(const float *a, const float *b, float *result, int n) {
    for (int i = 0; i < n; ++i) {
        result[i] = a[i] / b[i];
    }
}

// FMA: result[i] = a[i] * b[i] + c[i]
void array_fma(const float *a, const float *b, const float *c, float *result, int n) {
    for (int i = 0; i < n; ++i) {
        result[i] = a[i] * b[i] + c[i];
    }
}

// 测试主函数
int main() {
    float a[4] = {1.0, 2.0, 3.0, 4.0};
    float b[4] = {5.0, 6.0, 7.0, 8.0};
    float c[4] = {9.0, 10.0, 11.0, 12.0};
    float result[4];

    array_add(a, b, result, 4);
    printf("Add: ");
    for (int i = 0; i < 4; ++i) printf("%.2f ", result[i]);
    printf("\n");

    array_sub(a, b, result, 4);
    printf("Sub: ");
    for (int i = 0; i < 4; ++i) printf("%.2f ", result[i]);
    printf("\n");

    array_mul(a, b, result, 4);
    printf("Mul: ");
    for (int i = 0; i < 4; ++i) printf("%.2f ", result[i]);
    printf("\n");

    array_div(a, b, result, 4);
    printf("Div: ");
    for (int i = 0; i < 4; ++i) printf("%.2f ", result[i]);
    printf("\n");

    array_fma(a, b, c, result, 4);
    printf("FMA: ");
    for (int i = 0; i < 4; ++i) printf("%.2f ", result[i]);
    printf("\n");

    return 0;
}
