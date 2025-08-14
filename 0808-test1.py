import tensorflow as tf
import numpy as np
from PIL import Image
import os
import sys

def get_elasticity_score(model_path, image_path):
    """
    TFLite 모델과 이미지 경로를 받아 피부 탄력 점수를 반환합니다.
    """
    try:
        interpreter = tf.lite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        _, height, width, _ = input_details[0]['shape']
        input_type = input_details[0]['dtype']

        img = Image.open(image_path).convert('RGB')
        img = img.resize((width, height))
        input_data = np.array(img, dtype=np.float32)
        input_data = input_data / 255.0
        input_data = np.expand_dims(input_data, axis=0)
        if input_type == np.uint8:
             input_data = np.array(np.expand_dims(img, axis=0), dtype=np.uint8)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        
        predicted_class = int(np.argmax(output_data[0]))
        
        # 점수 범위를 10점 ~ 100점으로 조정하여 0점이 나오지 않도록 합니다.
        final_score = ((6 - predicted_class) / 6.0) * 90 + 10
        
        return final_score
    except Exception as e:
        # 오류 발생 시 None을 반환하여 조용히 실패 처리합니다.
        return None


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit()
    
    image_file_to_test = sys.argv[1]
    script_dir = os.path.dirname(__file__)
    model_file = os.path.join(script_dir, "filename.tflite")

    if not os.path.exists(model_file) or not os.path.exists(image_file_to_test):
        sys.exit()
        
    final_score = get_elasticity_score(model_file, image_file_to_test)

    if final_score is not None:
        final_score = np.clip(final_score, 0, 100)
        print(f"{final_score:.2f}")
    # final_score가 None이면, 아무것도 출력하지 않고 종료합니다.
