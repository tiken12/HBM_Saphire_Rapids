#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define BILLION 1000000000.0

// Fill vector with random doubles
void fill_random(double *arr, int N) {
    for (int i = 0; i < N; i++) {
        arr[i] = (double)rand() / RAND_MAX;
    }
}

// Compute dot product (read A, read B → write 1 scalar)
double dot_product(double *A, double *B, int N, int repeat) {
    double sum = 0.0;
    for (int r = 0; r < repeat; r++) {
        for (int i = 0; i < N; i++) {
            sum += A[i] * B[i];
        }
    }
    return sum;
}

// Perform vector addition (read A, read B → write to A)
void vector_add(double *A, double *B, int N, int repeat) {
    for (int r = 0; r < repeat; r++) {
        for (int i = 0; i < N; i++) {
            A[i] += B[i];
        }
    }
}

// Calculate elapsed time
double get_elapsed_time(struct timespec start, struct timespec end) {
    return (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / BILLION;
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Usage: %s <N> <repeat> <mode: dot|add> <output_csv>\n", argv[0]);
        return 1;
    }

    int N = atoi(argv[1]);
    int repeat = atoi(argv[2]);
    const char *mode = argv[3];
    const char *csv_file = argv[4];

    // Allocate vectors
    double *A = malloc(N * sizeof(double));
    double *B = malloc(N * sizeof(double));
    if (!A || !B) {
        perror("Memory allocation failed");
        return 1;
    }

    srand(time(NULL));
    fill_random(A, N);
    fill_random(B, N);

    // Warm-up to stabilize performance
    for (int i = 0; i < N; i++) A[i] += B[i];

    struct timespec start, end;
    double result = 0.0;

    clock_gettime(CLOCK_MONOTONIC, &start);

    if (strcmp(mode, "dot") == 0) {
        result = dot_product(A, B, N, repeat);
    } else if (strcmp(mode, "add") == 0) {
        vector_add(A, B, N, repeat);
    } else {
        fprintf(stderr, "Unknown mode: %s (use 'dot' or 'add')\n", mode);
        return 1;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    double elapsed = get_elapsed_time(start, end);
    size_t bytes = 0;

    if (strcmp(mode, "dot") == 0) {
        bytes = 2L * N * sizeof(double) * repeat;  // read A + B
    } else if (strcmp(mode, "add") == 0) {
        bytes = 3L * N * sizeof(double) * repeat;  // read A + B + write A
    }

    double bandwidth = bytes / elapsed / 1e9; // GB/s

    // Append to CSV file
    FILE *f = fopen(csv_file, "a");
    if (!f) {
        perror("Could not open CSV file");
        return 1;
    }

    fprintf(f, "%s,%d,%d,%.6f,%.2f", mode, N, repeat, elapsed, bandwidth);
    if (strcmp(mode, "dot") == 0) {
        fprintf(f, ",%.2f", result);
    }
    fprintf(f, "\n");
    fclose(f);

    // Also print to stdout
    printf("Mode: %s | N = %d | Repeat = %d\n", mode, N, repeat);
    printf("Elapsed Time: %.6f s | Bandwidth: %.2f GB/s\n", elapsed, bandwidth);
    if (strcmp(mode, "dot") == 0) printf("Dot Product Result: %.2f\n", result);

    free(A);
    free(B);
    return 0;
}
