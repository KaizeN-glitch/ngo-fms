import jwt
from datetime import datetime, timedelta
import os

SERVICE_SECRET = os.getenv("SERVICE_SECRET", "shared-service-secret")
ALGORITHM = "HS256"

def create_service_token():
    payload = {
        "service": True,
        "role_name": "Accountant",
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }
    token = jwt.encode(payload, SERVICE_SECRET, algorithm=ALGORITHM)
    print(token)

if __name__ == "__main__":
    create_service_token()
