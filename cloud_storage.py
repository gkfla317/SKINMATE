"""
Google Cloud Storage 연동 모듈
"""

import os
from google.cloud import storage
from werkzeug.utils import secure_filename
import uuid

class CloudStorageManager:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)
    
    def upload_file(self, file, folder="uploads"):
        """파일을 Cloud Storage에 업로드"""
        try:
            # 고유한 파일명 생성
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            blob_path = f"{folder}/{unique_filename}"
            
            # Cloud Storage에 업로드
            blob = self.bucket.blob(blob_path)
            blob.upload_from_file(file)
            
            # 공개 URL 생성
            blob.make_public()
            
            return {
                'filename': unique_filename,
                'url': blob.public_url,
                'path': blob_path
            }
        except Exception as e:
            print(f"파일 업로드 실패: {e}")
            return None
    
    def delete_file(self, blob_path):
        """Cloud Storage에서 파일 삭제"""
        try:
            blob = self.bucket.blob(blob_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"파일 삭제 실패: {e}")
            return False
    
    def get_file_url(self, blob_path):
        """파일의 공개 URL 반환"""
        try:
            blob = self.bucket.blob(blob_path)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            print(f"URL 생성 실패: {e}")
            return None
