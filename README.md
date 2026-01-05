# Otomasyon CRM

Proje Odaklı CRM, Sanal Depo ve Finansal Entegrasyon Modülü

## Kurulum

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # Ayarları düzenle
python -m uvicorn app.main:app --reload
```

### Frontend

Frontend statik HTML/CSS/JS dosyalarından oluşmaktadır. Herhangi bir HTTP server ile çalıştırılabilir:

```bash
cd frontend
python -m http.server 3000
```

## Proje Yapısı

```
betsan/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy modelleri
│   │   ├── schemas/        # Pydantic şemaları
│   │   ├── routers/        # API endpoint'leri
│   │   ├── services/       # İş mantığı
│   │   ├── integrations/   # Harici API'ler (TCMB, e-Fatura)
│   │   └── utils/          # Yardımcı fonksiyonlar
│   ├── alembic/            # Veritabanı migration'ları
│   └── tests/              # Test dosyaları
│
└── frontend/
    ├── css/                # Stil dosyaları
    ├── js/                 # JavaScript dosyaları
    ├── pages/              # HTML sayfaları
    └── assets/             # Görseller, ikonlar
```

## Teknolojiler

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Auth:** JWT
- **PDF:** ReportLab
- **Barkod:** python-barcode, qrcode
