# register.mahalaos.org — Deployment Notes

## Stack
- Python 3.11+
- Flask + flask-limiter
- SQLite (sufficient for thousands of devices; upgrade to Postgres if needed later)
- Nginx as reverse proxy (handles HTTPS via Let's Encrypt)

## Install

```bash
pip install flask flask-limiter gunicorn

# Run with gunicorn in production
gunicorn -w 2 -b 127.0.0.1:5000 registration_server:app
```

## Nginx config snippet

```nginx
server {
    server_name register.mahalaos.org;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Then: `certbot --nginx -d register.mahalaos.org`

## Database location
`/var/lib/mahalaos/registrations.db`

Only contains:
- device_id (SHA-256 hash — not reversible)
- first_seen / last_seen (UTC timestamps)
- reg_count (how many times this device has registered)

No IP addresses stored. No personal data. No device model or carrier info.

## Endpoints

| Endpoint       | Method | Auth | Description                        |
|----------------|--------|------|------------------------------------|
| /v1/device     | POST   | None | Register/update a device           |
| /v1/stats      | GET    | None | Returns total unique device count  |
| /health        | GET    | None | Health check                       |

## /v1/stats response
```json
{ "registered_devices": 142 }
```
Safe to expose publicly — useful for social proof on mahalaos.org.

## Rate limiting
5 POST requests per IP per hour — prevents trivial spam inflation.
Legitimate devices register once at setup; re-registration on reflash is fine.
