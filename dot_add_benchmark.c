#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#define BILLION 1000000000.0
#define MAX_EXPONENT 30
#define TRIALS 10

void fill_random(double *arr, int N) {
    for (int i = 0; i < N; i++) {
        arr[i] = (double)rand() / RAND_MAX;
    }
}

double dot_product(double *A, double *B, int N, int repeat) {
    double sum = 0.0;
    for (int r = 0; r < repeat; r++) {
        for (int i = 0; i < N; i++) {
            sum += A[i] * B[i];
        }
    }
    return sum;
}

void vector_add(double *A, double *B, int N, int repeat) {
    for (int r = 0; r < repeat; r++) {
        for (int i = 0; i < N; i++) {
            A[i] += B[i];
        }
    }
}

double get_elapsed_time(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / BILLION;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <dot|add> <output_csv>\n", argv[0]);
        return 1;
    }

    const char *mode = argv[1];
    const char *csv_file = argv[2];

    FILE *f = fopen(csv_file, "w");
    if (!f) {
        perror("Failed to open CSV file");
        return 1;
    }

    fprintf(f, "Trial,N,Repeat,Elapsed,Bandwidth_GBps");
    if (strcmp(mode, "dot") == 0)
        fprintf(f, ",Dot_Result");
    fprintf(f, "\n");

    srand(time(NULL));

    for (int exp = 5; exp <= MAX_EXPONENT; exp++) {
        int N1 = 1 << exp;
        int N2 = (int)(N1 * 1.5);
        int sizes[2] = {N1, N2};

        for (int s = 0; s < 2; s++) {
            int N = sizes[s];
            int repeat = (N > 0) ? 10000000 / N : 1;
            if (repeat < 1) repeat = 1;

            for (int trial = 1; trial <= TRIALS; trial++) {
                double *A = malloc(N * sizeof(double));
                double *B = malloc(N * sizeof(double));
                if (!A || !B) {
                    fprintf(stderr, "Memory allocation failed at N=%d\n", N);
                    return 1;
                }

                fill_random(A, N);
                fill_random(B, N);

                struct timespec start, end;
                double result = 0.0;

                clock_gettime(CLOCK_MONOTONIC, &start);
                if (strcmp(mode, "dot") == 0) {
                    result = dot_product(A, B, N, repeat);
                } else if (strcmp(mode, "add") == 0) {
                    vector_add(A, B, N, repeat);
                } else {
                    fprintf(stderr, "Unknown mode: %s\n", mode);
                    return 1;
                }
                clock_gettime(CLOCK_MONOTONIC, &end);

                double elapsed = get_elapsed_time(start, end);
                size_t bytes = (strcmp(mode, "dot") == 0)
                               ? 2L * N * sizeof(double) * repeat
                               : 3L * N * sizeof(double) * repeat;

                double bandwidth = bytes / elapsed / 1e9;

                fprintf(f, "%d,%d,%d,%.6f,%.2f", trial, N, repeat, elapsed, bandwidth);
                if (strcmp(mode, "dot") == 0) {
                    fprintf(f, ",%.2f", result);
                }
                fprintf(f, "\n");
                fflush(f);

                free(A);
                free(B);
            }
        }
    }

    fclose(f);
    printf("Finished. Data written to %s\n", csv_file);
    return 0;
}
