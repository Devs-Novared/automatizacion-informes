from src.utils import load_JSON_data

JSON_DATA = load_JSON_data(r'./static/configFile.json')
ARCHER_IDS = load_JSON_data(r'./static/archerIds.json')

URL = JSON_DATA['API']['url']

REQUESTS_DATA = (
    JSON_DATA['API']['instance_name'],
    JSON_DATA['API']['username'],
    JSON_DATA['API']['password']
)
APP_FLASK_DATA = (
    JSON_DATA['APP_FLASK']['port'],
    JSON_DATA['APP_FLASK']['host'],
    JSON_DATA['APP_FLASK']['debug_mode']
)