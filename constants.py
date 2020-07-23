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
PAID_FEATURE_TOP_DETAILED = 4

PAID_FEATURE_TYPES = (
    (PAID_FEATURE_PRO, 'Про аккаунт'),
    (PAID_FEATURE_TOP, 'Топ проект'),
    (PAID_FEATURE_DETAILED, 'Выделеный проект'),
    (PAID_FEATURE_TOP_DETAILED, 'Топ и Выделеный проект')
)

PAID_FEATURE_FOR_USER = 1
PAID_FEATURE_FOR_PROJECT = 2

PAID_FEATURE_FOR_TYPES = (
    (PAID_FEATURE_FOR_USER, 'Для пользователя'),
    (PAID_FEATURE_FOR_PROJECT, 'Для проекта')
)

TIME_DAY = 1
TIME_MONTH = 2
TIME_YEAR = 3
TIME_TEST = 4

TIME_TYPES = (
    (TIME_DAY, 'Дни'),
    (TIME_MONTH, 'Месяца'),
    (TIME_YEAR, 'Года')
)

STATISTICS_TIME_7_DAYS = 1
STATISTICS_TIME_30_DAYS = 2

STATISTICS_TIME_PERIODS = (
    (STATISTICS_TIME_7_DAYS, '7 Дней'),
    (STATISTICS_TIME_30_DAYS, '30 Дней')
)

STATISTICS_TYPE_VIEWS = 1
STATISTICS_TYPE_APPS = 2

STATISTICS_TYPES = (
    (STATISTICS_TYPE_VIEWS, 'Просмотры'),
    (STATISTICS_TYPE_APPS, 'Заявки')
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
RESPONSE_USER_EMAIL_NOT_EXIST = 'Пользователя с таким email или номером телефона не существует'
RESPONSE_INVALID_ROLE = 'Введенной роли не существует'
RESPONSE_INCORRECT_INPUT_DATA = 'Входные данные указаны неверно'
RESPONSE_EMPTY_INPUT_DATA = 'Входные данные отсутствуют'
RESPONSE_ENTER_EMAIL_OR_PHONE = 'Введите email или номер телефона'
RESPONSE_ENTER_ONLY_EMAIL_OR_PHONE = 'Введите только имейл или номер телефона'
RESPONSE_ENTER_ROLE = 'Введите роль'
RESPONSE_VERIFICATION_DOES_NOT_EXIST = 'Подтверждение с таким номером не найдено'
RESPONSE_VERIFICATION_EXPIRED = 'Код уже не действителен'
RESPONSE_VERIFICATION_INVALID_CODE = 'Код подтверждения не верный'
RESPONSE_PHONE_REGISTERED = 'Зарегестрирован на другого пользователя'
RESPONSE_PHONE_ALREADY_REGISTERED = 'Номер телефона уже зарегестрирован'
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
RESPONSE_NOT_OWNER = 'Вы не являетесь владельцем'
RESPONSE_FEATURE_TYPES = 'Типы платных услуг:'
RESPONSE_NO_PROJECTS = 'У вас нет ниодного проекта'
RESPONSE_REPLY_EXISTS = 'На этот отзыв уже существует ответ'
RESPONSE_COMMENT_REPLY_EXISTS = 'На этот комментарий уже существует ответ'
RESPONSE_DATA_TYPES_DIGITS = 'Должен быть числовым'
RESPONSE_NO_FEATURE = 'Подходящие виды платных услуг не существуют'
RESPONSE_NO_PK = 'Отсутствует параметр pk в url'

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
VALIDATION_PRICE_INVALID = 'Цена от должна быть меньше цены до'
VALIDATION_FEATURE_NOT_EXIST = 'Платная услуга не существует'
VALIDATION_TIME_PERIODS = 'Варианты временных отрезков: 1 - 7 дней, 2 - 30 дней'
VALIDATION_STATISTICS_TYPES = 'Виды статистики: 1 - Просмотры, 2- Заявки'
VALIDATION_TARGET_INVALID = 'Опции: 1 - для пользователя, 2 - для проекта'
VALIDATION_FEATURE_TYPE_NOT_FOR = 'Типы платных услуг для {0}: {1}'
VALIDATION_NO_LINKED_FEATURES = 'Платная услуга не имеет связаных платных услуг'
VALIDATION_TOKEN_INVALID = 'Токен недействителен'

NOTIFICATION_FEATURE_CREATED = 'Вы успешно приобрели'
NOTIFICATION_FEATURE_EXPIRING = 'Ваша услуга {0}, завтра заканчивается'

PHONE = 'Номер телефона'
EMAIL = 'Email'
PASSWORD = 'Пароль'
INCORRECT = 'Неверно'
MB = 'Мб'

FACEBOOK = 'facebook'
GOOGLE = 'google'
VK_WEB = 'vk_web'

FACEBOOK_INFO_URL = "https://graph.facebook.com/me?access_token={0}&fields=id,name,email,first_name,last_name&format=json"
GOOGLE_INFO_URL_V3 = "https://oauth2.googleapis.com/tokeninfo?id_token={}"
VK_INFO_URL = "https://api.vk.com/method/users.get?api_id=6714692&access_token={}&v=5.69&fields=photo_200"
VK_WEB_INFO_URL = "https://api.vk.com/method/users.get?api_id=6781515&access_token={}&v=5.69&fields=photo_200"
FACEBOOK_AVATAR_URL = "https://graph.facebook.com/{0}/picture?type=large"

SMS_TEXT = 'Код подтверждения для ISTOKHOME.COM:'

PAYMENT_REQUEST_PAYMENT = 1
PAYMENT_REQUEST_3DS = 2

PAYMENT_REQUEST_TYPES = (
    (PAYMENT_REQUEST_PAYMENT, 'PAYMENT'),
    (PAYMENT_REQUEST_3DS, '3DS')
)

PAYMENT_REQUEST_URL = 'https://api.cloudpayments.ru/payments/cards/charge'
PAYMENT_REQUEST_3DS_URL = 'https://api.cloudpayments.ru/payments/cards/post3ds'

PAYMENT_SUCCESS_URL = 'https://istokhome.com'
PAYMENT_FAILURE_URL = 'https://istokhome.com'
