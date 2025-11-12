import numpy as np

# These are the exact parameters from your App.jsx
class RealTimeSoDProcessor:
    def __init__(self, baseline_frac=0.2, smooth_window=50, sigma_factor=2.0, persistence_count=50):
        # Store parameters
        self.baseline_frac = baseline_frac
        self.smooth_window = smooth_window
        self.sigma_factor = sigma_factor
        self.persistence_count = persistence_count
        
        # Store data as it comes in
        self.raw_series = []
        self.smoothed_series = []
        
        # State variables
        self.baseline_samples = 0
        self.threshold = 0
        self.mean = 0
        self.std = 1e-6 # Start with a tiny std to avoid errors
        self.baseline_established = False
        
        self.above_counter = 0
        self.sod_index = -1
        self.sod_detected = False

    def _establish_baseline(self, total_data_len):
        """Calculates mean, std, and threshold from the baseline data."""
        self.baseline_samples = max(20, int(total_data_len * self.baseline_frac))
        
        # Check if we have enough data to set the baseline
        if len(self.raw_series) < self.baseline_samples:
            return # Not enough data yet
            
        baseline_data = self.raw_series[:self.baseline_samples]
        self.mean = np.mean(baseline_data)
        self.std = np.std(baseline_data)
        if self.std < 1e-6: self.std = 1e-6
        self.threshold = self.mean + self.sigma_factor * self.std
        self.baseline_established = True
        print(f"--- Baseline Established ---")
        print(f"Mean: {self.mean:.3f}, Std: {self.std:.3f}, Threshold: {self.threshold:.3f}")

    def process_point(self, raw_value, total_data_len):
        """Processes a single new data point and returns the full state."""
        current_index = len(self.raw_series)
        self.raw_series.append(raw_value)
        
        # --- 1. Calculate Smoothed Value ---
        window_start = max(0, current_index - self.smooth_window + 1)
        current_window = self.raw_series[window_start : current_index + 1]
        smoothed_value = np.mean(current_window)
        self.smoothed_series.append(smoothed_value)

        # --- 2. Establish Baseline (if not done) ---
        if not self.baseline_established and total_data_len > 0:
            # We need the total length to calculate the baseline fraction
            self._establish_baseline(total_data_len)
            
        # --- 3. Check for SoD (if baseline is ready) ---
        if self.baseline_established and not self.sod_detected:
            if smoothed_value > self.threshold:
                self.above_counter += 1
            else:
                self.above_counter = 0 # Reset
            
            if self.above_counter >= self.persistence_count:
                self.sod_index = current_index - self.persistence_count + 1
                self.sod_detected = True
                print(f"!!! SoD DETECTED AT INDEX {self.sod_index} !!!")

        # --- 4. Format data for frontend (matches App.jsx logic) ---
        return {
            "index": current_index,
            "raw": raw_value,
            "below_threshold": smoothed_value if not self.baseline_established or smoothed_value < self.threshold else None,
            "above_threshold": smoothed_value if self.baseline_established and smoothed_value >= self.threshold else None,
            "threshold": self.threshold if self.baseline_established else 0,
            "sod_index": self.sod_index
        }