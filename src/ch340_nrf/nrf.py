"""Main nrf class for controlling nrf modules with CH340 serial adapters"""

import time
import enum
from typing import Iterable
import serial
from . import translator


class BAUDRATE(enum.Enum):
    """A class for NRF baudrates"""

    BAUDRATE_4800 = 4800
    BAUDRATE_9600 = 9600
    BAUDRATE_14400 = 14400
    BAUDRATE_19200 = 19200
    BAUDRATE_38400 = 38400
    BAUDRATE_115200 = 115200


class RATE(enum.Enum):
    """A class for NRF transmission rates"""

    @staticmethod
    def parse_string(rate: str) -> "RATE":
        """Parses a string to a RATE enum"""

        rate = rate.lower()

        if rate == "2mbps":
            return RATE.RATE_2M
        if rate == "1mbps":
            return RATE.RATE_1M
        if rate == "250kbps":
            return RATE.RATE_250K

        raise ValueError("Invalid String")

    RATE_250K = 1
    RATE_1M = 2
    RATE_2M = 3


class AddressType(enum.Enum):
    """A class for different address types"""

    ADDRESS_LOCAL = "local"
    ADDRESS_TARGET = "target"


class Address:
    """Address class for controlling nrf modules with CH340 serial adapters"""

    def __init__(self, address: Iterable[int] = (0x00, 0x00, 0x00, 0x00, 0x00)) -> None:
        if len(address) != 5:
            raise ValueError("Invalid address")

        self.address = list(address)

    def __repr__(self) -> str:
        return f"Address({self.address})"

    def __str__(self) -> str:
        return ":".join([f"{byte:02X}" for byte in self.address])

    def __eq__(self, other: "Address") -> bool:
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        return hash(self.__str__())

    def __len__(self) -> int:
        return len(self.address)

    def __getitem__(self, key: int) -> int:
        return self.address[key]

    def __setitem__(self, key: int, value: int) -> None:
        self.address[key] = value


