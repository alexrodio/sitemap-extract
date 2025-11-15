# Задачи Фазы 3: Оркестрация и CLI

## Обзор Фазы

Эта фаза объединяет все базовые модули через Orchestrator, который управляет многопоточной обработкой множественных sitemap. Также создаётся CLI интерфейс для взаимодействия с пользователем.

**Зависимости**: Фаза 2 (все core модули должны быть готовы)

**Результат**: Полностью функциональное приложение с CLI

---

# МОДУЛЬ ORCHESTRATOR

## Задача 5.1: Создание Модуля Оркестрации

### Цель
Создать файл orchestrator.py - центральный компонент для управления обработкой множественных sitemap с многопоточностью.

### Детали Реализации

1. **Создание файла**
   - sitemap_extract/orchestrator.py
   - Module docstring описывающий назначение

2. **Импорты**
   - from concurrent.futures import ThreadPoolExecutor
   - from typing import List, Set, Tuple
   - from .parser import process_sitemap
   - from .file_operations import save_urls
   - from .constants import DEFAULT_MAX_WORKERS
   - import logging

3. **Logger**
   - logger = logging.getLogger(__name__)

### Критерии Принятия

- [ ] Файл orchestrator.py создан
- [ ] Все импорты добавлены
- [ ] Logger инициализирован
- [ ] Docstring добавлен

---

## Задача 5.2: Функция Обработки Всех Sitemap

### Цель
Реализовать главную функцию process_all_sitemaps для оркестрации обработки.

### Детали Реализации

1. **Сигнатура функции**
   - Имя: process_all_sitemaps
   - Параметры:
     - start_urls (List[str])
     - use_cloudscraper (bool, default=True)
     - use_proxy (bool, default=False)
   - Возврат: Tuple[Set[str], Set[str]]

2. **Инициализация структур данных**
   - all_sitemap_urls = set() - множество всех обнаруженных sitemap
   - all_page_urls = set() - множество всех page URLs
   - queue = start_urls.copy() - очередь для обработки

3. **Документация**
   - Docstring с описанием параметров
   - Объяснение возвращаемого значения
   - Примеры использования

### Сценарии Тестирования

1. **Тест инициализации**
   - Вызов с пустым списком
   - Должен вернуть (set(), set())
   - Нет ошибок

2. **Тест с одним URL**
   - Mock process_sitemap
   - Должен обработаться один URL
   - Результаты агрегируются

### Критерии Принятия

- [ ] Функция определена
- [ ] Структуры данных инициализированы
- [ ] Сигнатура корректна
- [ ] Документирована

---

## Задача 5.3: Настройка ThreadPoolExecutor

### Цель
Создать и настроить пул потоков для параллельной обработки sitemap.

### Детали Реализации

1. **Создание пула**
   - with ThreadPoolExecutor(max_workers=DEFAULT_MAX_WORKERS) as executor:
   - DEFAULT_MAX_WORKERS = 5 из констант
   - Context manager для автоматической очистки

2. **Обоснование max_workers=5**
   - Баланс между производительностью и нагрузкой
   - Не перегружает целевые серверы
   - Достаточно для параллелизма I/O операций
   - Документировать в комментарии

3. **Thread-Safety**
   - set.update() thread-safe в Python
   - list операции не всегда thread-safe
   - Минимизировать shared mutable state

4. **Альтернативные подходы**
   - ProcessPoolExecutor для CPU-bound задач
   - asyncio для более высокой конкурентности
   - Выбор ThreadPoolExecutor обоснован для I/O

### Сценарии Тестирования

1. **Тест создания пула**
   - Пул создаётся без ошибок
   - max_workers установлен корректно

2. **Тест выполнения задач**
   - Submit несколько задач
   - Все задачи выполняются
   - Результаты возвращаются

3. **Тест параллелизма**
   - Submit 10 задач
   - Выполняются параллельно (не последовательно)
   - Max 5 одновременно

### Потенциальные Проблемы

1. **GIL (Global Interpreter Lock)**
   - Python GIL ограничивает параллелизм CPU
   - Не проблема для I/O bound задач
   - Сетевые запросы освобождают GIL

