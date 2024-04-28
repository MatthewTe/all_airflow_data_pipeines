import geopandas as gpd
import matplotlib.pyplot as plt

gdf = gpd.read_file("/Users/matthewteelucksingh/Downloads/tto_adm1/TTO_adm1.shp")

print(gdf)

gdf.to_csv("/Users/matthewteelucksingh/Repos/TT_info_classifier/data/regions_tt.csv")

gdf.plot()
plt.show()