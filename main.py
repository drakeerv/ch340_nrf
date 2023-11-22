import src.ch340_nrf as nrf

if __name__ == "__main__":
    module = nrf.NRF("COM15", nrf.Config(rate=nrf.RATE.RATE_250K))

    print(module.get_system_info())
