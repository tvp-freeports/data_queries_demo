import pandas as pd

def list_filter_df(df, ohchr2023, unsr_opt, dbio2024, ohchr2025, traseearth, testonly):
    """
    Filters the given DataFrame based on the selected lists.
    """
    if ohchr2025:
        df = df[df['OHCHR25/UN/2025-09-26'] == 1]
    if ohchr2023:
        df = df[df['OHCHR23/UN/2023-06-30'] == 1]
    if unsr_opt:
        df = df[df['UNSR_OPT/UN/2025-01-01'] == 1]
    if dbio2024:
        df = df[df['DBIO/NGO/2024-01-01'] == 1]
    if traseearth:
        df = df[df['BR_SOY_DEFOREST_3K/TRASE.EARTH/2022-01-01'] == 1]
    if testonly:
        df = df[df['TEST/FREEPORTS/2025-01-01'] == 1]
    return df