2. **Resource exhaustion**
   - Каждый поток потребляет память
   - 5 потоков с большими данными могут быть проблемой
   - Мониторинг использования памяти

3. **Deadlocks**
   - Неправильная синхронизация может вызвать deadlock
   - Минимизировать shared state
   - Использовать thread-safe структуры

4. **Настройка производительности**
   - max_workers=5 может быть неоптимально
   - Зависит от системы и сети
   - Рассмотреть configurable параметр

### Критерии Принятия

- [ ] ThreadPoolExecutor создан
- [ ] max_workers=5 установлен
- [ ] Context manager использован
- [ ] Thread-safety обеспечена

---

## Задача 5.4: Основной Цикл Обработки

### Цель
Реализовать while-цикл для обработки очереди URL.

### Детали Реализации

1. **Структура цикла**
   - while queue: (пока очередь не пуста)
   - current_url = queue.pop(0) - FIFO извлечение
   - is_compressed = current_url.endswith('.xml.gz')

2. **Submit задачи**
   - future = executor.submit(process_sitemap, current_url, is_compressed, use_cloudscraper, use_proxy)
   - Параметры передаются корректно
   - Future объект возвращается немедленно

3. **Получение результата**
   - sitemap_urls, page_urls = future.result()
   - Блокирующий вызов - ждёт завершения
   - Результаты распаковываются

4. **Логирование**
   - DEBUG: "Processing URL: {current_url}"
   - DEBUG: "Compressed: {is_compressed}"
   - INFO: "Found {len(sitemap_urls)} sitemaps, {len(page_urls)} pages"

### Сценарии Тестирования

1. **Тест FIFO порядка**
   - Добавить URL в очередь: A, B, C
   - Должны обрабатываться в порядке A, B, C

2. **Тест определения сжатия**
   - URL ending .xml.gz -> is_compressed=True
   - URL ending .xml -> is_compressed=False

3. **Тест обработки результатов**
   - Mock process_sitemap с конкретными результатами
   - Результаты корректно извлекаются

4. **Тест пустой очереди**
   - queue = []
   - Цикл не должен выполниться
   - Нет ошибок

### Потенциальные Проблемы

1. **Последовательная обработка**
   - future.result() немедленно после submit блокирует
   - Теряется параллелизм
   - Нужно submit несколько задач перед ожиданием

2. **Queue.pop(0) неэффективен**
   - list.pop(0) это O(n) операция
   - Для больших очередей медленно
   - collections.deque более эффективен

3. **Динамическое расширение очереди**
   - Очередь модифицируется во время итерации
   - Может привести к бесконечному циклу при ошибках
   - Нужен механизм предотвращения циклов

4. **Блокировка на future.result()**
   - Если одна задача зависла, блокирует всё
   - Таймаут на future.result() может помочь
   - Но может потерять результаты

### Критерии Принятия

- [ ] While цикл реализован
- [ ] FIFO извлечение из очереди
- [ ] is_compressed определяется правильно
- [ ] Future submit и result работают
- [ ] Логирование добавлено

---

## Задача 5.5: Динамическое Расширение Очереди

### Цель
Реализовать механизм добавления обнаруженных вложенных sitemap в очередь.

### Детали Реализации

1. **Обновление множеств**
   - all_sitemap_urls.update(sitemap_urls)
   - all_page_urls.update(page_urls)
   - set.update() thread-safe

2. **Добавление новых URL**
   - Для каждого url в sitemap_urls:
     - ЕСЛИ url НЕ В all_sitemap_urls:
       - Добавить url в queue
   - Проверка предотвращает дублирование

3. **Предотвращение циклов**
   - Множество all_sitemap_urls отслеживает обработанные
   - URL добавляется только один раз
   - Циклические ссылки обрабатываются корректно

4. **Логирование**
   - DEBUG: "Adding {count} new sitemaps to queue"
   - DEBUG: "Skipping {count} already processed"

### Сценарии Тестирования

1. **Тест добавления новых URL**
   - process_sitemap возвращает 2 новых sitemap URL
   - Оба должны быть добавлены в queue
   - all_sitemap_urls должен содержать их

