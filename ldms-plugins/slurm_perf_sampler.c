#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ldms.h>
#include <ldmsd.h>
#include <ldmsd_sampler_base.h>

static ldms_set_t set = NULL;
static base_data_t base;
static int metric_offset = 0;

// Example metric names
static const char *metric_names[] = {
    "job_id",
    "user_id",
    "bandwidth_MBps",
    NULL
};

static int slurm_perf_config(struct ldmsd_plugin *self, struct attr_value_list *kwl, struct attr_value_list *inst_avl) {
    base = base_config(self, "slurm_perf", kwl, inst_avl);
    if (!base) return -1;
    return 0;
}

static int slurm_perf_sample(struct ldmsd_sampler *self) {
    ldms_transaction_begin(set);
    
    // Simulated data – replace with real SLURM + perf/PAPI calls
    ldms_set_u64(set, metric_offset + 0, 123456);   // job_id
    ldms_set_u64(set, metric_offset + 1, 1001);     // user_id
    ldms_set_double(set, metric_offset + 2, 15432.0); // bandwidth_MBps

    ldms_transaction_end(set);
    return 0;
}

static int slurm_perf_set_create(struct ldmsd_sampler *self) {
    ldms_schema_t schema = base_schema_new("slurm_perf", base);
    if (!schema) return ENOMEM;

    metric_offset = 0;
    ldms_schema_metric_add(schema, "job_id", LDMS_V_U64);
    ldms_schema_metric_add(schema, "user_id", LDMS_V_U64);
    ldms_schema_metric_add(schema, "bandwidth_MBps", LDMS_V_D64);

    set = base_set_new("slurm_perf", base, schema);
    if (!set) return ENOMEM;
    return 0;
}

static void slurm_perf_term(struct ldmsd_plugin *self) {
    base_del(base);
    set = NULL;
}

static struct ldmsd_sampler slurm_perf_sampler = {
    .base = {
        .name = "slurm_perf",
        .type = LDMSD_PLUGIN_SAMPLER,
        .config = slurm_perf_config,
        .term = slurm_perf_term,
    },
    .sample = slurm_perf_sample,
    .set_new = slurm_perf_set_create,
};

struct ldmsd_plugin *ldmsd_plugin_get() {
    return &slurm_perf_sampler.base;
}
