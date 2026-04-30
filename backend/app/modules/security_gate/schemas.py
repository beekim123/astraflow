from pydantic import BaseModel


class CaptchaOut(BaseModel):
    captcha_id: str
    question: str


class CaptchaVerifyRequest(BaseModel):
    captcha_id: str
    answer: str