2. **Тест предотвращения дублирования**
   - process_sitemap возвращает уже обработанный URL
   - URL не должен быть добавлен в queue снова
   - all_sitemap_urls содержит его один раз

3. **Тест циклических ссылок**
   - Sitemap A ссылается на B
   - Sitemap B ссылается на A
   - Каждый обрабатывается только один раз
   - Нет бесконечного цикла

4. **Тест глубокой вложенности**
   - Цепочка A -> B -> C -> D -> E
   - Все обрабатываются
   - Правильный порядок (breadth-first)

### Потенциальные Проблемы

1. **Race conditions**
   - Множественные потоки могут обновлять all_sitemap_urls
   - set.update() должен быть thread-safe (это так в CPython)
   - Проверка "url not in all_sitemap_urls" может быть racy

2. **Проверка "not in" после update**
   - Текущий алгоритм: сначала update, потом проверка
   - Проблема: URL уже в all_sitemap_urls, не добавится в queue
   - Решение: проверять ДО update

3. **Порядок обработки**
   - Breadth-first vs depth-first
   - FIFO queue дает breadth-first
   - Может быть неоптимально для некоторых структур

4. **Бесконечные sitemap**
   - Генерируемые динамически sitemap могут быть бесконечными
   - Нужен limit на глубину или количество
   - Timeout на общую обработку

### Критерии Принятия

- [ ] Множества обновляются корректно
- [ ] Новые URL добавляются в queue
- [ ] Дублирование предотвращено
- [ ] Циклы не возникают
- [ ] Тесты с вложенностью проходят

---

## Задача 5.6: Обработка Ошибок в Пуле Потоков

### Цель
Реализовать graceful обработку ошибок при выполнении задач в потоках.

### Детали Реализации

1. **Try-except блок**
   - Обернуть future.result() в try-except
   - Ловить все Exception
   - Логировать с полным traceback

2. **Типы ошибок**
   - NetworkError из process_sitemap
   - ParseError из process_sitemap
   - TimeoutError от future
   - Любые неожиданные исключения

3. **Fail-soft поведение**
   - При ошибке одной sitemap продолжить другие
   - Не ломать весь процесс
   - Агрегировать успешные результаты

4. **Логирование ошибок**
   - ERROR: "Error processing {url}: {error}"
   - DEBUG: полный traceback
   - Сохранять URL с ошибкой для анализа

### Сценарии Тестирования

1. **Тест с ошибкой в задаче**
   - Mock process_sitemap raising Exception
   - Должна быть залогирована ошибка
   - Обработка продолжается

2. **Тест частичного успеха**
   - 3 URL: один с ошибкой, два успешных
   - Два успешных должны обработаться
   - Ошибка одного не влияет на другие

3. **Тест множественных ошибок**
   - Все URL с ошибками
   - Все ошибки логируются
   - Возвращается (set(), set())

### Потенциальные Проблемы

1. **Скрытие ошибок**
   - Catch-all Exception может скрыть серьёзные баги
   - Баланс между robustness и debugging
   - Логировать достаточно информации

2. **Накопление ошибок**
   - Множественные ошибки могут указывать на системную проблему
   - Рассмотреть threshold для прерывания
   - "Fail after N consecutive errors"

3. **Ошибки в logging**
   - Что если logger сам падает?
   - Может создать cascade failures
   - Fallback механизм

### Критерии Принятия

- [ ] Try-except вокруг future.result()
- [ ] Все исключения ловятся
- [ ] Ошибки логируются
- [ ] Обработка продолжается
- [ ] Тесты с ошибками проходят

---

## Задача 5.7: Финализация Обработки

### Цель
Сохранить индексный файл и вернуть агрегированные результаты.

### Детали Реализации

1. **Сохранение индекса**
   - ЕСЛИ all_sitemap_urls не пусто:
     - Преобразовать set в list
     - Вызвать save_urls("sitemap_index", list(all_sitemap_urls))
   - Обработать возможные ошибки save_urls

2. **Возврат результатов**
   - return (all_sitemap_urls, all_page_urls)
   - Оба это множества (set)
   - Вызывающий код может преобразовать при необходимости

