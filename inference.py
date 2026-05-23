import cv2
import numpy as np
import onnxruntime as ort
from picamera2 import Picamera2

class PurePetClassifier:
    def __init__(self, model_path="best.onnx"):
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        self.session = ort.InferenceSession(model_path, options)
        self.input_name = self.session.get_inputs()[0].name
        
        # [교정] AI 모델의 실제 출력 순서와 요청하신 명칭으로 완벽 매핑
        self.classes_ko = ["라벨제거 페트병", "라벨 미제거", "재활용 불가능"]
        self.classes_en = ["Pure PET", "Label Alert", "Unrecyclable PET"]

    def preprocess(self, frame):
        """이미지 비율 왜곡을 막기 위한 센터 크롭 적용"""
        h, w = frame.shape[:2]
        min_dim = min(h, w)
        
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        crop_img = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]

        # 지훈님의 원본 색상/전처리 로직 (절대 수정 없음)
        img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 640), interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.expand_dims(img, axis=0)
        
        return img, crop_img

    def predict(self, frame):
        """추론 수행 및 결과 도출 (YOLOv8 ONNX 내장 Softmax 활용)"""
        input_data, crop_img = self.preprocess(frame)
        
        # ONNX Runtime 추론 실행
        outputs = self.session.run(None, {self.input_name: input_data})
        probabilities = outputs[0][0]
        
        # 가장 높은 확률의 인덱스 및 신뢰도 추출
        class_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[class_idx])
        
        return class_idx, confidence, crop_img

if __name__ == "__main__":
    classifier = PurePetClassifier("best.onnx")
    
    picam2 = Picamera2()
    # 지훈님의 원본 카메라 포맷 세팅 (절대 수정 없음)
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    
    print("[SYSTEM] Pure-PET AI Inference Unit Ready.")

    try:
        while True:
            frame = picam2.capture_array()
            class_idx, conf, display_frame = classifier.predict(frame)
            
            label_en = classifier.classes_en[class_idx]
            label_ko = classifier.classes_ko[class_idx]
            
            # 화면 출력 및 로그 기록
            log_text = f"{label_en} ({conf*100:.1f}%)"
            cv2.putText(display_frame, log_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("PURE-PET Sorter AI Test (Cropped)", display_frame)
            
            print(f"[LOG] Detected: {label_ko} | Code: {class_idx} | Conf: {conf:.4f}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[SYSTEM] 사용자에 의해 테스트가 중단되었습니다.")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        print("[SYSTEM] 자원 해제 완료.")
