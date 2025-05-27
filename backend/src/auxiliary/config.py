from fastapi.security import OAuth2PasswordBearer
import os
from passlib.context import CryptContext

# OAuth2 configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login", auto_error=False)

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

static_url_root = os.environ["STATIC_URL_ROOT"]