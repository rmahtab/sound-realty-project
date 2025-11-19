import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class HouseDateFeatures(BaseEstimator, TransformerMixin):
    def __init__(self, sale_date_col="date", yr_built_col="yr_built", yr_renov_col="yr_renovated"):
        self.sale_date_col = sale_date_col
        self.yr_built_col = yr_built_col
        self.yr_renov_col = yr_renov_col

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        # Extract year from sale_date string
        X["sale_year"] = X[self.sale_date_col].str[:4].astype(int)
        # house age
        X["house_age"] = X["sale_year"] - X[self.yr_built_col]
        # years since renovation (0 if never renovated)
        X["renovated_yrs_ago"] = np.where(X[self.yr_renov_col] > 0,
                                          X["sale_year"] - X[self.yr_renov_col],
                                          X["house_age"])
        # drop original columns
        X = X.drop(columns=[self.sale_date_col, self.yr_built_col, self.yr_renov_col, "sale_year"])
        return X
