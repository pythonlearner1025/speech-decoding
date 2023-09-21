import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import concurrent.futures
import zipfile

def download_file(fname, link, dest_folder):
    response = requests.get(link, stream=True)
    fname = os.path.join(dest_folder, fname)

    with open(fname, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {fname}")

def download_audios_from_site(site_url, dest_folder):
    res = requests.get(site_url)
    fname = os.path.join(dest_folder, 'audio.zip')

    with open(fname, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            f.write(chunk)
    
    with zipfile.ZipFile(fname, 'r') as zip_ref:
        zip_ref.extractall(dest_folder)
    

def download_raws_from_site(site_url, dest_folder):
    # Ensure destination folder exists or create it
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    # Setup the selenium driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("disable-dev-shm-usage") #/ Bypass OS security model
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(site_url)

        # Parse all elements with id="file_download"
        elements = driver.find_elements(By.ID, 'file_download')

        # Filter the elements based on the inner text
        to_download = [
            e for e in elements if e.text.endswith('.mat') and 'dat' not in e.text 
        ]

        # Construct the download links
        base_url = 'https://deepblue.lib.umich.edu'
        download_links = []
        for e in to_download:
            href = e.get_attribute('href')
            if href.startswith('http') or href.startswith('https'):
                download_links.append((e.text,href))
            else:
                download_links.append((e.text, base_url + href))

        # Use ThreadPoolExecutor to download files in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(download_file, fname, link, dest_folder) for fname, link in download_links]
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                print("downloading file: ", i)
                try:
                    future.result()
                except Exception as exc:
                    print(f"Generated an exception: {exc}")
    finally:
        driver.quit()

if __name__ == '__main__':
    ABS = os.getcwd()
    DEST_RAW = os.path.join(ABS, "data/Brennan2018/raw")  # Replace with your actual destination folder path
    DEST_AUDIO = os.path.join(ABS,"data/Brennan2018")
    URL = "https://deepblue.lib.umich.edu/data/concern/data_sets/bg257f92t#items_display"  # Replace with the website URL you want to scrape
    download_raws_from_site(URL, DEST_RAW)
    download_audios_from_site('https://deepblue.lib.umich.edu/data/downloads/t435gf09p',DEST_AUDIO)


