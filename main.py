import time
import os
import csv
import subprocess
from datetime import datetime
from gpiozero import LED, Button, DigitalInputDevice, DistanceSensor
from RPLCD.i2c import CharLCD

# =========================
# 핀 설정
# =========================
led_module = LED(26)
start_button = Button(10, pull_up=True)

# IR 센서 3개
ir_top = DigitalInputDevice(17, pull_up=False)
ir_mid = DigitalInputDevice(27, pull_up=False)
ir_bottom = DigitalInputDevice(22, pull_up=False)

# 초음파 센서
ultrasonic = DistanceSensor(echo=24, trigger=23)

# =========================
# LCD 설정
# =========================
lcd = CharLCD(
    i2c_expander="PCF8574",
    address=0x27,
    port=1,
    cols=16,
    rows=2,
    charmap="A00",
    auto_linebreaks=True
)

# =========================
# LCD 출력
# =========================
def lcd_show(line1="", line2=""):
    lcd.clear()
    lcd.write_string(line1[:16])
    lcd.cursor_pos = (1, 0)
    lcd.write_string(line2[:16])

# =========================
# 상태 변수
# =========================
reset_requested = False
is_checking = False

# =========================
# 검사 중 버튼 입력 시 리셋 요청
# =========================
def request_reset():
    global reset_requested

    # 검사 중일 때만 리셋으로 처리
    if is_checking:
        reset_requested = True
        print("\n버튼 입력 감지")
        print("사용자 요청으로 대기 상태로 돌아갑니다.")

start_button.when_pressed = request_reset

# =========================
# 폴더 / 파일 설정
# =========================
BASE_DIR = os.path.expanduser("~/pure-pet")
IMAGE_DIR = os.path.join(BASE_DIR, "captures")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "sensor_log.csv")

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# =========================
# 로그 파일 초기화
# =========================
def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "image_file",
                "distance_cm",
                "ir_top",
                "ir_mid",
                "ir_bottom"
            ])

# =========================
# 대기 복귀 확인
# =========================
def check_reset():
    if reset_requested:
        raise RuntimeError("USER_RESET")

# =========================
# IR 센서 읽기
# =========================
def read_ir_states():
    check_reset()
    return {
        "top": ir_top.value,
        "mid": ir_mid.value,
        "bottom": ir_bottom.value
    }

# =========================
# 초음파 거리 읽기
# =========================
def read_distance_cm():
    check_reset()
    distance_cm = ultrasonic.distance * 100
    return round(distance_cm, 2)

# =========================
# 카메라 촬영
# =========================
def capture_image():
    check_reset()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    image_path = os.path.join(IMAGE_DIR, filename)

    cmd = [
        "rpicam-jpeg",
        "-o", image_path,
        "--width", "1280",
        "--height", "720",
        "-t", "1000"
    ]

    subprocess.run(cmd, check=True)

    check_reset()

    return filename, image_path

# =========================
# 로그 저장
# =========================
def save_log(image_file, distance_cm, ir_data):
    check_reset()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            image_file,
            distance_cm,
            ir_data["top"],
            ir_data["mid"],
            ir_data["bottom"]
        ])

# =========================
# 대기 상태
# =========================
def wait_start_button():
    global reset_requested
    global is_checking

    reset_requested = False
    is_checking = False
    led_module.off()

    print("\n1. 대기 상태")
    print("버튼을 누르면 검사를 시작합니다.")

    lcd_show("READY", "PRESS BUTTON")

    start_button.wait_for_press()
    time.sleep(0.2)

    # 버튼에서 손을 뗄 때까지 기다림
    start_button.wait_for_release()
    time.sleep(0.3)

    # 시작 버튼 입력은 리셋 요청이 아니므로 초기화
    reset_requested = False

# =========================
# 메인 프로그램
# =========================
init_log_file()
print("Pure-PET 메인 프로그램 시작")
lcd_show("READY", "PRESS BUTTON")

while True:
    try:
        wait_start_button()

        # 여기부터 검사 중 상태
        is_checking = True
        reset_requested = False

        print("버튼이 눌렸습니다. 검사 시작")
        lcd_show("CHECKING", "PLEASE WAIT")

        print("2. LED 켜기")
        led_module.on()
        time.sleep(0.5)
        check_reset()

        print("3. 초음파 센서 거리 측정")
        distance = read_distance_cm()
        print(f"초음파 거리: {distance} cm")
        check_reset()

        print("4. IR 센서 값 읽기")
        ir_data = read_ir_states()
        print(f"IR 결과: {ir_data}")
        check_reset()

        print("5. 카메라 촬영")
        image_file, image_path = capture_image()
        print(f"이미지 저장 완료: {image_path}")
        check_reset()

        print("6. 센서 정보 저장")
        save_log(image_file, distance, ir_data)
        print(f"로그 저장 완료: {LOG_FILE}")
        check_reset()

        print("7. 초기화 후 대기 상태로 복귀")

        is_checking = False
        reset_requested = False
        led_module.off()

        time.sleep(1)

        print("-----------------------------")

    except KeyboardInterrupt:
        print("\n프로그램 종료")
        is_checking = False
        reset_requested = False
        led_module.off()
        lcd_show("SYSTEM", "STOPPED")
        break

    except RuntimeError as e:
        if str(e) == "USER_RESET":
            is_checking = False
            reset_requested = False
            led_module.off()

            lcd_show("RESET", "RETURN READY")

            print("대기 상태로 복귀합니다.")

            # 버튼에서 손을 뗄 때까지 기다려서 바로 재시작되는 것 방지
            if start_button.is_pressed:
                start_button.wait_for_release()

            time.sleep(1)

        else:
            is_checking = False
            reset_requested = False
            led_module.off()

            lcd_show("RESET", "RETURN READY")

            print("동작이 중단되었습니다.")
            print("대기 상태로 돌아갑니다.")

            time.sleep(1)

    except Exception as e:
        is_checking = False
        reset_requested = False
        led_module.off()

        lcd_show("RESET", "RETURN READY")

        print(f"동작이 정상적으로 진행되지 않았습니다: {e}")
        print("버튼을 누르면 대기 상태로 돌아갑니다.")

        start_button.wait_for_press()
        start_button.wait_for_release()

        time.sleep(0.5)
