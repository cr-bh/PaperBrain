"""
配置文件
从 .env 文件加载环境变量
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

# Gemini API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
LLM_API_URL = os.getenv('LLM_API_URL', '')
LLM_BEARER_TOKEN = os.getenv('LLM_BEARER_TOKEN', '')

# Doubao API Configuration (Auto-Scholar)
DOUBAO_API_URL = os.getenv('DOUBAO_API_URL', '')
DOUBAO_BEARER_TOKEN = os.getenv('DOUBAO_BEARER_TOKEN', '')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/paperbrain.db')
CHROMA_DB_PATH = os.getenv('CHROMA_DB_PATH', 'data/chroma_db')

# File Storage
PAPERS_DIR = os.getenv('PAPERS_DIR', 'data/papers')
IMAGES_DIR = os.getenv('IMAGES_DIR', 'data/images')

# Model Configuration
MODEL_NAME = os.getenv('MODEL_NAME', 'gemini-pro')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'models/embedding-001')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '8192'))

# RAG Configuration
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1000'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '200'))
TOP_K_RESULTS = int(os.getenv('TOP_K_RESULTS', '5'))

# Auto-Scholar Configuration
ARXIV_CATEGORIES = os.getenv('ARXIV_CATEGORIES', 'cs.AI,cs.LG,cs.CL,math.OC').split(',')
ARXIV_MAX_RESULTS = int(os.getenv('ARXIV_MAX_RESULTS', '200'))
SCORE_THRESHOLD = float(os.getenv('SCORE_THRESHOLD', '5.0'))

# 筛选配置
KEYWORD_MIN_MATCHES = int(os.getenv('KEYWORD_MIN_MATCHES', '2'))
S2_MIN_CITATIONS = int(os.getenv('S2_MIN_CITATIONS', '3'))
S2_MIN_INFLUENTIAL = int(os.getenv('S2_MIN_INFLUENTIAL', '1'))
S2_API_KEY = os.getenv('S2_API_KEY', '')

# S2 API 重试配置
S2_MAX_RETRIES = int(os.getenv('S2_MAX_RETRIES', '3'))
S2_RETRY_DELAY = float(os.getenv('S2_RETRY_DELAY', '1.0'))
S2_REQUEST_INTERVAL = float(os.getenv('S2_REQUEST_INTERVAL', '0.3'))
S2_CACHE_PATH = os.getenv('S2_CACHE_PATH', 'data/s2_cache.json')

# 降级规则关键词
S2_FALLBACK_KEYWORDS = os.getenv(
    'S2_FALLBACK_KEYWORDS',
    'large language model,llm,transformer,bert,gpt,attention mechanism,neural network,deep learning,machine learning,reinforcement learning,computer vision,natural language processing,nlp'
).split(',')

# 确保数据目录存在
for dir_path in [PAPERS_DIR, IMAGES_DIR, Path(DATABASE_PATH).parent, Path(CHROMA_DB_PATH)]:
    Path(dir_path).mkdir(parents=True, exist_ok=True)
