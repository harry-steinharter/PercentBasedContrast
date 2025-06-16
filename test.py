# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %%
df1 = pd.read_csv('Baselines/18_baseline.csv')
df2 = pd.read_csv('Baselines/19_baseline.csv')
df = pd.concat([df1, df2], ignore_index=True)
# %%
# Group by 'id' and compute mean of 'TC'
grouped = df.groupby('id')['TC'].mean()

# Plot
grouped.plot(kind='bar')
plt.xlabel('Participant ID')
plt.ylabel('Mean TC')
plt.title('Mean TC per Participant')
plt.tight_layout()
plt.show()