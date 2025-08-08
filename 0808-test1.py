
import tensorflow as tf
import numpy as np
from PIL import Image
import os

def get_elasticity_score(model_path, image_path):
    """
    TFLite 모델과 이미지 경로를 받아 피부 탄력 점수를 반환합니다.

    :param model_path: .tflite 모델 파일의 경로
    :param image_path: 분석할 이미지 파일의 경로
    :return: 모델이 예측한 탄력 점수 (float) 또는 에러 발생 시 None
    """
    # --- 1. 모델 로드 ---
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"모델 로드에 실패했습니다: {e}")
        return None

    # --- 2. 모델의 입력 및 출력 정보 확인 ---
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    try:
        # 모델이 요구하는 입력 이미지의 크기를 가져옵니다.
        _, height, width, _ = input_details[0]['shape']
        input_type = input_details[0]['dtype']
    except Exception as e:
        print(f"모델의 입력 형태를 확인하는 데 실패했습니다. 모델이 올바른 이미지 모델인지 확인하세요. 오류: {e}")
        return None

    # --- 3. 이미지 전처리 ---
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((width, height))
        input_data = np.array(img, dtype=np.float32)
        
        # 정규화 (모델이 0~1 사이의 값을 기대하는 경우)
        input_data = input_data / 255.0
        input_data = np.expand_dims(input_data, axis=0)

        # 만약 모델의 입력 타입이 정수형(UINT8)이라면 변환합니다.
        if input_type == np.uint8:
             input_data = np.array(np.expand_dims(img, axis=0), dtype=np.uint8)

    except FileNotFoundError:
        print(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    except Exception as e:
        print(f"이미지 처리 중 오류가 발생했습니다: {e}")
        return None

    # --- 4. 추론 실행 ---
    try:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
    except Exception as e:
        print(f"모델 추론 중 오류가 발생했습니다: {e}")
        return None

    # --- 5. 결과 반환 ---
    score = output_data[0][0]
    return score

if __name__ == '__main__':
    # --- 중요 ---
    # 모델과 이미지가 이 스크립트와 동일한 폴더에 있다고 가정합니다.

    # 1. 모델 파일 경로 설정
    model_file = "filename.tflite"

    # 2. 분석할 이미지 파일 경로 설정
    # **이 부분을 분석하고 싶은 실제 이미지 파일 이름으로 꼭 변경해주세요.**
    image_file_to_test = "test2.jpg" # 예시: "my_photo.jpg"

    # --- 실행 ---
    if not os.path.exists(model_file):
        print(f"오류: 모델 파일을 찾을 수 없습니다. '{model_file}' 파일이 스크립트와 같은 폴더에 있는지 확인하세요.")
    elif not os.path.exists(image_file_to_test):
        print(f"오류: 분석할 이미지 파일을 찾을 수 없습니다: {image_file_to_test}")
        print(f"스크립트의 'image_file_to_test' 변수를 실제 이미지 파일 이름으로 수정하고, 파일이 스크립트와 같은 폴더에 있는지 확인해주세요.")
    else:
        elasticity_score = get_elasticity_score(model_file, image_file_to_test)

        if elasticity_score is not None:
            # 점수를 0점에서 100점 사이로 변환 (모델의 출력 범위가 0~1이라고 가정)
            final_score = elasticity_score * 100
            print(f"\n분석 완료!")
            print(f"이미지: {os.path.basename(image_file_to_test)}")
            print(f"측정된 피부 탄력 점수: {final_score:.2f} / 100")
