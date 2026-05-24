import os
import subprocess
import time

def test_usb_speaker():
    print("[SYSTEM] Pure-PET 오디오 유닛 검증을 시작합니다 (RPi5 Card 2 고정).")
    
    # 라즈베리 파이 시스템 내장 오디오 테스트 파일 경로
    test_sound = "/usr/share/sounds/alsa/Front_Center.wav"
    
    # 만약 위 파일이 없을 경우를 대비한 백업 파일 경로
    if not os.path.exists(test_sound):
        test_sound = "/usr/share/sounds/alsa/Front_Left.wav"
        
    if not os.path.exists(test_sound):
        print("[ERROR] 라즈베리 파이 내부에 기본 내장된 테스트 음원 파일이 없습니다.")
        print("대신 터미널 명령어로 'speaker-test -c2 -t wav'를 실행해 보세요.")
        return

    print(f"[INFO] 타겟 오디오 파일 발견: {test_sound}")
    print("[SYSTEM] 3초 뒤 스피커 출력을 시도합니다. 스피커 본체의 볼륨을 올려주세요.")
    time.sleep(3)

    try:
        print("[AUDIO] 지금 스피커에서 소리가 나야 합니다... (Front, Center!)")
        
        # [교정] -D plughw:2,0 인자를 추가하여 USB 스피커 장치로 사운드를 강제 라우팅합니다.
        subprocess.run(["aplay", "-D", "plughw:2,0", test_sound], check=True)
        print("[SYSTEM] 오디오 출력이 정상적으로 완료되었습니다.")
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 오디오 장치 구동 실패: {e}")
        print("[TIP] 스피커 전원이 켜져 있는지, USB 포트에 제대로 밀착되었는지 확인하세요.")

if __name__ == "__main__":
    test_usb_speaker()
