import os
import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input

# -----------------------------
# 1. 데이터 경로 설정
# -----------------------------
# 폴더 경로 대신 특정 이미지 파일의 경로를 지정합니다.
IMG_PATH = "d.jpg"

# -----------------------------
# 2. ResNet50 임베딩 모델 로드
# -----------------------------
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def get_embedding(img_path, target_size=(224, 224)):
    """이미지 → 2048차원 임베딩 벡터"""
    img = image.load_img(img_path, target_size=target_size)
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model.predict(x, verbose=0)
    return features.flatten()

# -----------------------------
# 3. 특정 이미지 임베딩 추출
# -----------------------------
# 지정된 이미지 파일의 임베딩을 직접 추출합니다.
embedding = get_embedding(IMG_PATH)

# 파일명을 경로에서 추출하고, 데이터 리스트를 생성합니다.
filename = os.path.basename(IMG_PATH)
data = [[filename] + embedding.tolist()]  # DataFrame 생성을 위해 리스트의 리스트 형태로 구성

# -----------------------------
# 4. CSV 저장
# -----------------------------
# 컬럼명을 생성하고 DataFrame으로 변환합니다.
columns = ["filename"] + [f"feat_{i}" for i in range(len(embedding))]
df = pd.DataFrame(data, columns=columns)

# 혼동을 피하기 위해 출력 파일명을 변경합니다.
output_csv_path = "dtest.csv"
df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")

print(f"✅ 단일 이미지 임베딩 저장 완료: {output_csv_path}")