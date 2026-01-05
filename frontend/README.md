# Otomasyon CRM — Frontend

Vanilla JavaScript tabanlı statik web arayüzü.

## 🚀 Çalıştırma

Frontend herhangi bir derleme (build) işlemi gerektirmez. Basit bir HTTP sunucusu ile çalıştırılabilir:

**Node.js ile (Önerilen):**
```bash
npx serve -l 5500
```

**Python ile:**
```bash
python -m http.server 5500
```

Tarayıcınızdan `http://localhost:5500` adresine giderek uygulamaya erişebilirsiniz.

## 🔐 Giriş Bilgileri

- **E-posta:** `admin@otomasyon.com`
- **Şifre:** `admin123`

## 📂 Proje Yapısı

```
frontend/
├── index.html          # Dashboard (ana sayfa)
├── favicon.ico         # Site ikonu
├── css/
│   ├── variables.css   # CSS değişkenleri ve renk paleti
│   ├── main.css        # Temel stiller
│   ├── layout.css      # Sidebar, header, ana layout
│   ├── forms.css       # Form elemanları
│   ├── tables.css      # Tablo stilleri
│   ├── components.css  # Butonlar, kartlar, badge'ler
│   └── responsive.css  # Mobil uyumluluk
├── js/
│   ├── api.js          # API istemcisi ve endpoint tanımları
│   ├── utils.js        # Yardımcı fonksiyonlar (formatCurrency, formatDate vb.)
│   └── components/     # Yeniden kullanılabilir JS bileşenleri
└── pages/
    ├── login.html      # Giriş sayfası
    ├── customers.html  # Müşteriler
    ├── opportunities.html # Fırsatlar
    ├── projects.html   # Projeler
    └── ...             # Diğer sayfalar
```

## 🎨 Tasarım Sistemi

- **Renk Paleti:** Mavi tonları (`#1E3A5F`, `#3498DB`)
- **Tipografi:** Inter font ailesi
- **Bileşenler:** Modern glassmorphism efektleri, yumuşak gölgeler
