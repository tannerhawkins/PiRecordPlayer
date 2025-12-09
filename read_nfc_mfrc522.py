
def read_from_nfc_tag_mfrc522():
    """
    Read text data from an NFC tag using MFRC522 reader.
    Returns the text content or None if failed.
    """
    try:
        from mfrc522 import SimpleMFRC522
        from RPi import GPIO
    except ImportError:
        return None, "MFRC522 library not found"

    try:
        reader = SimpleMFRC522()

        print("📱 Waiting for NFC tag...")
        print("    (Place tag on reader... Press Ctrl+C to cancel)")

        _, text = reader.read()
        GPIO.cleanup()

        # Clean up the text (remove trailing nulls/whitespace)
        text = text.strip().rstrip('\x00')

        return text, None

    except KeyboardInterrupt:
        GPIO.cleanup()
        return None, "Cancelled by user"
    except Exception as e:
        try:
            GPIO.cleanup()
        except Exception:
            pass
        return None, f"Error reading tag: {str(e)}"
