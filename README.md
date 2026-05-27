# Sheet Master Backend

FastAPI приложение для оптимизации раскроя листового материала.

## Деплой на Netlify

### Способ 1: Через Netlify Dashboard (рекомендуется)

1. **Подготовьте репозиторий**
   - Убедитесь, что все файлы закоммичены и запушены в GitHub/GitLab/Bitbucket

2. **Подключите репозиторий к Netlify**
   - Зайдите на [app.netlify.com](https://app.netlify.com)
   - Нажмите "Add new site" → "Import an existing project"
   - Выберите ваш репозиторий

3. **Настройте деплой**
   - **Build command**: оставьте пустым или `echo 'No build step required'`
   - **Publish directory**: оставьте пустым
   - **Functions directory**: `netlify/functions`
   - **Python version**: Netlify автоматически определит из `runtime.txt`

4. **Деплой**
   - Нажмите "Deploy site"
   - Дождитесь завершения деплоя

### Способ 2: Через Netlify CLI

1. **Установите Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Войдите в Netlify**
   ```bash
   netlify login
   ```

3. **Инициализируйте сайт**
   ```bash
   netlify init
   ```
   Следуйте инструкциям для подключения к существующему сайту или создания нового.

4. **Задеплойте**
   ```bash
   netlify deploy --prod
   ```

## Использование API

После деплоя ваше API будет доступно по адресу:
- `https://your-site-name.netlify.app/` - проверка статуса
- `https://your-site-name.netlify.app/optimize` - оптимизация раскроя

### Пример запроса

```bash
curl -X POST https://your-site-name.netlify.app/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "sheet": {"width": 1000, "height": 500},
    "parts": [
      {"points": [[0, 0], [200, 0], [200, 100], [0, 100]]},
      {"points": [[0, 0], [300, 0], [300, 200], [0, 200]]}
    ]
  }'
```

## Локальная разработка

1. **Установите зависимости**
   ```bash
   pip install -r requirements.txt
   ```

2. **Запустите сервер**
   ```bash
   uvicorn main:app --reload
   ```

3. **Откройте в браузере**
   - API: http://localhost:8000
   - Документация: http://localhost:8000/docs

## Структура проекта

```
.
├── main.py                 # FastAPI приложение
├── backend/
│   ├── __init__.py
│   └── algorithm.py       # Алгоритм оптимизации раскроя
├── netlify/
│   └── functions/
│       └── api.py         # Netlify Function handler
├── netlify.toml           # Конфигурация Netlify
├── requirements.txt       # Python зависимости
└── runtime.txt           # Версия Python для Netlify
```

## Примечания

- Netlify Functions имеют ограничение на время выполнения (10 секунд для бесплатного плана)
- Для больших вычислений рассмотрите использование Netlify Background Functions
- Все зависимости должны быть указаны в `requirements.txt`

