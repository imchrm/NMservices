# Документация NMservices

Добро пожаловать в документацию проекта NMservices. Здесь вы найдете всю необходимую информацию для работы над проектом.

---

## Быстрый старт

Новичок в проекте? Начните здесь:

1. **[Onboarding Guide](onboarding/ONBOARDING_GUIDE.md)** - Полное руководство для нового разработчика
2. **[Quick Start Deploy](onboarding/QUICKSTART_DEPLOY.md)** - Быстрый деплой проекта

---

## Разработка

### Git Workflow

- **[Git Workflow Guide](git/GIT_WORKFLOW_GUIDE.md)** - Полное руководство по работе с Git
- **[Merge Guide](git/MERGE_GUIDE.md)** - Детальное руководство по мерджу веток
- **[Quick Merge](git/QUICK_MERGE.md)** - Быстрая инструкция по мерджу
- **[PR Description](git/PR_DESCRIPTION.md)** - Как правильно оформлять Pull Request

### Процесс разработки

- **[Database Setup](development/DATABASE_SETUP.md)** - Настройка базы данных
- **[Refactoring Guide](development/REFACTORING.md)** - Руководство по рефакторингу
- **[Testing Guide](development/TESTING.md)** - Тестирование проекта
- **[DB Testing](development/DB_TESTING.md)** - Тестирование базы данных
- **[Network Testing](development/NETWORK_TESTING.md)** - Тестирование сети
- **[Troubleshooting DB](development/TROUBLESHOOTING_DB.md)** - Устранение неполадок БД

### Admin API

- **[Admin API](admin/ADMIN_API.md)** - Полная документация Admin API
- **[Quickstart Admin](admin/QUICKSTART_ADMIN.md)** - Быстрый старт с Admin API
- **[CORS Setup](admin/CORS_SETUP_SUMMARY.md)** - Настройка CORS

---

## Деплой и эксплуатация

- **[Deployment Guide](deployment/DEPLOYMENT.md)** - Инструкции по деплою в продакшн
- **[Local Deployment](deployment/DEPLOYMENT_LOCAL.md)** - Локальный деплой
- **[PostgreSQL Deployment](deployment/postgresql-deployment.md)** - Деплой PostgreSQL

---

## Структура документации

```
docs/
├── README.md                          # Этот файл (индекс документации)
│
├── onboarding/                        # Для новых разработчиков
│   ├── ONBOARDING_GUIDE.md            # Полное руководство для новичков
│   └── QUICKSTART_DEPLOY.md           # Быстрый старт
│
├── git/                               # Git workflow
│   ├── GIT_WORKFLOW_GUIDE.md          # Полное руководство по Git
│   ├── MERGE_GUIDE.md                 # Детальный гайд по мерджу
│   ├── QUICK_MERGE.md                 # Краткая инструкция
│   └── PR_DESCRIPTION.md              # Оформление Pull Request
│
├── admin/                             # Администрирование
│   ├── ADMIN_API.md                   # API документация
│   └── QUICKSTART_ADMIN.md            # Быстрый старт
│
├── development/                       # Процесс разработки
│   ├── DATABASE_SETUP.md              # Настройка БД
│   ├── REFACTORING.md                 # Рефакторинг
│   ├── TESTING.md                     # Тестирование
│   └── TROUBLESHOOTING_DB.md          # Отладка БД
│
├── deployment/                        # Деплой
│   ├── DEPLOYMENT.md                  # Инструкции по деплою
│   ├── DEPLOYMENT_LOCAL.md            # Локальный запуск
│   └── postgresql-deployment.md       # Настройка PG
│
└── archive/                           # Устаревшие документы
    ├── DOCS_INDEX.md                  # Старый индекс
    ├── SUMMARY.md                     # Старое резюме
    └── Separate Bot & Service Project.md
```

---

## Частые вопросы

### Как начать работу над проектом?

1. Прочитайте [Onboarding Guide](onboarding/ONBOARDING_GUIDE.md)
2. Настройте окружение по [Quick Start Deploy](onboarding/QUICKSTART_DEPLOY.md)
3. Изучите [Git Workflow](git/GIT_WORKFLOW_GUIDE.md)

### Как создать Pull Request?

См. [PR Description Guide](git/PR_DESCRIPTION.md)

### Как задеплоить проект?

См. [Deployment Guide](deployment/DEPLOYMENT.md)

### Как запустить тесты?

См. [Testing Guide](development/TESTING.md) или используйте:

```bash
# Linux/Mac
./scripts/test_api.sh

# Windows PowerShell
.\scripts\test_api.ps1
```

---

## Поиск информации

Используйте поиск GitHub для быстрого нахождения информации:

```
# В поисковой строке GitHub
repo:imchrm/NMservices path:docs/ <ваш запрос>
```

Или используйте grep локально:

```bash
# Поиск по всем документам
grep -r "ключевое слово" docs/

# Поиск только в markdown файлах
find docs/ -name "*.md" -exec grep -l "ключевое слово" {} \;
```

---

## Обновление документации

Документация должна обновляться вместе с кодом:

1. При изменении функциональности - обновите соответствующие документы
2. Pull Request с изменениями кода должен включать обновление документации
3. Следуйте формату Markdown и структуре существующих документов
4. Добавляйте новые документы в соответствующие разделы

---

## Архив

Устаревшие документы находятся в [archive/](archive/). Они сохранены для истории, но могут содержать неактуальную информацию.

---

## Контакты

Если не нашли ответ в документации:

1. Проверьте [Issues на GitHub](https://github.com/imchrm/NMservices/issues)
2. Спросите в командном чате
3. Создайте новый Issue с тегом `documentation`

---

**Последнее обновление:** 2025-12-12
