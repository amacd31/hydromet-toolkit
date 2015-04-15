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
    Kling-Gupta efficiency.

    References:
        * Gupta, Hoshin V., Harald Kling, Koray K. Yilmaz, and Guillermo F. Martinez. "Decomposition of the Mean Squared Error and NSE Performance Criteria: Implications for Improving Hydrological Modelling." Journal of Hydrology 377, no. 1–2 (October 20, 2009): 80–91. doi:10.1016/j.jhydrol.2009.08.003.
*/
double kge(const void * obsv, const void * simv, int n) {
    const double * obs = (double *) obsv;
    const double * sim = (double *) simv;

    double obs_mean = gsl_stats_mean(obs, 1, n);
    double sim_mean = gsl_stats_mean(sim, 1, n);
    double obs_std = gsl_stats_sd(obs, 1, n);
    double sim_std = gsl_stats_sd(sim, 1, n);

    double beta = (sim_mean / obs_mean);
    double cov_so = gsl_stats_covariance_m(sim, 1, obs, 1, n, sim_mean, obs_mean);
    // Round to the nearest 5th decimal place to avoid floating point
    // comparison errors.
    cov_so = round(cov_so * 10000) / 10000;

    // Default to zero, we set later if sim_std != 0
    double alpha = 0;
    double r = 0;
    if (sim_std != 0) {
        alpha = sim_std / obs_std;
        r = cov_so / ((round(sim_std * obs_std * 10000) / 10000));
    }

    return 1 - sqrt(pow(r - 1, 2) + pow(alpha - 1, 2) + pow(beta - 1, 2));
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
