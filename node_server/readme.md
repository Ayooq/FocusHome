## обработка сообщений от mosquito

```python
cd /var/www/focus/node_server
forever start server.js # запуск
forever stop server.js # остановка
forever restart server.js # перезапуск
```

### логи
```sql
SELECT id, created, user_id, device_id, topic, payload, source, result_code, result_message
FROM focus.broker_dispatcher_log
```