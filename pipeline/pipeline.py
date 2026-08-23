import sys
import pandas as pd 


print('arguments', sys.argv)
month = int(sys.argv[1])

df = pd.DataFrame({"A": [1,2], "B":[3,4]})
df.to_parquet(f'output_{month}.parquet')
print(df.head())
print(f'hello pipeline, month={month}')