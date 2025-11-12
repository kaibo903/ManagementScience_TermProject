"""
Supabase 客戶端工具
"""
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# 從環境變數讀取 Supabase 設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # 使用 service role key 以獲得完整權限

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("請設定 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 環境變數")

# 建立 Supabase 客戶端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

