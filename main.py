import json
import requests
import time
from authlib.jose import jwt
import os
import sys
import pandas as pd
import common
from dotenv import load_dotenv


EXPIRATION_TIME = int(round(time.time() + (20.0 * 60.0)))  # 20 minutes timestamp
MERGED_FILE = 'merged_file.json'
XLSX_FILE = "TestLocalization.xlsx"
XLSX_IN_APP_EVENTS = "Inn_App_Events.xlsx"

# load .env file to environment
load_dotenv()

# Security keys
KEY_ID = os.getenv('KEY_ID')
ISSUER_ID = os.getenv('ISSUER_ID')
PATH_TO_KEY = os.getenv('PATH_TO_KEY')


# Create authorization token
def get_headers(key_path):
    with open(key_path, 'r') as f:
        private_key = f.read()

    header = {
        "alg": "ES256",
        "kid": KEY_ID,
        "typ": "JWT"
    }

    payload = {
        "iss": ISSUER_ID,
        "exp": EXPIRATION_TIME,
        "aud": "appstoreconnect-v1"
    }

    # Create the JWT
    token = jwt.encode(header, payload, private_key)

    # API Request
    jwt_token = 'Bearer ' + token.decode()

    head = {
        'Authorization': jwt_token,
        "Content-Type": "application/json",
    }
    return head


#  Get list of all applications in store
def get_list_apps():
    url = f'https://api.appstoreconnect.apple.com/v1/apps'
    r = requests.get(url, headers=get_headers(PATH_TO_KEY))

    if r.status_code == 200:
        print("success get apps list")
    else:
        print(f"Помилка: {r.status_code}, {r.text}")

    common.make_directory("data")
    common.make_directory("data/applications")
    # Write the response in a pretty printed JSON file
    with open('data/applications/apps.json', 'w') as out:
        out.write(json.dumps(r.json(), indent=4))

    return r.json()


# Get versions of current application
def get_app_store_versions(application_id, directory_name):
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{application_id}/appStoreVersions"
    r = requests.get(url, headers=get_headers(PATH_TO_KEY))

    if r.status_code == 200:
        print(f"success get app ({application_id}) store versions")
    else:
        print(f"Помилка: {r.status_code}, {r.text}")

    common.make_directory(f"data/applications/{directory_name}")
    # Write the response in a pretty printed JSON file
    file_name = f"data/applications/{directory_name}/versions.json"

    with open(file_name, 'w') as out:
        out.write(json.dumps(r.json(), indent=4))

    return r.json()


# Get the list of application events and save it in the application directory.
def get_app_events(application_id, directory_name):
    url = f"https://api.appstoreconnect.apple.com/v1/apps/{application_id}/appEvents"
    r = requests.get(url, headers=get_headers(PATH_TO_KEY))

    if r.status_code == 200:
        print(f"Success get In-App events for ({application_id})")
    else:
        print(f"Помилка: {r.status_code}, {r.text}")

    common.make_directory(f"data/applications/{directory_name}")
    # Write the response in a pretty printed JSON file
    file_name = f"data/applications/{directory_name}/events.json"

    with open(file_name, 'w') as out:
        out.write(json.dumps(r.json(), indent=4))

    return r.json()


# List of localizations for current application and version
def get_app_store_version_localizations(id_version, directory_name):
    url = f"https://api.appstoreconnect.apple.com/v1/appStoreVersions/{id_version}/appStoreVersionLocalizations"
    r = requests.get(url, headers=get_headers(PATH_TO_KEY))

    if r.status_code == 200:
        print(f"success get store version localizations")
    else:
        print(f"Помилка: {r.status_code}, {r.text}")

    common.make_directory(f"data/applications/{directory_name}")
    # Write the response in a pretty printed JSON file
    file_name = f"data/applications/{directory_name}/version_localizations.json"
    with open(file_name, 'w') as out:
        out.write(json.dumps(r.json(), indent=4))

    return r.json()


# Get localizations for specific event id
def get_app_event_localizations(event_id, directory_name):
    url = f"https://api.appstoreconnect.apple.com/v1/appEvents/{event_id}/localizations"
    r = requests.get(url, headers=get_headers(PATH_TO_KEY))

    if r.status_code == 200:
        print(f"Success get event localizations")
    else:
        print(f"Помилка: {r.status_code}, {r.text}")

    common.make_directory(f"data/applications/{directory_name}")
    # Write the response in a pretty printed JSON file
    file_name = f"data/applications/{directory_name}/event_localizations.json"
    with open(file_name, 'w') as out:
        out.write(json.dumps(r.json(), indent=4))

    return r.json()


