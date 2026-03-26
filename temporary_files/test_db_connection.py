import psycopg2
from utils.settings import settings

def test_connection():
    try:
        print(f"Testing connection to: {settings.DB_URL}")

        # Try to connect
        conn = psycopg2.connect(settings.DB_URL)
        cursor = conn.cursor()

        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ Connection successful!")
        print(f"PostgreSQL version: {version[0]}")

        # Check categories table
        cursor.execute("SELECT COUNT(*) FROM categories;")
        cat_count = cursor.fetchone()[0]
        print(f"✓ Categories in DB: {cat_count}")

        # Check if missing category IDs exist
        missing_ids = [316, 331, 332, 333, 336, 337, 629, 630, 631, 632, 633]
        cursor.execute(f"SELECT id FROM categories WHERE id IN ({','.join(map(str, missing_ids))});")
        existing = [row[0] for row in cursor.fetchall()]
        print(f"\nMissing category IDs from errors: {missing_ids}")
        print(f"Found in DB: {existing}")
        print(f"Still missing: {set(missing_ids) - set(existing)}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
