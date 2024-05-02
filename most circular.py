import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.affinity import rotate, translate

def generate_points(geometry, n=2000):
    if isinstance(geometry, MultiPolygon):
        largest_polygon = max(geometry.geoms, key=lambda a: a.area)
        exterior = largest_polygon.exterior
    elif isinstance(geometry, Polygon):
        exterior = geometry.exterior
    else:
        raise ValueError("Unhandled geometry type")

    length = exterior.length
    points = [exterior.interpolate(distance) for distance in np.linspace(0, length, n)]
    return points

def calculate_circularity(points, centroid):
    distances = [centroid.distance(point) for point in points]
    return np.std(distances)

def fit_minimum_bounding_square(geometry):
    min_rect = geometry.minimum_rotated_rectangle
    rect_coords = min_rect.exterior.coords[:-1]
    edges = [np.linalg.norm(np.array(rect_coords[i])-np.array(rect_coords[i-1])) for i in range(4)]
    edge_length = min(edges)
    cx, cy = min_rect.centroid.xy
    square = box(cx[0] - edge_length / 2, cy[0] - edge_length / 2,
                 cx[0] + edge_length / 2, cy[0] + edge_length / 2)
    return square

def calculate_squareness(geometry):
    fitted_square = fit_minimum_bounding_square(geometry)
    intersection = geometry.intersection(fitted_square)
    overlap_area = intersection.area
    area_ratio = overlap_area / fitted_square.area
    squareness_score = area_ratio
    return squareness_score

def main():
    shp_path = "C:\\Users\\Zord\\Downloads\\ne_110m_admin_0_countries\\ne_110m_admin_0_countries.shp"
    gdf = gpd.read_file(shp_path)

    circularity_scores = {}
    squareness_scores = {}
    for index, country in gdf.iterrows():
        geometry = country['geometry']
        centroid = geometry.centroid
        points = generate_points(geometry)
        circularity_scores[country['NAME']] = calculate_circularity(points, centroid)
        squareness_scores[country['NAME']] = calculate_squareness(geometry)

    sorted_circularity_scores = sorted(circularity_scores.items(), key=lambda x: x[1])
    sorted_squareness_scores = sorted(squareness_scores.items(), key=lambda x: x[1], reverse=True)

    top_10_circular_countries = sorted_circularity_scores[:10]
    top_10_square_countries = sorted_squareness_scores[:10]

    fig, ax = plt.subplots(figsize=(15, 10))

    gdf.plot(ax=ax, color='lightgrey')

    for country_name, _ in top_10_circular_countries:
        country = gdf[gdf['NAME'] == country_name]
        country.plot(ax=ax, color='red')

    for country_name, _ in top_10_square_countries:
        country = gdf[gdf['NAME'] == country_name]
        country.plot(ax=ax, color='blue')

    plt.show()

    print(f"The most circular country is: {top_10_circular_countries[0][0]}")
    print(f"The most square country is: {top_10_square_countries[0][0]}")

    print("\nTop 10 most circular countries:")
    for rank, (country_name, score) in enumerate(top_10_circular_countries, start=1):
        print(f"{rank}. {country_name}: {score}")

    print("\nTop 10 most square countries:")
    for rank, (country_name, score) in enumerate(top_10_square_countries, start=1):
        print(f"{rank}. {country_name}: {score}")

    egypt_circularity_score = circularity_scores.get("Egypt")
    egypt_squareness_score = squareness_scores.get("Egypt")
    egypt_circularity_rank = next((rank for rank, (name, _) in enumerate(sorted_circularity_scores, start=1) if name == "Egypt"), None)
    egypt_squareness_rank = next((rank for rank, (name, _) in enumerate(sorted_squareness_scores, start=1) if name == "Egypt"), None)

    print(f"\nDetails for Egypt:")
    print(f"Egypt's circularity score: {egypt_circularity_score}")
    print(f"Egypt's circularity rank: {egypt_circularity_rank}")
    print(f"Egypt's squareness score: {egypt_squareness_score}")
    print(f"Egypt's squareness rank: {egypt_squareness_rank}")

if __name__ == "__main__":
    main()
