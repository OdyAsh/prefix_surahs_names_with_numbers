# %%
# Importing required libraries
import os
import pickle
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


# %%

# # Scraping the webpage to get the chronological order of Surahs
# url = "https://www.wikiwand.com/en/List_of_chapters_in_the_Quran"
# response = requests.get(url)
# soup = BeautifulSoup(response.text, 'html.parser')

# # Finding the table in the webpage
# table = soup.find_all('table')[0]

# # Creating a dictionary to store Surah names and their chronological order
# surah_order = {}

# # Iterating over the rows in the table (skipping the header row)
# for row in table.find_all('tr')[1:]:
#     # Extracting the chronological order and Surah name from the row
#     order, anglicized_name, all_names = [cell.text for cell in row.find_all('td')[:3]]
#     # Adding the Surah and its order to the dictionary
#     surah_order[anglicized_name] = int(order)


# %%
def flatten(lst):
    result = []
    for i in lst:
        if isinstance(i, list):
            result.extend(flatten(i))
        else:
            result.append(i)
    return result

# %%
import time
# List of URLs to scrape
urls = [
    "https://www.wikiwand.com/en/List_of_chapters_in_the_Quran",
    "https://m.wordofallah.com/quran-index",
    "https://www.arabicbible.com/for-christians/quran/1375-list-of-suras-in-the-quran.html",
]
soup = None
# Function to scrape a URL and return a dictionary of Surah names and their chronological order
def scrape_url(url, get_from_pickle=True, save_to_pickle=True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    surah_order_dicts = []
    surah_order_dict = {}
    surah_order_dict_2 = {}

    url_split_domains = url.split('//')[1].split('.')
    pickle_file_name = url_split_domains[1] + '.pickle'
    
    if get_from_pickle and os.path.exists(pickle_file_name):
        with open(pickle_file_name, 'rb') as f:
            return pickle.load(f)

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    if 'wikiwand' in url:
        table = soup.find('table')
        for row in table.find_all('tr')[1:]:
            order, anglicized_name, all_names = [cell.text for cell in row.find_all('td')[:3]]
            # Adding the Surah and its order to the dictionary
            surah_order_dict[anglicized_name.lower()] = int(order)
            surah_order_dict_2[all_names.lower()] = int(order)
    elif 'wordofallah' in url:
        # # Find all divs with class 'item' 
        divs = soup.find_all('div', class_='en')
        surah_order_list = [divs.text.split('\n')[0] for divs in divs]
        counter = 1
        for surah in surah_order_list:
            if surah.lower() not in surah_order_dict:
                surah_order_dict[surah.lower()] = counter
                counter += 1
    elif 'arabicbible' in url:
        table = soup.find('table')
        # print(table)
        for row in table.find_all('tr')[1:]:
            try:
                order, anglicized_name, en_name_but_with_ar_pronounciation = [cell.text.lower() for cell in row.find_all('td')[:3]]
            except:
                continue
            # Adding the Surah and its order to the dictionary
            surah_order_dict[anglicized_name.lower()] = int(order)
            surah_order_dict_2[en_name_but_with_ar_pronounciation.lower()] = int(order)

    surah_order_dicts.append(surah_order_dict)
    if surah_order_dict_2 != {}:
        surah_order_dicts.append(surah_order_dict_2)

    with save_to_pickle and open(pickle_file_name, 'wb') as f:
        pickle.dump(surah_order_dicts, f)

    return surah_order_dicts

# %%
# Scrape each URL and store the results in a list of dictionaries
surah_order_dicts = [so for so in flatten([scrape_url(url) for url in urls]) if  so != {}]

# %%
# Getting the list of folder names (replace this with the actual path where the folders are located)
base_path = "YOUR PATH HERE"
folder_names = os.listdir(base_path)

# Iterating over the folder names
results = []
for folder in folder_names:
    # Initialize a list to store the best match and score from each dictionary
    best_matches = []
    # Perform fuzzy matching on each dictionary
    for surah_order_dict in surah_order_dicts:
        if surah_order_dict == {}:
            continue
        best_match, score = process.extractOne(folder.lower(), surah_order_dict.keys())
        best_matches.append((best_match, score))
    # Find the best match with the highest score
    best_match, best_score = max(best_matches, key=lambda x: x[1])
    # Find the corresponding order number for the best match
    for surah_order_dict in surah_order_dicts:
        if best_match in surah_order_dict.keys():
            folder_order = surah_order_dict[best_match] 
            break
    results.append((folder_order, folder, best_match, best_score))


# %%
# sort results list by folder_order
results.sort(key=lambda x: x[0])

# %%
def rename_folders(results, debuging=False):
    global base_path
    for result in results:
        folder_order, folder_orig_name, best_match, best_score = result
        new_folder_name = f"{folder_order:03d} - {best_match.capitalize()}"
        print(f"Renaming {folder_orig_name:<15} to -> {new_folder_name}")
        if not debuging:
            src = os.path.join(base_path, folder_orig_name)
            dst = os.path.join(base_path, new_folder_name)
            try:
                os.rename(src, dst)
            except:
                print(f"WARNING: Seems that two folders have been renamed to the same name: {new_folder_name}")
                print(f"will add ({counter}) to the second folder...")
                dst = os.path.join(base_path, f"{new_folder_name} ({counter})")
                os.rename(src, dst)
                counter += 1
            counter = 1

# %%
rename_folders(results, debuging=False)

# %% [markdown]
# # Visualization of Variables (for Debugging)

# %%
surah_order_dicts[0]

# %%
surah_order_dicts[1]

# %%
surah_order_dicts[2]

# %%
results


