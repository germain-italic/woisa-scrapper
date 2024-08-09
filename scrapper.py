import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import configparser
import logging
from urllib.parse import urljoin

# Set up logging to file
logging.basicConfig(filename='debug.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')  # 'w' mode overwrites the file on each run

def load_config(config_file='config.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_session(cookie_name, cookie_value):
    session = requests.Session()
    session.cookies.set(cookie_name, cookie_value)
    return session

def navigate_to_documents(session, document_url):
    logging.info(f"Navigating to document page: {document_url}")
    response = session.get(document_url)
    if response.status_code != 200:
        logging.error(f"Failed to load document page. Status code: {response.status_code}")
        logging.error(f"Response content: {response.text}")
        raise Exception("Failed to load document page")
    logging.info("Successfully loaded document page.")
    return response.text

def get_document_links(html_content, base_url):
    logging.info("Extracting document links from the page.")
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', id='TabDoc')
    if not table:
        logging.error("Could not find the document table on the page.")
        return []

    documents = []
    for row in table.find_all('tr'):
        date_cell = row.find('td', {'data-title': 'Date'})
        link_cell = row.find('a', class_='voir')
        if date_cell and link_cell:
            date = date_cell.text.strip()
            link = urljoin(base_url, link_cell['href'])
            documents.append((date, link))

    logging.info(f"Found {len(documents)} documents.")
    return documents

def download_document(session, link, date, save_dir):
    date_obj = datetime.strptime(date, '%d/%m/%Y %Hh%M')
    filename = f"{date_obj.strftime('%Y-%m-%d_%Hh%M')}.pdf"
    save_path = os.path.join(save_dir, filename)

    logging.info(f"Attempting to download: {filename}")

    response = session.get(link, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Successfully downloaded: {filename}")
    else:
        logging.error(f"Failed to download: {filename}. Status code: {response.status_code}")

def main():
    config = load_config()

    cookie_name = config['Cookie']['name']
    cookie_value = config['Cookie']['value']
    start_page = int(config['Scraping']['start_page'])
    end_page = int(config['Scraping']['end_page'])
    save_dir = config['Paths']['save_dir']
    base_url = config['URLs']['base_url']
    document_base_url = config['URLs']['document_base_url']

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    session = create_session(cookie_name, cookie_value)

    try:
        for page in range(start_page, end_page + 1):
            page_url = f"{document_base_url}{page}"
            html_content = navigate_to_documents(session, page_url)
            documents = get_document_links(html_content, base_url)

            for date, link in documents:
                download_document(session, link, date, save_dir)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()