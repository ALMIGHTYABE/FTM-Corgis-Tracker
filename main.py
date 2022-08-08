# Importing Libraries
import time
import pandas as pd  # read csv, df manipulation
import streamlit as st  # data web app development
import yaml

# App
st.set_page_config(
    page_title="FTM Corgis Tracker",
    page_icon="icons/corgi.png",
    layout="wide",
)

# Dashboard Title
col1, col2 = st.columns(2)
col1.title("FTM Corgis Tracker")
col2.markdown('<div style="text-align: right;">Data is updated every 30 minutes</div>', unsafe_allow_html=True)

# Params
params_path = "params.yaml"


def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


config = read_params(params_path)

# Read Data
dataset_url = config["main"]["data-source"]


def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)


df = get_data()

# Top-Level Filters
address_filter = st.multiselect("Select your address", pd.unique(df["address"]))


# creating a single-element container
placeholder = st.empty()

# dataframe filter
df = df[df["address"].isin(address_filter)]


# calculate tickets
print(df)


# Empty Placeholder Filled
with placeholder.container():
    if address_filter:
        # Number of NFTS
        st.markdown("### Number of FTM Corgis: {}".format(str(df.shape[0])))

        # Image
        st.image(df["image"].tolist(), caption=[i for i in df["name"]])  # Images


    time.sleep(1)
