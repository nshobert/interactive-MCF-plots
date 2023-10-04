import numpy as np
from scipy import stats
import get_my_data as getData

# Function to calculate the Kolmogorov-Smirnov statistic.
def MCF(year, vmin_limit):
    df = getData.dataframes[year]  # Get the dataframe from the dictionary.
    days = getData.year_to_days[year]  # Get the number of days in observation period.
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
    ecdf = (np.arange(1, n_truncated + 1) / n_truncated)

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

# Function to calculate empirical CDF (eCDF).
def ecdf(n_truncated):
    ecdf = 1- (np.arange(1, n_truncated + 1) / n_truncated)
    return ecdf

# Function to calculate theoreteical CDF (tCDF)
def tcdf(volumes_truncated, selected_vmin, n_truncated):
    log_values_theoretical = np.log(volumes_truncated / selected_vmin)
    b_hat = 1 + n_truncated * (np.sum(log_values_theoretical)) ** (-1)
    tcdf = 1 - (volumes_truncated / selected_vmin) ** (1 - b_hat)
    return tcdf, b_hat

# Function to calculate power law fit.
def power_law(v_max, selected_vmin, n_truncated, number_of_days, b_hat):
    x_values = np.linspace(v_max, selected_vmin, 1000)
    y_annual = (n_truncated / number_of_days) * (x_values / selected_vmin) ** (-b_hat + 1)
    return x_values, y_annual