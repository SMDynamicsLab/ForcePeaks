# -*- coding: utf-8 -*-
"""
Created on Tue Oct 10 10:42:14 2023

@author: Tomas
"""
import pandas as pd 
import numpy as np
from plotnine import *
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from IPython import get_ipython
get_ipython().run_line_magic("matplotlib","qt5")


#%%

df = pd.read_csv("Df.csv")
df_voltage = pd.read_csv("Df_Voltage.csv")

df_voltage_2 = df_voltage.copy(deep=True)
df_voltage_2['Subjs'] = df_voltage_2.Subjs.astype('string')
df_voltage_2['Block'] = df_voltage_2.Block.astype('string')
df_voltage_2['Trial'] = df_voltage_2.Trial.astype('string')
df_voltage_2['Tap'] = df_voltage_2.Tap.astype('string')
df_voltage_2 = (df_voltage_2
				   # create label for plot grouping
				   .assign(label = lambda df: df.Subjs + df.Block + df.Trial + df.Tap)
				   )

df['Subjs'] = df.Subjs.astype('string')
df['Cond'] = df.Cond.astype('string')
df['Trial'] = df.Trial.astype('string')
df['Tap'] = df.Tap.astype('string')


#%%


df_voltage_3 = (df_voltage_2
                .groupby(['Subjs','Cond','Trial','Time'], as_index=False)
                .agg(mean_voltage = ('Voltages','mean'))
                .assign(label = lambda df: df.Subjs + df.Cond + df.Trial))

df_voltage_4 = (df_voltage_3
                .groupby(['Subjs','Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'),
                     voltage_std = ('mean_voltage','std'))
                .assign(label = lambda df: df.Subjs + df.Cond))

df_voltage_5 = (df_voltage_4
                .groupby(['Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'))
                .assign(label = lambda df: df.Cond))

df_voltage_6 = (df_voltage_2                                   #ESTE ES LA "BOLSA" PARA C/SUJETO
                .groupby(['Subjs','Cond','Time'], as_index=False)
                .agg(mean_voltage = ('Voltages','mean'))
                .assign(label = lambda df: df.Subjs + df.Cond))


df_voltage_7 = (df_voltage_6                                   #ESTE ES LA "BOLSA" 
                .groupby(['Cond','Time'], as_index=False)
                .agg(mean_voltage = ('mean_voltage','mean'))
                .assign(label = lambda df: df.Cond))

df_voltage_8 = (df_voltage_6                                   #ESTE ES LA "BOLSA" 
                .groupby(['Cond','Time'], as_index=False)
                .apply(lambda df: pd.Series({
		'mean_voltage': df.mean_voltage.mean(),
		'sd_voltage': df.mean_voltage.std(),
		'n_voltage': df.mean_voltage.count(),
		'ci_voltage': 1.96*df.mean_voltage.sem()
		}))
                .assign(label = lambda df: df.Cond))





#%% GRAFICA UN TAP DE UN TRIAL DE UNA COND DE UN SUJETO
tap_lenght=50

plt.figure()
plt.plot(df_voltage_2['Time'][:tap_lenght],df_voltage_2['Voltages'][:tap_lenght])

#%%% GRAFICA EL TAP PROMEDIO DE UN TRIAL PARA UN SUJETO

# plt.close("all")
plt.figure()
plt.plot(df_voltage_3['Time'][:tap_lenght],df_voltage_3['mean_voltage'][:tap_lenght])

#%%% GRAFICA EL TAP PROMEDIO DE UNA CONDICION PARA UN SUJETO

# plt.close("all")
plt.figure()
plt.plot(df_voltage_4['Time'][:tap_lenght],df_voltage_4['mean_voltage'][:tap_lenght])

#%%% GRAFICA EL TAP PROMEDIO DE TODOS LOS SUJETOS PARA UNA CONDICION

# plt.close("all")
plt.figure()
plt.plot(df_voltage_5['Time'][:tap_lenght],df_voltage_5['mean_voltage'][:tap_lenght])

