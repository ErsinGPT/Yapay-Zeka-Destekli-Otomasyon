# Otomasyon CRM

Proje odaklı çalışan firmalar için geliştirilmiş geniş kapsamlı **CRM (Müşteri İlişkileri Yönetimi)**, **Sanal Depo** ve **Finansal Entegrasyon** modülüdür.

## 🚀 Özellikler

- **Müşteri ve Fırsat Yönetimi:** Satış süreçlerini ve potansiyel projeleri takip edin.
- **Proje Yönetimi:** Kazanılan projelerin üretim ve teslimat süreçlerini yönetin.
- **Stok & Depo Otomasyonu:** Barkod destekli stok takibi, depo transferleri ve rezervasyon sistemi.
- **Finans Modülü:** Fatura oluşturma (PDF), gelir/gider takibi ve TCMB döviz entegrasyonu.
- **Operasyon Dosyaları:** Teknik servis formları ve sevkiyat irsaliyeleri.

## 🛠️ Kurulum ve Çalıştırma

### 1. Backend Kurulumu (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
copy .env.example .env  # Ayarları ihtiyacınıza göre düzenleyin
```

**Veritabanı Başlatma (SQLite/SQLite):**
```bash
python scripts/init_db.py --test --seed
```
*Bu komut tabloları oluşturur ve `admin@otomasyon.com` (şifre: `admin123`) kullanıcısını tanımlar.*

**Sunucuyu Başlatma:**
```bash
python -m uvicorn app.main:app --reload
```

### 2. Frontend Çalıştırma (Vanilla JS)

Frontend tarafı herhangi bir derleme (build) işlemi gerektirmez. Basit bir HTTP sunucusu ile çalıştırılabilir:

**Python ile hızlı başlatma:**
```bash
cd frontend
python -m http.server 5500
```
Daha sonra tarayıcınızdan `http://localhost:5500` adresine giderek uygulamaya erişebilirsiniz.

---

## 📂 Proje Yapısı

```
Otomasyon CRM/
├── backend/            # FastAPI Backend
│   ├── app/            # Uygulama mantığı
│   ├── scripts/        # Veritabanı ve yardımcı scriptler
│   └── tests/          # Pytest ünit testleri
└── frontend/           # Statik Frontend
    ├── css/            # Modern CSS Tasarımları
    ├── js/             # Vanilla JS API Entegrasyonu
    └── pages/          # HTML Sayfa Şablonları
```

## 🏗️ Kullanılan Teknolojiler

- **Backend:** FastAPI, SQLAlchemy, Pydantic, SQLite/PostgreSQL
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Güvenlik:** JWT (JSON Web Token)
- **Raporlama:** ReportLab (PDF), python-barcode, qrcode
