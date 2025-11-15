# Задачи Фазы 4: Тестирование и Обеспечение Качества

## Обзор Фазы

Эта фаза полностью посвящена тестированию всех компонентов приложения на различных уровнях: unit, integration, performance и stress тесты. Цель - обеспечить надёжность, корректность и производительность.

**Зависимости**: Фазы 1-3 (весь код должен быть реализован)

**Результат**: Комплексное тестовое покрытие, выявленные и исправленные баги

---

## Задача 8.1: Настройка Тестовой Инфраструктуры

### Цель
Создать инфраструктуру для тестирования с использованием pytest.

### Детали Реализации

1. **Создание директории tests**
   - Создать tests/ в корне проекта
   - Создать tests/__init__.py (может быть пустым)

2. **Создание conftest.py**
   - tests/conftest.py
   - Определение общих fixtures
   - Конфигурация pytest

3. **Создание requirements-dev.txt**
   - pytest>=6.0
   - pytest-cov для coverage
   - pytest-mock для mocking
   - Другие dev зависимости

4. **Структура тестов**
   - tests/test_constants.py
   - tests/test_network.py
   - tests/test_parser.py
   - tests/test_file_operations.py
   - tests/test_orchestrator.py
   - tests/test_cli.py

5. **Fixtures директория**
   - tests/fixtures/ для тестовых данных
   - Примеры XML файлов
   - Примеры .gz файлов
   - Примеры txt файлов со списками URL

### Сценарии Тестирования

1. **Тест запуска pytest**
   - pytest должен обнаружить все тесты
   - Начальный запуск без ошибок

2. **Тест fixtures**
   - Все fixture функции работают
   - Данные загружаются корректно

3. **Тест coverage**
   - pytest --cov запускается
   - Генерируется отчёт покрытия

### Потенциальные Проблемы

1. **Import paths**
   - Проблемы с импортом модулей из sitemap_extract
   - Необходимость настройки PYTHONPATH
   - Использовать editable install: pip install -e .

2. **Fixtures данные**
   - Создание валидных test XML файлов
   - Создание валидных .gz архивов
   - Поддержание актуальности test данных

3. **Изоляция тестов**
   - Тесты не должны зависеть друг от друга
   - Каждый тест должен cleanup
   - Временные файлы должны удаляться

4. **Mock внешних зависимостей**
   - Cloudscraper не всегда легко mock
   - Сетевые запросы должны быть mock
   - Файловая система может быть mock или использовать tmpdir

### Критерии Принятия

- [ ] tests/ директория создана
- [ ] conftest.py с базовыми fixtures
- [ ] requirements-dev.txt с pytest
- [ ] pytest запускается успешно
- [ ] Fixtures директория с test данными

---

## Задача 8.2: Unit Тесты - Модуль Constants

### Цель
Написать unit тесты для модуля constants.py.

### Детали Реализации

1. **tests/test_constants.py**

2. **Тест XML_NAMESPACE**
   - Проверить что это dict
   - Проверить наличие ключа 'sm'
   - Проверить правильность URI
   - Проверить неизменяемость (warning если изменён)

3. **Тест USER_AGENTS**
   - Проверить что это list
   - Проверить наличие минимум 2 элементов
   - Проверить что все элементы строки
   - Проверить отсутствие пустых строк

4. **Тест DEFAULT_MAX_WORKERS**
   - Проверить что это int
   - Проверить что > 0
   - Проверить разумное значение (не слишком большое)

5. **Тест логирующих констант**
   - DEFAULT_LOG_FILE существует
   - DEFAULT_LOG_FORMAT содержит нужные placeholders
   - DEFAULT_LOG_LEVEL валиден

### Сценарии Тестирования

1. **Тест импорта всех констант**
   - from sitemap_extract.constants import *
   - Все ожидаемые имена доступны

2. **Тест типов**
   - Каждая константа правильного типа
   - Нет None значений

3. **Тест значений**
   - Значения соответствуют спецификации
   - Namespace URI корректен

### Потенциальные Проблемы

1. **Изменяемые константы**
   - LIST и DICT могут быть изменены
   - Тест может изменить глобальное состояние
   - Использовать deepcopy для сравнений

