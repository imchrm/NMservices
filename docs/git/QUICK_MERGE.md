# Быстрая инструкция по merge ветки `strange-lederberg`

## 🚀 Быстрый старт (рекомендуется)

### 1. Пуш на GitHub
```bash
cd C:\Users\zum\.claude-worktrees\NMservices\strange-lederberg
git push origin strange-lederberg
```

### 2. Создайте Pull Request
- Откройте https://github.com/imchrm/NMservices
- Нажмите "Compare & pull request"
- Заполните описание (можно скопировать из MERGE_GUIDE.md)
- Нажмите "Create pull request"

### 3. Смержите на GitHub
- Review изменений
- Нажмите "Merge pull request"
- Подтвердите

### 4. Обновите локальный main
```bash
cd C:/Users/zum/dev/python/NMservices
git checkout main
git pull origin main
```

### 5. Удалите worktree
```bash
git worktree remove C:\Users\zum\.claude-worktrees\NMservices\strange-lederberg
git branch -d strange-lederberg
```

## ✅ Готово!

---

## 📋 Чек-лист перед push

- [x] Все тесты проходят (6/6)
- [x] Working tree чистый
- [x] `.claude/` в .gitignore
- [x] `.env.example` добавлен
- [x] 3 коммита готовы

---

## 📖 Подробная инструкция

См. файл `MERGE_GUIDE.md` для:
- Детального описания изменений
- Альтернативных способов merge
- Инструкций по откату
- Troubleshooting

---

## 🆘 Быстрая помощь

**Проблема:** Конфликты при merge
```bash
git status  # посмотреть конфликты
# Разрешить конфликты вручную
git add <files>
git commit
```

**Проблема:** Тесты не проходят после merge
```bash
cd C:/Users/zum/dev/python/NMservices
poetry install
poetry run pytest -v
```

**Проблема:** Нужно откатить merge
```bash
git reset --hard HEAD~1  # если не запушено
git revert -m 1 <hash>   # если запушено
```
