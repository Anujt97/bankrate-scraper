import scrapy
import datetime
import json
import csv
import os

class TableSpider(scrapy.Spider):
    name = "table_spider"
    start_urls = ["https://www.bankrate.com/mortgages/mortgage-rates/"]

    def parse(self, response):
        rows = response.xpath('//table[contains(@class, "Table--numerical")]/tbody/tr')

        data = []

        for row in rows[:7]:
            product = row.xpath('.//th/a/text()').get()
            if not product:
                product = row.xpath('.//th/text()').get()

            interest_rate = row.xpath('.//td[1]/text()').get()
            apr = row.xpath('.//td[2]/text()').get()

            item = {
                'Product': product.strip() if product else None,
                'Interest Rate': interest_rate.strip() if interest_rate else None,
                'APR': apr.strip() if apr else None,
                'timestamp': datetime.datetime.now().isoformat(),
            }

            data.append(item)

        # File paths
        json_path = "output.json"
        csv_path = "output.csv"

        # ✅ Overwrite JSON file (acts as temporary storage)
        with open(json_path, 'w') as f_json:
            json.dump(data, f_json, indent=4)

        # ✅ Append to CSV file (create if doesn't exist)
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, 'a', newline='') as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=['Product', 'Interest Rate', 'APR', 'timestamp'])
            if not file_exists or os.path.getsize(csv_path) == 0:
                writer.writeheader()
            writer.writerows(data)

        # ✅ Clear JSON file after appending to CSV
        open(json_path, 'w').close()

        def parse(self, response):
            self.logger.info(f"Status code: {response.status}")
            self.logger.info(f"Response length: {len(response.text)}")
