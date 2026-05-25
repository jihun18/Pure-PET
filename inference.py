import cv2
import numpy as np
import onnxruntime as ort
import ast
import time
from picamera2 import Picamera2

class PurePetClassifier:
    def __init__(self, model_path="best.onnx"):
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4  # RPi5 쿼드코어 자원 최대 할당
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        
        self.session = ort.InferenceSession(model_path, options)
        model_inputs = self.session.get_inputs()[0]
        self.input_name = model_inputs.name
        self.model_shape = model_inputs.shape 
        
        self.img_h = self.model_shape[2]
        self.img_w = self.model_shape[3]
        print(f"[SYSTEM] AI 모델 요구 해상도 자동 동기화: ({self.img_w}x{self.img_h})")
        
        self.model_classes = {0: "LABEL_REQUIRED", 1: "PASS", 2: "REJECT"}
        try:
            meta = self.session.get_modelmeta().custom_metadata_map
            if 'names' in meta:
                self.model_classes = ast.literal_eval(meta['names'])
                print(f"[SYSTEM] 모델 내장 클래스 메타데이터 로드 성공: {self.model_classes}")
        except Exception as e:
            print(f"[WARNING] 모델 메타데이터 로드 실패: {e}")
            
        self.label_map = {
            "PASS": {"ko": "라벨제거 페트병", "en": "Pure PET"},
            "LABEL_REQUIRED": {"ko": "라벨 미제거", "en": "Label Alert"},
            "REJECT": {"ko": "재활용 불가능", "en": "Unrecyclable PET"}
        }

    def detect_label_by_color_optimized(self, bgr_resized):
        """
        [연산 가속 최적화] 리사이징이 완료된 (224x224) 이미지에서 HSV 연산을 수행하여 CPU 부하 경감
        """
        hsv = cv2.cvtColor(bgr_resized, cv2.COLOR_BGR2HSV)
        
        # 기성 3대 제조사 라벨(포카리스웨트 파랑, 사이다 초록, 아이시스 핑크) 검출 경계면 고정
        lower_blue, upper_blue = np.array([90, 50, 50]), np.array([130, 255, 255])
        lower_green, upper_green = np.array([35, 40, 40]), np.array([85, 255, 255])
        lower_pink, upper_pink = np.array([140, 40, 40]), np.array([170, 255, 255])
        
        mask_b = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_g = cv2.inRange(hsv, lower_green, upper_green)
        mask_p = cv2.inRange(hsv, lower_pink, upper_pink)
        
        total_label_pixels = cv2.countNonZero(mask_b) + cv2.countNonZero(mask_g) + cv2.countNonZero(mask_p)
        total_pixels = bgr_resized.shape[0] * bgr_resized.shape[1] # 224 * 224 = 50,176 pixels 고정
        
        # 면적 점유율 임계치 가드 (2.5% 기준 검증)
        return (total_label_pixels / total_pixels) > 0.025

    def predict(self, frame):
        h, w = frame.shape[:2]
        min_dim = min(h, w)
        
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        crop_img = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]
        
        # 1. 고속 비전 제어용 BGR 매트릭스 변환 및 축소
        display_frame = cv2.cvtColor(crop_img, cv2.COLOR_RGB2BGR)
        resized_bgr = cv2.resize(display_frame, (self.img_w, self.img_h), interpolation=cv2.INTER_LINEAR)
        
        # [최적화 적용] 224x224 버퍼를 피딩하여 컴퓨터 비전 알고리즘 연산 속도 고도화
        has_label_color = self.detect_label_by_color_optimized(resized_bgr)
        
        # 2. 딥러닝용 데이터 정규화 및 차원 확장
        img_input = resized_bgr.astype(np.float32) / 255.0
        img_input = img_input.transpose(2, 0, 1) # HWC to CHW
        img_input = np.expand_dims(img_input, axis=0)
        img_input = np.ascontiguousarray(img_input)
        
        # 3. 딥러닝 추론 실행 (ONNX Runtime)
        start_inf = time.perf_counter()
        outputs = self.session.run(None, {self.input_name: img_input})
        inference_time = (time.perf_counter() - start_inf) * 1000
        
        raw_output = outputs[0][0]
        
        # Softmax 가드 처리
        if not np.isclose(np.sum(raw_output), 1.0, atol=1e-3):
            exp_logits = np.exp(raw_output - np.max(raw_output))
            probabilities = exp_logits / np.sum(exp_logits)
        else:
            probabilities = raw_output
            
        class_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[class_idx])
        
        # 4. 하이브리드 예외 처리 결정 판정문 인터록
        raw_class_name = self.model_classes.get(class_idx, "UNKNOWN")
        if has_label_color and raw_class_name in ["PASS", "REJECT"]:
            raw_class_name = "LABEL_REQUIRED"
            confidence = 0.99  # 오버라이드 확신도 강제 하이스코어 바인딩
            
        mapped_labels = self.label_map.get(raw_class_name, {"ko": raw_class_name, "en": raw_class_name})
        return mapped_labels["ko"], mapped_labels["en"], confidence, display_frame, inference_time

# =========================================================================
# 메인 하드웨어 가동 루프 인터페이스 (추가 결합 완료)
# =========================================================================
if __name__ == "__main__":
    classifier = PurePetClassifier("best.onnx")
    
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    
    print("[SYSTEM] Pure-PET 하이브리드 비전 인프라 가동.")
    prev_time = time.time()

    try:
        while True:
            frame = picam2.capture_array()
            label_ko, label_en, conf, display_frame, inf_time = classifier.predict(frame)
            
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time
            
            log_text = f"{label_en} ({conf*100:.1f}%)"
            perf_text = f"Latency: {inf_time:.1f}ms | FPS: {fps:.1f}"
            
            cv2.putText(display_frame, log_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(display_frame, perf_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
            cv2.imshow("PURE-PET Sorter AI Test (Cropped)", display_frame)
            
            # 시나리오 문서 규격 파싱을 위한 고정 로그 스트링 출력
            print(f"[LOG] Result: {label_ko} | Conf: {conf:.4f}")
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n[SYSTEM] 사용자에 의해 시스템이 종료되었습니다.")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        print("[SYSTEM] 자원 해제 완료.")
