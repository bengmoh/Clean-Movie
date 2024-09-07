import base64

def encode(interval_string):
    encoded_string = base64.b85encode(interval_string.encode()).decode()
    return encoded_string

def decode(code):
    decoded_string = base64.b85decode(code).decode()
    return decoded_string