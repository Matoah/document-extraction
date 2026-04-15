from dotenv import load_dotenv
import logging
from workflow.parse_document import parse_document
from workflow.sysnc_graph_databse import sync_graph_database
from workflow.upload_to_knowledge import upload_to_knowledge

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

load_dotenv()

if __name__ == "__main__":
    parse_document()
    sync_graph_database()
    upload_to_knowledge()
