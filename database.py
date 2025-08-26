"""
화해 뷰티 제품 데이터베이스 관리 모듈
20년차 개발자의 실용적 접근: 트랜잭션 안정성과 성능 최적화
"""

import logging
import os # 환경 변수를 읽기 위해 추가
import psycopg2 # PostgreSQL 연결을 위해 추가
from psycopg2 import Error as PgError # 에러 처리를 위해 추가
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductDatabase:
    """제품 데이터베이스 관리 클래스"""

    def __init__(self):
        # Cloud SQL 연결 정보는 환경 변수에서 가져옵니다.
        # 이 환경 변수들은 나중에 Cloud Run 서비스에 설정할 것입니다.
        self.db_host = os.environ.get("DB_HOST")
        self.db_name = os.environ.get("DB_NAME")
        self.db_user = os.environ.get("DB_USER")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.db_port = os.environ.get("DB_PORT", "5432") # PostgreSQL 기본 포트

        # 로컬 SQLite 관련 초기화 제거
        # self.db_path = db_path
        # self.ensure_db_directory()
        self.init_database() # Cloud SQL 연결 후 테이블 초기화
    
    def get_connection(self) -> psycopg2.extensions.connection: # 반환 타입 힌트 변경
        """데이터베이스 연결을 반환합니다."""
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            return conn
        except PgError as e: # psycopg2 에러 타입으로 변경
            logger.error(f"데이터베이스 연결 실패: {e}")
            raise
    
    def init_database(self):
        """데이터베이스 테이블을 초기화합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # products 테이블 생성 (PostgreSQL 문법에 맞게 수정)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS products (
                        id SERIAL PRIMARY KEY, -- AUTOINCREMENT 대신 SERIAL
                        product_id INTEGER UNIQUE,
                        name TEXT NOT NULL,
                        brand TEXT NOT NULL,
                        image_url TEXT,
                        product_url TEXT,
                        rank INTEGER NOT NULL,
                        main_category TEXT NOT NULL,
                        middle_category TEXT,
                        sub_category TEXT NOT NULL,
                        scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # middle_category 컬럼이 없으면 추가 (PostgreSQL 에러 처리)
                try:
                    cursor.execute("ALTER TABLE products ADD COLUMN middle_category TEXT")
                    logger.info("middle_category 컬럼 추가 완료")
                except PgError as e: # psycopg2 에러 타입으로 변경
                    # 컬럼이 이미 존재하는 경우 (PostgreSQL에서는 'duplicate column' 에러 발생)
                    if "duplicate column" in str(e).lower():
                        pass
                    else:
                        raise # 다른 에러는 다시 발생

                # 인덱스 생성 (성능 최적화) - SQLite와 동일하게 사용 가능
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_product_id
                    ON products(product_id)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_category
                    ON products(main_category, sub_category)
                """)

                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_scraped_at
                    ON products(scraped_at)
                """)

                conn.commit()
                logger.info("데이터베이스 초기화 완료")

        except PgError as e: # psycopg2 에러 타입으로 변경
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
        except Exception as e: # 기타 예외 처리
            logger.error(f"데이터베이스 초기화 실패 (일반 오류): {e}")
            raise
    
    def upsert_products(self, products: List[Dict]) -> int:
        """
        제품 데이터를 UPSERT합니다.
        product_id를 기준으로 기존 데이터는 업데이트, 새로운 데이터는 삽입합니다.
        
        Args:
            products: 제품 데이터 리스트
            
        Returns:
            처리된 제품 수
        """
        if not products:
            logger.warning("업데이트할 제품이 없습니다.")
            return 0
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # UPSERT 쿼리 (SQLite 3.24.0+ 지원)
                upsert_query = """
                    INSERT INTO products (
                        product_id, name, brand, image_url, product_url, 
                        rank, main_category, middle_category, sub_category, scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(product_id) DO UPDATE SET
                        name = excluded.name,
                        brand = excluded.brand,
                        image_url = excluded.image_url,
                        product_url = excluded.product_url,
                        rank = excluded.rank,
                        main_category = excluded.main_category,
                        middle_category = excluded.middle_category,
                        sub_category = excluded.sub_category,
                        scraped_at = excluded.scraped_at
                """
                
                # 배치 처리로 성능 최적화
                batch_size = 100
                total_processed = 0
                
                for i in range(0, len(products), batch_size):
                    batch = products[i:i + batch_size]
                    batch_data = []
                    
                    for product in batch:
                        batch_data.append((
                            product['product_id'],
                            product['name'],
                            product['brand'],
                            product.get('image_url', ''),
                            product.get('product_url', ''),
                            product['rank'],
                            product['main_category'],
                            product['middle_category'],
                            product['sub_category'],
                            datetime.now()
                        ))
                    
                    cursor.executemany(upsert_query, batch_data)
                    total_processed += len(batch)
                    
                    logger.info(f"배치 처리 완료: {total_processed}/{len(products)} 제품")
                
                conn.commit()
                logger.info(f"UPSERT 완료: {total_processed}개 제품 처리")
                return total_processed
                
        except Exception as e:
            logger.error(f"UPSERT 실패: {e}")
            raise
    
    def get_products_by_category(self, main_category: str, sub_category: str, limit: int = 50) -> List[Dict]:
        """특정 카테고리의 제품을 조회합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM products 
                    WHERE main_category = ? AND sub_category = ?
                    ORDER BY rank ASC, scraped_at DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (main_category, sub_category, limit))
                rows = cursor.fetchall()
                
                products = []
                for row in rows:
                    products.append(dict(row))
                
                logger.info(f"카테고리 조회 완료: {main_category} > {sub_category} - {len(products)}개 제품")
                return products
                
        except Exception as e:
            logger.error(f"카테고리 조회 실패: {e}")
            return []
    
    def get_top_products(self, limit: int = 100) -> List[Dict]:
        """랭킹 상위 제품을 조회합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                    SELECT * FROM products 
                    ORDER BY rank ASC, scraped_at DESC
                    LIMIT ?
                """
                
                cursor.execute(query, (limit,))
                rows = cursor.fetchall()
                
                products = []
                for row in rows:
                    products.append(dict(row))
                
                logger.info(f"상위 제품 조회 완료: {len(products)}개 제품")
                return products
                
        except Exception as e:
            logger.error(f"상위 제품 조회 실패: {e}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """제품 ID로 특정 제품을 조회합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = "SELECT * FROM products WHERE product_id = ?"
                cursor.execute(query, (product_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"제품 조회 실패: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """데이터베이스 통계 정보를 반환합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 전체 제품 수
                cursor.execute("SELECT COUNT(*) FROM products")
                total_products = cursor.fetchone()[0]
                
                # 카테고리별 제품 수
                cursor.execute("""
                    SELECT main_category, sub_category, COUNT(*) as count
                    FROM products
                    GROUP BY main_category, sub_category
                    ORDER BY main_category, sub_category
                """)
                category_stats = cursor.fetchall()
                
                # 최근 업데이트 시간
                cursor.execute("SELECT MAX(scraped_at) FROM products")
                last_update = cursor.fetchone()[0]
                
                return {
                    'total_products': total_products,
                    'category_stats': [dict(row) for row in category_stats],
                    'last_update': last_update
                }
                
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """지정된 일수 이전의 데이터를 정리합니다."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 중복 데이터 정리 (같은 product_id 중 최신 것만 유지)
                cursor.execute("""
                    DELETE FROM products 
                    WHERE id NOT IN (
                        SELECT MAX(id) 
                        FROM products 
                        GROUP BY product_id
                    )
                """)
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"데이터 정리 완료: {deleted_count}개 중복 레코드 삭제")
                
        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")

def main():
    """데이터베이스 테스트"""
    db = ProductDatabase()
    
    # 통계 정보 출력
    stats = db.get_statistics()
    print(f"전체 제품 수: {stats.get('total_products', 0)}")
    print(f"최근 업데이트: {stats.get('last_update', 'N/A')}")
    
    # 카테고리별 통계
    for stat in stats.get('category_stats', []):
        print(f"{stat['main_category']} > {stat['sub_category']}: {stat['count']}개")

if __name__ == "__main__":
    main()
