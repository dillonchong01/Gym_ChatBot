import re


MODEL_PATH = ""
GYMS = ["Ang Mo Kio CC", "Bukit Gombak", "Kallang Basin",
        "Katong", "Bukit Canberra", "Bishan",
        "Bukit Batok", "Sengkang", "Fernvale Square",
        "Pasir Ris", "Enabling Village", "Delta",
        "Clementi", "Jalan Besar", "Serangoon Central",
        "Toa Payoh West CC", "Yio Chu Kang", "Toa Payoh",
        "Yishun", "Tampines", "Senja-Cashew",
        "Heartbeat Bedok", "Jurong Lake Gardens", "Choa Chu Kang",
        "Woodlands", "Jurong West", "Jurong East"]

# Regex for Time Parsing
TIME_REGEX = re.compile(
    r'\b(?:'
    r'(?P<h24>(?:[01]?\d|2[0-3])):(?P<m24>[0-5]\d)'
    r'|(?P<h24nc>(?:[01]\d|2[0-3])[0-5]\d)'
    r'|(?P<h12>\d{1,2})(?::?(?P<m12>[0-5]\d))?\s*(?P<period>[AaPp][Mm])'
    r')\b'
)