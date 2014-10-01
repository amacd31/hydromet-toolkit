#include <stdio.h>
#include <math.h>
#include <gsl/gsl_statistics.h>

/*
    Nash-Sutcliffe efficiency.
*/
double nse(const void * obsv, const void * simv, int n) {
    const double * obs = (double *) obsv;
    const double * sim = (double *) simv;

    double mean = gsl_stats_mean(obs, 1, n);

    int t;
    double e1 = 0;
    double e2 = 0;
    for (t = 0; t < n; t++) {
        e1 += pow(obs[t] - sim[t], 2);
        e2 += pow(obs[t] - mean, 2);
    }

    return 1 - e1 / e2;
}
