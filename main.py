"""A basic example of using the library"""

import src.ch340_nrf as nrf
import time

if __name__ == "__main__":
    module = nrf.NRF(
        "COM16",
        nrf.Config(
            freq=404,
            local_address=nrf.Address((0x41, 0x41, 0x41, 0x41, 0x41)),
            target_address=nrf.Address((0x41, 0x41, 0x41, 0x41, 0x42)),
        ),
    )

    print(module.get_system_info())

    while True:
        module.send_message("Hello World!".encode("utf-8"))
        print("Sent message")
        time.sleep(1)
