import os
import glob
import numpy as np
import pandas as pd
import json
from scipy.stats import kurtosis # Make sure you have scipy: pip install scipy

print("Starting pre-processing... This may take a few minutes.")

# --- 1. Define Paths and ALL Mappings ---
BASE_PATH = '.\IMS' 


# Dataset 1: 8 channels
path_1st = os.path.join(BASE_PATH, '1st_test', '1st_test')
bearings_1st_all = {
    'B1-Ch1 (Healthy)': 0, 'B1-Ch2 (Healthy)': 1,
    'B2-Ch1 (Healthy)': 2, 'B2-Ch2 (Healthy)': 3,
    'B3-Ch1 (Fail-Inner)': 4, 'B3-Ch2 (Fail-Inner)': 5,
    'B4-Ch1 (Fail-Roller)': 6, 'B4-Ch2 (Fail-Roller)': 7
}

# Dataset 2: 4 channels
path_2nd = os.path.join(BASE_PATH, '2nd_test', '2nd_test')
bearings_2nd_all = {
    'B1-Ch1 (Fail-Outer)': 0, 'B2-Ch1 (Healthy)': 1,
    'B3-Ch1 (Healthy)': 2, 'B4-Ch1 (Healthy)': 3
}

# Dataset 3: 4 channels
path_3rd = os.path.join(BASE_PATH, '3rd_test', '4th_test', 'txt')
bearings_3rd_all = {
    'B1-Ch1 (Healthy)': 0, 'B2-Ch1 (Healthy)': 1,
    'B3-Ch1 (Fail-Outer)': 2, 'B4-Ch1 (Healthy)': 3
}

# Combine all test info into one structure
all_tests_info = {
    "1st_test": {"path": path_1st, "bearings": bearings_1st_all},
    "2nd_test": {"path": path_2nd, "bearings": bearings_2nd_all},
    "3rd_test": {"path": path_3rd, "bearings": bearings_3rd_all}
}

# --- 2. Kurtosis-per-File Function ---
def get_kurtosis_series_from_files(data_path, col_index):
    """
    Processes a directory of files, calculating one Kurtosis value per file
    for the specified column.
    """
    all_files = sorted(glob.glob(os.path.join(data_path, "*")))
    if not all_files:
        print(f"  Warning: No files found in {data_path}")
        return []
    
    kurtosis_list = []
    for file in all_files:
        try:
            # Read only the single column we need
            df = pd.read_csv(file, sep='\t', header=None, usecols=[col_index])
            signal_chunk = df[col_index].values
            
            # Calculate Pearson's kurtosis (normal is 3.0)
            kurtosis_val = kurtosis(signal_chunk, fisher=False) 
            kurtosis_list.append(kurtosis_val)
        except Exception as e:
            #print(f"  Error processing file {file}: {e}")
            kurtosis_list.append(np.nan) # Append NaN if file is corrupt
    
    print(f"  ...processed {len(kurtosis_list)} files for col {col_index}.")
    return kurtosis_list

# --- 3. Main Execution ---
all_data_cache = {}

for test_name, info in all_tests_info.items():
    print(f"\nProcessing {test_name} at {info['path']}...")
    all_data_cache[test_name] = {}
    
    # Check if the path exists before trying to read from it
    if not os.path.isdir(info['path']):
        print(f"  !! SKIPPING: Directory not found: {info['path']}")
        continue
        
    for bearing_name, col_idx in info['bearings'].items():
        print(f"  Calculating for {bearing_name} (Col {col_idx})...")
        kurtosis_series = get_kurtosis_series_from_files(info['path'], col_idx)
        
        # Handle cases where all files failed or directory was empty
        if not kurtosis_series:
            print(f"  !! SKIPPING {bearing_name}: No data processed.")
            continue
            
        # Clean up NaNs by filling with the mean of the valid data
        series_mean = np.nanmean(kurtosis_series)
        if np.isnan(series_mean): # Handle if ALL data was NaN
            series_mean = 3.0 # Default to 3.0 (kurtosis of normal data)
            
        cleaned_series = [x if not np.isnan(x) else series_mean for x in kurtosis_series]
        
        all_data_cache[test_name][bearing_name] = cleaned_series

# --- 4. Save to JSON ---
output_filename = 'kurtosis_data.json'
with open(output_filename, 'w') as f:
    json.dump(all_data_cache, f)

print(f"\nSUCCESS: All data processed and saved to '{output_filename}'.")