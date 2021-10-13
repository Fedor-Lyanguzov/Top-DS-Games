# Выбрать лучшие игры для Nintendo DS

## Идея

Есть портативная игровая консоль Nintendo DS, гипотетически есть устройство для запуска игр с SD-карты. Максимальный объем SD-карты -- 16 Гб. Игры представлены в виде файлов-образов, размером [1; 256] Мб. 

*Задача:* Набить SD-карту наибольшим количеством наилучших игр.

## Исходные данные

Полный набор игр возьмем с торрентов. Всего существует 7180 различных игр, новых уже не выпускают. Полный набор представляет собой директорию с zip-архивами, по одному на игру, в каждом файл .nds -- образ игры.

Топ игр возьмем с сайта metacritic.com:
- По оценкам критиков: https://www.metacritic.com/browse/games/release-date/available/ds/metascore
- По оценкам игроков: https://www.metacritic.com/browse/games/release-date/available/ds/userscore

## Планирование

1. Возьмем топ-300 по оценкам критиков и топ-300 по оценкам игроков. Найдем пересечение, назовем базовым набором игр.
2. Возьмем полный набор игр, измерим для каждой размер образа
3. Сопоставим базовый набор игр с полным набором игр, найдем результирующий набор игр весом не более 15 Гб, лучший по критериям:
    1. Выше оценка критиков
    2. Выше оценка игроков
    3. Меньше размер
4. Результирующий набор игр разобъем на категории по жанрам
5. Запишем результирующий набор игр на SD-карту

## Решение

### Построение базового набора игр

- *Входные данные:* html-страницы с сайта metacritic
- *Выходные данные:* таблица со столбцами (название, ссылка, оценка критиков, оценка игроков)
- *Решение:* смотри файл make_db.py

### Измерение размера образов в полном наборе игр

- *Входные данные:* директория с zip-архивами, в каждом nds-образ
- *Выходные данные:* таблица со столбцами (название архива, название файла, размер в Мб)
- *Решение:* смотри файл archive_table.py

### Сопоставление игр с жанрами

Необходимо для каждой игры из базового набора найти жанры на ее странице на metacritic. Создать таблицу жанров и соединить отношением многие-ко-многим с таблицей базового набора игр.

- *Входные данные:* html-страницы, по одной на игру из базового набора
- *Выходные данные:* таблица жанров, таблица связей со столбцами (игра, жанр)
- *Решение:* смотри файл scrape_genres.py

## Задачи

### Выделить из базы данных кеш

html-страницы складывать в отдельную базу данных, не загружать кеш в гитхаб.

### Проверить базовый набор

Необходимо просмотреть жанры, маловстречающиеся и повторяющиеся объединить, построить примерное дерево категорий.

### Сопоставление базового с полным набором игр

Необходимо реализовать быстрый неточный поиск из базового набора в полном. Предложение: построить однословные индексы по базовому и полному набору, при сопоставлении использовать расстояние Левенштейна около 3.

### Построение результирующего набора игр

Необходимо решить задачу минимизации критериальной функции с ограничением в 15 Гб размера на основе критериев:
  1. Выше оценка критиков
  2. Выше оценка игроков
  3. Меньше размер
