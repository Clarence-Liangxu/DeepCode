#pragma once
#include <stdio.h>
#include <stdint.h>
#include <time.h>

typedef struct {
    const char *label;
    struct timespec start;
} ScopedTimer;

static inline void start_timer(ScopedTimer *t, const char *label)
{
    t->label = label;
    clock_gettime(CLOCK_MONOTONIC, &t->start);
}

static inline void end_timer(ScopedTimer *t)
{
    struct timespec end;
    clock_gettime(CLOCK_MONOTONIC, &end);
    long ns = (end.tv_sec - t->start.tv_sec) * 1000000000L + (end.tv_nsec - t->start.tv_nsec);
    printf("%s time: %ld ns\n", t->label, ns);
}

// 用于 GNU cleanup 属性自动调用 end_timer()
static inline void timer_cleanup(ScopedTimer *t)
{
    end_timer(t);
}

#define SCOPED_TIMER(name, label) \
    ScopedTimer name __attribute__((cleanup(timer_cleanup))); \
    start_timer(&name, label)
