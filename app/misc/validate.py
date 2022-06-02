from multidict import MultiDictProxy

from app.misc.exceptions import AdminRegisterFormValidateError
from app.misc.models import AdminRegisterForm


def validate_admin_register_data(data: MultiDictProxy) -> AdminRegisterForm | None:
    first_name: str = data.get('firstName').strip()
    if not first_name.isalpha():
        raise AdminRegisterFormValidateError()
    
    last_name: str = data.get('lastName').strip()
    if not last_name.isalpha():
        raise AdminRegisterFormValidateError()
    
    patronymic: str = data.get('patronymic').strip()
    if not patronymic.isalpha():
        raise AdminRegisterFormValidateError()
    
    tel: int = int(data.get('tel'))
    email: str = data.get('email').strip()
    tg_id: int = int(data.get('tgId'))
    user_name: str = data.get('userName').strip()
    level: str = data.get('level').strip()
    description: str = data.get('description').strip()
    msg_id: int = int(data.get('msgId'))
    
    return AdminRegisterForm(
        first_name=first_name,
        last_name=last_name,
        patronymic=patronymic,
        tel=tel,
        email=email,
        tg_id=tg_id,
        user_name=user_name,
        level=level,
        description=description,
        msg_id=msg_id
    )
    