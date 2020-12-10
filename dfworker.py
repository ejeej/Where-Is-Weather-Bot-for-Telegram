import datetime
import random

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas
from mpl_toolkits.basemap import Basemap
from scipy.stats import skew


def get_tmpr(uid, df_file, month, day):
    '''
    По заданному номеру месяца и дню определяет номер недели в году для этого дня, 
    начиная с 1 января, и из заданного файла с данными о погоде возвращает 
    отфильтрованные в нём данные для этой недели в году.
    '''
    df = pandas.read_csv(df_file)

    date_diff = datetime.date(2020, month, day) - datetime.date(2020, 1, 1)
    week = date_diff.days // 7 + 1
    
    filtered_df = df[df['WEEK'] == week]
    tmpr_min = filtered_df['TEMP'].min()
    tmpr_max = filtered_df['TEMP'].max()

    df_filtered_week = '%s-df_filtered_week.csv' % str(uid)
    filtered_df.to_csv(df_filtered_week, index=False, encoding='utf-8')

    return df_filtered_week, tmpr_min, tmpr_max

def get_prcp(uid, df_file, desired_min_temp, desired_max_temp):
    '''
    По заданному диапазону желаемой температуры отфильтровывает из базы подходящие
    наблюдения.
    '''
    df = pandas.read_csv(df_file)

    filtered_df = df[(df['TEMP'] >= desired_min_temp) & (df['TEMP'] <= desired_max_temp)]
    prcp_min = filtered_df['ANY_PRCP'].min()
    prcp_max = filtered_df['ANY_PRCP'].max()

    df_filtered_tmpr = '%s-df_filtered_tmpr.csv' % str(uid)
    filtered_df.to_csv(df_filtered_tmpr, index=False, encoding='utf-8')

    return df_filtered_tmpr, prcp_min, prcp_max

def get_final(uid, df_file, prcp_min_desired, prcp_max_desired):
    '''
    По заданному диапазону желаемого количества дней с осадками отфильтровывает
    из базы подходящие наблюдения.
    '''
    df = pandas.read_csv(df_file)

    filtered_df = df[(df['ANY_PRCP'] >= prcp_min_desired) & (df['ANY_PRCP'] <= prcp_max_desired)]

    df_filtered_final = '%s-df_filtered_final.csv' % str(uid)
    filtered_df.to_csv(df_filtered_final, index=False, encoding='utf-8')

    return df_filtered_final

def get_results(uid, df_file):
    '''
    Получает на вход pandas DataFrame, наносит на карту точки по координатам (колонки 'LATITUDE, LONGITUDE'). Если диапазон между
    максимальной и минимальной температурой (колонка TEMP) больше 1 градуса Цельсия, раскрашивает точки в зависимости от температуры.
    Сохраняет файл с картой. На выходе - тапл с названием файла, количеством найденных уникальных
    мест, лист со ссылками на google maps с <=5 из них.
    '''
    df = pandas.read_csv(df_file)

    lngs = df['LONGITUDE'].tolist()
    lats = df['LATITUDE'].tolist()
    temps = df['TEMP'].tolist()
    countries = df['COUNTRY'].unique().tolist()
    
    if len(lngs) > 500:
        set_size = 10
        set_alpha = 0.5
        set_edge = 'face'
    elif len(lngs) > 100:
        set_size = 15
        set_alpha = 0.5
        set_edge = 'dimgray'
    else:
        set_size = 20
        set_alpha = 0.6
        set_edge = 'black'

    if df['TEMP'].max() - df['TEMP'].min() > 1:
        if df['TEMP'].min() < 0:
            if skew(df['TEMP']) < -1:
                set_cmap = 'rainbow'
            else:
                set_cmap = 'viridis'
        else:
            if skew(df['TEMP']) < -1:
                set_cmap = 'rainbow'
            else:
                set_cmap = 'plasma'
    
    if df['TEMP'].max() - df['TEMP'].min() > 40:
        set_ticks = list(range(df['TEMP'].min(), df['TEMP'].max()+1, 10))
    elif df['TEMP'].max() - df['TEMP'].min() > 20:
        set_ticks = list(range(df['TEMP'].min(), df['TEMP'].max()+1, 5))
    elif df['TEMP'].max() - df['TEMP'].min() > 10:
        set_ticks = list(range(df['TEMP'].min(), df['TEMP'].max()+1, 2))
    else:
        set_ticks = list(range(df['TEMP'].min(), df['TEMP'].max()+1))
            
    fig, ax = plt.subplots(figsize=(16, 8))
    m = Basemap(ax=ax, llcrnrlon=-170, llcrnrlat=-60, urcrnrlon=190, urcrnrlat=85)
    m.drawcoastlines(color='#333333', linewidth = 0.3)
    m.drawcountries(linewidth = 0.3, linestyle = "--")
    m.drawmapboundary(fill_color='lightcyan')
    m.fillcontinents(color='silver', lake_color='lightcyan')
    if df['TEMP'].max() - df['TEMP'].min() > 1:
        dots = ax.scatter(lngs, lats, cmap=set_cmap, c=temps, s=set_size, alpha=set_alpha, edgecolors=set_edge, zorder=10)
        plt.colorbar(dots, orientation='horizontal', pad=0.01, aspect=50, ticks=set_ticks, 
                 format='%d\u00b0C')
    else:
        ax.scatter(lngs, lats, c='red', s=set_size, alpha=set_alpha, edgecolors=set_edge, zorder=10)
        
    plt.savefig(str(uid) + '-map.png', bbox_inches='tight', pad_inches=0)
    
    if len(countries) > 5:
        selected_countries = random.sample(countries, 5)
    else:
        selected_countries = countries
    
    df_selected = df[df['COUNTRY'].isin(selected_countries)]
    
    if df_selected.shape[0] > 5:
        selected_places = df_selected.groupby('COUNTRY').agg(np.random.choice)
    else:
        selected_places = df_selected

    places = selected_places['PLACE']
    urls = selected_places[['LATITUDE','LONGITUDE']].apply(lambda x: 'https://maps.google.com/?q=' + str(x['LATITUDE']) + ',' + str(x['LONGITUDE']) + '&ll=' + str(x['LATITUDE']) + ',' + str(x['LONGITUDE']) +'&z=10', axis=1).tolist()
        
    return (str(uid) + '-map.png', len(df['PLACE'].unique().tolist()), places, urls)
