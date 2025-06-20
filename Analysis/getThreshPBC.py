# %%
import glob
from psychopy.tools.filetools import fromFile
from psychopy.data import functionFromStaircase, FitLogistic
import pylab
import os
import numpy as np
import pandas as pd
# %%
def MC(L_max, L_min = 112.6482, nDigits=4):
  # Function to find michelson contrast using L_min as the background luminance in PsychoPy units
  michelson_contrast = (L_max-L_min) / (L_max+L_min)
  michelson_contrast = round(michelson_contrast,nDigits)
  return michelson_contrast

def toCandela(x, nDigits = 10):
  CandelaPerMeterSquared = (x * 112.417) + 112.6482
  CandelaPerMeterSquared = round(CandelaPerMeterSquared,nDigits)
  return CandelaPerMeterSquared

# %% Get Files
csv_files = glob.glob("../Experiment_outputs/*.csv")
df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
df = df[ (~df['label'].str.endswith('_null')) ]
# %%
new_df = {'id':[], 
          'label':[], 
          'FC':[],
          'threshold':[],
          'baseline':[],
          'FC_michelson':[], 
          'threshold_michelson':[],
          'baseline_michelson':[]}

# set to 0.5 for Yes/No (or PSE). Set to 0.8 for a 2AFC threshold
threshVal = 0.5

# set to zero for Yes/No (or PSE). Set to 0.5 for 2AFC
expectedMin = 0.0

for this_id in df.id.unique():
    baseline = df.loc[(df['id'] == this_id) &
                      (df['label'] == '100'), 'FC'].iloc[0]
    baseline_mich = MC(toCandela(baseline))

    for this_label in df.label.unique():
            
        allIntensities, allResponses = [], []
        
        this_subset = df.loc[(df["id"] == this_id) &
                                (df["label"] == this_label)]
        FC_dict = this_subset.groupby("label")["FC"].unique().apply(list).to_dict()
        this_FC = FC_dict[this_label][0]

        allIntensities.extend(this_subset["TC"].tolist())
        allResponses.extend(this_subset["response"].tolist())

        i, r, n = functionFromStaircase(allIntensities, allResponses, bins='unique')
        combinedInten, combinedResp, combinedN = i, r, n
        combinedN = pylab.array(combinedN)  # convert to array so we can do maths

        fit = FitLogistic(combinedInten, combinedResp, expectedMin=expectedMin,
                                sems=1.0 / combinedN,
                                optimize_kws={'maxfev':int(1e6)})
        
        thresh = fit.inverse(threshVal)

        this_FC_mich = MC(toCandela(this_FC))
        this_thresh_mich = MC(toCandela(thresh))

        print(f'{this_id}, {this_label}, {this_FC_mich}: {this_thresh_mich} w/ baseline == {baseline_mich}')
        new_df['id'].append(this_id)
        new_df['label'].append(this_label)
        new_df['FC'].append(this_FC)
        new_df['threshold'].append(thresh)
        new_df['baseline'].append(baseline)
        new_df['FC_michelson'].append(this_FC_mich)
        new_df['threshold_michelson'].append(this_thresh_mich)
        new_df['baseline_michelson'].append(baseline_mich)
# pd.DataFrame(new_df)

# %%
new_df_pd = pd.DataFrame(new_df)
new_df_pd.to_csv('df1Way_fromPy.csv', index=False)
# %%
