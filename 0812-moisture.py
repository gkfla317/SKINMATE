import tensorflow as tf
import numpy as np
from PIL import Image
import os
import sys

def predict_moisture_score(model_path, image_path):
    """
    TFLite 모델과 이미지 경로를 받아 피부 수분 점수를 반환합니다.
    """
    # --- 1. 모델 로드 ---
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
    except Exception as e:
        return None

    # --- 2. 모델의 입력 및 출력 정보 확인 ---
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    try:
        _, height, width, _ = input_details[0]['shape']
        # moisture.tflite 모델은 UINT8 입력을 기대합니다.
        input_type = input_details[0]['dtype']
        if input_type != np.uint8:
            pass

    except Exception as e:
        return None

    # --- 3. 이미지 전처리 ---
    try:
        img = Image.open(image_path).convert('RGB')
        img = img.resize((width, height))
        
        # moisture.tflite 모델의 입력 타입은 UINT8 입니다.
        input_data = np.array(np.expand_dims(img, axis=0), dtype=np.uint8)

    except FileNotFoundError:
        return None
    except Exception as e:
        return None

    # --- 4. 추론 실행 ---
    try:
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
    except Exception as e:
        return None

    # --- 5. 결과 반환 ---
    score = output_data[0][0]
    return score

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)

    image_file_to_test = sys.argv[1]
    
    script_dir = os.path.dirname(__file__)
    model_file = os.path.join(script_dir, "moisture.tflite")

    if not os.path.exists(model_file):
        sys.exit(1)
    elif not os.path.exists(image_file_to_test):
        sys.exit(1)
    else:
        moisture_score = predict_moisture_score(model_file, image_file_to_test)

        if moisture_score is not None:
            MAX_RAW_SCORE = 10.0
            
            final_score = (moisture_score / MAX_RAW_SCORE) * 100
            final_score = np.clip(final_score, 0, 100)

            print(f"{final_score:.2f}")
