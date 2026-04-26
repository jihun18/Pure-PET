import smbus
from time import sleep

ADDRESS = 0x27
bus = smbus.SMBus(1)

class lcd:
    def __init__(self):
        # 파이 5의 속도에 맞춘 초기화 시퀀스
        self.lcd_write(0x33)
        sleep(0.1)
        self.lcd_write(0x32)
        sleep(0.1)
        self.lcd_write(0x28) # 4비트 모드, 2라인
        self.lcd_write(0x0C) # 디스플레이 ON
        self.lcd_write(0x06) # 커서 이동 설정
        self.lcd_write(0x01) # 화면 초기화
        sleep(0.2)

    def lcd_device_write(self, data):
        bus.write_byte(ADDRESS, data | 0x08)

    def lcd_write(self, cmd, mode=0):
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    def lcd_write_four_bits(self, data):
        self.lcd_device_write(data | 0x04)
        sleep(0.005) # 타이밍을 넉넉하게 줌
        self.lcd_device_write(data & ~0x04)
        sleep(0.005)

    def lcd_display_string(self, string, line):
        if line == 1: self.lcd_write(0x80)
        if line == 2: self.lcd_write(0xC0)
        for char in string:
            self.lcd_write(ord(char), 0x01)

    def lcd_clear(self):
        self.lcd_write(0x01)
        sleep(0.1)