2. **Зависимость от order**
   - USER_AGENTS порядок не гарантирован
   - Не тестировать конкретные индексы

### Критерии Принятия

- [ ] test_constants.py создан
- [ ] Все константы проверены
- [ ] Тесты проходят
- [ ] Coverage 100% для constants.py

---

## Задача 8.3: Unit Тесты - Модуль Network

### Цель
Написать unit тесты для модуля network.py с mock сетевых запросов.

### Детали Реализации

1. **tests/test_network.py**

2. **Тест create_scraper**
   - Mock cloudscraper.create_scraper
   - Проверить вызов с правильными параметрами
   - Тест с use_cloudscraper=True
   - Тест с use_cloudscraper=False
   - Тест с use_proxy=True
   - Тест конфигурации proxies

3. **Тест get_random_user_agent**
   - Проверить что возвращается строка
   - Проверить что результат в USER_AGENTS
   - Многократный вызов даёт разные результаты (вероятностно)

4. **Тест fetch_xml**
   - Mock scraper.get()
   - Mock response с валидным XML
   - Проверить парсинг в ET.Element
   - Тест с невалидным XML
   - Тест с HTTP ошибкой
   - Тест с сетевой ошибкой
   - Проверить логирование

5. **Тест decompress_gz**
   - Mock scraper.get() с stream=True
   - Mock response.raw с gzip данными
   - Проверить декомпрессию
   - Проверить парсинг
   - Тест с невалидным gzip
   - Тест с HTTP ошибкой

### Сценарии Тестирования

1. **Тест с pytest-mock**
   - Использовать mocker fixture
   - Mock всех внешних зависимостей
   - Изоляция от сети

2. **Тест с responses библиотекой**
   - Mock HTTP запросов на уровне requests
   - Определить mock ответы
   - Проверить actual HTTP calls

3. **Тест установки User-Agent**
   - Mock scraper
   - Вызвать fetch_xml
   - Проверить что headers['User-Agent'] установлен
   - Проверить значение

### Потенциальные Проблемы

1. **Mock Cloudscraper сложен**
   - Cloudscraper имеет нестандартный API
   - Может требовать специфичного mocking
   - Тестировать интерфейс, не детали

2. **Mock gzip.open**
   - Требует mock file-like объекта
   - BytesIO может помочь
   - Сложная цепочка mocks

3. **Async поведение**
   - requests может иметь async поведение
   - Mock должен имитировать это

4. **XML парсинг errors**
   - ET.fromstring может поднимать разные исключения
   - Mock должен покрывать все случаи

### Критерии Принятия

- [ ] test_network.py создан
- [ ] Все функции покрыты тестами
- [ ] Mock сетевых запросов
- [ ] Тесты ошибок
- [ ] Тесты проходят
- [ ] Coverage >90%

---

## Задача 8.4: Unit Тесты - Модуль Parser

### Цель
Написать unit тесты для parser.py с использованием test XML данных.

### Детали Реализации

1. **tests/test_parser.py**

2. **Создание test XML fixtures**
   - tests/fixtures/sitemap_index.xml - с <sitemap> элементами
   - tests/fixtures/sitemap_urls.xml - с <url> элементами
   - tests/fixtures/empty_sitemap.xml - пустой
   - tests/fixtures/invalid_sitemap.xml - невалидный XML

3. **Тест extract_sitemap_urls**
   - Загрузить test XML с 3 sitemap
   - Проверить возврат списка из 3 URL
   - Тест с пустым XML
   - Тест с отсутствующим namespace
   - Тест с пустыми <loc>

4. **Тест extract_page_urls**
   - Загрузить test XML с 10 URL
   - Проверить возврат списка из 10 URL
   - Проверить игнорирование <lastmod> и др.
   - Тест с большим количеством URL (1000+)

5. **Тест process_sitemap**
   - Mock fetch_xml
   - Mock decompress_gz
   - Mock save_urls
   - Тест с is_compressed=True и False
   - Проверить вызовы правильных функций
   - Проверить возвращаемый кортеж

### Сценарии Тестирования

1. **Тест с реальными XML файлами**
   - Не mock парсинга
   - Использовать реальные test XML
   - Проверить корректность извлечения

