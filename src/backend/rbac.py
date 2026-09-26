from pathlib import Path
from typing import Annotated

import casbin
from fastapi import Depends, Header, HTTPException, Request

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "casbin_model.conf"
POLICY_PATH = BASE_DIR / "casbin_policy.csv"
_enforcer = None
ROLE_LEVELS = {"ACCOUNTS": 1, "EXECUTIVE": 2, "MANAGER": 3, "ADMIN": 4}


def get_enforcer():
    global _enforcer
    if _enforcer is None:
        _enforcer = casbin.Enforcer(str(MODEL_PATH), str(POLICY_PATH))
    return _enforcer


def check_permission(role: str, path: str, method: str) -> bool:
    return bool(get_enforcer().enforce(role.upper(), path, method.upper()))


def require_role(required_role: str):
    required_role = required_role.upper()
    if required_role not in ROLE_LEVELS:
        raise ValueError(f"Invalid required role: {required_role}")

    def dependency(
        request: Request,
        user_role: Annotated[str | None, Header(alias="X-User-Role")] = None,
    ) -> str:
        if not user_role:
            raise HTTPException(
                status_code=401,
                detail="X-User-Role header is required",
            )
        user_role = user_role.upper()
        if user_role not in ROLE_LEVELS:
            raise HTTPException(status_code=403, detail="Invalid role")
        if ROLE_LEVELS[user_role] < ROLE_LEVELS[required_role]:
            raise HTTPException(status_code=403, detail="Insufficient role")
        if not check_permission(user_role, request.url.path, request.method):
            raise HTTPException(status_code=403, detail="Access denied")
        return user_role

    return dependency
