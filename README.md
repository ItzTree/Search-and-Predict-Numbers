# Maple Vault: Predicting the Lowest Unique Number

This project is designed to scrape result images from a website, extract previous winning numbers using Optical Character Recognition(OCR), and establish a strategy to predict future winning numbers through statistical and trend analysis.

## ✨ Key Features
- **Image Scraping**   
  Automatically downloads all images from the web page post.
- **Number Extraction (OCR)**   
  Recognizes and extracts numbers from yellow rectangles within the downloaded images.
- **Data Management**   
  Processes and saves the extracted numbers into seperate `.csv` files based on their group (round/day).
- **Outlier Filtering**   
  Filters out anomalous numbers that may result from OCR errors to improve data quality.
- **Cyclical Analysis**   
  Analyzes historical data based on a 7-day cyclical pattern.
- **Statistical Visualization**   
  Generates plots for data distribution, frequency by buckets, last-digit frequency, and trends.
- **Number Recommendation**   
  Provides a list of the top 5 recommended numbers for a future round based on a comprehensive scoring model.

## 📁 Project Structure
The project is organized into several key directories and files, each with a specific purpose. The `images/`, `data/`, and `plots/` directories are generated locally and have been excluded from this repository to keep it lightweight.
- **main.py** : This script is used to execute the primary workflows, such as initiating image scraping or data processing tasks.
- **images/** : This directory serves as the storage location for all images downloaded from the web. The OCR process reads images from this folder.
- **data/** : All generated `.csv` files are stored here. Each file, suck as `1.csv`, `2.csv`, etc., contains the extracted numbers for a specific group (round/day).
- **plots/** : This directory holds all the visual outputs from the analysis phase. Generated graphs, including distribution plots and trend charts, are saved here as image files.
- **utils/** : A package containing all the core logic of the project, broken down into modular Python Scripts:
  - \_\_init__.py : An empty file that allows the `utils` dictory to be treated as a Python package.
  - image_scraper.py : 
