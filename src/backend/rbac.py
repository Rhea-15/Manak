from pathlib import Path

import casbin
from fastapi import Depends, HTTPException, Request

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "casbin_model.conf"
POLICY_PATH = BASE_DIR / "casbin_policy.csv"

_enforcer = None


def get_enforcer():
    global _enforcer

    if _enforcer is None:
        _enforcer = casbin.Enforcer(
            str(MODEL_PATH),
            str(POLICY_PATH)
        )

    return _enforcer


def check_permission(role: str, path: str, method: str) -> bool:
    enforcer = get_enforcer()

    return bool(
        enforcer.enforce(
            role.upper(),
            path,
            method.upper()
        )
    )


def require_role(required_role: str):
    def dependency(request: Request):
        user_role = request.headers.get("X-User-Role")

        if not user_role:
            raise HTTPException(
                status_code=401,
                detail="X-User-Role header is required"
            )

        user_role = user_role.upper()

        allowed = check_permission(
            user_role,
            request.url.path,
            request.method
        )

        if not allowed:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return user_role

    return Depends(dependency)