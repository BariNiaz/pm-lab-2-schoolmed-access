# SchoolMed Access

> Геоинформационный сервис для оценки доступности школ и поликлиник. Проект использует изохроны, чтобы оценивать территории, достижимые за заданное время, и выявлять районы с недостаточной доступностью социальных объектов.

**Вариант:** 2 Доступность школ и поликлиник (изохроны) · **Город / регион:** Уфа, Республика Башкортостан

<!-- С ЛР 4: значок автопроверки. Замените OWNER/REPO на свой репозиторий и уберите знаки комментария вокруг строки ниже.
![ci](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
-->

## Команда

| Участник | Роль в ЛР 1| GitHub |
|---|---|---|
| Нияз Бадриев | Менеджер проекта | @BariNiaz |
| Виктория Исаева | Аналитик предметной области / Технический организатор | @Intheclouds122 |
| Зайнуллин Тимур | Руководитель рисков и решений | @usifuwoj |



## Ссылки

- Доска проекта: <ссылка на GitHub Project>
- Устав проекта: [docs/charter.md](docs/charter.md)
- Риски и качество: [реестр рисков](docs/risk-register.md), [план качества](docs/quality-plan.md), [правила работы с репозиторием](CONTRIBUTING.md)
- План проекта: [оценки](docs/estimation.md), [календарный план](docs/schedule.md), [бюджет](docs/budget.md), [коммуникации](docs/communication-plan.md)
- Как сделать Pull Request в браузере: [docs/guides/pr-web-ui.md](docs/guides/pr-web-ui.md)
- Данные и реестр источников: [data/README.md](data/README.md), [data/sources.md](data/sources.md)
- Ноутбуки (запуск в Google Colab): [notebooks/README.md](notebooks/README.md)
- Журнал использования ИИ: [docs/ai-usage.md](docs/ai-usage.md)

## Структура репозитория

```
├── README.md
├── docs/
│   ├── team-agreement.md        командный договор
│   ├── business-case.md         проблема, ценность, альтернативы
│   ├── charter.md               устав проекта
│   ├── stakeholders.md          стейкхолдеры, матрица, RACI
│   ├── adr/                     записи о принятых решениях
│   ├── meetings/                протоколы и интервью
│   ├── ai-usage.md              журнал использования ИИ с инструкцией
│   ├── ai-logs/                 экспорт переписки с ИИ (по желанию)
│   ├── requirements.md          требования (ЛР 2)
│   ├── wbs.md                   иерархическая структура работ (ЛР 2)
│   ├── definition-of-done.md    DoR и DoD (ЛР 2)
│   ├── data-quality.md          отчёт о качестве данных (ЛР 2)
│   ├── estimation.md            оценки трудоёмкости (ЛР 3)
│   ├── schedule.md              сетевой график, Гант, ресурсы, спринты (ЛР 3)
│   ├── budget.md                бюджет, TCO и окупаемость (ЛР 3)
│   ├── communication-plan.md    план коммуникаций (ЛР 3)
│   ├── risk-register.md         реестр рисков, Монте-Карло, правовые риски (ЛР 4)
│   ├── quality-plan.md          план управления качеством (ЛР 4)
│   ├── img/, maps/              карты: статичные и интерактивные
│   ├── guides/                  инструкции (Pull Request в браузере)
│   └── tasks/                   тексты заданий лабораторных работ (ЛР 1–4)
├── data/
│   ├── README.md                как получить данные
│   ├── sources.md               реестр источников данных
│   ├── raw/                     сырые данные (не хранятся в Git)
│   ├── manual/                  таблицы, собранные вручную
│   ├── processed/               очищенные слои
│   └── validation.json          правила проверки слоёв (ЛР 4)
├── notebooks/                   сбор, профилирование и анализ данных, калькулятор плана, Монте-Карло
├── src/                         расчётные функции, проверяемые тестами (ЛР 4)
├── tests/                       автотесты pytest (ЛР 4)
├── scripts/validate_data.py     проверка слоёв по data/validation.json (ЛР 4)
├── CONTRIBUTING.md              правила работы с репозиторием (ЛР 4)
├── requirements.txt             зависимости Python для ноутбуков
├── requirements-dev.txt         инструменты проверки качества (ЛР 4)
├── pyproject.toml               настройки ruff и pytest (ЛР 4)
└── .github/
    ├── ISSUE_TEMPLATE/          шаблоны задач: задача, история, эпик, риск, проблема данных, ошибка
    ├── pull_request_template.md шаблон Pull Request
    ├── release.yml              категории автоматических заметок к релизу (ЛР 4)
    ├── scripts/bootstrap.sh     создание меток, этапов и стартовых задач
    └── workflows/               bootstrap, ci (автопроверка качества), lab1-check … lab4-check
```