2. **Тест с различными namespace**
   - XML без namespace
   - XML с другим namespace
   - XML с множественными namespaces

3. **Тест производительности парсинга**
   - XML с тысячами элементов
   - Время парсинга должно быть разумным
   - Память не должна расти линейно

### Потенциальные Проблемы

1. **XML fixtures валидность**
   - Тестовые XML должны быть well-formed
   - Соответствовать sitemap schema
   - Покрывать различные edge cases

2. **Namespace handling**
   - ElementTree ограниченная XPath
   - Может не работать одинаково с lxml
   - Тестировать именно ElementTree

3. **Большие XML**
   - Fixtures не должны быть огромными
   - Но должны тестировать масштабируемость
   - Генерация на лету vs статичные файлы

### Критерии Принятия

- [ ] test_parser.py создан
- [ ] XML fixtures созданы
- [ ] Все функции покрыты
- [ ] Тесты с валидным и невалидным XML
- [ ] Тесты проходят
- [ ] Coverage >90%

---

## Задача 8.5: Unit Тесты - Модуль File Operations

### Цель
Написать unit тесты для file_operations.py с использованием временных файлов.

### Детали Реализации

1. **tests/test_file_operations.py**

2. **Использование tmpdir fixture**
   - pytest tmpdir для временных файлов
   - Автоматический cleanup

3. **Тест generate_filename**
   - Различные форматы URL
   - Проверить корректность алгоритма
   - Тест с .xml
   - Тест с .xml.gz
   - Тест с необычными URL

4. **Тест save_urls**
   - Создать временный файл
   - Проверить формат файла
   - Проверить содержимое
   - Тест с пустым списком
   - Тест с большим списком
   - Тест ошибок записи (mock)

5. **Тест read_urls_from_file**
   - Создать test файл с URL
   - Проверить чтение
   - Тест с пустыми строками
   - Тест с whitespace
   - Тест с несуществующим файлом
   - Тест с недоступным файлом (mock)

6. **Тест find_xml_files_in_directory**
   - Создать временную директорию
   - Создать test .xml и .xml.gz файлы
   - Проверить нахождение всех
   - Тест с пустой директорией
   - Тест с несуществующей директорией

### Сценарии Тестирования

1. **Тест с реальной файловой системой**
   - Использовать tmpdir
   - Реальные файловые операции
   - Не mock ОС

2. **Тест изоляции**
   - Каждый тест независим
   - Cleanup гарантирован
   - Нет side effects

3. **Тест конкурентности**
   - Множественные тесты одновременно
   - Нет конфликтов tmpdir

### Потенциальные Проблемы

1. **Права доступа**
   - Тесты могут упасть из-за прав
   - tmpdir обычно имеет полные права
   - Windows vs Linux различия

2. **Кодировка файлов**
   - UTF-8 vs системная кодировка
   - Особенно на Windows
   - Явно указывать encoding

3. **Временные файлы cleanup**
   - pytest tmpdir автоматически очищает
   - Но может оставаться при сбое
   - Периодическая ручная очистка

4. **Производительность I/O**
   - Много файловых операций в тестах
   - Может быть медленно на HDD
   - SSD или tmpfs быстрее

### Критерии Принятия

- [ ] test_file_operations.py создан
- [ ] Использование tmpdir
- [ ] Все функции покрыты
- [ ] Тесты с ошибками
- [ ] Тесты проходят
- [ ] Coverage >90%

---

## Задача 8.6: Unit Тесты - Модуль Orchestrator

### Цель
Написать unit тесты для orchestrator.py с mock всех зависимостей.

### Детали Реализации

1. **tests/test_orchestrator.py**

2. **Тест process_all_sitemaps - базовый**
   - Mock process_sitemap
   - Один URL в start_urls
   - Проверить вызов process_sitemap
   - Проверить возвращаемые множества

3. **Тест с множественными URL**
   - start_urls = [url1, url2, url3]
   - Mock process_sitemap для каждого
   - Проверить все вызваны

4. **Тест с вложенными sitemap**
   - Mock process_sitemap возвращает вложенные URL
   - Проверить добавление в очередь
   - Проверить вызов для вложенных

5. **Тест предотвращения циклов**
   - Mock process_sitemap с циклическими ссылками
   - A -> B, B -> A
   - Проверить обработка только один раз

