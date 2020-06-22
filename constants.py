IMAGE_EXTENSIONS = ['.jpg', '.png', '.jpeg']

ROLE_CLIENT = 1
ROLE_MERCHANT = 2

ROLES = (
    (ROLE_CLIENT, 'Клиент'),
    (ROLE_MERCHANT, 'Специалист'),
)

QUESTION_RADIO = 1
QUESTION_DROPDOWN = 2
QUESTION_CHECKBOX = 3

QUESTION_TYPES = (
    (QUESTION_RADIO, 'Переключатель'),
    (QUESTION_DROPDOWN, 'Выпадающий список'),
    (QUESTION_CHECKBOX, 'Чекбокс')
)

APPLICATION_CREATED = 1
APPLICATION_CONFIRMED = 2
APPLICATION_FINISHED = 3
APPLICATION_FINISHED_CONFIRMED = 4
APPLICATION_DECLINED_CLIENT = 5
APPLICATION_DECLINED_MERCHANT = 6

APPLICATION_STATUSES = (
    (APPLICATION_CREATED, 'Создана'),
    (APPLICATION_CONFIRMED, 'Принята'),
    (APPLICATION_FINISHED, 'Завершена (не подтверждено)'),
    (APPLICATION_FINISHED_CONFIRMED, 'Завершена'),
    (APPLICATION_DECLINED_CLIENT, 'Отклонена клиентом'),
    (APPLICATION_DECLINED_MERCHANT, 'Отклонена специалистом')
)

APPLICATION_CREATED_STRING = 'created'
APPLICATION_CONFIRMED_STRING = 'confirmed'
APPLICATION_FINISHED_STRING = 'finished'
APPLICATION_FINISHED_CONFIRMED_STRING = 'finished_confirmed'
APPLICATION_DECLINED_STRING = 'declined'
APPLICATION_STATUSES_STRING = [APPLICATION_CREATED_STRING, APPLICATION_CONFIRMED_STRING, APPLICATION_FINISHED_STRING,
                               APPLICATION_FINISHED_CONFIRMED_STRING, APPLICATION_DECLINED_STRING]

PAID_FEATURE_PRO = 1
PAID_FEATURE_TOP = 2
PAID_FEATURE_DETAILED = 3

PAID_FEATURE_TYPES = (
    (PAID_FEATURE_PRO, 'Про аккаунт'),
    (PAID_FEATURE_TOP, 'Топ проект'),
    (PAID_FEATURE_DETAILED, 'Выделеный проект')
)

TIME_DAY = 1
TIME_MONTH = 2
TIME_YEAR = 3

TIME_TYPES = (
    (TIME_DAY, 'Дни'),
    (TIME_MONTH, 'Месяца'),
    (TIME_YEAR, 'Года')
)

ACTIVATION_EMAIL_SUBJECT = 'test'
ACTIVATION_EMAIL_BODY_START = 'test'
ACTIVATION_EMAIL_BODY_END = 'test'

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
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
RESPONSE_USER_NOT_MERCHANT = 'Пользователь не является специалтстом'
RESPONSE_USER_NOT_CLIENT = 'Пользователь не является клиентом'
RESPONSE_FIELD_REQUIRED = 'Обязательное поле'
RESPONSE_STATUS_NOT_VALID = 'Введенный статус не действителен'
RESPONSE_APPLICATION_STATUS_NOT_VALID = 'Статусы заявки для этого действия:'
RESPONSE_CANT_MODIFY = 'Вы не можете изменять этот обьект'
RESPONSE_MAX_FILES = 'Максимальное количество файлов:'
RESPONSE_RIGHT_ONLY_DIGITS = 'Только цифровые значения'
RESPONSE_PAID_TYPE_INVALID = 'Типы платной услуги: 1 - Про, 2 - Топ, 3 - Выделеный'

VALIDATION_PHONE_FORMAT_ERROR = 'Формат номера телефона: +X (XXX) XXX-XX-XX'
VALIDATION_CANT_BE_BLANK = 'Не может быть пустым'
VALIDATION_NOT_ALLOWED_EXT = 'Запрещенное расширение файла, разрешенные расширения'
VALIDATION_MAX_FILE_SIZE = 'Максимальный размер файла'
VALIDATION_CODE_FORMAT = 'Формат кода подтверждения: XXXX'
VALIDATION_CODE_ONLY_DIGITS = 'Код подтверждения должен состоять только из цифр'
VALIDATION_PHONE_NOT_VERIFIED = 'Номер телефона не подтвержден'
VALIDATION_PASSWORD_DIGITS = 'Пароль должен содержать хотя бы 1 цифру'
VALIDATION_PASSWORD_UPPERCASE = 'Пароль должен содержать хотя бы 1 заглавную букву'
VALIDATION_PASSWORD_LOWERCASE = 'Пароль должен содержать хотя бы 1 прописную букву'
VALIDATION_PASSWORD_LENGTH = 'Пароль должен состоять минимум из 8 символов'
VALIDATION_FORM_NOT_COMPLETE = 'Вы не ответили на все вопросы анкеты'
VALIDATION_RATING_RANGE = 'Рейтинг может быть от 0 до 10'
VALIDATION_EMAIL_EXISTS = 'Email заянт другим пользователем'

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
