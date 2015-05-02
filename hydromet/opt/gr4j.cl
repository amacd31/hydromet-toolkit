#pragma OPENCL EXTENSION cl_amd_printf : enable
/**
GR4J OpenCL implementation for parallel computation of simulations from many parameter sets.

References:
    Perrin, Charles, Claude Michel, and Vazken Andréassian. "Improvement of a Parsimonious Model for Streamflow Simulation." Journal of Hydrology 279, no. 1-4 (August 25, 2003): 275-89. doi:10.1016/S0022-1694(03)00225-7.

    "Operation GR4J Hydrology Team Irstea Antony." Accessed September 11, 2014. http://webgr.irstea.fr/modeles/journalier-gr4j-2/fonctionnement_gr4j/.


*/

/*
    Unit hydrograph ordinates for UH1 derived from S-curves.
*/
float s_curves1(float t, float x4) {

    if (t <= 0) {
        return 0;
    }
    else if (t < x4) {
        return pow((t/x4), (float)2.5);
    }
    else { // t >= x4
        return 1;
    }
}

/*
    Unit hydrograph ordinates for UH2 derived from S-curves.
*/
float s_curves2(float t, float x4) {

    if (t <= 0) {
        return 0;
    }
    else if (t < x4) {
        return 0.5*pow((t/x4), (float)2.5);
    }
    else if (t < 2*x4) {
        return 1 - 0.5*pow((2 - t/x4), (float)2.5);
    }
    else { // t >= x4
        return 1;
    }
}

kernel void gr4j(__global const float* precip,
        __global const float* potential_evap,
        int data_len,
        __global const float* X1_a,
        __global const float* X2_a,
        __global const float* X3_a,
        __global const float* X4_a,
        __global const float* qobs,
        __global float* skillscores,
        __global float* qsim) {

    int gid = get_global_id(0);
    float X1 = X1_a[gid];
    float X2 = X2_a[gid];
    float X3 = X3_a[gid];
    float X4 = X4_a[gid];

    float production_store = 0;
    float routing_store = 0;

    float X[30] = {0};
    int NH = 10;

    float UH1[10] = {0};
    float UH2[20] = {0};

    int t;
    for (t = 1; t < NH; t++) {
        X[t - 1] = s_curves1(t, X4) - s_curves1(t-1, X4);
    }

    for (t = 1; t < 2*NH; t++) {
        X[NH + t - 1] = s_curves2(t, X4) - s_curves2(t-1, X4);
    }

    for (t = 0; t < 30; t++) {
    }

    int i;
    int j;
    float P;
    float E;
    float net_evap;
    float WS;
    float reservoir_production;
    float routing_pattern;
    float ps_div_x1;
    float percolation;
    float groundwater_exchange;
    float R2;
    float QR;
    float QD;
    float sum_square_error = 0;
    for (i = 0; i < data_len; i++) {
        P = precip[i];
        E = potential_evap[i];

        if (P > E) {
            net_evap = 0;
            WS = (P - E)/X1;
            WS = WS > 13 ? 13 : WS;

            reservoir_production = (X1 * (1 - pow(production_store/X1,2)) * tanh(WS)) / (1 + production_store/X1 * tanh(WS));

            routing_pattern = P-E-reservoir_production;
        }
        else {
            WS = (E - P)/X1;
            WS = WS > 13 ? 13 : WS;
            ps_div_x1 = (2 - production_store/X1) * tanh(WS);
            net_evap = production_store * (ps_div_x1) /
                    (1 + (1 - production_store/X1) * tanh(WS));

            reservoir_production = 0;
            routing_pattern = 0;
        }

        production_store = production_store - net_evap + reservoir_production;

        percolation = production_store / pow((1 + pow((production_store/(float)2.25/X1),(float)4)),(float)0.25);

        routing_pattern = routing_pattern + (production_store-percolation);
        production_store = percolation;

        for (j = 0; j <= NH - 2; j++) {
            UH1[j] = UH1[j+1] + X[j]*routing_pattern;
        }

        for (j = 0; j <= NH - 2; j++) {
            UH2[j] = UH2[j+1] + X[j+NH]*routing_pattern;
        }

        UH2[19] = X[29] * routing_pattern;
        groundwater_exchange = X2 * pow((routing_store / X3),(float)3.5);

        routing_store = fmax(0, routing_store + UH1[0] * (float)0.9 + groundwater_exchange);

        R2 = routing_store / pow((1 + pow((routing_store / X3),4)),(float)0.25);
        QR = routing_store - R2;
        routing_store = R2;
        QD = fmax(0, UH2[0]*0.1+groundwater_exchange);
        qsim[gid*data_len + i] = QR + QD;

        // Calc MSE sum
        sum_square_error += pow(qsim[gid*data_len + i] - qobs[i], 2);
    }


    skillscores[gid] = sum_square_error / data_len;

}
