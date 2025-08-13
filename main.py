from utils.extract_csv import create_csv
from utils.image_scraper import scrape_images
from utils.analyze_data import run_full_analysis

if __name__ == "__main__":
    IMG_DIR = 'images/'
    CSV_DIR= 'data/'

    URL = 'https://www.inven.co.kr/board/maple/5974/5470567'
    GID = 27

    # scrape_images(URL, GID, IMG_DIR)
    # create_csv(GID, IMG_DIR, CSV_DIR)

    # run_full_analysis(28)