import asyncio
import csv
import os
import re
import time
from collections import Counter

import aiohttp
import nltk
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


nltk.download("stopwords")

STOPWORDS = set(stopwords.words("english"))

VACANCIES_URL = "https://jobs.dou.ua/vacancies/?category=Python"


async def fetch_job_details(session: ClientSession, job_url: str) -> dict:
    try:
        async with session.get(job_url, timeout=10) as response:
            if response.status != 200:
                return {
                    "description": "Failed to fetch data",
                    "city": "Unknown",
                }

            job_page = await response.text()
            soup = BeautifulSoup(job_page, "html.parser")

            job_description_div = soup.find(
                "div",
                class_="b-typo vacancy-section"
            )
            job_description = (
                job_description_div.text.strip().replace("\xa0", " ")
                if job_description_div
                else "No description available"
            )

            city_span = soup.find("span", class_="place bi bi-geo-alt-fill")
            city = city_span.text.strip() if city_span else "Unknown"

            return {
                "description": job_description,
                "city": city,
            }

    except (asyncio.TimeoutError, aiohttp.ClientError) as e:
        return {
            "description": f"Error: {str(e)}",
            "city": "Unknown",
        }


def preprocess_text(text):
    words = re.findall(r"\b\w+\b", text.lower())
    words = [word for word in words if word not in STOPWORDS and len(word) > 2]
    return words


async def fetch_and_parse_vacancies(
    driver: webdriver.Chrome, session: ClientSession, url: str
) -> list:
    while True:
        try:
            load_more_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".more-btn a")
                )
            )

            if "display: none" in load_more_button.get_attribute("style"):
                print("'Load More' button is hidden.")
                break

            if (load_more_button.is_displayed()
                    and load_more_button.is_enabled()):
                load_more_button.click()
                time.sleep(2)
        except TimeoutException as e:
            print(f"Timeout while waiting for 'Load More' button: {e}")
            break
        except Exception as e:
            print(f"Error while clicking 'Load More' button: {e}")
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    vacancy_cards = soup.find_all("li", class_="l-vacancy")

    job_listings = []
    for vacancy in vacancy_cards:
        title_tag = vacancy.find("a", class_="vt")
        company_tag = vacancy.find("a", class_="company")
        salary_tag = vacancy.find("span", class_="salary")
        salary = (salary_tag.text.strip().replace("\xa0", "").
                  replace("від", "").
                  strip()) if salary_tag else "Not provided"
        if title_tag and company_tag:
            job_listings.append(
                {
                    "title": title_tag.text.strip(),
                    "company": company_tag.text.strip(),
                    "city": "",
                    "description": "",
                    "salary": salary,
                    "url": title_tag["href"],
                }
            )

    tasks = [fetch_job_details(session, job["url"]) for job in job_listings]
    descriptions = await asyncio.gather(*tasks)

    for i, job in enumerate(job_listings):
        job["description"] = descriptions[i]["description"]
        job["city"] = descriptions[i]["city"]

    return job_listings


async def scrape_all_vacancies() -> None:
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
            options=chrome_options
    ) as driver:
        async with ClientSession() as session:
            all_vacancies = []
            all_descriptions = []

            driver.get(VACANCIES_URL)
            job_listings = await fetch_and_parse_vacancies(
                driver, session, VACANCIES_URL
            )
            all_vacancies.extend(job_listings)
            all_descriptions.extend(
                [job["description"] for job in job_listings]
            )

            all_words = []
            for description in all_descriptions:
                all_words.extend(preprocess_text(description))

            word_freq = Counter(all_words)

            os.makedirs("data_download", exist_ok=True)
            with open(
                "data_download/python_vacancies.csv",
                    "w",
                    encoding="utf-8",
                    newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerow(
                    [
                        "title",
                        "company",
                        "city",
                        "description",
                        "salary",
                        "url"
                    ]
                )
                for vacancy in all_vacancies:
                    writer.writerow(
                        [
                            vacancy["title"],
                            vacancy["company"],
                            vacancy["city"],
                            vacancy["description"],
                            vacancy["salary"],
                            vacancy["url"],
                        ]
                    )

            with open(
                "data_download/word_frequencies.csv",
                    "w",
                    encoding="utf-8",
                    newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerow(["Word", "Frequency"])
                for word, freq in word_freq.most_common(100):
                    writer.writerow([word, freq])

            print("Data saved in 'data_download/'.")


if __name__ == "__main__":
    asyncio.run(scrape_all_vacancies())