6. **Тест многопоточности**
   - Mock process_sitemap с задержкой
   - Проверить параллельное выполнение
   - Проверить max 5 одновременных

7. **Тест обработки ошибок**
   - Mock process_sitemap raising Exception
   - Проверить graceful handling
   - Проверить продолжение обработки

8. **Тест сохранения индекса**
   - Mock save_urls
   - Проверить вызов для sitemap_index
   - Проверить параметры

### Сценарии Тестирования

1. **Тест с pytest-mock**
   - Mock ThreadPoolExecutor если нужно
   - Mock process_sitemap
   - Mock save_urls

2. **Тест фактической многопоточности**
   - Не mock ThreadPoolExecutor
   - Использовать real executor
   - Проверить параллелизм

3. **Integration-like тест**
   - Minimal mocking
   - Real executor
   - Mock только сетевые вызовы

### Потенциальные Проблемы

1. **Mock многопоточности сложен**
   - ThreadPoolExecutor трудно mock
   - Может быть проще тестировать с real executor
   - Mock только process_sitemap

2. **Timing issues**
   - Тесты многопоточности могут быть flaky
   - Race conditions в тестах
   - Использовать разумные задержки

3. **Проверка параллелизма**
   - Трудно проверить что задачи выполняются параллельно
   - Использовать timestamps
   - Проверять общее время выполнения

4. **Mock state**
   - Множественные вызовы mock с разными результатами
   - Использовать side_effect
   - Отслеживать состояние между вызовами

### Критерии Принятия

- [ ] test_orchestrator.py создан
- [ ] Тесты базовой функциональности
- [ ] Тесты вложенности
- [ ] Тесты циклов
- [ ] Тесты многопоточности
- [ ] Тесты ошибок
- [ ] Тесты проходят
- [ ] Coverage >85%

---

## Задача 8.7: Unit Тесты - Модуль CLI

### Цель
Написать unit тесты для cli.py, mock всех I/O операций.

### Детали Реализации

1. **tests/test_cli.py**

2. **Тест ArgumentParser**
   - Тест парсинга каждого аргумента
   - Тест дефолтных значений
   - Тест валидации

3. **Тест validate_and_collect_urls**
   - Mock read_urls_from_file
   - Mock find_xml_files_in_directory
   - Тест с каждым источником отдельно
   - Тест с комбинацией источников
   - Тест без источников (должен exit)

4. **Тест main функции**
   - Mock всех зависимостей
   - Mock setup_logging
   - Mock process_all_sitemaps
   - Mock sys.argv для аргументов
   - Проверить вызовы в правильном порядке
   - Проверить логирование

5. **Тест обработки KeyboardInterrupt**
   - Mock process_all_sitemaps raising KeyboardInterrupt
   - Проверить graceful exit

6. **Тест обработки исключений**
   - Mock raising Exception
   - Проверить логирование
   - Проверить exit code

### Сценарии Тестирования

1. **Тест с monkeypatch**
   - pytest monkeypatch для sys.argv
   - Установить test аргументы
   - Проверить парсинг

2. **Тест с capsys**
   - Захватить stdout/stderr
   - Проверить вывод справки
   - Проверить error сообщения

3. **Integration тест main**
   - Minimal mocking
   - Real ArgumentParser
   - Mock только external calls

### Потенциальные Проблемы

1. **sys.argv manipulation**
   - Глобальное состояние
   - Может влиять на другие тесты
   - Использовать monkeypatch для изоляции

2. **sys.exit в тестах**
   - sys.exit поднимает SystemExit
   - Тест должен catch
   - pytest.raises(SystemExit)

3. **Logging в тестах**
   - Логи могут засорять test output
   - Использовать caplog fixture
   - Или mock logger

4. **Порядок mock**
   - Важен порядок setup/teardown
   - Использовать fixtures правильно

### Критерии Принятия

- [ ] test_cli.py создан
- [ ] Тесты ArgumentParser
- [ ] Тесты валидации
- [ ] Тесты main функции
- [ ] Тесты error handling
- [ ] Тесты проходят
- [ ] Coverage >85%

---

## Задача 8.8: Integration Тесты

