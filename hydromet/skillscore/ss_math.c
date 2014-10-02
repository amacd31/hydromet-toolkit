#include <stdio.h>
#include <math.h>
#include <gsl/gsl_statistics.h>

/*
    Mean Square Error
*/
double mse(const void * obsv, const void * simv, int n) {
    const double * obs = (double *) obsv;
    const double * sim = (double *) simv;

    int t;
    double sum_y = 0;
    for (t = 0; t < n; t++) {
        sum_y += pow(sim[t] - obs[t], 2);
    }

    return sum_y / n;
}

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

    if (e1 == 0) {
        return 1;
    }
    else {
        return 1 - e1 / e2;
    }
}

/*
    Root Mean Square Error
*/
double rmse(const void * obsv, const void * simv, int n) {
    return sqrt(mse(obsv, simv, n));
}
