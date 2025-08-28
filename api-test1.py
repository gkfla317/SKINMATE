import base64
import os
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import google.oauth2.service_account
from google.api_core import exceptions

# --- ⚙️ 1. 여기에 내 정보 입력 (★★★★★) ---

# Google Cloud 프로젝트 ID
PROJECT_ID = "sesac-tkdgusdhzp"

# Vertex AI 모델을 배포한 리전 (예: "asia-northeast3")
REGION = "us-central1"

# ❗ Vertex AI 콘솔 > 엔드포인트 메뉴에서 확인한 '숫자' ID
ENDPOINT_ID = "1663696332755304448"

# ❗ 다운로드한 서비스 계정 키(JSON) 파일의 전체 또는 상대 경로
# 예시: "keys/my-secret-key.json" 또는 "C:/Users/user/keys/my-secret-key.json"
CREDENTIALS_FILE = r"C:\Users\user\Desktop\test_gemini1\skintype-api.json"

# ❗ 예측하고 싶은 이미지 파일의 경로
IMAGE_FILE = r"C:\Users\user\Desktop\test_gemini1\test-img.png"

# ----------------------------------------------------

def predict_skin_type(project_id, endpoint_id, filename, region, credentials_path):
    """Vertex AI 엔드포인트에 이미지 분류 예측을 요청하는 함수"""

    # --- 1. 파일 경로 및 인증 정보 유효성 검사 ---
    if not os.path.exists(credentials_path):
        print(f"❌ 오류: 인증 파일 '{credentials_path}'를 찾을 수 없습니다. 경로를 확인해주세요.")
        return
    if not os.path.exists(filename):
        print(f"❌ 오류: 이미지 파일 '{filename}'을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    try:
        # JSON 키 파일을 사용하여 명시적으로 인증 정보를 생성합니다.
        credentials = google.oauth2.service_account.Credentials.from_service_account_file(credentials_path)
    except Exception as e:
        print(f"❌ 오류: 인증 파일을 읽는 중 문제가 발생했습니다. 파일이 유효한지 확인해주세요. ({e})")
        return

    # API 엔드포인트 주소를 설정합니다.
    api_endpoint = f"{region}-aiplatform.googleapis.com"
    client_options = {"api_endpoint": api_endpoint}

    # 인증 정보와 함께 API 클라이언트를 생성합니다.
    client = aiplatform.gapic.PredictionServiceClient(
        credentials=credentials,
        client_options=client_options
    )

    # --- 2. 예측 요청 데이터 준비 ---
    # 이미지를 바이너리(binary)로 읽고 Base64 형식으로 인코딩합니다.
    with open(filename, "rb") as f:
        file_content = f.read()
    encoded_content = base64.b64encode(file_content).decode("utf-8")

    # API가 이해할 수 있는 JSON 형식으로 요청 내용을 구성합니다.
    instance = json_format.ParseDict({"content": encoded_content}, Value())
    instances = [instance]

    # 엔드포인트의 전체 경로를 지정합니다.
    endpoint_path = client.endpoint_path(
        project=project_id, location=region, endpoint=endpoint_id
    )

    # --- 3. API 호출 및 결과 처리 ---
    try:
        # 엔드포인트로 예측 요청을 보냅니다.
        response = client.predict(endpoint=endpoint_path, instances=instances)

        print("--- ✅ 전체 예측 결과 ---")
        predictions = response.predictions
        for prediction in predictions:
            print(dict(prediction))

        # 가장 높은 확률을 가진 예측 결과 찾기
        if predictions:
            top_prediction = dict(predictions[0])
            confidences = top_prediction.get('confidences', [])
            display_names = top_prediction.get('displayNames', [])

            if confidences and display_names and len(confidences) == len(display_names):
                max_confidence = max(confidences)
                max_index = confidences.index(max_confidence)
                predicted_class = display_names[max_index]

                print("\n--- 🤖 최종 결론 ---")
                print(f"가장 유력한 예측: {predicted_class} (신뢰도: {max_confidence:.2%})")
            else:
                print("\n⚠️ 경고: 예측 결과 형식이 예상과 다릅니다. 'confidences' 또는 'displayNames' 키를 확인해주세요.")
        else:
            print("\n⚠️ 경고: 예측 결과를 받았지만 비어 있습니다.")

    except exceptions.NotFound:
        print(f"❌ 오류: 엔드포인트를 찾을 수 없습니다. 프로젝트 ID, 리전, 엔드포인트 ID가 올바른지 확인해주세요.")
    except exceptions.PermissionDenied:
        print(f"❌ 오류: 권한이 거부되었습니다. 서비스 계정에 'Vertex AI 사용자' 역할이 있는지 확인해주세요.")
    except Exception as e:
        print(f"❌ 예측 중 오류가 발생했습니다: {e}")
        print("입력 데이터 형식이나 모델 엔드포인트 상태를 확인해보세요.")

# --- ▶️ 스크립트 실행 ---
if __name__ == "__main__":
    predict_skin_type(PROJECT_ID, ENDPOINT_ID, IMAGE_FILE, REGION, CREDENTIALS_FILE)