#%% GRAFICA TODO






color_map = ["blue","magenta"]
shape_map = ["s","D"]
marker_size = 2
error_width = 0.25
fig_xsize = 10
fig_ysize = 6
x_lims = (-3,11)

plot_taps = (
 		 ggplot(df_voltage_2,
				   aes(x = 'Time', y = 'Voltages',
					   group = 'label',
					   color = 'Trial',
					   linetype = 'Cond'))
#					   shape = 'perturb_type'))
 		 + geom_line()
		 + geom_point()
# 		 + geom_errorbar(aes(x = 'beep',
# 						   ymin = "diff-ci_diff",
# 						   ymax = "diff+ci_diff"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps)




#%% GRAFICA EL TAP PROMEDIO DE CADA TRIAL PARA CADA CONDICION Y CADA SUJETO

color_map = ["blue","magenta"]
shape_map = ["s","D"]
marker_size = 2
error_width = 0.25
fig_xsize = 10
fig_ysize = 6
x_lims = (-3,11)

plot_taps_ave = (
 		 ggplot(df_voltage_3,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Trial',
					   linetype = 'Cond'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
# 		 + geom_errorbar(aes(x = 'beep',
# 						   ymin = "diff-ci_diff",
# 						   ymax = "diff+ci_diff"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave)




#%% GRAFICA PARA CADA SUJETO UN TAP PROMEDIO PARA CADA CONDICION

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_voltage_4,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Cond',
					   linetype = 'Subjs'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
 		 + geom_errorbar(aes(x = 'Time',
 						   ymin = "mean_voltage-voltage_std",
 						   ymax = "mean_voltage+voltage_std"),
					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)




#%%%

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_voltage_5,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Cond'))
# 					   linetype = 'Subjs'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-voltage_std",
#  						   ymax = "mean_voltage+voltage_std"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%%%

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_voltage_6,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Cond',
 					   linetype = 'Subjs'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-voltage_std",
#  						   ymax = "mean_voltage+voltage_std"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%%%

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_voltage_6,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Cond'))
 					   # linetype = 'Subjs'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-voltage_std",
#  						   ymax = "mean_voltage+voltage_std"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%%%

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_voltage_8,
				   aes(x = 'Time', y = 'mean_voltage',
					   group = 'label',
					   color = 'Cond'))
 					   # linetype = 'Subjs'))
#					   shape = 'perturb_type'))
 		 + geom_path()
		 + geom_point()
 		 + geom_errorbar(aes(x = 'Time',
 						   ymin = "mean_voltage-ci_voltage",
 						   ymax = "mean_voltage+ci_voltage"),
					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%% GRAFICA ASYNS VS TIEMPO ENTRE PICOS


fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df,
				   aes(x = 'Asyns_p2-Asyns_p1', y = 'Asyns_p1',
					   group = 'Cond',
					   color = 'Cond',
 					   # linetype = ''))
					   shape = 'Subjs'))
 		 # + geom_path()
		 + geom_point()
         + facet_grid('Subjs ~ Cond')
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-ci_voltage",
#  						   ymax = "mean_voltage+ci_voltage"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%%

df_2 = df.copy(deep=True)
# df_2[['Effector', 'Period']] = df_2['Cond'].str.extract('(\w+)(\w+)', expand=True)

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_2,
				   aes(x = 'Asyns_p2-Asyns_p1', y = 'Asyns_p2',
# 					   group = 'Cond',
					   color = 'Effector'))
 					   # linetype = ''))
# 					   shape = 'Subjs'))
 		 # + geom_path()
		 + geom_point()
         + facet_grid('~ Period')
         +geom_smooth(method="lm",colour='Black')
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-ci_voltage",
#  						   ymax = "mean_voltage+ci_voltage"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%% Ajuste lineal

# loading the csv file


 
# fitting the model
# df.columns = ['Head_size', 'Brain_weight']
model = smf.mixedlm(formula= 'Asyns_p2 ~ Peak_interval + Period', data=df, groups= df['Subjs']).fit()
# model_anova = sm.stats.anova_lm(model)
# model summary
print(model.summary())
# print(model_anova)

#%%

#scikit-learn
df_3 = df.copy(deep=True)
asyns_p2=df_2["Asyns_p2"]
asyns_p1=df_2["Asyns_p1"]

data_p1 = np.asarray(asyns_p1)
data_p2 = np.asarray(asyns_p2)

q1 = np.percentile(data_p1, 25)
q3 = np.percentile(data_p1, 75)
iqr = q3 - q1
threshold = 1.5 * iqr
outliers_p1 = np.where((data_p1 < q1 - threshold) | (data_p1 > q3 + threshold))

q1 = np.percentile(data_p2, 25)
q3 = np.percentile(data_p2, 75)
iqr = q3 - q1
threshold = 1.5 * iqr
outliers_p2 = np.where((data_p2 < q1 - threshold) | (data_p2 > q3 + threshold))

outliers_total = np.concatenate((outliers_p1, outliers_p2), axis=None)
data_filtrada_p1 = np.delete(data_p1, outliers_total)
data_filtrada_p2 = np.delete(data_p2, outliers_total)
effector_filtrado = np.delete(df_3['Effector'], outliers_total)
sujetos_filtrado = np.delete(df_3['Subjs'], outliers_total)
period_filtrado = np.delete(df_3['Period'], outliers_total)
peak_interval_filtrado = np.delete(df_3['Peak_interval'], outliers_total)
# print("Outliers of array ",data,"is : \n", data[outliers])
#%%

df_asyns = pd.DataFrame()

df_asyns['Asyns_p1']=data_filtrada_p1
df_asyns['Asyns_p2']=data_filtrada_p2
df_asyns['Subjs']=sujetos_filtrado
df_asyns['Effector']=effector_filtrado
df_asyns['Period']=period_filtrado
df_asyns['Peak_interval']=peak_interval_filtrado
#%%
df_2 = df.copy(deep=True)
# df_2[['Effector', 'Period']] = df_2['Cond'].str.extract('(\w+)(\w+)', expand=True)

fig_xsize = 20
fig_ysize = 10

plot_taps_ave_cond = (
 		 ggplot(df_asyns,
				   aes(x = 'Peak_interval', y = 'Asyns_p2',
# 					   group = 'Cond',
					   color = 'Effector',
 					   # linetype = '',
# 					   shape = 'Subjs',
))
 		 # + geom_path()
		 + geom_point()
         # + facet_grid('~ Period')
         +geom_smooth(method="lm",colour='Black')
#  		 + geom_errorbar(aes(x = 'Time',
#  						   ymin = "mean_voltage-ci_voltage",
#  						   ymax = "mean_voltage+ci_voltage"),
# 					   width = error_width)
#   		 + scale_x_continuous(limits=x_lims,breaks=range(x_lims[0],x_lims[1]+1,1))
 		 + theme_bw()
 		 + theme(legend_key = element_rect(fill = "white", color = 'white'),
				figure_size = (fig_xsize, fig_ysize))
		 )

print(plot_taps_ave_cond)

#%%

 
# fitting the model
# df.columns = ['Head_size', 'Brain_weight']
model = smf.mixedlm(formula= 'Asyns_p1 ~ Peak_interval + Period', data=df_asyns, groups= df_asyns['Subjs']).fit()
# model_anova = sm.stats.anova_lm(model)
# model summary
print(model.summary())
# print(model_anova)


#%%
from scipy import stats
slope, intercept, r, p, se = stats.linregress(data_filtrada_p2 - data_filtrada_p1,data_filtrada_p1 )
res = stats.linregress(data_filtrada_p2 - data_filtrada_p1,data_filtrada_p1 )
x = data_filtrada_p2 - data_filtrada_p1
plt.close("all")
plt.figure()
plt.plot(x,data_filtrada_p1 , 'o', label='original data')
plt.plot(x, res.intercept + res.slope*x, 'r', label='fitted line')
plt.legend()
plt.show()

#%%




















