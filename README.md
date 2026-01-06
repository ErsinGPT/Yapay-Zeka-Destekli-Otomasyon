# Otomasyon CRM

Proje odaklı çalışan firmalar için geliştirilmiş geniş kapsamlı **CRM (Müşteri İlişkileri Yönetimi)**, **Sanal Depo** ve **Finansal Entegrasyon** modülüdür.

## 🚀 Özellikler

- **Müşteri ve Fırsat Yönetimi:** Satış süreçlerini ve potansiyel projeleri takip edin.
- **Proje Yönetimi:** Kazanılan projelerin üretim ve teslimat süreçlerini yönetin.
- **Stok & Depo Otomasyonu:** Barkod destekli stok takibi, depo transferleri ve rezervasyon sistemi.
- **Finans Modülü:** Fatura oluşturma (PDF), gelir/gider takibi ve TCMB döviz entegrasyonu.
- **Operasyon Dosyaları:** Teknik servis formları ve sevkiyat irsaliyeleri.

## 🔮 Gelecek Planları

### 🤖 Yapay Zeka Entegrasyonu
- **Akıllı Arama Barı:** Sayfadaki fonksiyonlar bulunamadığında yapay zeka tarafından otomatik yönlendirme yapılacak
- **Text-to-SQL Raporlama:** Raporlar sayfasındaki arama barı üzerinden doğal dil ile özel raporlar oluşturulabilecek
- **Eksik Fonksiyonlar:** Sayfalarda bulunan eksik fonksiyonlar eklenecek

### 📦 Stok & Depo Modülü
- [X] Ürünler sayfası ve API endpointleri
- [X] Depolar sayfası ve API endpointleri
- [X] Stok Hareketleri sayfası ve API endpointleri

### 🔧 Operasyon Modülü
- [X] Servis Formları sayfası ve API endpointleri
- [X] Transferler (Sevkiyat İrsaliyeleri) sayfası ve API endpointleri

### 💰 Finans Modülü
- [X] Faturalar sayfası ve API endpointleri
- [X] Masraflar sayfası ve API endpointleri

### 📊 Raporlama & Ayarlar
- [X] Raporlar sayfası ve API endpointleri
- [X] Ayarlar sayfası ve API endpointleri

---

## � Proje Yapısı

```
Otomasyon CRM/
├── backend/            # FastAPI Backend
└── frontend/           # Statik Frontend (Vanilla JS)
```

## 📖 Teknik Dokümantasyon

Kurulum ve çalıştırma talimatları için ilgili klasörlerin README dosyalarına bakınız:

- **[Backend Dokümantasyonu](backend/README.md)** — API kurulumu, veritabanı yapılandırması
- **[Frontend Dokümantasyonu](frontend/README.md)** — Arayüz çalıştırma ve yapı bilgisi

## 🏗️ Kullanılan Teknolojiler

| Katman | Teknolojiler |
|--------|--------------|
| Backend | FastAPI, SQLAlchemy, Pydantic, SQLite/PostgreSQL |
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| Güvenlik | JWT (JSON Web Token) |
| Raporlama | ReportLab (PDF), python-barcode, qrcode |
