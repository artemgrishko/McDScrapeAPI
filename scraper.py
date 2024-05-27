import json
import time
from contextlib import asynccontextmanager
import asyncio

import requests

from dataclasses import dataclass, fields, asdict
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy.exc import SQLAlchemyError

from db.engine import SessionLocal
from db.models import Product

URL = "https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"

NA_VALUE = "N/A"

NAME_SELECTOR = ".cmp-product-details-main__heading-title"
DESCRIPTION_SELECTOR = ".body"
CALORIES_SELECTOR = (
    "#pdp-nutrition-summary > div"
    " > div.primarynutritions.aem-GridColumn.aem-GridColumn--default--12"
    " > div > ul > li:nth-child(1) > span.value > span:nth-child(3)"
)
FATS_SELECTOR = (
    "#pdp-nutrition-summary > div "
    "> div.primarynutritions.aem-GridColumn.aem-GridColumn--default--12 > div > ul > li:nth-child(2) > span.value "
    "> span:nth-child(2)"
)
PROTEINS_SELECTOR = (
    "#pdp-nutrition-summary > div > div.primarynutritions.aem-GridColumn.aem-GridColumn--default--12 > div > ul > "
    "li:nth-child(3) > span.value > span:nth-child(2)"
)
UNSATURATED_FATS_SELECTOR = (
    "#pdp-nutrition-summary > div > div.secondarynutritions.aem-GridColumn--default--none.aem-GridColumn.aem"
    "-GridColumn--default--12.aem-GridColumn--offset--default--0 > div > div > div > "
    "div.cmp-nutrition-summary__details-column-view-desktop > ul > li:nth-child(1) > span.value > span:nth-child(1)"
)
SUGAR_SELECTOR = (
    "#pdp-nutrition-summary > div > div.secondarynutritions.aem-GridColumn--default--none.aem-GridColumn.aem"
    "-GridColumn--default--12.aem-GridColumn--offset--default--0 > div > div > div > "
    "div.cmp-nutrition-summary__details-column-view-desktop > ul > li:nth-child(2) > span.value > span:nth-child(1)"
)
SALT_SELECTOR = (
    "#pdp-nutrition-summary > div > div.secondarynutritions.aem-GridColumn--default--none.aem-GridColumn.aem"
    "-GridColumn--default--12.aem-GridColumn--offset--default--0 > div > div > div > "
    "div.cmp-nutrition-summary__details-column-view-desktop > ul > li:nth-child(3) > span.value > span.sr-only"
)
PORTION_SELECTOR = (
    "#pdp-nutrition-summary > div > div.secondarynutritions.aem-GridColumn--default--none.aem-GridColumn.aem"
    "-GridColumn--default--12.aem-GridColumn--offset--default--0 > div > div > div > "
    "div.cmp-nutrition-summary__details-column-view-desktop > ul > li:nth-child(4) > span.value > span:nth-child(1)"
)


@dataclass
class ProductDataclass:
    name: str
    description: str
    calories: int
    fats: float
    proteins: float
    unsaturated_fats: str
    sugar: str
    salt: str
    portion: str


PRODUCT_FIELDS = [field.name for field in fields(ProductDataclass)]


def normalize_str(product):
    return ' '.join(product.strip().split())


def normalize_str_to_float(product, first):
    result = product.strip().replace(f'{first}', '')
    if result == NA_VALUE:
        return None

    return float(result)


def normalize_str_to_int(product, first):
    result = product.strip().replace(f'{first}', '')
    if result == NA_VALUE:
        return None

    try:
        float_result = float(result)
        return int(float_result)
    except ValueError:
        print(f"Unable to convert {result} to int")
        return None


def safe_extract_text(selector, soup, default=""):
    try:
        return soup.select_one(selector).text
    except AttributeError:
        return default


def parse_single_product(product_soup: Tag) -> ProductDataclass:
    name = safe_extract_text(NAME_SELECTOR, product_soup)
    description = safe_extract_text(DESCRIPTION_SELECTOR, product_soup, "")

    calories = safe_extract_text(CALORIES_SELECTOR, product_soup)
    fats = safe_extract_text(FATS_SELECTOR, product_soup)
    proteins = safe_extract_text(PROTEINS_SELECTOR, product_soup)
    unsaturated_fats = safe_extract_text(UNSATURATED_FATS_SELECTOR, product_soup)
    sugar = safe_extract_text(SUGAR_SELECTOR, product_soup)
    salt = safe_extract_text(SALT_SELECTOR, product_soup)
    portion = safe_extract_text(PORTION_SELECTOR, product_soup)

    return ProductDataclass(
        name=name,
        description=description,
        calories=normalize_str_to_int(calories, "ккал"),
        fats=normalize_str_to_float(fats, "г/g"),
        proteins=normalize_str_to_float(proteins, "г/g"),
        unsaturated_fats=normalize_str(unsaturated_fats),
        sugar=normalize_str(sugar),
        salt=normalize_str(salt),
        portion=normalize_str(portion)
    )


def get_all_urls() -> list:
    page = requests.get(URL).content
    soup = BeautifulSoup(page, "html.parser")
    page_quotes = soup.select(".cmp-category__item a")

    return page_quotes


def get_all_urls_from_soup() -> list:
    links = get_all_urls()
    urls = []
    for link in links:
        href = link.get('href')
        if href:
            url = urljoin(URL, href)
            urls.append(url)

    return urls


def handle_show_more(driver: webdriver.Chrome) -> None:
    try:
        button = driver.find_element(By.CLASS_NAME, "cmp-accordion__button")
        time.sleep(1)
        button.click()
    except Exception:
        return


def get_page_soup(driver: webdriver.Chrome, url: str) -> BeautifulSoup:
    driver.get(url)
    handle_show_more(driver)

    return BeautifulSoup(driver.page_source, "html.parser")


@asynccontextmanager
async def session_scope():
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()


async def get_all_products() -> None:
    urls = get_all_urls_from_soup()
    all_products = []

    try:
        with webdriver.Chrome() as driver:
            for url in urls:
                try:
                    soup = get_page_soup(driver, url)
                    product_data = asdict(parse_single_product(soup))
                    replace_nbsp_with_space(product_data)

                    async with session_scope() as session:
                        new_product = Product(**product_data)
                        session.add(new_product)
                        all_products.append(product_data)
                except SQLAlchemyError as e:
                    print(f"Database error occurred while processing URL {url}: {e}")
                except Exception as e:
                    print(f"An error occurred while processing URL {url}: {e}")

        with open('products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"An error occurred outside the loop: {e}")


def replace_nbsp_with_space(data: dict) -> None:
    for key, value in data.items():
        if isinstance(value, str):
            data[key] = value.replace("\xa0", " ")


if __name__ == '__main__':
    asyncio.run(get_all_products())
