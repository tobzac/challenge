# simple collection of functions used for analysis
import requests
import zipfile
import io
import os
import pandas as pd


# function to download file from url
# url: URL for zip folder to download
# save_path: string of folder on disk, e.g. Data/downloads/folder
def download_url(url: str, save_path: str) -> None:
    # download zip file
    r = requests.get(url, stream=True)
    myzipfile = zipfile.ZipFile(io.BytesIO(r.content))
    myzipfile.extractall(save_path)


# function to perform per month analysis
# df_month: full (concatenated) dataframe with data from whole month
# n_bike_trips: number of bike trips for whole month
# df_coords: data frame with all used unique stations and their lng/lat coords
def analysis_per_month(df_month: pd.DataFrame) -> tuple[int, pd.DataFrame]:
    # -------------------------
    # get number of bike trips
    # full list used for simple stats like total number of trips etc.
    n_bike_trips = len(df_month.index)

    # cleaned list for analyses, where values are needed
    df_month_cleaned = df_month.dropna()

    # other stuff
    # -------------------------------------------------------
    # get station list per month and number of stations used
    # get number of occurences of different stations
    n_occurences_start = df_month_cleaned['start_station_name'].value_counts().to_dict()
    n_occurences_end = df_month_cleaned['end_station_name'].value_counts().to_dict()
    n_occurences = {key: n_occurences_start.get(key, 0) + n_occurences_end.get(key, 0) for key in
                    set(n_occurences_start) | set(n_occurences_end)}
    df_n_occurences = pd.DataFrame.from_dict(n_occurences, orient='index').rename(columns={0: 'usage'})

    # iterate through table and form map with coordinates of different stations
    start_station_names_to_coords = dict(pd.Series(list(zip(df_month_cleaned['start_lng'],
                                         df_month_cleaned['start_lat'])),
                                         index=df_month_cleaned.start_station_name).to_dict())
    end_station_names_to_coords = dict(pd.Series(list(zip(df_month_cleaned['end_lng'], df_month_cleaned['end_lat'])),
                                       index=df_month_cleaned.end_station_name).to_dict())

    station_names_to_coords = start_station_names_to_coords
    station_names_to_coords.update(end_station_names_to_coords)
    # len(station_names_to_coords)
    df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
    df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
    df_coords = df_coords.join(df_n_occurences)

    # get median bike trip duration

    return n_bike_trips, df_coords


# summarize number for whole year
# result_map: map: key: month, value: number of trips
# stations_analysis_list: list of dataframes of df_coords (unique stations and their usage in month)
# s: total number of bike trips per year
# df_coords_year: data frame with unique stations and usage
def analysis_summary_year(results_map: dict, stations_analysis_list: list[pd.DataFrame]) -> tuple[int, pd.DataFrame]:
    # -------------------------------------------
    # sum up all bike trips to get total number:
    s = 0
    for key in results_map:
        s = s + results_map[key]

    # -------------------------------------------------------------------
    # make one station list per year and number of stations used per year
    # is of course approximation, but can then be also used for building up a visualization grid
    # concatenate all dfs from list
    df_all = pd.concat(stations_analysis_list, axis=0)

    # sum over index to get usage values for all stations
    only_usage = pd.DataFrame(df_all["usage"].groupby(level=0).sum())
    station_names_to_coords = dict(pd.Series(list(zip(df_all['longitude'], df_all['latitude'])),
                                   index=df_all.index).to_dict())
    df_coords = pd.DataFrame.from_dict(station_names_to_coords, orient='index')
    df_coords = df_coords.rename(columns={0: 'longitude', 1: 'latitude'})
    df_coords_year = df_coords.join(only_usage).sort_values('usage', ascending=False)

    return s, df_coords_year


# function to perform an analysis for one year
# year: year for analysis
# result_map: map: key: month, value: number of trips
# stations_analysis_list: list of dataframes of df_coords (unique stations and their usage in month)
def analysis_one_year(year: int):

    month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    base_folder_name = str(year) + "-citibike-tripdata"

    # results
    result_map = {}
    stations_analysis_list = []

    # read in successively all data for month, then for all months
    for month in month_list:
        print("month: " + month)
        # collect all files for the month
        month_folder_name = str(year) + month + "-citibike-tripdata"
        # dataframe for month
        df_list = []
        full_path = "Data/" + base_folder_name + "/" + month_folder_name + "/"
        for filename in os.listdir(full_path):
            if filename.endswith(".csv") and month_folder_name in filename:
                print(filename)
                df_month_partial = pd.read_csv(full_path + filename)
                df_list.append(df_month_partial)

        df_month = pd.concat(df_list, axis=0, ignore_index=True)

        # perform monthly analysis
        result_n_trips, df_coords_stations = analysis_per_month(df_month)
        result_map[month] = result_n_trips
        stations_analysis_list.append(df_coords_stations)

        print("numer of trips: " + str(result_n_trips))
        print("number of stations used: " + str(len(df_coords_stations)))

    print(result_map)
    return result_map, stations_analysis_list
