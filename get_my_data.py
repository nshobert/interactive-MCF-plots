import pandas as pd

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
