# simple collection of functions used for analysis
import requests
import zipfile
import io
import os
import sys
import pandas as pd


def download_url(url: str, save_path: str) -> None:
    """
    function to perform per month analysis

    :param url: full URL for zip folder to download
    :param save_path: string of folder on disk, e.g. Data/downloads/folder
    """

    # download zip file
    r = requests.get(url, stream=True)
    myzipfile = zipfile.ZipFile(io.BytesIO(r.content))
    myzipfile.extractall(save_path)


def analysis_per_month(df_month: pd.DataFrame, df_geocode_all_stations: pd.DataFrame, analysis_type: str) \
        -> tuple[int, pd.DataFrame]:
    """
    function to perform per month analysis

    :param df_month: full (concatenated) dataframe with data from whole month
    :param df_geocode_all_stations: data frame with geocode annotated data for all stations
    :param: analysis_type: "normal" for unrestricted, "core_region" for restriction to core region
    :return n_bike_trips: number of bike trips for whole month
    :return df_coords: data frame with all used unique stations and their lng/lat coords
    """

    # cleaned list for analyses, where values are needed
    df_month_cleaned = df_month.dropna()

    # station lists
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

    # -------------------------
    # get number of bike trips
    n_bike_trips = 0
    if analysis_type == "core_region":
        # restrict the df_coords to core region for year with hard-coded core region
        # to get core region trip counts
        # read in geocode station list
        df_coords= df_coords.join(df_geocode_all_stations)

        df_coords = df_coords[df_coords['borough'] == 'Manhattan']
        df_coords = df_coords[
        (df_coords['latitude'] < (((df_coords['longitude'] + 73.965) *
        ((40.755 - 40.78) / (-73.965 + 73.99))) + 40.755)) & (df_coords['longitude'] > -74.03)]

        # count now in core region
        # restrict df_month to core region and simply count length of resulting df
        df_month_core = df_month[(df_month['start_station_name'].isin(df_coords.index))
        | (df_month['end_station_name'].isin(df_coords.index))]

        n_bike_trips = len(df_month_core.index)
    elif analysis_type == "normal":
        # full list used for simple stats like total number of trips etc.
        n_bike_trips = len(df_month.index)

    return n_bike_trips, df_coords


def analysis_summary_year(results_map: dict, stations_analysis_list: list[pd.DataFrame]) \
        -> tuple[int, pd.DataFrame]:
    """
        function to summarize numbers/results for whole year

    :param result_map: dictionary key: month, value: number of trips
    :param stations_analysis_list: list of dataframes of df_coords (unique stations and their usage in month)
    :return s: total number of bike trips per year
    :return df_coords_year: data frame with unique stations and usage
    """

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


def analysis_one_year(year: int, geocode_data_file_name: str, analysis_type: str) \
        -> tuple[dict, list[pd.DataFrame]]:
    """
    function to perform per month analysis

    :param year: full (concatenated) dataframe with data from whole month
    :param geocode_data_file_name: data frame with geocode annotated data for all stations
    :param: analysis_type: "normal" for unrestricted, "core_region" for restriction to core region
    :return result_map: dictionary key: month, value: number of trips
    :return stations_analysis_list: list of dataframes of df_coords (unique stations and their usage in month)
    """

    # results
    result_map = {}
    result_map_core = {}
    stations_analysis_list = []
    stations_core_analysis_list = []

    base_folder_name = str(year) + "-citibike-tripdata"
    month_list = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    numbers_2_name = {"01": "1_January", "02": "2_February", "03": "3_March", "04": "4_April",
                     "05": "5_May", "06": "6_June", "07": "7_July", "08": "8_August",
                     "09": "9_September", "10": "10_October", "11": "11_November", "12": "12_December"}

    # read in pre-processed geocode station list
    if analysis_type == "core_region":
        print("core region analysis performed")
    elif analysis_type == "normal":
        print("normal all region analysis performed")
    else:
        sys.exit("no valid analysis type: " + analysis_type)

    df_geocode_all_stations = pd.read_csv(geocode_data_file_name, index_col=0)

    # read in successively all data for month, then for all months
    for month in month_list:
        print("month: " + month)

        # get used folder/filename
        month_folder_name_new = str(year) + month + "-citibike-tripdata"

        # set path to csv files depending on year
        full_path = ""
        if year in [2020, 2021, 2022, 2023, 2024]:
            full_path = "Data/" + base_folder_name + "/" + month_folder_name_new + "/"
        elif year in [2013, 2014, 2015, 2016, 2017, 2018, 2019]:
            full_path = "Data/" + base_folder_name + "/" + numbers_2_name[month] + "/"
        else:
            sys.exit("No valid year: " + str(year))

        # collect all files for the month
        df_list = []
        for filename in os.listdir(full_path):
            if filename.endswith(".csv") and month_folder_name_new in filename:
                print(filename)
                df_month_partial = pd.read_csv(full_path + filename)

                # special treatment and renaming of columns if year before 2020
                if year in [2013, 2014, 2015, 2016, 2017, 2018, 2019]:
                    if 'User Type' in df_month_partial.columns:
                        df_month_partial = df_month_partial.drop(['Birth Year', 'Gender', 'User Type'], axis=1)
                        df_month_partial = df_month_partial.rename(
                            columns={'Start Time': 'started_at', 'Stop Time': 'ended_at',
                                     'Start Station ID': 'start_station_id', 'Start Station Name': 'start_station_name',
                                     'Start Station Latitude': 'start_lat', 'Start Station Longitude': 'start_lng',
                                     'End Station ID': 'end_station_id', 'End Station Name': 'end_station_name',
                                     'End Station Latitude': 'end_lat', 'End Station Longitude': 'end_lng'})
                    elif 'usertype' in df_month_partial.columns:
                        df_month_partial = df_month_partial.drop(['birth year', 'gender', 'usertype'], axis=1)
                        df_month_partial = df_month_partial.rename(
                            columns={'starttime': 'started_at', 'stoptime': 'ended_at',
                                     'start station id': 'start_station_id', 'start station name': 'start_station_name',
                                     'start station latitude': 'start_lat', 'start station longitude': 'start_lng',
                                     'end station id': 'end_station_id', 'end station name': 'end_station_name',
                                     'end station latitude': 'end_lat', 'end station longitude': 'end_lng'})

                df_list.append(df_month_partial)

        print(df_list)
        if len(df_list) > 0:
            df_month = pd.concat(df_list, axis=0, ignore_index=True)

            # perform monthly analysis
            result_n_trips, df_coords_stations = analysis_per_month(df_month, df_geocode_all_stations, analysis_type)
            result_map[month] = result_n_trips
            stations_analysis_list.append(df_coords_stations)

            print("number of trips: " + str(result_n_trips))
            print("number of stations used: " + str(len(df_coords_stations)))
        else:
            print("no data for month: " + month)

    print(result_map)
    return result_map, stations_analysis_list
