import numpy as np
import pandas as pd
import haversine
from airport import Airport
from plane import Plane
from data.data_worker import DataWorker

DISTANCE_UNCERTAINTY = 2500
STANDARD_ELEVATIONS = [800, 1200, 2500, 3500, 5000, 7500, 10000, 12500, 15000, 20000, 25000, 32000, 36000]
STANDARD_GLIDE_RATIOS = [15, 17, 20]
STANDARD_RUNWAY_MINIMUMS = [800, 900, 1200, 1000, 3000, 5000, 5900, 6000, 7900]


def estimate_distance(port_coords, plane_coords):

    distance = haversine.haversine(port_coords, plane_coords, unit='ft')
    return distance

    # This is an ESTIMATION of the viability of landing at a target airport.
    #
    # NOTE: The estimation is compared against the haversine dist, which IS NOT
    # intended to include elevation differences. The accuracy of this method will
    # likely decrease for larger distances between the plane and airport.


def is_valid_airport(port: Airport, plane: Plane):

    if port.runway_length < plane.min_runway_length:
        return 0, np.inf

    haversine_dist = estimate_distance((port.latitude, port.longitude), (plane.latitude, plane.longitude))

    elevation_diff = plane.elevation - port.elevation

    if elevation_diff < 0:
        return 0, np.inf
    else:
        max_range = elevation_diff * plane.glide_ratio - DISTANCE_UNCERTAINTY
        # print(elevation_diff)
        # print(max_range)
        # print(haversine_dist)
        return int(max_range >= haversine_dist), haversine_dist


def custom_dist(a, b):

    a.reshape((4,))
    b.reshape((4,))


    if a[3] > b[3] or a[3] < b[3]:
        return np.inf

    runaway_clearance = b[3] - a[3]

    haversine_dist = estimate_distance((b[0], b[1]), (a[0], a[1]))

    return haversine_dist / (runaway_clearance + .1)


    # haversine_dist = estimate_distance((port.latitude, port.longitude), (plane.latitude, plane.longitude))
    #
    # elevation_diff = plane.elevation - port.elevation
    #
    # if elevation_diff < 0:
    #     return 0, np.inf
    # else:
    #     max_range = elevation_diff * plane.glide_ratio - DISTANCE_UNCERTAINTY
    #     # print(elevation_diff)
    #     # print(max_range)
    #     # print(haversine_dist)
    #     return int(max_range >= haversine_dist), haversine_dist

def elevation_inverter(df: pd.DataFrame, curr):
    value: pd.DataFrame = (1 / (curr - df["elevation_ft"] + 1e-16))
    value.where(value > 0, other=np.inf)
    return value

def runway_inverter(df: pd.DataFrame, curr):
    # return (1 / abs(curr - df["length_ft"] + 1e-16))**2
    value: pd.DataFrame = (1 / (curr - df["length_ft"] + 1e-16))
    value.where(value > 0, other=np.inf)
    return value


def generate_random_plane(lat_spread, long_spread):

    latitude = np.random.random() * lat_spread - (lat_spread / 2)
    longitude = np.random.random() * long_spread - (long_spread / 2)

    elevation = np.random.choice(STANDARD_ELEVATIONS)
    min_runway_length = np.random.choice(STANDARD_RUNWAY_MINIMUMS)
    glide_ratio = np.random.choice(STANDARD_GLIDE_RATIOS)

    return Plane(latitude, longitude, elevation, min_runway_length, glide_ratio)


def generate_test_set(airports: pd.DataFrame, num_samples=100, name=None):

    test_df = pd.DataFrame(columns=["airport_ref", "latitude_deg", "longitude_deg",
                                    "elevation_ft", "length_ft"])
    for i in range(0, num_samples):
        rand_plane = generate_random_plane(120, 360)

        min_airport = 0
        min_airport_dist = 10000000000000
        for airport_idx in range(0, airports.shape[0]):
            airport = Airport(airports.iloc[airport_idx])
            valid, dist = is_valid_airport(airport, rand_plane)
            # if valid:
            #     print(valid)
            if dist < min_airport_dist:
                min_airport = airport.airport_ref
                min_airport_dist = dist

        test_df.loc[test_df.shape[0] - 1] = [min_airport, rand_plane.latitude, rand_plane.longitude,
                                             rand_plane.elevation, rand_plane.min_runway_length]

        print(i)

    if name:
        path = f"data/datasets_labeled/{name}.pkl"
    else:
        path = "data/datasets_labeled/test_set.pkl"

    test_df.to_pickle(path)
