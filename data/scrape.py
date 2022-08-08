# Import Packages
import yaml
import requests
import pandas as pd

params_path = "./params.yaml"


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


config = read_params(params_path)

# Scrape Data
try:
    corgis_df = pd.read_csv(config["scrape"]["sheets_url"])
    address = config["scrape"]["address"]
    metadata = config["scrape"]["metadata"]

    addy_list = []
    for i in corgis_df["token"]:
        nft = requests.get(address.format(i))
        # Status Code Check
        if nft.status_code == 200:
            addy_list.append(nft.json()["nft"]["owner"])

    corgis_df['address'] = addy_list  # Appending address to DF

    thumb_list = []
    for i in corgis_df["token"]:
        nft = requests.get(metadata.format(i))
        # Status Code Check
        if nft.status_code == 200:
            thumb_list.append(nft.json()['thumbnail'])

    corgis_df['image'] = thumb_list  # Appending image to DF

except Exception as e:
    error = {"error": e}

# Save to CSV
try:
    corgis_df.to_csv("data/corgis.csv", index=False)
except Exception as e:
    error = {"error": e}
