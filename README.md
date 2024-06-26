﻿# McDonald's Menu API

This project scrapes data from the McDonald's Ukraine website to create an API providing information about their menu items. It includes endpoints to retrieve information about all products, a specific product, or a specific field of a product.

## Installing using GitHub

```shell
git clone https://github.com/artemgrishko/McDScrapeAPI.git
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run the Web Scraping Script:**
```shell
python scraper.py
```

**For running FastAPI server:**
```shell
python -m uvicorn main:app --reload
```

## Endpoints

GET /all_products/: Returns information about all products on the menu.

GET /products/{product_name}: Returns information about a specific product.

GET /products/{product_name}/{product_field}: Returns information about a specific field of a specific product.

Also you can use docs:
GET /docs/