# Функція для відправлення локалізації In-App Events
def send_app_event_localization(entry):
    base_url = "https://api.appstoreconnect.apple.com/v1/appEventLocalizations/{id}"
    url = base_url.format(id=entry['id'])

    data = {
        "data": entry
    }

    try:
        r = requests.patch(url, headers=get_headers(PATH_TO_KEY), json=data)
        if r.status_code != 200:
            print(f"Помилка: {r.status_code}, {r.text}")
            return False

        print(f"Локалізація для ID {entry['id']} успішно відправлена.")
    except requests.exceptions.RequestException as e:
        print(f"Помилка відправки для ID {entry['id']}: {e}")
        return False
    return True


# Функція для відправлення локалізації
def send_app_version_localization(entry):
    base_url = "https://api.appstoreconnect.apple.com/v1/appStoreVersionLocalizations/{id}"
    url = base_url.format(id=entry['id'])

    data = {
        "data": entry
    }

    try:
        r = requests.patch(url, headers=get_headers(PATH_TO_KEY), json=data)
        if r.status_code != 200:
            print(f"Помилка: {r.status_code}, {r.text}")
            return False

        print(f"Локалізація для ID {entry['id']} успішно відправлена.")
    except requests.exceptions.RequestException as e:
        print(f"Помилка відправки для ID {entry['id']}: {e}")
        return False
    return True


def show_application_menu(applications_list):
    # Display folder names
    for i, one_app in enumerate(applications_list, 1):
        attributes = one_app['attributes']
        print(f"{i}. {attributes['name']}")

    # Ask user for folder selection
    choice = common.get_user_chose(len(applications_list))

    one_app = applications_list[choice - 1]
    attributes = one_app['attributes']
    print('')
    print(f"You chose {attributes['name']}")
    return one_app


def show_version_events_menu(application_name):
    choice_list = [f'Get versions of the {application_name}', f'Get events of the {application_name}', 'exit']
    for i, one_app in enumerate(choice_list, 1):
        print(f"{i}. {one_app}")

    # Ask user for folder selection
    choice = common.get_user_chose(len(choice_list))

    one_app = choice_list[choice - 1]
    print('')
    print(f"You chose {one_app}")
    return choice


def show_events_menu(app_events):
    data = app_events['data']
    for i, one_event in enumerate(data, 1):
        event_str = one_event['attributes']['referenceName']
        event_status = one_event['attributes']['eventState']
        print(f"{i}. {event_str}, status:{event_status}")

    choice = common.get_user_chose(len(data))
    one_event = data[choice - 1]
    version_str = one_event['attributes']['referenceName']
    print('')
    print(f"You chose {version_str} version")
    return one_event


def show_version_menu(app_version):
    data = app_version['data']
    for i, one_version in enumerate(data[:5], 1):
        version_str = one_version['attributes']['versionString']
        version_status = one_version['attributes']['appStoreState']
        print(f"{i}. {version_str}, status:{version_status}")

    choice = common.get_user_chose(len(data))
    one_version = data[choice - 1]
    version_str = one_version['attributes']['versionString']
    print('')
    print(f"You chose {version_str} version")
    return one_version


def load_xlsx_convert_to_app_version_localization(file_location):
    sheet = pd.read_excel(file_location)
    # Convert xlsx file to specified JSON format
    json_data = {"data": []}
    for _, row in sheet.iterrows():
        localization = {
            "type": "appStoreVersionLocalizations",
            "attributes": {
                "locale": row.get("locale"),
                "promotionalText": row.get("promotionalText"),
                "whatsNew": row.get("whatsNew")
            }
        }
        json_data["data"].append(localization)
    return json_data


def file_convert_to_in_app_event_localization(file_location):
    sheet = pd.read_excel(file_location)
    # Convert xlsx file to specified JSON format
    json_data = {"data": []}
    for _, row in sheet.iterrows():
        localization = {
            "type": "appEventLocalizations",
            "attributes": {
                "locale": row.get("locale"),
                "name": row.get("name"),
                "shortDescription": row.get("short"),
                "longDescription": row.get("long")
            }
        }
        json_data["data"].append(localization)
    return json_data


