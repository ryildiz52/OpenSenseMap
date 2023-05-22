import glob
import requests
import datetime
import os
import geopandas as gpd
import pandas as pd
def get_city_bounding_box(city_name):
    """
    Function to retrieve bounding box coordinates of a city. Input is city name as a string.
    Result can be used as input argument for function "get_box_data" which gets sensorbox data for all boxes within the given bounding box.
    """
    # Set the base URL for the API
    base_url = "https://nominatim.openstreetmap.org/search"
    # Set the search query
    query = city_name
    # Set the parameters for the API call
    params = {
        "q": query,
        "format": "json"
    }
    # Make the API call
    response = requests.get(base_url, params=params)
    #print(response.json())
    # Check the status code of the response
    if response.status_code == 200:
        # If the request was successful, the data will be in the response's JSON
        data = response.json()
        # Extract the bounding box from the response
        bounding_box = data[0]["boundingbox"]
        # Shift the order of the coordinates so that it is in the correct order as used in OpenSenseMap API calls
        bounding_box_ordered = [bounding_box[2], bounding_box[0], bounding_box[3], bounding_box[1]]
        # Join the bounding box coordinates with commas
        bounding_box_string = ",".join(bounding_box_ordered)
        # Print the result
        print(f"Bounding box of {city_name} retrieved: {bounding_box_string}")
        # Return the bounding box
        return bounding_box_string
    else:
        # If the request was not successful, print and return the error message
        print(response.text)
        return response.text
def get_box_data(bounding_box, phenomena, start_date=None, end_date=None, limit=100):
    """
    Function to retrieve data for multiple phenomena from senseboxes within a given bounding box.
    The bounding box should be a string in the format "min_lon,min_lat,max_lon,max_lat"; the function "get_city_bounding_box" returns the coordinates in this order.
    The 'phenomena' parameter should be a list containing the desired phenomena (e.g., ["Temperatur", "Temperature", "Luftdruck"]).
    The input variables start_date and end_date need to be in RFC 3339 format. If no input is given, the function will download data from the last 24 hours.
    """
    # If no start and end dates are given, set them to now-24hrs and now, respectively
    if start_date is None:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    if end_date is None:
        end_date = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            # Set the base URL for the API
    base_url = "https://api.opensensemap.org/boxes/data"
    files = ["A", "B" , "C"]
    for phenomenon,name in zip(phenomena,files):
        # Validate the phenomenon parameter
        if phenomenon not in ['Temperatur', 'Temperature', 'temperature', 'PM2.5', 'Luftdruck']:
            raise ValueError('Invalid phenomenon parameter. Must be one of: Temperatur, Temperature, temperature, Luftdruck')
        # Set the parameters for the API call
        payload = {
            "phenomenon": phenomenon,
            "bbox": bounding_box,
            "from-date": start_date,
            "to-date": end_date,
            "limit": limit
        }
        # Make the API call
        print(f"Downloading data for phenomenon: {phenomenon}")
        response = requests.get(base_url, params=payload)
        print(response.url)
        #print(response.content)
        #If the request was successful, save the data to a CSV file
        if response.status_code == 200:
            # Write API response of opensensemap into a CSV file
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = f'{name}_{phenomenon}_{today}.csv'
            filepath = os.path.join('C:\\Users\\yagmur\\work\\OpenSenseMapRequests', filename)
            print(filepath)
            with open(filepath, 'wb') as f:
                f.write(response.content)
        else:
            # If the request was not successful, print and return the error message
            print(response.text)
            return response.text
    # Return None at the end of the function if all requests were successful
    return None

# Example usage
b = get_city_bounding_box("Budapest")
print(b)
phenomena = ["Temperatur", "Temperature", "temperature"]
get_box_data(b, phenomena)

# Merge temperature files into a single CSV file
merged_data = pd.DataFrame()
files = glob.glob(os.path.join(os.getcwd(), '*.csv'))
for file in files:
    csv_content = pd.read_csv(file)
    merged_data = pd.concat([merged_data, csv_content])

# Save the merged temperature data to a CSV file
merged_filename = 'merged_temperature_data.csv'
merged_filepath = os.path.join(os.getcwd(), merged_filename)
merged_data.to_csv(merged_filepath, index=False)
print(f"Merged temperature data saved to: {merged_filepath}")
