import requests
import json
import time
import schedule
import threading
from datetime import datetime, timezone
import dotenv
import os
import logging

# Setup logging to file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("torbox_purge.log"),
        logging.StreamHandler()
    ]
)

dotenv.load_dotenv()
ETA_THRESHOLD = int(os.getenv('ETA_THRESHOLD_TORBOX', 60 * 60 * 24))  # 24 hours in seconds
STALL_THRESHOLD = int(os.getenv('STALL_THRESHOLD_TORBOX', 60 * 60 * 2))  # 2 hours in seconds
API_TOKEN_TORBOX = os.getenv('API_TOKEN_TORBOX')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL_TORBOX', 10 * 60 ))  # 10 minutes in seconds
REQUEST_TIMEOUT = 300
# Stop event for scheduler thread
stop_scheduler = threading.Event()

if not API_TOKEN_TORBOX:
    logging.warning("API_TOKEN_TORBOX environment variable is not set. API requests will fail.")

def delete_file(torrent_id,type):
    """
    Delete a torrent from the Torbox API.
    :param torrent_id: The ID of the torrent to delete.
    :return: The response from the API.
    """
    if type == 'torrent':
        url = "https://api.torbox.app/v1/api/torrents/controltorrent"
        payload = json.dumps({
            "torrent_id": torrent_id,
            "operation": "delete",
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN_TORBOX}'
        }
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            return response
        except requests.exceptions.Timeout:
            print(f"Request to delete torrent {torrent_id} timed out after {REQUEST_TIMEOUT} seconds")
            return None
        except Exception as e:
            print(f"Error deleting torrent {torrent_id}: {str(e)}")
            return None
    elif type == 'webdl':
        #{{api_base}}/{{api_version}}/api/webdl/controlwebdownload
        url = f"https://api.torbox.app/v1/api/webdl/controlwebdownload"
        payload = json.dumps({
            "webdl_id": torrent_id,
            "operation": "delete",
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {API_TOKEN_TORBOX}'
        }
        try:
            response = requests.post(url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            return response
        except requests.exceptions.Timeout:
            print(f"Request to delete webdl {torrent_id} timed out after {REQUEST_TIMEOUT} seconds")
            return None
        except Exception as e:
            print(f"Error deleting webdl {torrent_id}: {str(e)}")
            return None
    else:
        print(f"Invalid type: {type}")
        return None
            



def get_torrent_list():
    """
    Fetch all torrents from the API using pagination with offset
    Returns:
        dict: JSON response containing all torrents
    """
    all_torrents_data = []
    offset = 0
    limit = 1000
    has_more = True
    while has_more:
        url = f"https://api.torbox.app/v1/api/torrents/mylist?offset={offset}&limit={limit}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {API_TOKEN_TORBOX}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logging.error(f"Failed to fetch torrents: {response.status_code} {response.text}")
                break
            current_data = response.json()
            if 'data' in current_data and len(current_data['data']) > 0:
                all_torrents_data.extend(current_data['data'])
                offset += limit
                print(f"Fetched {len(current_data['data'])} torrents. Total so far: {len(all_torrents_data)}")
            else:
                has_more = False
        except requests.exceptions.Timeout:
            print(f"Request to get torrent list timed out after {REQUEST_TIMEOUT} seconds (offset={offset})")
            has_more = False
        except Exception as e:
            print(f"Error getting torrent list (offset={offset}): {str(e)}")
            has_more = False
    for item in all_torrents_data:
        item['type'] = 'torrent'


    return all_torrents_data


def get_webdl_list():
    """
    Fetch all webdl torrents from the API using pagination with offset
    Returns:
        dict: JSON response containing all webdl torrents
    """
    all_webdl_data = []
    offset = 0
    limit = 1000
    has_more = True
    while has_more:
        url = f"https://api.torbox.app/v1/api/webdl/mylist?offset={offset}&limit={limit}"
        payload = {}
        headers = {
            'Authorization': f'Bearer {API_TOKEN_TORBOX}'
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                logging.error(f"Failed to fetch webdl torrents: {response.status_code} {response.text}")
                break
            current_data = response.json()
            if 'data' in current_data and len(current_data['data']) > 0:
                all_webdl_data.extend(current_data['data'])
                offset += limit
                print(f"Fetched {len(current_data['data'])} webdl torrents. Total so far: {len(all_webdl_data)}")
            else:
                has_more = False
        except requests.exceptions.Timeout:
            print(f"Request to get webdl list timed out after {REQUEST_TIMEOUT} seconds (offset={offset})")
            has_more = False
        except Exception as e:
            print(f"Error getting webdl list (offset={offset}): {str(e)}")
            has_more = False

    for item in all_webdl_data:
        item['type'] = 'webdl'


    return all_webdl_data
        


def identify_stalled_files(torrents_data):
    """
    Identify torrents that are stalled or have excessive ETA
    Args:
        torrents_data (dict): The torrents data from the API
    Returns:
        list: List of stalled torrents
    """
    stalled_torrents = []
    for item in torrents_data:
        try:
            created = datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            item['time_since_created'] = (now - created).total_seconds()
        except Exception as e:
            logging.error(f"Error parsing created_at for torrent {item.get('id')}: {e}")
            continue
    
        if (
            item['download_state'] == 'metaDL' or 
            item['download_state'] == 'stalled (no seeds)' or 
            item['download_state'] == 'stalledDL' or 
            item['download_state'] == 'checking' or 
            item['download_state'] == 'missingFiles' or
            item['download_state'] == 'uploading (no peers)' or 
            item['download_state'] == 'uploading'
        ) and item['time_since_created'] >= STALL_THRESHOLD:
            stalled_torrents.append(item)
        elif item['download_state'] == 'downloading' and item['time_since_created'] > ETA_THRESHOLD:
            stalled_torrents.append(item)
    return stalled_torrents


def clean_up_files(stalled_torrents):
    """
    Delete stalled torrents
    
    Args:
        stalled_torrents (list): List of torrents to delete
    """
    for item in stalled_torrents:
        torrent_id = item['id']
        response = delete_file(torrent_id,item['type'])
        if response:
            print(f"Delete response for torrent {torrent_id}:")
            print(response.text)
            logging.info(f"Delete response for torrent {torrent_id}: {response.text}")
            logging.info(response.text)
        else:
            print(f"Failed to delete torrent {torrent_id}")
            logging.error(f"Failed to delete torrent {torrent_id}")
        print('---')



def main_task():
    """
    Main function that runs the torrent cleanup task
    """
    print(f"Running torrent cleanup task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Running torrent cleanup task at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    files_types = os.getenv('FILES_TYPES').split(',')
    data = [] 
    for file_type in files_types:
        if file_type == 'torrent':
            data.extend(get_torrent_list())
        elif file_type == 'webdl':
            data.extend(get_webdl_list())

    # Identify stalled torrents
    stalled_torrents = identify_stalled_files(data)
    # Print stalled torrents
    print('Stalled items:')
    logging.info('Stalled items:')
    for item in stalled_torrents:
        print(item['id'], end=', ')
    clean_up_files(stalled_torrents)



def run_scheduler():
    """
    Run the scheduler in a loop until stop_scheduler event is set
    """
    schedule.every(CHECK_INTERVAL).seconds.do(main_task)
    # Run once immediately at startup
    main_task()
    
    # Keep the scheduler running until stop event is set
    while not stop_scheduler.is_set():
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()