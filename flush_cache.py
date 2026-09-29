from src.backend.cache import get_redis_client

def clear_cache():
    try:
        client = get_redis_client()
        client.flushall()
        print("✅ Redis cache completely wiped!")
    except Exception as e:
        print(f"❌ Failed to clear cache: {e}")

if __name__ == "__main__":
    clear_cache()