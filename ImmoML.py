from urllib import request
import re
from bs4 import BeautifulSoup
import json
import pandas as pd
import pickle as pkl


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

def columns_fusion(properties_df_):
    properties_df_['bathrooms_number_verified'] = properties_df_.apply(verify_bathrooms, axis=1)
    properties_df_.drop(columns=['bathrooms', 'ga4Bathrooms'], inplace=True)

    properties_df_['floor_verified'] = properties_df_.apply(verify_floor, column1='floor', column2='featureList', axis=1)
    properties_df_.drop(columns=['floor'], inplace=True)

    properties_df_['floors_int'] = properties_df_['floors'].apply(convert_floor_description_to_int)
    properties_df_.drop(columns=['floors'], inplace=True)

    for index, row in properties_df_.iterrows():
        if row["ga4Condition"] != row["condition"]:
            print(f"WARNING: condition: Values are not equal at index: {index}")
    properties_df_.drop(columns=['condition'], inplace=True)

    properties_df_['price_int'] = properties_df_["price"].apply(extract_and_convert_to_int)

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
    columns_to_move = ["multimedia", "description", "photo", "furniture"]
    auxiliary_df = properties_df[columns_to_move].copy()
    properties_df.drop(columns=columns_to_drop, inplace=True)

    columns_fusion(properties_df)
    
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
    