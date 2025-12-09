import mfrc522

# Create an object of the MFRC522 class
mfrc522 = mfrc522.MFRC522()

def read_from_nfc_tag_ndef():
    """
    Read text data from an NFC tag using nfcpy library (PN532).
    Returns the text content or None if failed.
    """

    try:
        # Scan for tags
        (status, TagType) = mfrc522.MFRC522_Request(mfrc522.PICC_REQIDL)

        # If a tag is found
        if status == mfrc522.MI_OK:
            print("Tag detected")

            # Get the UID of the tag
            (status, uid) = mfrc522.MFRC522_Anticoll()

            # If the UID is successfully obtained
            if status == mfrc522.MI_OK:
                print("UID: " + ":".join([str(x) for x in uid]))

                # Select the tag
                mfrc522.MFRC522_SelectTag(uid)

                all_blocks = {}
                for index in range(4, 17, 4):
                    try:
                        data = [elem for index in [index] for elem in mfrc522.MFRC522_Read(index)]
                        result = ''.join([chr(charcode) for charcode in data])
                        all_blocks[index] = result
                        print("Data read from index {}: {}".format(index, result))
                    except Exception as e:
                        pass

                # After reading all blocks, parse them
                parsed_string = parse_nfc_data(all_blocks)
                if parsed_string:
                    print(f"\n✓ Parsed string: {parsed_string}")
                    return parsed_string, None
                else:
                    print("\n✗ Could not parse string from blocks")
                    return None, "Could not parse string from blocks"
            else:
                print("Error obtaining UID")
                return None, "Error obtaining UID"

    except Exception as e:
        return None, f"Error: {str(e)}"

def parse_nfc_data(block_data_dict):
    """
    Parse NFC tag data from multiple blocks.
    
    Args:
        block_data_dict: Dictionary mapping block index to data string
        Example: {0: "g½VÍ*öHá>", 1: "Í*öHá>Ð", ...}
    
    Returns:
        Parsed string (e.g., "spotify:album:test123445688")
    """
    # Convert all block data to bytes first
    all_bytes = []
    
    # Find the starting block (look for "Spotify" or recognizable pattern)
    start_block = None
    for idx in sorted(block_data_dict.keys()):
        block_str = block_data_dict[idx]
        # Convert string back to bytes (handling encoding issues)
        try:
            block_bytes = block_str.encode('latin-1')  # Preserves all byte values
            if b'spotify' in block_bytes:
                start_block = idx
                break
        except:
            pass
    
    # If we found a start, collect bytes from that point
    if start_block is not None:
        for idx in range(start_block, max(block_data_dict.keys()) + 1):
            if idx in block_data_dict:
                block_str = block_data_dict[idx]
                try:
                    block_bytes = block_str.encode('latin-1')
                    all_bytes.extend(block_bytes)
                except:
                    pass
    else:
        # Fallback: collect all blocks and search
        for idx in sorted(block_data_dict.keys()):
            block_str = block_data_dict[idx]
            try:
                block_bytes = block_str.encode('latin-1')
                all_bytes.extend(block_bytes)
            except:
                pass
    
    # Convert bytes to string, stopping at null bytes
    if all_bytes:
        # Find where the actual string starts
        byte_array = bytes(all_bytes)
        
        # Look for "Spotify" in the byte array
        spotify_marker = b'spotify'
        start_pos = byte_array.find(spotify_marker)
        
        if start_pos != -1:
            # Extract from "Spotify" onwards
            relevant_bytes = byte_array[start_pos:]
            # Stop at first null byte or non-printable garbage
            end_pos = len(relevant_bytes)
            for i, b in enumerate(relevant_bytes):
                if b == 0 or (b > 127 and chr(b) not in 'àá>þ'):  # Allow some special chars seen in output
                    # Check if we've hit the end of meaningful data
                    if i > 10:  # At least some data
                        end_pos = i
                        break
            
            result = relevant_bytes[:end_pos].decode('utf-8', errors='ignore').rstrip('\x00').strip()
            return result
    
    return None
