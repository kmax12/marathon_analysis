import pandas as pd
import numpy as np
import statsmodels.api as sm

five_km_to_miles = 3.10686
km_to_miles = 0.621371
half_km = 21.0975
full_km = 42.195
splits = [5, 10, 15, 20, 25, 30, 35, 40]
all_pace_cols = ['5km.pace',
                 '10km.pace',
                 '15km.pace',
                 '20km.pace',
                 '20km_to_half.pace',
                 'half_to_25km.pace',
                 '30km.pace',
                 '35km.pace',
                 '40km.pace',
                 '40km_to_finish.pace']
all_pace_names = ["0 - 5km", "5 - 10km", "10 - 15km", "15 - 20km", "20km - Half",
                  "Half - 25km", "25 - 30km", "30 - 35km", "35 - 40km", "40km - Finish"]


def time_to_seconds(time):
    if pd.isna(time) or time == "–":
        return None
    hour, minutes, seconds = time.split(":")
    return int(hour)*60*60 + int(minutes)*60 + int(seconds)


def zero_pad(num):
    num_str = "0" + str(num)
    return num_str[-2:]


def seconds_to_time(seconds):
    hours = int(seconds / (60*60))
    minutes = int((seconds - hours*(60*60)) / 60)
    secs = int(seconds - hours*(60*60) - minutes*60)
    return "{hours}:{minutes}:{seconds}".format(hours=zero_pad(hours), minutes=zero_pad(minutes), seconds=zero_pad(secs))


def seconds_to_time_short(seconds):
    time_str = seconds_to_time(seconds)
    no_seconds_or_leading_zero = time_str[1:-3]
    return no_seconds_or_leading_zero


def seconds_to_pace(seconds):
    time_str = seconds_to_time(seconds)
    return time_str[3:]


def save_figure(fig, name):
    fig.write_html(f"output/{name}.html", config={'displaylogo': False})
    scale = 2.8
    fig.write_image(F'output/{name}.jpg', scale=scale,
                    width=2200/scale, height=1500/scale)
    return fig


def pretty_print(df):
    df_copy = df.copy()
    time_cols = [c for c in df_copy.columns if ".time" in c]
    df_copy[time_cols] = df_copy[time_cols].applymap(seconds_to_time)
    return df_copy


def prep_data(data):
    df = data.copy()

    df["0km.time"] = "00:00:00"

    # convert to seconds to make easier to work with
    time_cols = [c for c in df.columns if ".time" in c]
    df[time_cols] = df[time_cols].applymap(time_to_seconds)

    # drop row with missing splits for now
    df = df.dropna(axis=0)

    # calculate pace
    df["finish.avg_pace"] = (df["finish.time"] / 26.2).astype(int)
    df["half.avg_pace"] = (df["half.time"] / 13.1).astype(int)
    df["2nd_half.time"] = df["finish.time"] - df["half.time"]
    df["2nd_half.avg_pace"] = (df["2nd_half.time"] / 13.1).astype(int)
    df["2nd_half.time_diff"] = df["2nd_half.time"] - df["half.time"]
    df["2nd_half.time_diff_percent"] = df["2nd_half.time_diff"] / \
        df["2nd_half.time"]*100
    df["2nd_half_faster"] = df["2nd_half.time_diff"] < 0
    df["below_four_hours"] = df["finish.time"] < time_to_seconds("04:00:00")

    def splits_list(df):
        l = []
        for s in splits:
            mile_pace = int(
                (df[str(s) + "km.time"] - df[str(s-5) + "km.time"]) / five_km_to_miles)
            l.append(mile_pace)
        return l

    df["5km_split_pace"] = df.apply(splits_list, axis=1)

    for s in splits:
        # handle separate due to half and 40km times
        if s != 25:
            df[str(s) + "km.pace"] = ((df[str(s) + "km.time"] -
                                       df[str(s-5) + "km.time"]) / five_km_to_miles).astype(int)

        df[str(s) + "km.avg_pace"] = df[str(s) + "km.time"] / (s*km_to_miles)

    df["20km_to_half.pace"] = (
        df["half.time"] - df["20km.time"]) / (half_km - 20) / km_to_miles
    df["half_to_25km.pace"] = (
        df["25km.time"] - df["half.time"]) / (25 - half_km) / km_to_miles
    df["40km_to_finish.pace"] = (
        df["finish.time"] - df["40km.time"]) / (full_km - 40) / km_to_miles

    df["finish.avg_pace_norm"] = df["finish.avg_pace"] / df["finish.time"]

    df["std_split_pace"] = df["5km_split_pace"].apply(np.std).astype(int)
    df["std_split_pace_norm"] = df["std_split_pace"]/df["finish.avg_pace"]

    # remove any rows that have a negative pace
    # for some reason there are a few in the dataset.
    df = df[~(df[all_pace_cols] < 0).any(axis=1)]
    df["fastest_split"] = df[all_pace_cols].min(axis=1)
    df["slowest_split"] = df[all_pace_cols].max(axis=1)
    df["max_split_diff"] = df["slowest_split"] - df["fastest_split"]
    df["max_split_diff_norm"] = df["max_split_diff"]/df["finish.avg_pace"]
    df["slowest_split.name"] = df[all_pace_cols].idxmax(axis=1)
    df["fastest_split.name"] = df[all_pace_cols].idxmin(axis=1)

    def calculate_trend(row, first_half=False, second_half=False):
        Y = row.values
        X = []
        if first_half:
            X += [5, 10, 15, 20, half_km]
        if second_half:
            X += [25, 30, 35, 40, full_km]
        X = sm.add_constant(X)
        model = sm.OLS(Y, X)
        results = model.fit()
        return results.params[1] / km_to_miles

    df["split_trend"] = df[all_pace_cols].apply(
        calculate_trend, axis=1, first_half=True, second_half=True)
    df["1st_half.split_trend"] = df[all_pace_cols[:5]].apply(
        calculate_trend, axis=1, first_half=True)
    df["2nd_half.split_trend"] = df[all_pace_cols[5:]].apply(
        calculate_trend, axis=1, second_half=True)

    return df
