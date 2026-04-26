import cv2

def test_cameras():
    # 0번부터 10번까지 다 찔러봅니다.
    for i in range(11):
        cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ 카메라 인덱스 {i}번 작동 확인!")
                cap.release()
                return i
            cap.release()
    print("❌ 작동하는 카메라 인덱스를 찾지 못했습니다.")
    return None

if __name__ == "__main__":
    test_cameras()
