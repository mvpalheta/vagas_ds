import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import streamlit as st
import io
from PIL import Image
import requests

def graph_top10(df, group_var, agg_var, agg_type, top=10, title="Top 10", xlabel="Não definido", ylabel="Não definido", figsize=(12,8)):

    if agg_type == 'sum':
        group = pd.DataFrame(df.groupby([group_var])[agg_var].sum()).reset_index().sort_values(agg_var, ascending=False)
    elif agg_type == 'count':
        group = pd.DataFrame(df.groupby([group_var])[agg_var].count()).reset_index().sort_values(agg_var, ascending=False)
    
        top10 = group.head(top).sort_values(agg_var)

    top10_list = top10[group_var].tolist()
    top10_count_list = top10[agg_var].tolist()
    
    plt.figure(figsize=figsize)

    plt.barh(top10_list, top10_count_list, color="#27add9")
    for index, value in enumerate(top10_count_list):
        plt.text(value+(top10[agg_var].max()*0.005), index-0.2, str(f'{int(value):,}').replace(",", "."), fontsize=14)

    plt.title(title, fontsize=16)
 
    plt.xlim(0,(top10[agg_var].max()+(top10[agg_var].max()*0.1)))
    plt.ylabel(ylabel, fontsize=14)
    plt.xlabel(xlabel, fontsize=14)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=12)

    return plt

def image_from_s3(img_url):
    response = requests.get(img_url)
    response.raise_for_status()    

    return Image.open(io.BytesIO(response.content))