### Цель
Написать end-to-end integration тесты с minimal mocking.

### Детали Реализации

1. **tests/test_integration.py**

2. **Тест полного цикла**
   - Создать test sitemap XML файлы
   - Создать test sitemap index
   - Mock только HTTP запросы (responses)
   - Запустить через CLI
   - Проверить созданные файлы
   - Проверить содержимое
   - Проверить логи

3. **Тест с вложенными sitemap**
   - Создать иерархию test XML
   - 2-3 уровня вложенности
   - Mock HTTP для каждого уровня
   - Проверить обработку всех уровней

4. **Тест с .gz файлами**
   - Создать test .xml.gz
   - Mock HTTP с gzip content
   - Проверить декомпрессию и обработку

5. **Тест всех CLI опций**
   - Тест с --url
   - Тест с --file
   - Тест с --directory
   - Тест с --no-cloudscraper
   - Тест с --proxy

6. **Тест с реальными данными (опционально)**
   - Использовать публичный test sitemap
   - Реальные HTTP запросы
   - Маркировать как slow test

### Сценарии Тестирования

1. **Тест с responses библиотекой**
   - Mock HTTP на уровне requests
   - Определить mock для каждого URL
   - Simulate real server

2. **Тест с pytest.mark.integration**
   - Маркировать integration тесты
   - Возможность запуска отдельно
   - pytest -m integration

3. **Тест в изолированной директории**
   - tmpdir для всех файлов
   - Нет pollution основной директории
   - Автоматический cleanup

### Потенциальные Проблемы

1. **Медленные тесты**
   - Integration тесты медленнее unit
   - Могут занимать секунды/минуты
   - Запускать реже или отдельно

2. **Сложность setup**
   - Много test данных
   - Сложная структура mocks
   - Документировать setup

3. **Flaky тесты**
   - Зависимость от timing
   - Зависимость от ресурсов системы
   - Retries для flaky тестов

4. **Cleanup**
   - Integration тесты создают много файлов
   - Логи, выходные файлы
   - Гарантировать cleanup

### Критерии Принятия

- [ ] test_integration.py создан
- [ ] End-to-end тесты
- [ ] Тесты вложенности
- [ ] Тесты всех CLI опций
- [ ] Mock минимален
- [ ] Тесты проходят
- [ ] Время выполнения разумно

---

## Задача 8.9: Performance и Stress Тесты

### Цель
Написать тесты производительности и стресс-тесты для выявления узких мест.

### Детали Реализации

1. **tests/test_performance.py**

2. **Benchmark парсинга**
   - Создать XML с 10,000 URL
   - Измерить время парсинга
   - Должно быть < 1 секунды
   - Использовать pytest-benchmark

3. **Benchmark многопоточности**
   - 100 URL для обработки
   - Mock process_sitemap с задержкой
   - Измерить общее время
   - Должно быть ~5x быстрее последовательного

4. **Stress тест с большими данными**
   - 50,000 URL в sitemap
   - Проверить использование памяти
   - Не должно превышать разумный лимит
   - Использовать memory_profiler

5. **Stress тест глубокой вложенности**
   - 10 уровней вложенных sitemap
   - Проверить отсутствие stack overflow
   - Проверить производительность

6. **Concurrent requests тест**
   - Симуляция 5 одновременных запросов
   - Проверить thread-safety
   - Проверить отсутствие race conditions

### Сценарии Тестирования

1. **Тест с pytest-benchmark**
   - benchmark fixture
   - Измерение времени выполнения
   - Сравнение с baseline

2. **Тест с memory_profiler**
   - @profile декоратор
   - Измерение peak memory
   - Проверка на утечки

3. **Тест маркированные как slow**
   - pytest.mark.slow
   - Не запускаются по умолчанию
   - pytest -m slow для запуска

### Потенциальные Проблемы

1. **Вариативность результатов**
   - Производительность зависит от системы
   - Нагрузка CPU влияет
   - Использовать percentiles, не absolute values

2. **Долгие тесты**
   - Stress тесты могут занимать минуты
   - Не запускать на каждый commit
   - CI/CD pipeline для периодического запуска

3. **Недетерминизм**
   - Timing тесты могут быть flaky
   - Многопоточность добавляет вариативность
   - Разумные tolerances

