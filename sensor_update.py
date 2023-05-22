import pandas as pd

# Load the sensor data from a CSV file
data = pd.read_csv('merged_temperature_data.csv')

# Convert the 'createdAt' column to datetime format
data['createdAt'] = pd.to_datetime(data['createdAt'])

# Sort the data based on the 'createdAt' column
data = data.sort_values('createdAt')

# Calculate the time difference between consecutive measurements for each sensor
data['acquisition_frequency(min)'] = data.groupby('sensorId')['createdAt'].diff()

# Calculate the average update frequency for each sensor in minutes
update_frequency = data.groupby('sensorId')['acquisition_frequency(min)'].mean().dt.total_seconds() / 60

# Save the update frequency data to a file
update_frequency.to_csv('update_frequency.csv', header=True)

# Get the number of unique sensors
num_sensors = data['sensorId'].nunique()

# Print the number of sensors
print("Number of Sensors:", num_sensors)

print("Data acquisition frequency saved to 'update_frequency.csv'.")

