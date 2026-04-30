import random
from uuid import uuid4

from app.core.cache import cache_delete, cache_get, cache_incr, cache_set

CAPTCHA_TTL_SECONDS = 180
FAIL_LOCK_SECONDS = 600
MAX_FAILS = 5


def fail_key(ip: str) -> str:
    return f"visitor_captcha_fail:{ip}"


def captcha_key(captcha_id: str) -> str:
    return f"visitor_captcha:{captcha_id}"


async def create_captcha(ip: str) -> tuple[str, str]:
    failed = await cache_get(fail_key(ip))
    if failed and int(failed) >= MAX_FAILS:
        raise ValueError("too many failed attempts, please try later")
    left = random.randint(1, 9)
    right = random.randint(1, 9)
    captcha_id = str(uuid4())
    await cache_set(captcha_key(captcha_id), str(left + right), ex=CAPTCHA_TTL_SECONDS)
    return captcha_id, f"{left} + {right} = ?"


async def verify_captcha(ip: str, captcha_id: str, answer: str) -> bool:
    expected = await cache_get(captcha_key(captcha_id))
    if expected is None:
        await cache_incr(fail_key(ip), ex=FAIL_LOCK_SECONDS)
        return False
    ok = str(answer).strip() == str(expected).strip()
    await cache_delete(captcha_key(captcha_id))
    if not ok:
        await cache_incr(fail_key(ip), ex=FAIL_LOCK_SECONDS)
    else:
        await cache_delete(fail_key(ip))
    return ok

