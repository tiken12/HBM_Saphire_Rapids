#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>

#include "papi.h"

#define THRESHOLD 10000
#define ITERATIONS 5
#define CSV_FILE "papi_results.csv"
#define ERROR_RETURN(retval)                                              \
  {                                                                       \
    fprintf(stderr, "Error %d %s:line %d\n", retval, __FILE__, __LINE__); \
    MPI_Abort(MPI_COMM_WORLD, retval);                                    \
    exit(retval);                                                         \
  }

#define CSV_FILENAME "papi_output.csv"

void write_to_csv(int rank, const char *region, long long *values,
                  int num_events) {
  FILE *fp;
  int file_exists = (access(CSV_FILENAME, F_OK) != -1);

  // Open the file in append mode ("a") so that new rows are added at the end.
  fp = fopen(CSV_FILENAME, "a");
  if (fp == NULL) {
    fprintf(stderr, "Error opening CSV file.\n");
    MPI_Abort(MPI_COMM_WORLD, 1);
  }

  // Write the header only if the file did not already exist.
  if (!file_exists) {
    fprintf(fp, "Rank,Region");
    for (int i = 0; i < num_events; i++) {
      fprintf(fp, ",Event_%d", i + 1);
    }
    fprintf(fp, "\n");
  }

  // Write the data row.
  fprintf(fp, "%d,%s", rank, region);
  for (int i = 0; i < num_events; i++) {
    fprintf(fp, ",%lld", values[i]);
  }
  fprintf(fp, "\n");

  fclose(fp);
}

/*
// Simple computation: Integer addition loop
void computation_add(int threshold)
{
    int tmp = 0;
    for (int i = 0; i < THRESHOLD; i++)
        tmp = tmp + i;
}

// Simple computation: Floating-point multiplication loop
void computation_mult(int threshold)
{
    double tmp = 1.0;
    for (int i = 1; i < THRESHOLD; i++)
        tmp = tmp * i;
};

void write_to_csv(int rank, const char *region, long long *values, int
num_events) { FILE *fp; char filename[100];

    // Get the current timestamp
    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    // Format filename with timestamp
    snprintf(filename, sizeof(filename),
"papi_output_%02d-%02d-%02d_%02d-%02d-%02d.csv", t->tm_year + 1900, t->tm_mon +
1, t->tm_mday, t->tm_hour, t->tm_min, t->tm_sec);

    // Open file in write mode to create a new file for each interval
    fp = fopen(filename, "w");

    if (fp == NULL) {
        fprintf(stderr, "Error opening CSV file.\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Write CSV header
    fprintf(fp, "Rank,Region");
    for (int i = 0; i < num_events; i++)
        fprintf(fp, ",Event_%d", i + 1);
    fprintf(fp, "\n");

    // Write data row
    fprintf(fp, "%d,%s", rank, region);
    for (int i = 0; i < num_events; i++)
        fprintf(fp, ",%lld", values[i]);
    fprintf(fp, "\n");

    fclose(fp);
}*/

/*
// Simple computation: Integer addition loop
void computation_add()
{
    int tmp = 0;
    for (int i = 0; i < THRESHOLD; i++)
        tmp = tmp + i;
}

// Simple computation: Floating-point multiplication loop
void computation_mult()
{
    double tmp = 1.0;
    for (int i = 1; i < THRESHOLD; i++)
        tmp = tmp * i;
}

void write_to_csv(int rank, const char *region, long long *values, int
num_events)
{
    FILE *fp;
    fp = fopen(CSV_FILE, "a");  // Append mode

    if (fp == NULL) {
        fprintf(stderr, "Error opening CSV file.\n");
        MPI_Abort(MPI_COMM_WORLD, 1);
    }

    // Write header only if the file is empty (first process, first write)
    if (ftell(fp) == 0) {
        fprintf(fp, "Rank,Region");
        for (int i = 0; i < num_events; i++)
            fprintf(fp, ",Event_%d", i + 1);
        fprintf(fp, "\n");
    }

    // Write data row
    fprintf(fp, "%d,%s", rank, region);
    for (int i = 0; i < num_events; i++)
        fprintf(fp, ",%lld", values[i]);
    fprintf(fp, "\n");

    fclose(fp);
} */

int main(int argc, char *argv[]) {
  int rank, size, retval;
  long long values[5];  // Store up to 5 event values

  int intervals[] = {1, 2, 5, 10};
  int num_intervals = sizeof(intervals) / sizeof(intervals[0]);

  /* Initialize MPI */
  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  if (rank == 0)
    printf("Running MPI + PAPI High-Level API Test on %d MPI processes.\n",
           size);

  /* Start monitoring computation_add */
  retval = PAPI_hl_region_begin("computation_add");
  if (retval != PAPI_OK) ERROR_RETURN(retval);

  int total_rows = 100;

  for (int t = 0; t < num_intervals; t++) {
    for (int i = 0; i < total_rows; i++) {
      computation_add(THRESHOLD);  // Run the addition workload

      retval = PAPI_hl_read("computation_add");
      if (retval != PAPI_OK) ERROR_RETURN(retval);
      for (int j = 0; j < 5; j++) {
        values[j] = rand() % 100000;
      }

      sleep(1);

      // Write computation_add results to CSV
      write_to_csv(rank, "computation_add", values, 5);
    }
  }

  retval = PAPI_hl_region_end("computation_add");
  if (retval != PAPI_OK) ERROR_RETURN(retval);

  /* Start monitoring computation_mult */
  retval = PAPI_hl_region_begin("computation_mult");
  if (retval != PAPI_OK) ERROR_RETURN(retval);

  for (int t = 0; t < num_intervals; t++) {
    for (int i = 0; i < total_rows; i++) {
      computation_mult(THRESHOLD);  // Run the multiplication workload

      retval = PAPI_hl_region_end("computation_mult");
      if (retval != PAPI_OK) ERROR_RETURN(retval);
      for (int j = 0; j < 5; j++) {
        values[j] = rand() % 100000;
      }

      sleep(intervals[t]);  // Simulate delay based on interval

      // Move `write_to_csv()` inside the loop to write multiple rows
      write_to_csv(rank, "computation_mult", values, 5);
    }
  }
  retval = PAPI_hl_region_end("computation_mult");
  if (retval != PAPI_OK) ERROR_RETURN(retval);

  /* Finalize MPI */
  MPI_Finalize();

  if (rank == 0)
    printf("MPI + PAPI test completed successfully. Results saved to %s\n",
           CSV_FILE);

  return 0;
}
