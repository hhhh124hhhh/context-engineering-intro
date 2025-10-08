from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """创建刷新令牌"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """验证令牌并返回用户ID"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type_from_token: str = payload.get("type")

        if user_id is None or token_type_from_token != token_type:
            return None

        return user_id
    except JWTError as e:
        logger.warning("JWT token verification failed", error=str(e))
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning("Password verification failed", error=str(e))
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def generate_password_reset_token(email: str) -> str:
    """生成密码重置令牌"""
    delta = timedelta(hours=1)  # 1小时有效期
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "password_reset"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    """验证密码重置令牌"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email = decoded_token.get("sub")
        token_type = decoded_token.get("type")

        if user_email is None or token_type != "password_reset":
            return None

        return user_email
    except JWTError:
        return None


def generate_session_token() -> str:
    """生成会话令牌"""
    return secrets.token_urlsafe(32)


def generate_verification_token(email: str) -> str:
    """生成邮箱验证令牌"""
    delta = timedelta(hours=24)  # 24小时有效期
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email, "type": "email_verification"},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_email_verification_token(token: str) -> Optional[str]:
    """验证邮箱验证令牌"""
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email = decoded_token.get("sub")
        token_type = decoded_token.get("type")

        if user_email is None or token_type != "email_verification":
            return None

        return user_email
    except JWTError:
        return None


def validate_password_strength(password: str) -> dict:
    """验证密码强度"""
    errors = []

    if len(password) < 8:
        errors.append("密码长度至少为8个字符")

    if len(password) > 128:
        errors.append("密码长度不能超过128个字符")

    if not any(c.isupper() for c in password):
        errors.append("密码必须包含至少一个大写字母")

    if not any(c.islower() for c in password):
        errors.append("密码必须包含至少一个小写字母")

    if not any(c.isdigit() for c in password):
        errors.append("密码必须包含至少一个数字")

    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        errors.append("密码必须包含至少一个特殊字符")

    # 检查常见弱密码
    weak_passwords = [
        "password", "123456", "123456789", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    if password.lower() in weak_passwords:
        errors.append("密码过于简单，请使用更复杂的密码")

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "strength_score": calculate_password_strength(password)
    }


def calculate_password_strength(password: str) -> int:
    """计算密码强度分数 (0-100)"""
    score = 0

    # 长度分数
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10

    # 字符类型分数
    if any(c.isupper() for c in password):
        score += 15
    if any(c.islower() for c in password):
        score += 15
    if any(c.isdigit() for c in password):
        score += 15

    # 特殊字符分数
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 15

    return min(score, 100)


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮蔽敏感数据"""
    if len(data) <= visible_chars:
        return mask_char * len(data)

    return data[:visible_chars] + mask_char * (len(data) - visible_chars)


def generate_api_key() -> str:
    """生成API密钥"""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """哈希API密钥"""
    return pwd_context.hash(api_key)


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """验证API密钥"""
    try:
        return pwd_context.verify(plain_key, hashed_key)
    except Exception:
        return False


def create_secure_cookie_data(user_id: int, remember_me: bool = False) -> dict:
    """创建安全的Cookie数据"""
    expires_delta = timedelta(days=30) if remember_me else timedelta(hours=24)
    expires = datetime.utcnow() + expires_delta

    return {
        "user_id": user_id,
        "expires": expires.timestamp(),
        "remember_me": remember_me
    }


def verify_secure_cookie_data(cookie_data: dict) -> Optional[int]:
    """验证安全的Cookie数据"""
    try:
        expires = cookie_data.get("expires")
        if expires and datetime.utcnow().timestamp() > expires:
            return None

        user_id = cookie_data.get("user_id")
        return user_id if user_id else None
    except Exception:
        return None