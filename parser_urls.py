import pickle
import requests
import os
import time
from datetime import timedelta, datetime
from loguru import logger
from urlextract import URLExtract
from multiprocessing import Process, Manager

str_time = '%Y-%m-%d_%H:%M:%S'
logger.add("dir_logs/file_{time}.log", rotation="5 minutes")


def clean_logs():
    files = [file for file in os.listdir('dir_logs') if file.endswith('.log')]
    file_time = [(file, file.split('_')[2].split('-')) for file in files]
    file_time = [(file, timedelta(hours=int(f_time[0]), minutes=int(f_time[1]))) for file, f_time in file_time]
    file_time.sort(key=lambda x: x[0])
    for log_file, f_time in file_time:
        current_time = timedelta(hours=datetime.now().hour, minutes=datetime.now().minute)
        elapsed_time = current_time.seconds - f_time.seconds
        minutes = int(time.ctime(elapsed_time).split()[3].split(':')[1])
        if minutes > 20:
            os.remove(f'dir_logs/{log_file}')
            logger.info(f"Logfile '{log_file}' has been deleted")


def get_list_urls(filename, list_urls):
    extractor = URLExtract()
    with open(filename, 'rb') as file:
        list_data = pickle.load(file)
        for line in list_data:
            urls = extractor.find_urls(line)
            if urls == []:
                continue
            else:
                for url in urls:
                    if 'http://' in url or 'https://' in url:
                        list_urls.append(url)
                    else:
                        http_url = f'http://{url}/'
                        list_urls.append(http_url)
            if len(list_urls) == 0:
                logger.info(f"In the file were found {len(list_urls)} link")
            elif len(list_urls) > 1:
                logger.info(f"In the file were found {len(list_urls)} links")
            clean_logs()
    return list_urls


def get_dict_urls(list_urls, urls_dict):
    for url in list_urls:
        try:
            response = requests.head(url)
            urls_dict[url] = response.status_code
            logger.info(f"| Link | ({url}) | Status code | {response.status_code} |")
            clean_logs()
        except Exception as ex:
            logger.error(f"| Link | ({url}) | Error | {ex} |")
            clean_logs()
            continue
    return urls_dict


def get_dict_unshorten_urls(list_urls, urls_dict):
    for url in list_urls:
        try:
            unshorten_link = requests.get(url, timeout=5)
            clean_logs()
            if unshorten_link.url.split('//')[1] == url.split('//')[1]:
                logger.info(f"| Link | ({url}) | Unshorten-link | False |")
                clean_logs()
                continue
            else:
                urls_dict[url] = unshorten_link.url
                logger.info(f"| Link | ({url}) | Unshorten-link | True |")
            clean_logs()
        except Exception as ex:
            logger.error(f"| Link | ({url}) | Error | {ex} |")
            clean_logs()
            continue
    return urls_dict


if __name__ == '__main__':
    file = input('Enter filename: ')    # 'messages_to_parse.dat'
    dir_logs = 'dir_logs'
    if not os.path.exists(dir_logs):
        os.mkdir(f'dir_logs')

    with Manager() as manager:
        list_urls = manager.list()
        dict_urls = manager.dict()
        dict_unshorten_urls = manager.dict()

        process1 = Process(target=get_list_urls, args=(file, list_urls))
        process2 = Process(target=get_dict_urls, args=(list_urls, dict_urls))
        process3 = Process(target=get_dict_unshorten_urls, args=(list_urls, dict_unshorten_urls))

        process1.start()
        process2.start()
        process3.start()

        process1.join()
        process2.join()
        process3.join()

        logger.info(f"| Dictionary urls | Length | {len(dict_urls)} |")
        logger.info(f"| Dictionary unshorten urls | Length | {len(dict_unshorten_urls)} |")
        clean_logs()