def merge_event_localizations(event_loc_list, new_localization_file_path):
    data2 = file_convert_to_in_app_event_localization(new_localization_file_path)

    # Створення словника для швидкого доступу до id на основі locale
    id_mapping = {item['attributes']['locale']: item['id'] for item in event_loc_list['data']}

    # Додавання id у другий файл
    for item in data2['data']:
        locale = item['attributes']['locale']
        if locale in id_mapping:
            item['id'] = id_mapping[locale]
        # deletion parameter "locale"
        item['attributes'].pop('locale', None)

    # Збереження результату
    with open(MERGED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data2, f, ensure_ascii=False, indent=4)

    print(f"Файли успішно об'єднано та збережено у '{MERGED_FILE}'.")
    return data2


def merge_localizations(localization_list, new_localization_file_path):
    data2 = load_xlsx_convert_to_app_version_localization(new_localization_file_path)

    # Створення словника для швидкого доступу до id на основі locale
    id_mapping = {item['attributes']['locale']: item['id'] for item in localization_list['data']}

    # Додавання id у другий файл
    for item in data2['data']:
        locale = item['attributes']['locale']
        if locale in id_mapping:
            item['id'] = id_mapping[locale]
        # deletion parametr "locale"
        item['attributes'].pop('locale', None)

    # Збереження результату
    with open(MERGED_FILE, 'w', encoding='utf-8') as f:
        json.dump(data2, f, ensure_ascii=False, indent=4)

    print(f"Файли успішно об'єднано та збережено у '{MERGED_FILE}'.")
    return data2


def upload_new_app_version_localizations(localization):
    # Відправка локалізацій
    all_successful = True
    for item in localization['data']:
        if not send_app_version_localization(item):
            all_successful = False
            print("Операція невдала. Припиняємо виконання.")
            break

    if all_successful:
        print("Усі локалізації успішно відправлені.")


def upload_new_in_app_event_localizations(localization):
    # Відправка локалізацій
    all_successful = True
    for item in localization['data']:
        if not send_app_event_localization(item):
            all_successful = False
            print("Операція невдала. Припиняємо виконання.")
            break

    if all_successful:
        print("Усі локалізації успішно відправлені.")


def update_version_localizations_pipeline():
    print(f"--  Versions for ({app_name})  --")
    app_versions = get_app_store_versions(app_id, app_sku)
    version = show_version_menu(app_versions)
    localizations_list = get_app_store_version_localizations(version['id'], app_sku)
    application_version = version['attributes']['versionString']
    print(f'-- Success get localizations for version: {application_version} --')
    print("- Try to find localization file ...")
    # If file with localization exist try to merge new localizations with id's to upload data later
    check_file = os.path.isfile(XLSX_FILE)
    if check_file:
        localization_data = merge_localizations(localizations_list, XLSX_FILE)
        can_upload = common.query_yes_no(f'Upload localizations to App Store for {app_name} and version:'
                                         f'{application_version}?')
        if can_upload:
            upload_new_app_version_localizations(localization_data)
    else:
        print(f'ERROR: Can`t find file:{XLSX_FILE}')


def update_events_localizations_pipeline():
    print(f"--  Events for ({app_name})  --")
    app_events = get_app_events(app_id, app_sku)
    event = show_events_menu(app_events)
    event_name = event['attributes']['referenceName']
    event_localizations = get_app_event_localizations(event['id'], app_sku)
    print("- Try to find localization file ...")
    check_file = os.path.isfile(XLSX_IN_APP_EVENTS)
    if check_file:
        localization_data = merge_event_localizations(event_localizations, XLSX_IN_APP_EVENTS)
        can_upload = common.query_yes_no(f'Upload localizations to App Store for {app_name} and In-App event:'
                                         f'{event_name}?')
        if can_upload:
            upload_new_in_app_event_localizations(localization_data)
    else:
        print(f'ERROR: Can`t find file:{XLSX_FILE}')


if __name__ == '__main__':
    applications = get_list_apps()

    if 'errors' in applications:
        sys.exit(1)

    print("")
    print("Select application")
    application = show_application_menu(applications['data'])
    app_name = application['attributes']['name']
    app_id = application['id']
    app_sku = application['attributes']['sku']

    user_choice = show_version_events_menu(app_sku)

    if user_choice == 3:
        sys.exit(0)
    elif user_choice == 1:
        update_version_localizations_pipeline()
    elif user_choice == 2:
        update_events_localizations_pipeline()
