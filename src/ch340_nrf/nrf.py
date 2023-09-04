from . import translator
import serial
import time

BAUDRATES = {
    1: 4800,
    2: 9600,
    3: 14400,
    4: 19200,
    5: 38400,
    6: 115200
}

BAUDRATE_4800 = 1
BAUDRATE_9600 = 2
BAUDRATE_14400 = 3
BAUDRATE_19200 = 4
BAUDRATE_38400 = 5
BAUDRATE_115200 = 6

RATE = {
    1: 250000,
    2: 1000000,
    3: 2000000
}

RATE_250K = 1
RATE_1M = 2
RATE_2M = 3

class NRF:
    def __init__(self, port: str, baudrate: int = 2, rate: int = 3, local_address: list[int] = [0xff, 0xff, 0xff, 0xff, 0xff], target_address: list[int] = [0xff, 0xff, 0xff, 0xff, 0xff], freq: int = 400, checksum: int = 16, translate: bool = True) -> None:
        if baudrate not in BAUDRATES:
            raise ValueError("Invalid baudrate")

        self.serial_port = serial.Serial(
            port=port,
            baudrate=BAUDRATES[baudrate]
        )

        self.translate = translate

        self.set_baudrate(baudrate)
        self.set_rate(rate)
        self.set_local_address(local_address)
        self.set_target_address(target_address)
        self.set_freq(freq)

    def send_message(self, message: str) -> None:
        self.serial_port.write((message + "\r\n").encode())

    def read_message(self, system=False) -> str | None:
        if self.serial_port.in_waiting > 0:
            message = self.serial_port.readline()

            if system:
                message = message.decode("gb18030")
            else:
                message = message.decode("utf-8")

            if self.translate:
                message = translator.translate(message)

            return message
        
    def read_all_messages(self, system=False) -> list[str]:
        messages = []

        while self.serial_port.in_waiting > 0:
            messages.append(self.read_message(system=system))

        return messages

    def set_baudrate(self, baudrate: int) -> None:
        if baudrate not in BAUDRATES:
            raise ValueError("Invalid baudrate")

        self.send_message("AT+BAUD=" + str(baudrate))
        self.serial_port.baudrate = BAUDRATES[baudrate]
        self.baudrate = baudrate

        time.sleep(0.2)
        self.read_all_messages(system=True)

    def set_rate(self, rate: int) -> None:
        if rate not in RATE:
            raise ValueError("Invalid rate")

        self.send_message("AT+RATE=" + str(rate))
        self.rate = rate

        time.sleep(0.2)

        while self.serial_port.in_waiting > 0:
            self.read_message(system=True)

    def set_local_address(self, local_address: list[int]) -> None:
        if len(local_address) != 5:
            raise ValueError("Invalid address")

        self.send_message("AT+RXA=" + ",".join([f"0x{byte:02X}" for byte in local_address]))
        self.local_address = local_address

        time.sleep(0.2)
        self.read_all_messages(system=True)

    def set_target_address(self, target_address: list[int]) -> None:
        if len(target_address) != 5:
            raise ValueError("Invalid address")

        self.send_message("AT+TXA=" + ",".join([f"0x{byte:02X}" for byte in target_address]))
        self.target_address = target_address

        time.sleep(0.2)
        self.read_all_messages(system=True)

    def set_freq(self, freq: int) -> None:
        if freq < 400 or freq > 525:
            raise ValueError("Invalid frequency")

        self.send_message("AT+FREQ=" + str(freq))
        self.freq = freq

        time.sleep(0.2)
        self.read_all_messages(system=True)

    def set_checksum(self, checksum: int) -> None:
        if checksum < 8 or checksum > 16:
            raise ValueError("Invalid checksum")
        
        self.send_message("AT+CRC=" + str(checksum))
        self.checksum = checksum

        time.sleep(0.2)
        self.read_all_messages(system=True)

    def get_system_info(self) -> dict[str, str]:
        self.send_message("AT?")
        time.sleep(1)

        data = self.read_all_messages(system=True)
        info = {}

        for line, text in enumerate(data):
            if line in [0, 1]:
                continue

            if line == 2:
                info["baudrate"] = int(text.split("：")[1].strip())

            elif line == 3:
                info["target_address"] = [int(byte, 16) for byte in text.split("：")[1].strip().split(",")]

            elif line == 4:
                info["local_address"] = [int(byte, 16) for byte in text.split("：")[1].strip().split(",")]

            elif line == 5:
                info["freq"] = float(text.split("：")[1].strip().replace("GHz", ""))

            elif line == 6:
                info["checksum"] = int(text.split("：")[1].strip().replace("Bit CRC Check", ""))

            elif line == 7:
                info["power"] = int(text.split("：")[1].strip().replace("dBm", ""))

            elif line == 8:
                info["rate"] = float(text.split("：")[1].strip().replace("Mbps", ""))

            elif line == 9:
                info["gain"] = text.split("：")[1].strip()

        return info