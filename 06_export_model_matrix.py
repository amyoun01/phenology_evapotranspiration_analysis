#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 09:33:27 2021

@author: ay394
"""


import os
import datetime as dt
import numpy as np
import pandas as pd
from scipy.stats import zscore

wdir = '/Volumes/GoogleDrive/My Drive/Young_evapotranspiration_phenology_analysis'

os.chdir(wdir + '/data/ancillary_data')

phenoflux_metadata = pd.read_csv("pheno_flux_sites_to_use.csv",\
                                 parse_dates=[9,10])

sites = phenoflux_metadata.fluxsite
start_date = phenoflux_metadata.start_date
end_date = phenoflux_metadata.end_date

transformation_df = pd.DataFrame({'transformation':['np.log','np.sqrt','np.log']})
transformation_df.index = ['VPD','precip_10day','gcc']

vars_to_use = ['EF','ET','netrad','Gs','VPD','gcc','VPD','gdd','cdd','t_air','precip_10day','SWC']

for i in range(0,len(sites)):
    
    os.chdir(wdir + '/results/flux_data/daily')
    fluxdat = pd.read_csv(sites[i] + '_daily_values.csv', \
                          parse_dates = [0])
    fluxdat = fluxdat.replace(to_replace=-9999,value=np.nan)
    
    dates = fluxdat.date
    yr = dates.dt.year
    
    dates_to_keep = (dates >= start_date[i]) & (dates <= end_date[i])
        
    fluxdat = fluxdat.loc[dates_to_keep]
    fluxdat = fluxdat.reset_index(drop = True)

    # Shift baseline gcc values for US-UMB due to change in camera FOV
    if sites[i] == 'US-UMB':
        
        gcc_to_shift = fluxdat.date.dt.date > dt.date(2014,5,1)
        fluxdat.loc[gcc_to_shift,'gcc'] = fluxdat.loc[gcc_to_shift,'gcc']+0.06  
    
    # Remove 2014 data
    if (sites[i] == 'US-KFS') | (sites[i] == 'US-UMB'):
        fluxdat.loc[yr == 2014,'to_remove_id'] = 1
  
    fluxdat.loc[fluxdat.gdd < 0,'gdd'] = np.nan
    fluxdat.loc[fluxdat.cdd < 0,'cdd'] = np.nan
    
    if (sites[i] == 'US-Var'):
        
        fluxdat.loc[fluxdat.Gs > 0.1,'to_remove_id'] = 1
  
    model_matrix = np.asarray(fluxdat[vars_to_use])
  
    for t in range(0,transformation_df.shape[0]):
    
      var_id = np.where(fluxdat.columns == transformation_df.index[t])[0]
    
      var_t = np.array(fluxdat[fluxdat.columns[var_id]])
      
      if transformation_df.transformation[t] == 'np.log':
          var_t[var_t <= 0] = np.nan
      
      fluxdat[fluxdat.columns[var_id]] = eval(transformation_df.iloc[t][0]+'(var_t)')
    
    
    complete_cases = fluxdat.to_remove_id == 0
    fluxdat = fluxdat.loc[complete_cases]
    fluxdat = fluxdat.reset_index(drop=True)
    fluxdat_new = fluxdat[vars_to_use]
    
    mm_std = zscore(fluxdat_new,axis = 0,nan_policy = 'omit')    
    mm_std = pd.DataFrame(data = mm_std,columns=vars_to_use)
    # mm_std = mm_std.dropna(axis = 0)
    mm_std = mm_std.replace(to_replace = np.nan,value = -9999.0)
    
    pd.DataFrame.to_csv(mm_std, \
                        wdir + '/results/flux_data/model_matrices/' + sites[i] + '_model_matrix.csv', \
                        index = False)

# End of script ---------------------------------------------------------------------