4. **Resource exhaustion**
   - Stress тесты могут исчерпать ресурсы
   - Особенно на CI серверах
   - Limits на размер test данных

### Критерии Принятия

- [ ] test_performance.py создан
- [ ] Benchmark тесты
- [ ] Stress тесты
- [ ] Memory тесты
- [ ] Concurrency тесты
- [ ] Маркированы как slow
- [ ] Документированы thresholds

---

## Задача 8.10: Test Coverage и Отчётность

### Цель
Обеспечить высокое test coverage и настроить отчёты.

### Детали Реализации

1. **Настройка pytest-cov**
   - Конфигурация в pytest.ini или setup.cfg
   - Указать source=sitemap_extract
   - Исключить tests/ из coverage

2. **Генерация отчётов**
   - pytest --cov=sitemap_extract --cov-report=html
   - pytest --cov=sitemap_extract --cov-report=term
   - HTML отчёт в htmlcov/

3. **Цели coverage**
   - Общий coverage >85%
   - Critical модули >90%
   - CLI может быть ниже

4. **Идентификация пробелов**
   - Uncovered lines
   - Uncovered branches
   - Приоритизация покрытия

5. **Coverage badges**
   - Генерация badge для README
   - Интеграция с CI

6. **Документация coverage**
   - Объяснить низкий coverage в некоторых местах
   - Обосновать непокрытые ветки

### Сценарии Тестирования

1. **Тест минимального coverage**
   - pytest --cov --cov-fail-under=85
   - Должен упасть если < 85%

2. **Тест HTML отчёта**
   - Отчёт генерируется
   - Открывается в браузере
   - Показывает uncovered lines

### Потенциальные Проблемы

1. **Ложно высокий coverage**
   - 100% line coverage != полное тестирование
   - Branch coverage важнее
   - Mutation testing для качества

2. **Недостижимый код**
   - Некоторый код может быть недостижим
   - Defensive programming
   - Исключить из coverage

3. **Coverage в CI/CD**
   - Интеграция с GitHub Actions/Travis
   - Upload в Codecov/Coveralls
   - Автоматические отчёты

### Критерии Принятия

- [ ] pytest-cov настроен
- [ ] Coverage >85% достигнут
- [ ] HTML отчёт генерируется
- [ ] Пробелы coverage идентифицированы
- [ ] План по улучшению coverage

---

## Сводка Фазы 4

### Что Достигнуто

После завершения Фазы 4:

1. **Тестовая инфраструктура**
   - pytest настроен
   - fixtures созданы
   - requirements-dev.txt

2. **Unit тесты для всех модулей**
   - constants
   - network
   - parser
   - file_operations
   - orchestrator
   - cli

3. **Integration тесты**
   - End-to-end сценарии
   - Минимальный mocking
   - Реальные файловые операции

4. **Performance и Stress тесты**
   - Benchmark тесты
   - Memory тесты
   - Concurrency тесты

5. **High test coverage**
   - >85% общий coverage
   - >90% для core модулей
   - Coverage отчёты

### Обнаруженные Проблемы

Во время тестирования могут быть обнаружены:

1. **Баги в обработке ошибок**
   - Edge cases не обработаны
   - Неправильные exceptions
   - Потеря данных

2. **Performance issues**
   - Медленный парсинг
   - Утечки памяти
   - Неоптимальные алгоритмы

3. **Concurrency bugs**
   - Race conditions
   - Deadlocks
   - Неправильная синхронизация

4. **Compatibility issues**
   - Проблемы на разных ОС
   - Проблемы с разными версиями Python
   - Проблемы с зависимостями

### Следующая Фаза

Фаза 5 фокусируется на упаковке, документации и релизе.

### Рекомендации

1. **Continuous testing**
   - Запускать тесты на каждый commit
   - Pre-commit hooks
   - CI/CD integration

2. **Test-driven development**
   - Писать тесты перед кодом (когда возможно)
   - Red-Green-Refactor цикл

3. **Regression testing**
   - Каждый bug fix = новый тест
   - Предотвращение повторения багов

4. **Regular coverage review**
   - Еженедельный review coverage
   - Цель постепенного улучшения
