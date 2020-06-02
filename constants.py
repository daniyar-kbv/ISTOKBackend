IMAGE_EXTENSIONS = ['.jpg', '.png', '.jpeg']

ROLE_CLIENT = 1
ROLE_MERCHANT = 2

ROLES = (
    (ROLE_CLIENT, 'Клиент'),
    (ROLE_MERCHANT, 'Специалист'),
)

ACTIVATION_EMAIL_SUBJECT = 'test'
ACTIVATION_EMAIL_BODY_START = 'test'
ACTIVATION_EMAIL_BODY_END = 'test'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
PHONE_FORMAT = '\+7 \(\w{3}\) \w{3}-\w{2}-\w{2}'

MAX_REGULAR_FILE_SIZE = 10000000

RESPONSE_SERVER_ERROR = 'Ошибка на сервере'
RESPONSE_USER_EXISTS = 'Пользователь с этим почтовым ящиком уже зарегестрирован'
RESPONSE_USER_EMAIL_NOT_EXIST = 'Пользователя с таким email не существует'
RESPONSE_USER_PHONE_NOT_EXIST = 'Пользователя с таким номером телефона не существует'
RESPONSE_INVALID_ROLE = 'Введенной роли не существует'
RESPONSE_ENTER_EMAIL_OR_PHONE = 'Введите имейл или номер телефона'
RESPONSE_ENTER_ONLY_EMAIL_OR_PHONE = 'Введите только имейл или номер телефона'
RESPONSE_VERIFICATION_DOES_NOT_EXIST = 'Подтверждение с таким номером не найдено'
RESPONSE_VERIFICATION_INVALID_CODE = 'Код подтверждения не верный'
RESPONSE_PHONE_REGISTERED = 'Зарегестрирован на другого пользователя'
RESPONSE_SOCIAL_TOKEN_INVALID = 'Токен не действителен'
RESPONSE_DOES_NOT_EXIST = 'не существует'

VALIDATION_PHONE_FORMAT_ERROR = 'Формат номера телефона: +X (XXX) XXX-XX-XX'
VALIDATION_CANT_BE_BLANK = 'Не может быть пустым'
VALIDATION_NOT_ALLOWED_EXT = 'Запрещенное расширение файла, разрешенные расширения'
VALIDATION_MAX_FILE_SIZE = 'Максимальный размер файла'
VALIDATION_CODE_FORMAT = 'Формат кода подтверждения: XXXX'
VALIDATION_CODE_ONLY_DIGITS = 'Код подтверждения должен состоять только из цифр'
VALIDATION_PHONE_NOT_VERIFIED = 'Номер телефона не подтвержден'

PHONE = 'Номер телефона'
EMAIL = 'Email'
PASSWORD = 'Пароль'
INCORRECT = 'Неверно'
MB = 'Мб'


FACEBOOK = 'facebook'
GOOGLE = 'google'
VK_WEB = 'vk_web'

FACEBOOK_INFO_URL = "https://graph.facebook.com/me?access_token={0}&fields=id,name,email,first_name,last_name&format=json"
GOOGLE_INFO_URL_V3 = "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={}"
VK_WEB_INFO_URL = "https://api.vk.com/method/users.get?api_id=6781515&access_token={}&v=5.69&fields=photo_200"
FACEBOOK_AVATAR_URL = "https://graph.facebook.com/{0}/picture?type=large"
