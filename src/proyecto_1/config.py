from dotenv import load_dotenv
import os
from proyecto_1.modules.functions import verify_env_vars

# configure environment variables to get the OpenAI API key

_ = load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = os.getenv("REPO_URL")
GITHUB_USER = os.getenv("GITHUB_USER")
REPO_URL_T = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@{REPO_URL.lstrip('https://')}"
env_vars = {
    "APY_KEY" : API_KEY,
    "GITHUB_TOKEN" : GITHUB_TOKEN,
    "REPO_URL" : REPO_URL,
    "GITHUB_USER" : GITHUB_USER
    }

verify_env_vars(env_vars= env_vars)