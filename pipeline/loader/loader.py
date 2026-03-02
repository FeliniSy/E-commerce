from db_manager.pg_connection import get_connection, release_connection
from utils.logger import logger


class Loader:
    def execute_query(self, query, params=None, fetch=True):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                result = cursor.fetchall() if fetch else None
                conn.commit()
                return result
        except Exception as e:
            conn.rollback()
            logger.error(f"Query failed: {e} | params: {params}")
            raise
        finally:
            release_connection(conn)

    def fetch(self, query, params=None):
        return self.execute_query(query, params, fetch=True)

    def execute(self, query, params=None):
        return self.execute_query(query, params, fetch=False)

    def execute_many(self, query, params_list: list):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Batch query failed: {e}")
            raise
        finally:
            release_connection(conn)


loader = Loader()