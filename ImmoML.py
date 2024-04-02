from urllib import request
import re
from bs4 import BeautifulSoup
import json
import pandas as pd
import pickle as pkl
import re

#costanti
FLOOR_MAPPING = {
    'piano terra': -1,
    'terra': -1,
    'seminterrato': -2,
    'interrato': -2,
    'rialzato': 0,
    'mezzanino': 0,
}




#funzioni ausiliarie
def find_integers_in_string(s):
    pattern = r'\b\d+\b'  # matches any sequence of digits that forms a whole word
    numbers = [int(num) for num in re.findall(pattern, s)]
    return numbers

# Define the function to convert floor descriptions to integers
def convert_floor_description_to_int(floor_description):
    match = re.search(r'\d+', str(floor_description))
    if match:
        return int(match.group())
    return None

# Function to normalize and extract a coherent bathroom count
def normalize_bathroom_count(value):
    try:
        # Check if the value is a string and contains '+', indicating 'more than'
        if isinstance(value, str) and '+' in value:
            # Remove the '+' and convert to int, then add 1 to indicate 'more than'
            return int(value.replace('+', '')) + 1
        # Convert to int if possible
        return int(value)
    except:
        return None

# Function to extract bathrooms count from featureList
def extract_bathrooms_from_featurelist(feature_list):
    try:
        for item in feature_list:
            if item['type'] == 'bathrooms':
                # Assuming the label is like "1 bagno", extract the number only
                return int(item['label'].split()[0])
    except:
        return None

# Main function to determine the verified bathrooms count
def verify_bathrooms(row):
    bathrooms = normalize_bathroom_count(row['bathrooms'])
    ga4Bathrooms = normalize_bathroom_count(row['ga4Bathrooms'])
    feature_list_bathrooms = extract_bathrooms_from_featurelist(row['featureList'])

    # Create a set of non-None values
    unique_values = {bathrooms, ga4Bathrooms, feature_list_bathrooms} - {None}

    # If all available values are the same, or there's only one unique value, return it
    if len(unique_values) == 1:
        return unique_values.pop()
    else:
        # If there's incoherence, prioritize ga4Bathrooms, else fallback to bathrooms
        return ga4Bathrooms if ga4Bathrooms is not None else bathrooms

# Function to normalize floor descriptions and prioritize ga4FloorValue from floor column
def normalize_floor(floor_description):
    if isinstance(floor_description, dict) and 'ga4FloorValue' in floor_description:
        floor = floor_description['ga4FloorValue']
    else:
        floor = str(floor_description)
    
    floor = floor.lower().strip()
    special_cases = {
        'piano terra': -1, 'terra': -1,
        'seminterrato': -2, 'interrato': -2, 'sotterraneo': -2,
        'rialzato': 0, 'mezzanino': 0, 'piano rialzato': 0
    }
    for key, value in special_cases.items():
        if key in floor:
            return value
    if '+' in floor:
        try:
            return int(''.join(filter(str.isdigit, floor))) + 1
        except ValueError:
            pass
    else:
        try:
            return int(''.join(filter(str.isdigit, floor)))
        except ValueError:
            pass
    return None

# Function to extract the floor number from featureList using compactLabel
def extract_floor_from_featurelist(feature_list):
    for feature in feature_list:
        if feature['type'] == 'floor':
            # Use compactLabel for floor information
            return normalize_floor(feature['compactLabel'])
    return -99  # Return None if no floor info is found in featureList

# Adjusted verify_floor function
def verify_floor(row, column1, column2):
    feature_list_floor = extract_floor_from_featurelist(row['featureList'])
    floor1 = normalize_floor(row[column1])
    floor2 = normalize_floor(row[column2])

    floors = [f for f in [floor1, floor2, feature_list_floor] if f is not None]

    if len(set(floors)) == 1:
        return floors[0]
    elif len(floors) > 0:
        print(f"Warning: Inconsistent floor data at index {row.name} - choosing first non-None value")
        return floors[0]
    else:
        return None
def convert_to_int_with_plus_handling(value):
    try:
        if isinstance(value, str) and value.endswith("+"):
            # Remove the '+' and convert to int, then add 1
            return int(value[:-1]) + 1
        else:
            return int(value)
    except ValueError:
        return None

# Function to extract room number from featureList
def extract_rooms_from_featurelist(feature_list):
    for feature in feature_list:
        if feature['type'] == 'rooms':
            return convert_to_int_with_plus_handling(feature['compactLabel'])
    return None

# Function to merge room information and create the 'rooms_number' column
def merge_room_info(row):
    feature_list_rooms = extract_rooms_from_featurelist(row['featureList'])
    rooms = convert_to_int_with_plus_handling(row['rooms'])

    if rooms is not None and feature_list_rooms is not None and rooms != feature_list_rooms:
        print(f"Warning: Discrepancy in room count at index {row.name}")

    return rooms if rooms is not None else feature_list_rooms

