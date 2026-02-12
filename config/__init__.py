"""
Config 包初始化文件
导入原 config.py 的所有配置 + 新增的 venues 和 institutions 模块
"""
import sys
from pathlib import Path

# 导入父目录的 config.py 中的所有配置
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# 临时重命名导入以避免循环
import importlib.util
spec = importlib.util.spec_from_file_location("_config_module", parent_dir / "config.py")
_config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_config_module)

# 导出所有原配置变量
DATABASE_PATH = _config_module.DATABASE_PATH
CHROMA_DB_PATH = _config_module.CHROMA_DB_PATH
PAPERS_DIR = _config_module.PAPERS_DIR
IMAGES_DIR = _config_module.IMAGES_DIR
GEMINI_API_KEY = _config_module.GEMINI_API_KEY
LLM_API_URL = _config_module.LLM_API_URL
LLM_BEARER_TOKEN = _config_module.LLM_BEARER_TOKEN
DOUBAO_API_URL = _config_module.DOUBAO_API_URL
DOUBAO_BEARER_TOKEN = _config_module.DOUBAO_BEARER_TOKEN
MODEL_NAME = _config_module.MODEL_NAME
EMBEDDING_MODEL = _config_module.EMBEDDING_MODEL
TEMPERATURE = _config_module.TEMPERATURE
MAX_TOKENS = _config_module.MAX_TOKENS
CHUNK_SIZE = _config_module.CHUNK_SIZE
CHUNK_OVERLAP = _config_module.CHUNK_OVERLAP
TOP_K_RESULTS = _config_module.TOP_K_RESULTS
ARXIV_CATEGORIES = _config_module.ARXIV_CATEGORIES
ARXIV_MAX_RESULTS = _config_module.ARXIV_MAX_RESULTS
SCORE_THRESHOLD = _config_module.SCORE_THRESHOLD
KEYWORD_MIN_MATCHES = _config_module.KEYWORD_MIN_MATCHES
S2_MIN_CITATIONS = _config_module.S2_MIN_CITATIONS
S2_MIN_INFLUENTIAL = _config_module.S2_MIN_INFLUENTIAL
S2_API_KEY = _config_module.S2_API_KEY
S2_MAX_RETRIES = _config_module.S2_MAX_RETRIES
S2_RETRY_DELAY = _config_module.S2_RETRY_DELAY
S2_REQUEST_INTERVAL = _config_module.S2_REQUEST_INTERVAL
S2_CACHE_PATH = _config_module.S2_CACHE_PATH
S2_FALLBACK_KEYWORDS = _config_module.S2_FALLBACK_KEYWORDS

# 导入新增的 venues 和 institutions 模块
from .venues import (
    normalize_venue_name,
    is_top_venue,
    get_venue_info,
    ALL_TOP_VENUES
)

from .institutions import (
    normalize_institution_name,
    is_top_institution,
    get_institution_info,
    extract_institutions_from_authors,
    ALL_INSTITUTIONS
)

__all__ = [
    # 原配置变量
    'DATABASE_PATH',
    'CHROMA_DB_PATH',
    'PAPERS_DIR',
    'IMAGES_DIR',
    'GEMINI_API_KEY',
    'LLM_API_URL',
    'LLM_BEARER_TOKEN',
    'DOUBAO_API_URL',
    'DOUBAO_BEARER_TOKEN',
    'MODEL_NAME',
    'EMBEDDING_MODEL',
    'TEMPERATURE',
    'MAX_TOKENS',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
    'TOP_K_RESULTS',
    'ARXIV_CATEGORIES',
    'ARXIV_MAX_RESULTS',
    'SCORE_THRESHOLD',
    'KEYWORD_MIN_MATCHES',
    'S2_MIN_CITATIONS',
    'S2_MIN_INFLUENTIAL',
    'S2_API_KEY',
    'S2_MAX_RETRIES',
    'S2_RETRY_DELAY',
    'S2_REQUEST_INTERVAL',
    'S2_CACHE_PATH',
    'S2_FALLBACK_KEYWORDS',
    # 新增功能
    'normalize_venue_name',
    'is_top_venue',
    'get_venue_info',
    'ALL_TOP_VENUES',
    'normalize_institution_name',
    'is_top_institution',
    'get_institution_info',
    'extract_institutions_from_authors',
    'ALL_INSTITUTIONS',
]
