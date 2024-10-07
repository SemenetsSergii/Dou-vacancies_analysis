# DOU Vacancies Analysis

## Overview

This project is designed to scrape job vacancies from the DOU website for Python-related jobs and process the job descriptions to extract useful insights. It performs the following tasks:

- Scrapes Python job vacancies using Selenium and BeautifulSoup.
- Fetches job details (e.g., description, salary, city) asynchronously using aiohttp.
- Preprocesses and tokenizes the job descriptions.
- Counts word frequencies, excluding stopwords.
- Saves the scraped data and word frequencies in CSV files.

## Prerequisites

Make sure to have the following installed:

- Python 3.9 or higher
- pip package manager

## Installation

1. Clone the repository:

```
git clone https://github.com/SemenetsSergii/Dou-vacancies_analysis.git
cd dou-vacancies-analysis
```
2. :Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
```
3. Install dependencies:
```
pip install -r requirements.txt
```

## Running the Scraper
To run the scraper and generate the CSV files:
```
python scraping/scraper.py
```
### The scraper will:
- Extract job listings for Python developers.
- Save the job listings in data_download/python_vacancies.csv.
- Save word frequencies (top 100) in data_download/word_frequencies.csv.

### CSV Output Files
- python_vacancies.csv: Contains job title, company, city, description, salary, and URL.
- word_frequencies.csv: Contains words (excluding stopwords) and their frequency counts based on job descriptions.

## Analyzing Data using data-analysis.ipynb
Once the data has been scraped and saved into CSV files, you can further analyze it using the provided Jupyter notebook data-analysis.ipynb.

### How to Use the Notebook
- Install Jupyter Notebook: If you don't have Jupyter installed, run the following command:
```
pip install jupyter
```
- Run Jupyter Notebook: Start the notebook by navigating to the project directory and running:
```
jupyter notebook
```
This will open the Jupyter Notebook interface in your browser. From there, open the data-analysis/data-analysis.ipynb file.

### Notebook Overview: The notebook loads the python_vacancies.csv file and performs data analysis, including:

- Loading and displaying the job vacancies dataset.
- Visualizing the distribution of job titles, companies, and cities.
- Analyzing the word frequencies in job descriptions using the word_frequencies.csv file.