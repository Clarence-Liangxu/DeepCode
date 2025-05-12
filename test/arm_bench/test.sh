#!/usr/bin/env bash

rm -f main
gcc -O2 -march=armv8-a+simd -o main neon_add_sub_compare.c

./main
