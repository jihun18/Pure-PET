import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice

# 지훈님이 연결하신 라즈베리 파이 5 GPIO 핀 번호 (BCM 규격)
DT_PIN = 5
SCK_PIN = 6

class RPi5HX711:
    def __init__(self, dout_pin, sck_pin):
        # 라즈베리 파이 5 호환을 위해 gpiozero 디바이스로 초기화
        self.dout = DigitalInputDevice(dout_pin)
        self.sck = DigitalOutputDevice(sck_pin, initial_value=False)
        self.offset = 0
        
        # 센서 안정화 대기
        time.sleep(0.5)

    def is_ready(self):
        # DOUT 핀이 Low(0)가 되면 데이터 출격 준비 완료 상태임
        return self.dout.value == 0

    def read(self):
        # 데이터가 준비될 때까지 대기
        while not self.is_ready():
            time.sleep(0.001)

        raw_val = 0
        # 24비트 데이터 수신 (MSB 순서로 한 비트씩 시프트하며 읽기)
        for _ in range(24):
            self.sck.on()
            raw_val = (raw_val << 1) | self.dout.value
            self.sck.off()

        # 25번째 펄스를 주어 다음 데이터 수신 채널을 A(Gain 128)로 고정
        self.sck.on()
        self.sck.off()

        # 24비트 부호 있는 정수(2의 보수) 표현형 처리 (음수 보정)
        if raw_val & 0x800000:
            raw_val -= 0x1000000

        return raw_val

    def tare(self, count=15):
        print("[SYSTEM] 현재 영점(Tare) 조절 중입니다... 상판을 비워두세요.")
        sum_val = 0
        for _ in range(count):
            sum_val += self.read()
            time.sleep(0.05)
        # 빈 상태의 평균 데이터값을 기준점(Offset)으로 저장
        self.offset = sum_val / count
        print(f"[SYSTEM] 영점 조절 완료! 기준값(Offset): {self.offset:.1f}")

    def get_raw_weight(self):
        # 현재 측정값에서 기준 영점값을 뺀 결과 반환
        return self.read() - self.offset


if __name__ == "__main__":
    print("[SYSTEM] HX711 로드셀 센서 검증을 시작합니다.")
    try:
        # 센서 객체 생성 및 영점 잡기
        hx = RPi5HX711(dout_pin=DT_PIN, sck_pin=SCK_PIN)
        hx.tare()
        
        print("\n==============================================")
        print(" 실시간 센서 값 출력 중 (Ctrl + C 누르면 종료)")
        print(" 아크릴판을 손으로 지긋이 누르거나 페트병을 올려보세요.")
        print("==============================================\n")
        
        while True:
            # 영점이 제거된 순수 무게 변화 수치 읽기
            weight_signal = hx.get_raw_weight()
            print(f"[DATA] 로드셀 변동 신호값 (Raw Signal): {weight_signal:.0f}")
            time.sleep(0.4)
            
    except KeyboardInterrupt:
        print("\n[SYSTEM] 사용자에 의해 센서 테스트가 종료되었습니다.")
