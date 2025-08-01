import scrapy
import datetime
import json
import csv
import os
import re
import pytz

class TableSpider(scrapy.Spider):
    name = "table_spider"
    start_urls = ["https://www.bankrate.com/mortgages/mortgage-rates/"]

    def parse(self, response):
        ist = pytz.timezone('Asia/Kolkata')
        today = datetime.datetime.now(ist).date().isoformat()
        csv_path = "output.csv"
        json_path = "output.json"

        rows = response.xpath('(//ul[.//li//button[contains(text(), "Purchase") and @tabindex="0"]]/following-sibling::div/div/table[contains(@class, "Table--numerical")])[1]/tbody/tr')

        scraped_data = []

        for row in rows:
            product = row.xpath('.//th/a/text()').get()
            if not product:
                product = row.xpath('.//th/text()').get()

            interest_rate = row.xpath('.//td[1]/text()').get()
            apr = row.xpath('.//td[2]/text()').get()

            # Extract year from product using regex
            loan_term_years = None
            if product:
                match = re.search(r'(\d+)-Year', product)
                if match:
                    loan_term_years = int(match.group(1))

            # Get just the text content (not the full <p> tag)
            updated_text = row.xpath('(//p[starts-with(text(), "Rates as of")])[1]/text()').get()

            date_match = re.search(r'([A-Za-z]+ \d{1,2}, \d{4})', updated_text)

            updated_date = None
            if date_match:
                raw_date = date_match.group(1)  # "July 25, 2025"
                parsed_date = ist.localize(datetime.datetime.strptime(raw_date, "%B %d, %Y"))
                updated_date = parsed_date.strftime("%Y-%m-%d")             

            item = {
                'Product': product.strip() if product else None,
                'Interest Rate': interest_rate.strip() if interest_rate else None,
                'APR': apr.strip() if apr else None,
                'timestamp': today,
                'lender_name': 'BankRate',
                'loan_term_years': loan_term_years,
                'updated_date': updated_date
            }

            scraped_data.append(item)

        # Load existing JSON data (if any)
        existing_data = []
        if os.path.exists(json_path):
            with open(json_path, 'r') as f_json:
                try:
                    existing_data = json.load(f_json)
                except json.JSONDecodeError:
                    existing_data = []

        # Filter out duplicates based on Product + timestamp
        new_data = []
        existing_keys = {(item['Product'], item['timestamp']) for item in existing_data}

        for item in scraped_data:
            key = (item['Product'], item['timestamp'])
            if key not in existing_keys:
                new_data.append(item)

        if not new_data:
            self.logger.info(f"No new data for {today}. Skipping write.")
            return

        # Load existing CSV keys to check duplicates
        csv_keys = set()
        if os.path.exists(csv_path):
            with open(csv_path, 'r', newline='') as f:
                csv_keys = {(row['Product'], row['timestamp']) for row in csv.DictReader(f)}

        # Filter out duplicates for CSV
        unique_data = [item for item in new_data if (item['Product'], item['timestamp']) not in csv_keys]

        # Write only new rows to CSV
        if unique_data:
            file_exists = os.path.exists(csv_path)
            with open(csv_path, 'a', newline='') as f_csv:
                writer = csv.DictWriter(f_csv, fieldnames=['Product', 'Interest Rate', 'APR', 'timestamp', 'lender_name', 'loan_term_years', 'updated_date'])
                if not file_exists or os.path.getsize(csv_path) == 0:
                    writer.writeheader()
                writer.writerows(unique_data)
        else:
            self.logger.info(f"No unique rows to add to CSV for {today}. Skipping CSV write.")


        # Overwrite JSON to keep only today's scraped data
        with open(json_path, 'w') as f_json:
            json.dump(scraped_data, f_json, indent=4)
