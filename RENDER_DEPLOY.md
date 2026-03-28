# BrainForge on Render

## 1. Prepare the project

Render backend entry point:

```bash
python render_app.py
```

Important files:

- `render_app.py`: Flask API + reminder monitor
- `requirements.txt`: Render install dependencies
- `.env.example`: required environment variables
- `render.yaml`: optional Render Blueprint file

## 2. Create the Render service

1. Push this project to GitHub.
2. In Render, click `New +`.
3. Choose `Web Service`.
4. Connect the repository.
5. Use these settings:

```text
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: python render_app.py
```

## 3. Set environment variables

Set these in Render:

```text
DISCORD_WEBHOOK_URL=your existing Discord webhook URL
DATABASE_PATH=/var/data/engineer_hub.db
REMINDER_POLL_INTERVAL_SECONDS=30
```

If you want the desktop app to connect to Render reminders API:

```text
BRAINFORGE_API_BASE_URL=https://your-service-name.onrender.com
```

## 4. Persistent database

If reminders must survive redeploys/restarts, attach a Render Disk and mount it at:

```text
/var/data
```

Then keep:

```text
DATABASE_PATH=/var/data/engineer_hub.db
```

Without a persistent disk, SQLite data may be lost on redeploy.

## 5. Test Discord webhook

After deploy, test with:

```bash
curl -X POST https://your-service-name.onrender.com/test-discord
```

You can also open:

```text
https://your-service-name.onrender.com/test-discord
```

Expected success response:

```json
{"ok": true, "message": "Discord test message sent."}
```

## 6. Reminder API examples

List reminders:

```bash
curl https://your-service-name.onrender.com/api/reminders
```

Create reminder:

```bash
curl -X POST https://your-service-name.onrender.com/api/reminders ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Demo\",\"category\":\"Work\",\"description\":\"Render test\",\"due_at\":\"2026-03-28 18:00:00\",\"priority\":1,\"status\":\"pending\"}"
```

Search reminders:

```bash
curl "https://your-service-name.onrender.com/api/reminders?q=Demo"
```

## 7. Desktop app cloud mode

If the desktop app should read reminders from Render instead of local SQLite, set:

```text
BRAINFORGE_API_BASE_URL=https://your-service-name.onrender.com
```

Then start the desktop app normally:

```bash
python main.py
```

In this mode:

- reminder CRUD uses the cloud API
- `/test-discord` is called through the Render backend
- Discord webhook itself stays on the server as `DISCORD_WEBHOOK_URL`
