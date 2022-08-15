# Import Packages
import pandas as pd
import numpy as np
import requests
import yaml

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

# Data Manipulation
try:
    sides_batch_wise = pd.DataFrame()
    sides_list = []
    max_batch = corgis_df['batch'].value_counts().count()
    for addy in corgis_df["address"].unique():
        sides_df = corgis_df[corgis_df["address"] == addy]

        # Sides per Batch
        batch_counts = pd.DataFrame(sides_df['batch'].dropna().value_counts())
        batch_counts.reset_index(inplace=True)
        batch_counts.columns = ['Batch', 'Number of Sides']
        batch_counts.sort_values(by=['Batch'], axis=0, inplace=True)
        min_sides = batch_counts['Number of Sides'].min()
        batch_counts['Bool'] = batch_counts['Number of Sides'].apply(lambda i: True if i >= min_sides else False)
        batch_counts['address'] = addy

        # Multiplier
        if (batch_counts["Bool"].all(axis=0)) & (min_sides >= 1) & (len(batch_counts) == max_batch):
            sides_list.append([addy, min_sides])

        batch_counts = batch_counts[["address", "Batch", "Number of Sides"]]
        sides_batch_wise = pd.concat([sides_batch_wise, batch_counts], axis=0)

    sides_batch_wise.to_csv("data/Sides Batch Wise.csv", index=False)

    multiplier = pd.DataFrame(sides_list)
    multiplier.columns = ["address", "Multiplier"]
    multiplier = multiplier.sort_values(by="Multiplier", ascending=False)
    multiplier.to_csv("data/Multiplier Address Wise.csv", index=False)

    # Ticket Calculation
    tickets = 0
    tickets_list = []
    for addy in corgis_df["address"].unique():

        # Address Filter
        filtered = corgis_df[corgis_df["address"] == addy]

        # Main Tickets
        main = filtered[filtered["type"] == "main"].shape[0] * 4

        # Side Tickets
        if filtered["address"].isin(multiplier["address"]).all():
            side = ((multiplier.loc[multiplier["address"] == addy, "Multiplier"].values[0] * max_batch * 2) +
                    (filtered.loc[filtered["type"] == "side"].shape[0] -
                     multiplier.loc[multiplier["address"] == addy, "Multiplier"].values[0] * max_batch))
        else:
            side = filtered[filtered["type"] == "side"].shape[0]

        # Special Tickets
        special = filtered[filtered["type"] == "special"].shape[0]

        # Total Tickets
        tickets = main + side + special

        tickets_list.append([addy, tickets])

    tickets_df = pd.DataFrame(tickets_list)
    tickets_df.columns = ["address", "tickets"]
    tickets_df = tickets_df.sort_values(by="tickets", ascending=False)
    tickets_df.to_csv("data/Tickets Address Wise.csv", index=False)

    address_df = tickets_df.set_index(keys = "address")
    address_df = address_df.squeeze()
    address_df = pd.Series(np.repeat(address_df.index, address_df))
    address_df.to_csv("data/Address List.csv", index=False)

except Exception as e:
    error = {"error": e}
