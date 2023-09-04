"""
This module contains the translation dictionary for the CH340-NRF module.
"""

TRANSLATIONS = {
    "通讯波特率设置成功": "Communication baud rate set successfully",
    "传输速率设置成功": "Transmission rate set successfully",
    "地址设置成功": "Address set successfully",
    "系统信息": "System Information",
    "波特率": "Baud Rate",
    "目标地址": "Target Address",
    "本地接收地址": "Local Receive Address",
    "通讯频率": "Communication Frequency",
    "校验模式": "Check Mode",
    "位CRC校验": "Bit CRC Check",
    "发射功率": "Transmit Power",
    "空中传输速率": "Air Transmission Rate",
    "传输速率": "Transmission Rate",
    "低噪声放大增益": "Low Noise Amplifier Gain",
    "开启": "On",
    "关闭": "Off"
}


def translate(text: str) -> str:
    """
    Translates the given text from Chinese to English
    """

    for chinese, english in TRANSLATIONS.items():
        text = text.replace(chinese, english)

    return text
