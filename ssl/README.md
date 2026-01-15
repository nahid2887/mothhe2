# SSL Certificates Directory

Add your SSL certificates here:
- cert.pem: Your SSL certificate
- key.pem: Your private key

## Getting SSL Certificates

### Option 1: Let's Encrypt (Free, Recommended)
```bash
sudo certbot certonly --standalone -d app.preqly.com -d www.app.preqly.com
sudo cp /etc/letsencrypt/live/app.preqly.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.preqly.com/privkey.pem ssl/key.pem
```

### Option 2: Self-signed (Testing Only)
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365
```

### Option 3: Commercial Certificate
Place your cert.pem and key.pem files in this directory.
