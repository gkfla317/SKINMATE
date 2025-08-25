import sqlite3
import pandas as pd

DB_PATH = 'instance/skinmate.sqlite'

def inspect_db():
    print(f"--- 데이터베이스 검사 시작: {DB_PATH} ---")
    try:
        con = sqlite3.connect(DB_PATH)
        print("✅ 데이터베이스 연결 성공.")
        
        print("\n--- 크림 카테고리 TOP 5 제품 데이터 확인 ---")
        cream_query = """
            SELECT name, rank, sub_category FROM products 
            WHERE main_category = '스킨케어' AND middle_category = '크림'
            ORDER BY rank ASC
            LIMIT 5
        """
        creams = pd.read_sql_query(cream_query, con)
        print(creams)

        con.close()

    except Exception as e:
        print(f"❌ 데이터베이스 검사 중 오류 발생: {e}")

if __name__ == '__main__':
    inspect_db()