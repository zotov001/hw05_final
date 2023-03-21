Социальная сеть блогеров. Учебный проект.

Сообщество для публикаций. Блог с возможностью публикации постов, подпиской на группы и авторов, а также комментированием постов.

Технологии

    Python 3.7, Django 2.2.19, Pillow, Pytest, Requests

Как запустить проект:

Cоздать и активировать виртуальное окружение:

    python -m venv venv

    source env/bin/activate

Установить зависимости из файла requirements.txt:

    python -m pip install --upgrade pip

    pip install -r requirements.txt

Выполнить миграции:

    python manage.py migrate

Запустить проект:

    python manage.py runserver
    
Документация API доступна по эндпойнту:

    http://localhost/redoc/

Автор сборки Марк zotov001@yandex.ru
