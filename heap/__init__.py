import uuid
from datetime import datetime

def unique_batch():
    date_str = datetime.now().strftime("%Y%m%d")
    unique_id = uuid.uuid4().hex[:8] 
    return f"{date_str}_{unique_id}"
