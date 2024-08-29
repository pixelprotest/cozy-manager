import requests
from bs4 import BeautifulSoup

def get_model_type(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all table rows
    rows = soup.find_all('tr')
    
    for row in rows:
        # Check if 'Type' is in the row text
        if 'Type' in row.get_text():
            # Find the badge within this row
            badge = row.find('span', class_='mantine-Badge-inner')
            if badge:
                return badge.text.strip()
    
    print("Type row or badge not found")
    return None

def get_base_model(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all table rows
    rows = soup.find_all('tr')

    model_base_index = None 
    for i, row in enumerate(rows):
        if 'Base Model' in row.get_text():
            model_base_index = i + 1
    
    ## now we know the model base index, we can look into this row.
    if model_base_index is not None:
        base_model_row = rows[model_base_index]
        base_model_div = base_model_row.find('div', class_='mantine-Text-root')
        if base_model_div:
            return base_model_div.text.strip()
         
    print("Base Model information not found")
    return None

if __name__ == "__main__":
    url = "https://civitai.com/models/118025/360redmond-a-360-view-panorama-lora-for-sd-xl-10"
    print(get_model_type(url))
    print(get_base_model(url))