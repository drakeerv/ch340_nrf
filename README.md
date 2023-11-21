# Warning: This project is currently in developement. Use at your own risk

## Installation

```bash
pip install ch340_nrf
```

## Usage

```python
import ch340_nrf
import time

# Create a new instance of the ch340_nrf class
module = ch340_nrf.NRF("COM3")

# Get the system information
print(module.get_system_info())

# Send a message
module.send_message("Hello World!")

# Wait for a response
time.sleep(0.5)

# Print the response
print(module.get_message())
```

## Reason

I made this library because there are no other libraries that allow you to use the ch340 nrf usb adapter with python. After reading the thread on the arduino forums [here](https://forum.arduino.cc/t/talking-to-a-usb-nrf24l01/395290/35), I decided to make my own library. I hope this library helps you with your projects!

## Dependencies

- [pyserial](https://pypi.org/project/pyserial/)

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## TODO

- [ ] Organize code better
- [ ] Add more functions
- [ ] Add more documentation
- [ ] Add more examples
- [ ] Add more error handling
- [ ] Improve initialization time
- [ ] Improve reliablity (remove time.sleep())

## Thanks

Thanks for using ch340_nrf!
