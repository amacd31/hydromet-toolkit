from sklearn import linear_model

class LinearRegressionModel(object):

    @property
    def name(self):
        return "LinearRegression"

    def __init__(self):
        self.lrm = linear_model.LinearRegression()

    def calibrate(self, predictors, predictands):
        predictor_list = []
        for p_name, predictor in predictors.items():
            predictor_list.append(predictor.values)
        predictors = list(zip(*predictor_list))

        predictand_list = []
        for p_name, predictand in predictands.items():
            predictand_list.append(predictand.values)
        predictands = list(zip(*predictand_list))

        self.model = self.lrm.fit(predictors, predictands)

    def forecast(self, predictors):
        predictor_list = []
        for p_name, predictor in predictors.items():
            predictor_list.append(predictor.values)
        predictors = list(zip(*predictor_list))

        return self.model.predict(predictors)
