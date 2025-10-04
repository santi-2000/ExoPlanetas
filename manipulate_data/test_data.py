import pandas as pd

df_kepler = pd.read_csv("data/data_kepler.csv", sep='\t', engine='python')
print(df_kepler.head())