3. **Финальное логирование**
   - INFO: "Processing complete"
   - INFO: "Found {len(all_sitemap_urls)} unique sitemaps"
   - INFO: "Found {len(all_page_urls)} unique pages"

4. **Cleanup**
   - ThreadPoolExecutor cleanup автоматический (context manager)
   - Нет явных ресурсов для освобождения

### Сценарии Тестирования

1. **Тест сохранения индекса**
   - all_sitemap_urls содержит 5 URL
   - save_urls должен быть вызван
   - Файл sitemap_index.txt создан

2. **Тест без sitemap**
   - all_sitemap_urls пусто
   - save_urls НЕ должен быть вызван
   - Нет ошибок

3. **Тест возврата**
   - Вызов process_all_sitemaps
   - Возвращаемые множества корректны
   - Содержат ожидаемые URL

### Потенциальные Проблемы

1. **Ошибка save_urls на финализации**
   - Вся обработка успешна, но save_urls падает
   - Потеря данных о sitemap index
   - Try-except вокруг save_urls

2. **Порядок в множествах**
   - set не гарантирует порядок
   - При сохранении в файл порядок случайный
   - Рассмотреть сортировку для консистентности

### Критерии Принятия

- [ ] Индексный файл сохраняется
- [ ] Результаты возвращаются
- [ ] Финальное логирование
- [ ] Cleanup выполняется

---

# МОДУЛЬ CLI

## Задача 6.1: Создание CLI Модуля

### Цель
Создать файл cli.py с интерфейсом командной строки.

### Детали Реализации

1. **Создание файла**
   - sitemap_extract/cli.py
   - Module docstring

2. **Импорты**
   - import argparse
   - import logging
   - import sys
   - from .logger import setup_logging
   - from .orchestrator import process_all_sitemaps
   - from .file_operations import read_urls_from_file, find_xml_files_in_directory

3. **Logger**
   - logger = logging.getLogger(__name__)

### Критерии Принятия

- [ ] Файл cli.py создан
- [ ] Импорты добавлены
- [ ] Logger готов

---

## Задача 6.2: Настройка ArgumentParser

### Цель
Создать и настроить ArgumentParser со всеми необходимыми аргументами.

### Детали Реализации

1. **Создание парсера**
   - parser = argparse.ArgumentParser(description="Process XML sitemaps and extract URLs")
   - Добавить дополнительную информацию
   - Установить formatter_class для красивого вывода

2. **Аргумент --url**
   - parser.add_argument('--url', type=str, help='Direct URL of the sitemap')
   - Опциональный аргумент
   - Пример в help: "https://example.com/sitemap.xml"

3. **Аргумент --file**
   - parser.add_argument('--file', type=str, help='File containing list of URLs (one per line)')
   - Описать формат: один URL на строку

4. **Аргумент --directory**
   - parser.add_argument('--directory', type=str, help='Directory containing XML files')
   - Указать поддерживаемые форматы: .xml, .xml.gz

5. **Флаг --no-cloudscraper**
   - parser.add_argument('--no-cloudscraper', action='store_true', help='Disable Cloudscraper, use requests.Session')
   - Дефолт: Cloudscraper включен

6. **Флаг --proxy**
   - parser.add_argument('--proxy', action='store_true', help='Enable proxy support')
   - Дефолт: прокси выключены
   - Примечание о необходимости конфигурации в коде

