# Library file for functions to display various tabular and geospatial datasets
# Imports:
import matplotlib
import shapely
import cartoframes
from cartoframes.viz import Map, Layer, popup_element, color_category_style
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
from IPython import display
import time, sys
from IPython.display import clear_output
import sys
import time


class map:
    @staticmethod
    def create_layer(geodataframe, display_column=None, annotation=None, legend=False, edgecolor='k', alpha=0.25):
        """
        Creates a layer for a map from a GeoDataFrame and parameters
        """
        layer = {
            'geodataframe': geodataframe,
            'display_column': display_column,
            'annotation': annotation,
            'legend': legend,
            'edgecolor': edgecolor,
            'alpha': alpha
        }
        return layer

    @staticmethod
    def display_map(layers, size):
        """
        Displays a map of geodataframes, and annotates each according to their dictionary values.
        """
        f, ax = plt.subplots(1, figsize=(size, size))

        for layer in layers:
            webmercator = layer['geodataframe'].to_crs(epsg=3857)
            if layer['display_column'] == None:
                ax = webmercator.plot(ax=ax, alpha=layer['alpha'], edgecolor=layer['edgecolor'], legend=layer['legend'])
            else:
                ax = webmercator.plot(ax=ax, column=layer['display_column'], alpha=layer['alpha'], edgecolor=layer['edgecolor'], legend=layer['legend'])

        if layer['annotation'] != None:
            webmercator.apply(lambda x: ax.annotate(s=x[layer['annotation']], xy=x.geometry.representative_point().coords[0], ha='center'),axis=1)

        ax.axis('off')
        ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)#, crs=layers[0]['geodataframe'].crs.to_string())

    @staticmethod
    def display_satellitemap(layers, size):
        """
        Displays a map of geodataframes, and annotates each according to their dictionary values.
        """
        f, ax = plt.subplots(1, figsize=(size, size))

        for layer in layers:
            webmercator = layer['geodataframe'].to_crs(epsg=3857)
            if layer['display_column'] == None:
                ax = webmercator.plot(ax=ax, alpha=layer['alpha'], edgecolor=layer['edgecolor'], legend=layer['legend'])
            else:
                ax = webmercator.plot(ax=ax, column=layer['display_column'], alpha=layer['alpha'], edgecolor=layer['edgecolor'], legend=layer['legend'])

        if layer['annotation'] != None:
            webmercator.apply(lambda x: ax.annotate(s=x[layer['annotation']], xy=x.geometry.representative_point().coords[0], ha='center'),axis=1)

        ax.axis('off')
        ctx.add_basemap(ax, source=ctx.providers.HERE.satelliteDay)