class Config:
    """Config class for controlling nrf modules with CH340 serial adapters"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        baudrate: BAUDRATE = BAUDRATE.BAUDRATE_9600,
        rate: RATE = RATE.RATE_1M,
        local_address: Address = Address((0x00, 0x00, 0x00, 0x00, 0x00)),
        target_address: Address = Address((0x00, 0x00, 0x00, 0x00, 0x00)),
        freq: int = 400,
        checksum: int = 16,
    ) -> None:
        self.baudrate = baudrate
        self.rate = rate
        self.local_address = local_address
        self.target_address = target_address
        self.freq = freq
        self.checksum = checksum

    def __repr__(self) -> str:
        return (
            f"Config("
            f"baudrate={self.baudrate}, "
            f"rate={self.rate}, "
            f"local_address={self.local_address}, "
            f"target_address={self.target_address}, "
            f"freq={self.freq}, "
            f"checksum={self.checksum}"
            f")"
        )

    def __str__(self) -> str:
        return (
            f"baudrate={self.baudrate}, "
            f"rate={self.rate}, "
            f"local_address={self.local_address}, "
            f"target_address={self.target_address}, "
            f"freq={self.freq}, "
            f"checksum={self.checksum}"
        )

    def __eq__(self, other: "Config") -> bool:
        return self.__dict__ == other.__dict__


class NRF:
    """
    NRF class for controlling nrf modules with CH340 serial adapters
    """

    def __init__(
        self, port: str, config: Config | None = None, translate: bool = True
    ) -> None:
        self.serial_port = serial.Serial(port=port, baudrate=config.baudrate.value)

        self.translate = translate

        if config:
            self._config = config
            self.set_config(config)
        else:
            self._config = self.get_config()

    def send_message(self, message: str) -> None:
        """Sends a message to the nrf module"""

        self.serial_port.write((message + "\r\n").encode())

    def read_message(self, system=False) -> str | None:
        """Reads a message from the nrf module"""

        if self.serial_port.in_waiting > 0:
            message = self.serial_port.readline()

            if system:
                message = message.decode("gb18030")
            else:
                message = message.decode("utf-8")

            if self.translate:
                message = translator.translate(message)

            return message
        return None

    def read_all_messages(self, system=False) -> list[str]:
        """Reads all messages from the nrf module"""

        messages = []

        while self.serial_port.in_waiting > 0:
            messages.append(self.read_message(system=system))

        return messages

    def set_baudrate(self, baudrate: BAUDRATE) -> list[str]:
        """Sets the baudrate of the serial port"""

        if baudrate not in BAUDRATE:
            raise ValueError("Invalid baudrate")

        self.send_message("AT+BAUD=" + str(baudrate.value))
        self.serial_port.baudrate = baudrate.value
        self._config.baudrate = baudrate

        while not self.serial_port.in_waiting:
            time.sleep(0.01)
        return self.read_all_messages(system=True)

    def set_rate(self, rate: RATE) -> list[str]:
        """Sets the transmission rate of the nrf module"""

        if rate not in RATE:
            raise ValueError("Invalid rate")

        self.send_message("AT+RATE=" + str(rate.value))
        self._config.rate = rate

        while not self.serial_port.in_waiting:
            time.sleep(0.01)
        return self.read_all_messages(system=True)

    def set_address(
        self,
        address: Address | tuple[int],
        address_type: AddressType = AddressType.ADDRESS_LOCAL,
    ) -> list[str]:
        """Sets the specified address of the nrf module"""

        if isinstance(address, tuple):
            address = Address(address)

        self.send_message(
            "AT+"
            + ("R" if address_type == AddressType.ADDRESS_LOCAL else "T")
            + "XA="
            + ",".join([f"0x{byte:02X}" for byte in address])
        )

        if address_type == AddressType.ADDRESS_LOCAL:
            self._config.local_address = address
        else:
            self._config.target_address = address

        while not self.serial_port.in_waiting:
            time.sleep(0.01)
        return self.read_all_messages(system=True)

    def set_freq(self, freq: int) -> list[str]:
        """Sets the frequency of the nrf module"""

        if freq < 400 or freq > 525:
            raise ValueError("Invalid frequency")

        self.send_message("AT+FREQ=" + str(freq))
        self._config.freq = freq

        while not self.serial_port.in_waiting:
            time.sleep(0.01)
        return self.read_all_messages(system=True)

    def set_checksum(self, checksum: int) -> None:
        """Sets the checksum of the nrf module"""

        if checksum < 8 or checksum > 16:
            raise ValueError("Invalid checksum")

        self.send_message("AT+CRC=" + str(checksum))
        self._config.checksum = checksum

        while not self.serial_port.in_waiting:
            time.sleep(0.01)
        self.read_all_messages(system=True)

    def get_system_info(self) -> dict[str, object] | None:
        """Gets the system information of the nrf module"""

        def get_value(line: str) -> str:
            return line.split("：")[1].strip()

        self.send_message("AT?")

        while not self.serial_port.in_waiting:
            time.sleep(0.01)

        data = self.read_all_messages(system=True)
        info = {}

        for line, text in enumerate(data):
            if line in [0, 1]:
                continue

            if line == 2:
                info["baudrate"] = BAUDRATE(int(get_value(text)))

            elif line == 3:
                info["target_address"] = Address(
                    [int(byte, 16) for byte in get_value(text).split(",")]
                )

            elif line == 4:
                info["local_address"] = Address(
                    [int(byte, 16) for byte in get_value(text).split(",")]
                )

            elif line == 5:
                info["freq"] = int(get_value(text).replace("GHz", "").replace("2.", ""))

            elif line == 6:
                info["checksum"] = int(get_value(text).replace("Bit CRC Check", ""))

            elif line == 7:
                info["power"] = int(get_value(text).replace("dBm", ""))

            elif line == 8:
                info["rate"] = RATE.parse_string(get_value(text))

            elif line == 9:
                info["gain"] = get_value(text)

        if not info:
            return None

        return info

    def get_config(self, system_info: dict[str, object] | None = None) -> Config | None:
        """Convert system info into a Config"""

        return Config(**(system_info if system_info else self.get_system_info()))

    def set_config(self, config: Config) -> None:
        """Sets the configuration of the nrf module"""

        if config.baudrate != self._config.baudrate:
            self.set_baudrate(config.baudrate)

        if config.rate != self._config.rate:
            self.set_rate(config.rate)

        if config.local_address != self._config.local_address:
            self.set_address(config.local_address, AddressType.ADDRESS_LOCAL)

        if config.target_address != self._config.target_address:
            self.set_address(config.target_address, AddressType.ADDRESS_TARGET)

        if config.freq != self._config.freq:
            self.set_freq(config.freq)

        if config.checksum != self._config.checksum:
            self.set_checksum(config.checksum)

        self._config = config

    @property
    def config(self):
        """Returns the configuration of the nrf module"""

        return self._config

    @config.setter
    def config(self, config: Config) -> None:
        """Sets the configuration of the nrf module"""

        self.set_config(config)