7. **Справка**
   - parser.add_argument('-h', '--help' автоматически
   - Красивое форматирование help

### Сценарии Тестирования

1. **Тест парсинга --url**
   - Аргументы: ['--url', 'http://example.com/sitemap.xml']
   - args.url должен быть 'http://example.com/sitemap.xml'

2. **Тест парсинга --file**
   - Аргументы: ['--file', 'urls.txt']
   - args.file должен быть 'urls.txt'

3. **Тест парсинга флагов**
   - Аргументы: ['--url', 'http://test.com', '--no-cloudscraper', '--proxy']
   - args.no_cloudscraper должен быть True
   - args.proxy должен быть True

4. **Тест вывода help**
   - Аргументы: ['--help']
   - Должен вывести справку
   - Выход с кодом 0

5. **Тест без аргументов**
   - Аргументы: []
   - Все опциональные должны быть None/False

### Потенциальные Проблемы

1. **Взаимоисключающие аргументы**
   - Можно указать и --url, и --file, и --directory
   - Все будут обработаны (объединены)
   - Это ожидаемое поведение согласно спецификации

2. **Валидация путей**
   - Нет проверки существования --file или --directory
   - Будет обработано позже в коде
   - argparse type=argparse.FileType может помочь

3. **Дефолтные значения**
   - Cloudsc raper по умолчанию ВКЛючен (через --no-cloudscraper)
   - Прокси по умолчанию ВЫКЛючен (через --proxy)
   - Логика инверсии для no-cloudscraper

### Критерии Принятия

- [ ] ArgumentParser создан
- [ ] Все 5 аргументов добавлены
- [ ] Help корректен и информативен
- [ ] Тесты парсинга проходят

---

## Задача 6.3: Валидация и Сбор URL

### Цель
Реализовать функцию для валидации аргументов и сбора всех URL из источников.

### Детали Реализации

1. **Функция validate_and_collect_urls**
   - Параметр: args (argparse.Namespace)
   - Возврат: List[str]

2. **Инициализация**
   - urls_to_process = []

3. **Обработка --url**
   - ЕСЛИ args.url:
     - urls_to_process.append(args.url)

4. **Обработка --file**
   - ЕСЛИ args.file:
     - urls = read_urls_from_file(args.file)
     - urls_to_process.extend(urls)

5. **Обработка --directory**
   - ЕСЛИ args.directory:
     - files = find_xml_files_in_directory(args.directory)
     - urls_to_process.extend(files)

6. **Валидация**
   - ЕСЛИ urls_to_process пуст:
     - logger.error("No valid input sources provided")
     - parser.print_help()
     - sys.exit(1)

7. **Возврат**
   - return urls_to_process

### Сценарии Тестирования

1. **Тест с --url**
   - args.url = "http://test.com"
   - Должен вернуть ["http://test.com"]

2. **Тест с --file**
   - Mock read_urls_from_file -> ["url1", "url2"]
   - Должен вернуть ["url1", "url2"]

3. **Тест с --directory**
   - Mock find_xml_files_in_directory -> ["file1.xml"]
   - Должен вернуть ["file1.xml"]

4. **Тест с комбинацией**
   - args.url + args.file + args.directory
   - Все должны быть объединены
   - Порядок: url, затем file, затем directory

5. **Тест без источников**
   - Все None
   - Должен вызвать sys.exit(1)
   - Справка выведена

### Потенциальные Проблемы

1. **Дублирование URL**
   - Один URL может быть в --url и в --file
   - Будет обработан дважды
   - orchestrator предотвращает дубли через set

2. **Невалидные URL**
   - Нет проверки формата URL
   - Невалидные URL упадут позже при fetch
   - Раннее выявление могло бы помочь

3. **Несуществующие файлы**
   - read_urls_from_file вернёт []
   - find_xml_files_in_directory вернёт []
   - Может привести к "No valid input sources"

### Критерии Принятия

- [ ] Функция реализована
- [ ] Все источники обрабатываются
- [ ] URL агрегируются корректно
- [ ] Валидация работает
- [ ] Выход при отсутствии источников

---

## Задача 6.4: Главная Функция main()

### Цель
Реализовать точку входа приложения, объединяющую всю логику.

### Детали Реализации

1. **Сигнатура**
   - def main():
   - Параметров нет
   - Возврат: None (или int для exit code)

2. **Инициализация логирования**
   - setup_logging()
   - Вызывается первым делом
   - logger.info("Starting sitemap extraction")

3. **Парсинг аргументов**
   - parser = create_argument_parser()
   - args = parser.parse_args()

4. **Сбор URL**
   - urls_to_process = validate_and_collect_urls(args)
   - logger.info(f"Processing {len(urls_to_process)} sitemap(s)")

5. **Запуск обработки**
   - use_cloudscraper = not args.no_cloudscraper
   - sitemaps, pages = process_all_sitemaps(urls_to_process, use_cloudscraper, args.proxy)

6. **Финальное логирование**
   - logger.info("Processing complete")
   - logger.info(f"Found {len(sitemaps)} sitemap URLs")
   - logger.info(f"Found {len(pages)} page URLs")

7. **Обработка исключений верхнего уровня**
   - Try-except вокруг всего
   - Ловить KeyboardInterrupt отдельно
   - Ловить все Exception
   - Логировать критические ошибки

### Сценарии Тестирования

1. **Тест успешного выполнения**
   - Mock все зависимости
   - main() должен выполниться
   - Логи должны быть записаны

2. **Тест с KeyboardInterrupt**
   - Mock process_all_sitemaps raising KeyboardInterrupt
   - Должно быть graceful завершение
   - Логирование прерывания

3. **Тест с ошибкой**
   - Mock поднимающий Exception
   - Должна быть залогирована ошибка
   - Программа завершается (не крашится)

4. **Integration тест**
   - Реальный запуск с test данными
   - End-to-end проверка
   - Проверка выходных файлов

### Потенциальные Проблемы

1. **Долгое выполнение**
   - Обработка может занять часы
   - Пользователь не видит прогресса
   - Рассмотреть progress bar или verbose логирование

2. **Ctrl+C handling**
   - KeyboardInterrupt должен обрабатываться gracefully
   - Текущие результаты могут быть потеряны
   - Рассмотреть сохранение промежуточных результатов

3. **Exit codes**
   - Успех: exit 0
   - Ошибка: exit 1
   - Сигналы: exit соответствующим кодом
   - Важно для скриптов

4. **Логирование в консоль**
   - Текущая setup_logging только в файл
   - Пользователь может не знать о прогрессе
   - Добавить StreamHandler для консоли

### Критерии Принятия

- [ ] Функция main() реализована
- [ ] Логирование инициализируется
- [ ] Аргументы парсятся
- [ ] Обработка запускается
- [ ] Результаты логируются
- [ ] Ошибки обрабатываются

---

## Задача 6.5: Entry Point (__main__.py)

### Цель
Создать __main__.py для запуска приложения как модуля.

### Детали Реализации

1. **Создание файла**
   - sitemap_extract/__main__.py

2. **Содержимое**
   - if __name__ == "__main__":
   - from .cli import main
   - main()

3. **Альтернатива: в cli.py**
   - Добавить в конец cli.py
   - if __name__ == "__main__": main()

### Сценарии Тестирования

1. **Тест запуска модуля**
   - python -m sitemap_extract
   - Должен запуститься main()
   - Эквивалентно прямому вызову

### Критерии Принятия

- [ ] __main__.py создан
- [ ] Импортирует и вызывает main
- [ ] python -m sitemap_extract работает

---

## Сводка Фазы 3

### Что Достигнуто

После завершения Фазы 3:

1. **Orchestrator модуль**
   - Многопоточная обработка
   - Управление очередью
   - Предотвращение циклов
   - Агрегация результатов
   - Fail-soft error handling

2. **CLI модуль**
   - ArgumentParser со всеми аргументами
   - Валидация входных данных
   - Сбор URL из множественных источников
   - Главная функция main()
   - Entry point

3. **Полностью функциональное приложение**
   - Можно запустить из командной строки
   - Обрабатывает sitemap различных форматов
   - Поддерживает все режимы работы

### Критические Аспекты

1. **Многопоточность**
   - ThreadPoolExecutor с 5 потоками
   - Thread-safe операции с set
   - Правильная обработка Future

2. **Предотвращение циклов**
   - Множество отслеживает обработанные URL
   - Проверка перед добавлением в очередь

3. **Error handling**
   - Fail-soft на всех уровнях
   - Детальное логирование ошибок
   - Graceful degradation

### Известные Ограничения

1. **Последовательная обработка Future**
   - future.result() сразу после submit
   - Теряется часть параллелизма
   - Оптимизация: batch processing

2. **Нет прогресс-индикации**
   - Пользователь не видит текущий прогресс
   - Только логи в файле

3. **Фиксированный max_workers**
   - Не настраивается через CLI
   - Не адаптируется под систему

### Следующая Фаза

Фаза 4 фокусируется на комплексном тестировании всех компонентов.
