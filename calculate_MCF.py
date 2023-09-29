import numpy as np
import pandas as pd
from scipy import stats

# Define file paths #TODO: change to iterate through data folder and assign keys.
file_paths = {
    '2013': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2013_ranked.csv',
    '2015': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2015_ranked.csv',
    '2017': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2017_ranked.csv',
    '2018': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2018_ranked.csv',
    '2019': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2019_ranked.csv',
    '2020': 'C:\\Users\\marcu\\Code\\KS-Statistic-Interactive\\data\\2020_ranked.csv'
}

# Load data into a dictionary of dataframes
dataframes = {year: pd.read_csv(path) for year, path in file_paths.items()}

# Show the first few rows of one of the dataframes to confirm it loaded correctly
#print(dataframes['2013'].head())

# Dictionary to map years to number of days
year_to_days = {
    '2013': 656,
    '2015': 812,
    '2017': 378,
    '2018': 347,
    '2019': 276,
    '2020': 366
}

# Verify by printing a sample
#print("Sample year-to-days mapping for 2013:", year_to_days['2013'])

# Function to calculate the Kolmogorov-Smirnov statistic.
def MCF(year, vmin_limit):
    df = dataframes[year]  # Get the dataframe from the dictionary.
    days = year_to_days[year]  # Get the number of days in observation period.
    volumes = df['Volume']

    # Initialize an array to store vmin, D* pairs
    vmin_Dstar_pairs = []

    # Limit the value that volumes can take to only those below the top 1 order of magnitude.
    #vmin_limit = min(vmin_limit, 10 ** (int(np.floor(np.log10(volumes.max()))) - 1))
    #TODO: get rid of this vmin limit? why did i implement this again? leave commented out for now...
    # Truncate the data set
    truncated_volumes = volumes[volumes >= vmin_limit]
    n_truncated = len(truncated_volumes)

    # Calculate empirical CDF
    ecdf = np.arange(1, n_truncated + 1) / n_truncated

    # Calculate theoretical CDF
    log_values_theoretical = np.log(truncated_volumes / vmin_limit)
    b_hat = 1 + n_truncated * (np.sum(log_values_theoretical)) ** (-1)
    tcdf = 1 - (truncated_volumes / vmin_limit) ** (1 - b_hat)

    # Calculate D*, the weighted Kolmogorov-Smirnov statistic
    D_star, p_value = stats.ks_2samp(ecdf, tcdf)

    # Store current vmin, D*, and theoretical fit parameters
    vmin_Dstar_pairs.append((vmin_limit, D_star, p_value, b_hat, n_truncated))

    # Once done with the loop, store the vmin and D* where D* was minimized.
    vmin_best, D_star_best, p_value, b_hat_best, n_truncated_best = min(vmin_Dstar_pairs, key=lambda x: x[1])

    # Return the values where D* was minimized
    return vmin_best, D_star_best, p_value, b_hat_best, n_truncated_best