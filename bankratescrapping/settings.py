BOT_NAME = 'bankratescrapping'
SPIDER_MODULES = ['bankratescrapping.spiders']
NEWSPIDER_MODULE = 'bankratescrapping.spiders'
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
LOG_ENABLED = True
LOG_LEVEL = 'INFO'  # Options: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
LOG_FILE = 'scrapy_log.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'