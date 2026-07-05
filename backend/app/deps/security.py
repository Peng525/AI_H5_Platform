"""密码哈希等安全工具（供 auth、seed、admin 共用）。"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
