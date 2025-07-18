import scrapy
import datetime
import json
import csv
import os

class TableSpider(scrapy.Spider):
    name = "table_spider"
    start_urls = ["https://www.bankrate.com/mortgages/mortgage-rates/"]

    def parse(self, response):
        today = datetime.datetime.now().date().isoformat()
        csv_path = "output.csv"
        json_path = "output.json"

        # ✅ Check if today's data already exists
        if os.path.exists(csv_path):
            with open(csv_path, 'r') as f_csv:
                reader = csv.DictReader(f_csv)
                for row in reader:
                    if row['timestamp'] == today:
                        self.logger.info(f"Data for {today} already exists. Skipping scraping.")
                        return  # Exit early if today's data already exists

        rows = response.xpath('(//ul[.//li//button[contains(text(), "Purchase") and @tabindex="0"]]/following-sibling::div/div/table[contains(@class, "Table--numerical")])[1]/tbody/tr')

        data = []

        for row in rows:
            product = row.xpath('.//th/a/text()').get()
            if not product:
                product = row.xpath('.//th/text()').get()

            interest_rate = row.xpath('.//td[1]/text()').get()
            apr = row.xpath('.//td[2]/text()').get()

            item = {
                'Product': product.strip() if product else None,
                'Interest Rate': interest_rate.strip() if interest_rate else None,
                'APR': apr.strip() if apr else None,
                'timestamp': today,
            }

            data.append(item)

        # ✅ Write JSON (temporary file, overwritten)
        with open(json_path, 'w') as f_json:
            json.dump(data, f_json, indent=4)

        # ✅ Append to CSV
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=['Product', 'Interest Rate', 'APR', 'timestamp'])
            if not file_exists or os.path.getsize(csv_path) == 0:
                writer.writeheader()
            writer.writerows(data)

        # ✅ Clear JSON after write
        open(json_path, 'w').close()