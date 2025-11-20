# app/utils/logger.py
import logging
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "../../logs")
os.makedirs(LOG_DIR, exist_ok=True)

MCP_LOG_FILE = os.path.join(LOG_DIR, "mcp_requests.log")

# Създаваме отделен логър
mcp_logger = logging.getLogger("mcp_logger")
mcp_logger.setLevel(logging.INFO)

# Формат за логовете
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler = logging.FileHandler(MCP_LOG_FILE, encoding="utf-8")
file_handler.setFormatter(formatter)

# За да не дублира логове в root
if not mcp_logger.handlers:
    mcp_logger.addHandler(file_handler)

mcp_logger.propagate = False
