"""A basic example of using the library"""

import math
import src.ch340_nrf as nrf

if __name__ == "__main__":
    module = nrf.NRF("COM15", nrf.Config(rate=nrf.RATE.RATE_250K))

    print(module.get_system_info())

    while True:
        message = module.read_message(blocking=True, timeout=math.inf)
        module.send_message(message)
