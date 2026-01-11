# ⚡ Быстрый деплой на 12.34.56.78

## 🔑 Подключение

```bash
ssh -p 2251 username@12.34.56.78
```

## 📦 Установка (первый раз)

```bash
# 1. Установить Poetry (если нет)
curl -sSL https://install.python-poetry.org | python3 -
export PATH="$HOME/.local/bin:$PATH"

# 2. Клонировать проект
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/imchrm/NMservices.git
cd NMservices

# 3. Создать .env
cat > .env << 'EOF'
API_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
HOST=0.0.0.0
PORT=9800
ENVIRONMENT=production
EOF

# 4. Установить зависимости
poetry install --no-dev

# 5. Тесты
poetry run pytest -v
```

## 🚀 Запуск

### Вариант A: Быстрый старт (tmux)

```bash
# Терминал 1 - запуск
tmux new -s nms
cd ~/projects/NMservices
poetry run uvicorn nms.main:app --host 0.0.0.0 --port 9800
# Отключиться: Ctrl+B, затем D

# Терминал 2 - тесты
ssh -p 2251 username@12.34.56.78
curl http://localhost:9800/
```

### Вариант B: В фоне (nohup)

```bash
cd ~/projects/NMservices
nohup poetry run uvicorn nms.main:app --host 0.0.0.0 --port 9800 > ~/nms.log 2>&1 &
echo $! > ~/nms.pid

# Проверка
tail -f ~/nms.log
```

## ✅ Проверка

```bash
# Локально (на сервере)
curl http://localhost:9800/

# Удалённо (с вашей машины)
./scripts/test_api.sh --host 12.34.56.78 --port 9800 --key "your_key"
```

## 🛑 Остановка

```bash
# nohup
kill $(cat ~/nms.pid)

# tmux
tmux kill-session -t nms
```

## 🔄 Обновление

```bash
cd ~/projects/NMservices
kill $(cat ~/nms.pid)  # Остановить
git pull origin main   # Обновить
poetry install         # Установить зависимости
nohup poetry run uvicorn nms.main:app --host 0.0.0.0 --port 9800 > ~/nms.log 2>&1 &
echo $! > ~/nms.pid
```

## 📋 Полезные команды

```bash
# Статус порта
ss -tuln | grep 9800

# Процессы
ps aux | grep uvicorn

# Логи
tail -f ~/nms.log

# Повторное подключение к tmux
tmux attach -t nms
```

---

**См. DEPLOYMENT.md для подробностей**
