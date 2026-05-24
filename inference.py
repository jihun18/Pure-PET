import cv2
import numpy as np
import onnxruntime as ort
import ast
import time
from picamera2 import Picamera2

class PurePetClassifier:
    def __init__(self, model_path="best.onnx"):
        options = ort.SessionOptions()
        options.intra_op_num_threads = 4
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

        self.session = ort.InferenceSession(model_path, options)

        model_inputs = self.session.get_inputs()[0]
        self.input_name = model_inputs.name
        self.model_shape = model_inputs.shape 

        self.img_h = self.model_shape[2]
        self.img_w = self.model_shape[3]
        print(f"[SYSTEM] AI 모델 요구 해상도 자동 동기화: ({self.img_w}x{self.img_h})")

        # ONNX 모델 내부 메타데이터에서 클래스 사전 동적 로드
        self.model_classes = {0: "LABEL_REQUIRED", 1: "PASS", 2: "REJECT"}  # Fallback 기본값
        try:
            meta = self.session.get_modelmeta().custom_metadata_map
            if 'names' in meta:
                self.model_classes = ast.literal_eval(meta['names'])
                print(f"[SYSTEM] 모델 내장 클래스 메타데이터 로드 성공: {self.model_classes}")
        except Exception as e:
            print(f"[WARNING] 모델 메타데이터 로드 실패, 기본 알파벳 순서 적용: {e}")

        # 모델의 영문 키값을 실제 화면 및 대시보드에 뿌릴 명칭으로 매핑
        self.label_map = {
            "PASS": {"ko": "라벨제거 페트병", "en": "Pure PET"},
            "LABEL_REQUIRED": {"ko": "라벨 미제거", "en": "Label Alert"},
            "REJECT": {"ko": "재활용 불가능", "en": "Unrecyclable PET"}
        }

    def preprocess(self, frame):
        """이미지 비율 왜곡 방지 및 정확한 채널 정렬"""
        h, w = frame.shape[:2]
        min_dim = min(h, w)

        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        crop_img = frame[start_y:start_y+min_dim, start_x:start_x+min_dim]

        img = crop_img.copy()
        img = cv2.resize(img, (self.img_w, self.img_h), interpolation=cv2.INTER_LINEAR)

        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        img = np.expand_dims(img, axis=0)

        # ONNX Runtime의 안정적인 연산을 위한 메모리 연속성 보장
        img = np.ascontiguousarray(img)

        return img, crop_img

    def predict(self, frame):
        """추론 수행, Softmax 자동 예외처리 및 데이터 정밀 매핑 (+ 지연 시간 정밀 측정)"""
        input_data, crop_img = self.preprocess(frame)

        # [성능 지표] 순수 ONNX 추론 연산 지연 시간(Latency) 측정 시작
        start_inf = time.perf_counter()
        outputs = self.session.run(None, {self.input_name: input_data})
        inference_time = (time.perf_counter() - start_inf) * 1000  # ms(밀리초) 단위 변환

        raw_output = outputs[0][0]

        # ONNX 출력 값이 Raw Logits인지 Probability인지 합(Sum)으로 동적 판별
        if not np.isclose(np.sum(raw_output), 1.0, atol=1e-3):
            exp_logits = np.exp(raw_output - np.max(raw_output))
            probabilities = exp_logits / np.sum(exp_logits)
        else:
            probabilities = raw_output

        class_idx = int(np.argmax(probabilities))
        confidence = float(probabilities[class_idx])

        # 인덱스 매핑이 아닌, 모델 고유 메타데이터 키 추출 (예: 'PASS')
        raw_class_name = self.model_classes.get(class_idx, "UNKNOWN")

        # 최종 출력 텍스트 딕셔너리 획득
        mapped_labels = self.label_map.get(raw_class_name, {"ko": raw_class_name, "en": raw_class_name})

        return mapped_labels["ko"], mapped_labels["en"], confidence, crop_img, inference_time

# =========================================================================
# 메인 하드웨어 실행 루프 (시나리오 및 하드웨어 최적화 완료 버전)
# =========================================================================
if __name__ == "__main__":
    classifier = PurePetClassifier("best.onnx")

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()

    print("[SYSTEM] Pure-PET AI 관제 시스템 엔진 가동 완료.")

    # FPS 연산용 타임스탬프 초기화
    prev_time = time.time()

    try:
        while True:
            frame = picam2.capture_array()

            # 수치 가공 및 지연시간 데이터 수용 (5개 인자 정상 언패킹)
            label_ko, label_en, conf, crop_frame, inf_time = classifier.predict(frame)

            # 실시간 전체 프레임 레이트(FPS) 계산
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
            prev_time = curr_time

            # 화면 표시용 텍스트 포맷팅
            log_text = f"{label_en} ({conf*100:.1f}%)"
            perf_text = f"Latency: {inf_time:.1f}ms | FPS: {fps:.1f}"

            # [교정 완료] 3안 반영: 파란 화면 방지를 위해 추가 변환 없이 원본 크롭 프레임 복사본을 그대로 디스플레이에 사용
            display_frame = crop_frame.copy()

            # 초록색(0, 255, 0)으로 분류 결과 표기, 노란색(0, 255, 255)으로 하드웨어 체급 표기
            cv2.putText(display_frame, log_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(display_frame, perf_text, (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            cv2.imshow("PURE-PET Sorter AI Test (Cropped)", display_frame)

            # [교정 완료] 동작 테스트 시나리오 문서 및 OpenClaw IPC 규격에 100% 맞춘 로그 스트링 출력
            print(f"[LOG] Result: {label_ko} | Conf: {conf:.4f}")

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("\n[SYSTEM] 사용자에 의해 시스템이 종료되었습니다.")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()
        print("[SYSTEM] 자원 해제 완료.")
