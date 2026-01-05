# Otomasyon CRM — Backend

FastAPI tabanlı RESTful API servisi.

## 🛠️ Kurulum

```bash
# 1. Virtual environment oluştur
python -m venv venv

# 2. Aktive et
venv\Scripts\activate      # Windows
# source venv/bin/activate # Linux/Mac

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Ortam değişkenlerini ayarla
copy .env.example .env
```

## 🗄️ Veritabanı

**SQLite ile hızlı başlangıç:**
```bash
python scripts/init_db.py --test --seed
```

Bu komut:
- Tüm tabloları oluşturur
- Admin kullanıcısı ekler: `admin@otomasyon.com` / `admin123`

## 🚀 Sunucuyu Başlatma

```bash
python -m uvicorn app.main:app --reload
```

API şu adreste çalışacaktır: `http://localhost:8000`

**Swagger UI:** `http://localhost:8000/docs`

## 📂 Proje Yapısı

```
backend/
├── app/
│   ├── models/         # SQLAlchemy modelleri
│   ├── schemas/        # Pydantic şemaları
│   ├── routers/        # API endpoint'leri
│   ├── services/       # İş mantığı
│   ├── integrations/   # Harici API'ler (TCMB, e-Fatura)
│   └── utils/          # Yardımcı fonksiyonlar
├── scripts/            # Veritabanı ve yardımcı scriptler
└── tests/              # Pytest ünit testleri
```

## 🔑 Ortam Değişkenleri

| Değişken | Açıklama | Varsayılan |
|----------|----------|------------|
| `ENVIRONMENT` | development / testing / production | development |
| `DATABASE_URL` | PostgreSQL bağlantı URL'i | - |
| `TEST_DATABASE_URL` | SQLite test veritabanı | sqlite:///./test_otomasyon.db |
| `SECRET_KEY` | JWT şifreleme anahtarı | - |