# Function to extract the 'value' and convert it to integer
def extract_and_convert_to_int(item):
    try:
        # Assuming the item is a dictionary and 'value' is a key
        value = int(item['value'])
        return value
    except KeyError:
        # 'value' key is missing
        print(f"'value' key not found in item: {item}")
    except (ValueError, TypeError):
        # Value cannot be converted to integer
        print(f"Value cannot be converted to integer in item: {item}")
    return None  # Return None if conversion is not possible

# Function to extract elevator information from featureList
def extract_elevator_from_featurelist(feature_list):
    for feature in feature_list:
        if feature['type'].lower() == 'elevator':
            return feature['compactLabel'].lower() == 'si'  # Convert to lowercase for case independence
    return None  # Return None if no elevator info is found

# Function to merge elevator information and create the 'elevator_present' column
def merge_elevator_info(row):
    feature_list_elevator = extract_elevator_from_featurelist(row['featureList'])
    
    # Convert the values in "elevator" column to boolean, ensuring case independence
    elevator_column_value = None
    elevator_value = str(row['elevator']).lower()  # Convert to lowercase
    if elevator_value == 'vero':
        elevator_column_value = True
    elif elevator_value == 'falso':
        elevator_column_value = False

    # If there's a discrepancy, handle it based on your preference
    if feature_list_elevator is not None and elevator_column_value is not None:
        if feature_list_elevator != elevator_column_value:
            print(f"Warning: Discrepancy in elevator information at index {row.name}")
    
    # Decide which value to prefer in case of discrepancy or if one is None
    return elevator_column_value if elevator_column_value is not None else feature_list_elevator

def extract_surface_int(value):
    if pd.isnull(value):
        return None
    try:
        # Use regular expression to find the first sequence of digits
        match = re.search(r'\d+', value)
        return int(match.group()) if match else None
    except ValueError:
        return None

def extract_surface_from_featurelist(feature_list):
    if not isinstance(feature_list, list):  # Check if the input is a list
        return None
    for feature in feature_list:
        if isinstance(feature, dict) and feature.get('type') == 'surface':
            # Use regular expression to find the first sequence of digits in the 'label' value
            match = re.search(r'\d+', feature.get('label', ''))
            return int(match.group()) if match else None
    return None  # Return None if no 'surface' type is found

def surface_fusion(df):
    # Apply extraction functions to the relevant columns
    df['surface_int_from_surface'] = df['surface'].apply(extract_surface_int)
    df['surface_int_from_surfaceValue'] = df['surfaceValue'].apply(extract_surface_int)
    df['surface_int_from_featureList'] = df['featureList'].apply(extract_surface_from_featurelist)
    # Compare and assign values to surface_int column according to the provided logic
    for index, row in df.iterrows():
        surface_values = [row['surface_int_from_surface'], row['surface_int_from_surfaceValue'], row['surface_int_from_featureList']]
        if len(set([v for v in surface_values if v is not None])) <= 1:  # All values are equal or None
            df.loc[index, 'surface_int'] = row['surface_int_from_surfaceValue']  # Prefer surfaceValue, but they are all equal here
        else:
            print(f"WARNING: surface: Values are not equal at index: {index}")
            # Prefer surfaceValue unless it's None, then surface, then featureList
            df.loc[index, 'surface_int'] = row['surface_int_from_surfaceValue'] or row['surface_int_from_surface'] or row['surface_int_from_featureList']

    # Dropping the temporary columns used for comparisons
    df.drop(['surface', 'surfaceValue', 'surface_int_from_surface', 'surface_int_from_surfaceValue', 'surface_int_from_featureList'], axis=1, inplace=True)

    return df

def columns_fusion(properties_df_):
    properties_df_['bathrooms_number_verified'] = properties_df_.apply(verify_bathrooms, axis=1)
    properties_df_.drop(columns=['bathrooms', 'ga4Bathrooms'], inplace=True)

    properties_df_['floor_int'] = properties_df_.apply(verify_floor, column1='floor', column2='featureList', axis=1)
    properties_df_.drop(columns=['floor'], inplace=True)

    properties_df_['floors#_int'] = properties_df_['floors'].apply(convert_floor_description_to_int)
    properties_df_.drop(columns=['floors'], inplace=True)

    for index, row in properties_df_.iterrows():
        if row["ga4Condition"] != row["condition"]:
            print(f"WARNING: condition: Values are not equal at index: {index}")
    properties_df_.drop(columns=['condition'], inplace=True)

    properties_df_['price_int'] = properties_df_["price"].apply(extract_and_convert_to_int)
    properties_df_.drop(columns=['price'], inplace=True)

    properties_df_['rooms_number_int'] = properties_df_.apply(merge_room_info, axis=1)
    properties_df_.drop(columns=['rooms'], inplace=True)
    
    properties_df_['elevator_bool'] = properties_df_.apply(merge_elevator_info, axis=1)
    properties_df_.drop(columns=['elevator'], inplace=True)

    properties_df_ = surface_fusion(properties_df_)
    #creare una funzione generica per la fusione dei dati
    #typology, typologyV2,typologyGA4Translation,ga4features, category,energy,photo,location,balcony,featureList, ga4Garage,terrace,basement,auction

    import pdb; pdb.set_trace() 

