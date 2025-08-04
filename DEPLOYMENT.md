# Deployment and Secrets Management

This document describes how to deploy the PDF Sender Bot and manage secrets securely.

## Environment Variables

The application requires the following environment variables:

### Required
- `BOT_TOKEN`: Your Telegram bot token from @BotFather

### Optional (with defaults)
- `PAGES_PER_SEND`: Number of pages to send at once (default: 3)
- `INTERVAL_HOURS`: Hours between automatic sends (default: 6)
- `SCHEDULE_TIME`: Daily send time in HH:MM format (default: 09:00)
- `PDF_PATH`: Default PDF file path (default: book.pdf)
- `OUTPUT_DIR`: Directory for generated images (default: output)
- `UPLOAD_DIR`: Directory for uploaded PDFs (default: uploads)
- `DATABASE_PATH`: Path to JSON database file (default: database.json)

## Secrets Management

### Development
1. Copy `.env.example` to `.env`
2. Fill in your bot token and adjust settings
3. Never commit `.env` files to version control

### Production Deployment

#### GitHub Actions (for CI/CD)
Set secrets in your repository settings:
```
BOT_TOKEN=your_production_bot_token
```

#### Docker
```bash
# Using environment file
docker run --env-file .env your-image

# Using Docker secrets
echo "your_bot_token" | docker secret create bot_token -
docker service create --secret bot_token your-image
```

#### Kubernetes
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: pdf-sender-secrets
type: Opaque
stringData:
  BOT_TOKEN: your_bot_token
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pdf-sender
spec:
  template:
    spec:
      containers:
      - name: pdf-sender
        image: your-image
        envFrom:
        - secretRef:
            name: pdf-sender-secrets
```

#### Cloud Platforms

**Heroku:**
```bash
heroku config:set BOT_TOKEN=your_bot_token
```

**Railway:**
```bash
railway variables set BOT_TOKEN=your_bot_token
```

**Vercel:**
```bash
vercel env add BOT_TOKEN
```

## Security Best Practices

1. **Never hardcode secrets** in your application code
2. **Use different tokens** for development and production
3. **Rotate tokens regularly** - regenerate bot tokens periodically
4. **Limit token permissions** - only use bot tokens with necessary permissions
5. **Monitor token usage** - watch for unusual activity
6. **Use secrets management services** in production environments
7. **Enable 2FA** on accounts that have access to tokens

## Monitoring

Monitor your bot for:
- Unexpected API calls
- High error rates
- Unusual user activity
- Resource usage spikes

Set up alerts for production deployments to catch issues early.