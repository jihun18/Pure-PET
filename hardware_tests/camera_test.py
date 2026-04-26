import cv2
import numpy as np
from picamera2 import Picamera2

# 1. Picamera2 객체 생성
picam2 = Picamera2()

# 2. 카메라 설정 (해상도를 640x480으로 고정하여 부하를 줄임)
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)

# 3. 카메라 시작
picam2.start()

print("Picamera2를 이용한 Pure-PET 카메라 테스트 중...")
print("종료하려면 영상 창을 클릭하고 'q'를 누르세요.")

try:
    while True:
        # 실시간 프레임을 배열(Array) 형태로 가져오기
        frame = picam2.capture_array()

        # 화면에 출력
        cv2.imshow('Pure-PET Pi5 (Picamera2)', frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    # 4. 카메라 및 창 닫기
    picam2.stop()
    cv2.destroyAllWindows()
