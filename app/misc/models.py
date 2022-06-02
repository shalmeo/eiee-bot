from dataclasses import dataclass


@dataclass
class AdminRegisterForm:
    first_name: str
    last_name: str
    patronymic: str
    tel: int
    email: str
    tg_id: int
    user_name: int
    level: str
    description: str
    msg_id: int