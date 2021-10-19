import geopandas as gpd
import shapely
from tqdm import tqdm


def append_dimensions(geodataframe: gpd.GeoDataFrame):
    """
    Append the minimum bounding (rotated) rectangle, and its depth and width, to a GeoDataFrame's Series
    :param geodataframe:
    :return:
    """

    # Check that the SRID of the geodataframe is not in degrees (is 'geographic'):
    if geodataframe.crs.is_geographic:
        raise ValueError("Error: The GeoDataFrame's CRS is geographic; Cannot measure lengths consistently")

    tqdm.pandas(desc='Calculating Minimum Rotated Bounding Rectangle')
    geodataframe['minimum_rectangle'] = geodataframe['geometry'].progress_apply(lambda geometry : geometry.minimum_rotated_rectangle)
    coords = geodataframe['minimum_rectangle'].apply(lambda rectangle : rectangle.exterior.coords.xy)
    edge_lengths = coords.apply(lambda coord:
                               (shapely.geometry.Point(coord[0][0], coord[1][0]).distance(shapely.geometry.Point(coord[0][1], coord[1][1])),
                                shapely.geometry.Point(coord[0][1], coord[1][1]).distance(shapely.geometry.Point(coord[0][2], coord[1][2]))))
    geodataframe['width'] = edge_lengths.apply(lambda edge_length: min(edge_length))
    geodataframe['depth'] = edge_lengths.apply(lambda edge_length: max(edge_length))

    # geodataframe['depth'] = min(edge_length)
#
# min_rects = []
# min_rect_widths = []
# min_rect_depths = []
#
# for i in range(len(parcels.index)):
#     lot_min_rect = parcels.iloc[i]['geometry'].minimum_rotated_rectangle
#     min_rects.append(lot_min_rect)
#
#     # get coordinates of polygon vertices
#     x, y = lot_min_rect.exterior.coords.xy
#     # get length of bounding box edges
#     edge_length = (shapely.geometry.Point(x[0], y[0]).distance(shapely.geometry.Point(x[1], y[1])), shapely.geometry.Point(x[1], y[1]).distance(shapely.geometry.Point(x[2], y[2])))
#     # get length of polygon as the longest edge of the bounding box
#     min_rect_depths.append(max(edge_length))
#     # get width of polygon as the shortest edge of the bounding box
#     min_rect_widths.append(min(edge_length))
#
# parcels['lot_min_rect'] = min_rects
# parcels['lot_width'] = min_rect_widths
# parcels['lot_depth'] = min_rect_depths
#
# parcels.info()
#
# properties_foo['propertyvaluerange'] = properties_foo.progress_apply(
#     lambda property : modules.corelogic_api.Query
#         .get_property_value_range(
#         address=property['fulladdress'],
#         access_token=access_token),
#     axis=1)