#funzioni core
#def extract_features_from_apartments(apartment_list):
    #extract the features for a given feature list

def check_for_features_possible_combos_part1(apartment_list):
    all_apartment_features = []

    for apartment in apartment_list:
        # Dictionary to hold features for the current apartment
        apartment_features = {}
        
        # Extract features for the current apartment (different features collected in other func)
        features = apartment.find_all('div', class_='in-reListCardFeatureList__item')
        for feature in features:
            # Extract text from each feature, separating the feature type from its value
            feature_name = feature.find('use').get('xlink:href')
            feature_value = feature.get_text(strip=True)
                        
            # Add the feature to the apartment's dictionary
            apartment_features[feature_name] = feature_value

        # Add the apartment's features to the list
        all_apartment_features.append(apartment_features)

    # Create a DataFrame from the list of feature dictionaries
    df = pd.DataFrame.from_records(all_apartment_features)
    return df


    
def check_for_features_possible_combos_part2(script_tags):
    json_data = json.loads(script_tags.string)
    data = json_data['props']['pageProps']["dehydratedState"]["queries"][0]["state"]["data"]
    all_properties_data = []

    # Iterate through each result in the dataset
    for result in data['results']:
        # Check if the realEstate and properties keys exist
        if 'realEstate' in result and 'properties' in result['realEstate']:
            # Extract the ID for reference
            real_estate_id = result['realEstate']['id']
            
            # Extract each property under the 'properties' key
            for property in result['realEstate']['properties']:
                # Start with a dictionary containing the ID
                property_data = {'ID': real_estate_id}
                
                # Add all features from the property to the dictionary
                for feature_key, feature_value in property.items():
                    property_data[feature_key] = feature_value
                
                # Add the compiled property data to the list
                all_properties_data.append(property_data)

    # Convert the list of dictionaries into a DataFrame
    properties_df = pd.DataFrame(all_properties_data)
    columns_to_drop = ["income", "caption"]
    columns_to_move = ["multimedia", "description", "photo", "furniture", "typology"]
    auxiliary_df = properties_df[columns_to_move].copy()
    properties_df.drop(columns=columns_to_drop+columns_to_move, inplace=True)

    columns_fusion(properties_df)
    
    properties_df.drop(properties_df[(properties_df['auction_bool'] == True) | (properties_df['Residential_bool'] == False)].index, inplace=True)
    
    import pdb; pdb.set_trace()
    return properties_df, auxiliary_df

def download_new_data(check_features_combos=False):
    resp=request.urlopen("https://www.immobiliare.it/vendita-case/roma/")
    soup = BeautifulSoup(resp, "html.parser")
    ii=0
    if check_features_combos:
        features1_df = pd.DataFrame()
        features2_df = pd.DataFrame()
        aux_df = pd.DataFrame()
        while True:
            ii+=1
            print("Page #"+str(ii))

            apartments = soup.find_all('li', class_='in-reListItem')
            new_features1_df = check_for_features_possible_combos_part1(apartments)
            features1_df = pd.concat([features1_df, new_features1_df], ignore_index=True)

            script_tags = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
            new_features2_df, aux_new_df = check_for_features_possible_combos_part2(script_tags)
            features2_df = pd.concat([features2_df, new_features2_df], ignore_index=True)
            aux_df = pd.concat([aux_df, aux_new_df], ignore_index=True)

            next_page = soup.find('link', attrs={'rel': 'next'})
            if next_page is not None:
                next_page = next_page['href']
            else:
                print("Completed")
                break
            resp=request.urlopen(next_page)
            soup = BeautifulSoup(resp, "html.parser")
    features1_df.to_excel("features1_df.xlsx")
    features2_df.to_excel("features2_df.xlsx")
    aux_df.to_excel("aux_df.xlsx")
    return 2


if __name__ == "__main__":
    check_features_combos = True
    update_data = True
    if update_data:
        new_data_df = download_new_data(check_features_combos)
        print("Data updated")
    