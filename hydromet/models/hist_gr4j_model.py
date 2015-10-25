import calendar
import numpy as np

from hydromet.models.gr4j_model import GR4J

class HistGR4J(GR4J):

    def forecast(self, fc_date, predictors):

        warmup_data = {
            'P': predictors['P'][self.warmup_start_date:fc_date],
            'PE': predictors['PE'][self.warmup_start_date:fc_date],
        }

        self.warmup(warmup_data)

        p = predictors['P']
        grp = p.groupby(p.index.dayofyear)
        p_ens = {}

        start_dayofyear = fc_date.utctimetuple().tm_yday
        end_dayofyear = start_dayofyear + calendar.monthrange(fc_date.year, fc_date.month)[1]

        nens = len(grp.groups[1])

        p_ens = []
        for dayofyear in range(start_dayofyear, end_dayofyear):
            p_ens.append(p.ix[grp.groups[dayofyear]].values)

        p_ens = np.array(p_ens).T

        sims = []
        for ens in p_ens:
            fc_data = {
                'P': ens,
                'PE': predictors['PE']
            }

            sims.append(np.sum(self.run(fc_data)))

        return sims


