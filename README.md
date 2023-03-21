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
    
    
Набор доступных эндпоинтов:
posts/ - Отображение постов и публикаций (GET, POST);
posts/{id} - Получение, изменение, удаление поста с соответствующим id (GET, PUT, PATCH, DELETE);
posts/{post_id}/comments/ - Получение комментариев к посту с соответствующим post_id и публикация новых комментариев(GET, POST);
posts/{post_id}/comments/{id} - Получение, изменение, удаление комментария с соответствующим id к посту с соответствующим post_id (GET, PUT, PATCH, DELETE);
posts/groups/ - Получение описания зарегестрированных сообществ (GET);
posts/groups/{id}/ - Получение описания сообщества с соответствующим id (GET);
posts/follow/ - Получение информации о подписках текущего пользователя, создание новой подписки на пользователя (GET, POST).

Автор сборки Марк zotov001@yandex.ru
