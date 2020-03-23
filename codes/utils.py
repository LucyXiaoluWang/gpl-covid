from . import __file__ as pkg_init_name
from pathlib import Path
import pandas as pd
import requests
import json

HOME = Path(pkg_init_name).parent.parent
DATA = HOME / 'data'
DATA_RAW = DATA / 'raw'
DATA_PROCESSED = DATA / 'processed'
DATA_INTERIM = DATA / 'interim'
MODELS = HOME / 'models'
REG_DATA = MODELS / 'reg_data'
CODES = HOME / "codes"

ISOS = ['USA','ITA','FRA','CHN','KOR','IRN']
adm3_dir_fmt = 'gadm36_{iso3}_{datestamp}.zip'

CUM_CASE_MIN_FILTER = 10

try:
    with open(CODES / "api_keys.json", "r") as f:
        API_KEYS = json.load(f)
except FileNotFoundError:
    API_KEYS = None
    
def zipify_path(path):
    return 'zip://'+str(path)


def download_zip(url, out_path, overwrite=False):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if (not out_path.exists()) or overwrite:
        r = requests.get(url, allow_redirects=True)
        with open(out_path, "wb") as f:
            f.write(r.content)
            

def iso_to_dirname(iso3):
    mapping = {
        "FRA": "france",
        "ITA": "italy",
        "USA": "usa",
        "CHN": "china",
        "IRN": "iran",
        "KOR": "korea"
    }
    return mapping[iso3]
    
    
def get_adm_zip_path(iso3, datestamp):
    dirname = iso_to_dirname(iso3)
    assert (DATA_RAW / dirname).is_dir(), DATA_RAW / dirname
    return DATA_RAW / dirname / adm3_dir_fmt.format(iso3=iso3, datestamp=datestamp)


def downcast_floats(ser):
    try:
        new_ser = ser.astype('int')
        if (new_ser == ser).all():
            return new_ser
        else:
            return ser
    except ValueError:
        return ser
    
    
def get_processed_fpath(iso3, adm_lvl):
    return DATA_PROCESSED / f'adm{adm_lvl}' / f'{iso3}_processed.csv'


def load_processed_data(iso3, adm_lvl):
    index_cols = [f'adm{i}_name' for i in range(adm_lvl+1)] + ['date']
    return pd.read_csv(get_processed_fpath(iso3, adm_lvl), index_col = index_cols, parse_dates=True).sort_index()