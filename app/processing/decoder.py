import struct
import binascii
from app.utils.logger import log

def decode_signal(raw_values_hex: str, data_format: str = "float") -> list:
    """
    Decodes a hex-encoded string of signal data from the microcontroller.
    
    Args:
        raw_values_hex (str): Hexadecimal string, e.g., "41C80000..." (from WPT...:<hex>)
        data_format (str): Either 'float' or 'uint16' based on encoding by client

    Returns:
        List of decoded float or int values.
    """
    try:
        log(f"[Decoder] Raw hex input (preview): {raw_values_hex[:50]}...")

        raw_bytes = binascii.unhexlify(raw_values_hex)

        values = []
        if data_format == "float":
            for i in range(0, len(raw_bytes), 4):
                value = struct.unpack('<f', raw_bytes[i:i+4])[0]
                values.append(value)

        elif data_format == "uint16":
            for i in range(0, len(raw_bytes), 2):
                value = struct.unpack('<H', raw_bytes[i:i+2])[0]
                values.append(value)

        else:
            raise ValueError("Unsupported data format.")

        log(f"[Decoder] Decoded {len(values)} values")
        return values

    except Exception as e:
        log(f"[Decoder] Failed to decode signal: {e}", level="ERROR")
        return []
