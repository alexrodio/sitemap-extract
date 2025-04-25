import os
import xml.etree.ElementTree as ET
import gzip
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse
import cloudscraper
import random
import glob

# Setup logging
logging.basicConfig(
    filename='sitemap_processing.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
]


def create_scraper(use_cloudscraper=True, use_proxy=False):
    if use_cloudscraper:
        scraper = cloudscraper.create_scraper()
    else:
        import requests
        scraper = requests.Session()

    if use_proxy:
        proxy = "http://your-proxy-server:port"
        scraper.proxies.update({'http': proxy, 'https': proxy})

    return scraper


def fetch_xml(url, use_cloudscraper=True, use_proxy=False):
    try:
        scraper = create_scraper(use_cloudscraper, use_proxy)
        scraper.headers['User-Agent'] = random.choice(USER_AGENTS)
        response = scraper.get(url)
        response.raise_for_status()
        return ET.fromstring(response.content)
    except Exception as e:
        logging.error(f"Failed to fetch URL {url}: {str(e)}")
        return None


def decompress_gz(url, use_cloudscraper=True, use_proxy=False):
    try:
        scraper = create_scraper(use_cloudscraper, use_proxy)
        scraper.headers['User-Agent'] = random.choice(USER_AGENTS)
        response = scraper.get(url, stream=True)
        response.raise_for_status()
        with gzip.open(response.raw, 'rb') as f:
            return ET.fromstring(f.read())
    except Exception as e:
        logging.error(f"Failed to decompress URL {url}: {str(e)}")
        return None


def save_urls(url, urls):
    try:
        filename = url.split('/')[-1].split('.')[0] + ".txt"
        with open(filename, 'w') as f:
            f.write(f"Source URL: {url}\n")
            for url_entry in urls:
                f.write(f"{url_entry}\n")
        logging.info(f"Saved {len(urls)} URLs to {filename}")
    except Exception as e:
        logging.error(f"Failed to save URLs: {str(e)}")


def read_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        return []


def find_xml_files_in_directory(directory):
    try:
        return (
                glob.glob(os.path.join(directory, '*.xml')) +
                glob.glob(os.path.join(directory, '*.xml.gz'))
        )
    except Exception as e:
        logging.error(f"Error scanning directory {directory}: {str(e)}")
        return []


def process_sitemap(url, is_compressed=False, use_cloudscraper=True, use_proxy=False):
    root = (
        decompress_gz(url, use_cloudscraper, use_proxy)
        if is_compressed
        else fetch_xml(url, use_cloudscraper, use_proxy)
    )

    if not root:
        return [], []

    sitemap_urls = []
    page_urls = []
    namespace = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    for sitemap in root.findall('.//sm:sitemap', namespace):
        loc = sitemap.find('sm:loc', namespace).text
        sitemap_urls.append(loc)

    for page in root.findall('.//sm:url', namespace):
        loc = page.find('sm:loc', namespace).text
        page_urls.append(loc)

    if page_urls:
        save_urls(url, page_urls)

    return sitemap_urls, page_urls


def process_all_sitemaps(start_urls, use_cloudscraper=True, use_proxy=False):
    all_sitemap_urls = set()
    all_page_urls = set()
    queue = start_urls.copy()

    with ThreadPoolExecutor(max_workers=5) as executor:
        while queue:
            current_url = queue.pop(0)
            is_compressed = current_url.endswith('.xml.gz')

            future = executor.submit(
                process_sitemap,
                current_url,
                is_compressed,
                use_cloudscraper,
                use_proxy
            )

            try:
                sitemap_urls, page_urls = future.result()
                all_sitemap_urls.update(sitemap_urls)
                all_page_urls.update(page_urls)
                queue.extend([url for url in sitemap_urls if url not in all_sitemap_urls])
            except Exception as e:
                logging.error(f"Error processing {current_url}: {str(e)}")

    if all_sitemap_urls:
        save_urls("sitemap_index", all_sitemap_urls)

    return all_sitemap_urls, all_page_urls


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process XML sitemaps')
    parser.add_argument('--url', type=str, help='Direct URL of the sitemap index file')
    parser.add_argument('--file', type=str, help='File containing list of URLs')
    parser.add_argument('--directory', type=str, help='Directory containing XML files')
    parser.add_argument('--no-cloudscraper', action='store_true', help='Disable Cloudscraper')
    parser.add_argument('--proxy', action='store_true', help='Enable proxy support')

    args = parser.parse_args()
    urls_to_process = []

    if args.url:
        urls_to_process.append(args.url)
    if args.file:
        urls_to_process.extend(read_urls_from_file(args.file))
    if args.directory:
        urls_to_process.extend(find_xml_files_in_directory(args.directory))

    if not urls_to_process:
        logging.error("No valid input sources provided")
        parser.print_help()
        exit(1)

    logging.info(f"Starting processing of {len(urls_to_process)} sitemap(s)")
    sitemaps, pages = process_all_sitemaps(
        urls_to_process,
        not args.no_cloudscraper,
        args.proxy
    )

    logging.info(f"Processing complete. Found:")
    logging.info(f"- {len(sitemaps)} sitemap URLs")
    logging.info(f"- {len(pages)} page URLs")
