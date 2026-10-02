# 📚 Kütüphane Yönetim Sistemi

Kitapların, üyelerin ve ödünç işlemlerinin takip edildiği, verileri **SQLite** veritabanında saklayan menü tabanlı bir konsol uygulaması. Python ile, nesne yönelimli programlama (OOP) prensipleriyle yazıldı.

## ✨ Özellikler

**Kitap işlemleri**
- Kitap ekleme (başlık, yazar, yıl, ISBN), silme ve listeleme
- Başlığa veya yazara göre arama (Türkçe karakter duyarlı: "ince" araması "İnce Memed"i bulur)
- Türk alfabesine göre doğru sıralama

**Üye işlemleri**
- Üye kaydı ve üyelerin elindeki kitap sayısıyla listelenmesi

**Ödünç işlemleri**
- 14 günlük ödünç süresi ve otomatik son teslim tarihi
- Geciken kitapların ve gecikme gün sayısının takibi

**İş kuralları**
- Ödünçteki bir kitap başka üyeye verilemez ve silinemez
- Bir üye en fazla 3 kitap alabilir
- Teslim tarihi geçmiş kitabı olan üye yeni kitap alamaz
- Aynı ISBN ile iki kitap eklenemez

**Diğer**
- İstatistikler (toplam kitap ve üye, ödünçteki ve geciken kitaplar, en çok okunan kitap)
- Hızlı deneme için tek tuşla örnek veri yükleme

## 🚀 Nasıl Çalıştırılır?

Python 3.8 veya üstü gerekir. SQLite Python ile birlikte gelir, ek kurulum gerekmez.

```bash
python main.py
```

İlk açılışta menüden **12** seçeneğiyle örnek kitap ve üyeleri yükleyebilirsin.

## 🖥️ Ekran Görüntüsü

```
========== KÜTÜPHANE YÖNETİM SİSTEMİ ==========
 KİTAP                ÜYE                ÖDÜNÇ
 1) Kitap ekle        5) Üye ekle        7) Ödünç ver
 2) Kitapları listele 6) Üyeleri listele 8) İade al
 3) Kitap ara                            9) Ödünçteki kitaplar
 4) Kitap sil                           10) Geciken kitaplar

11) İstatistikler   12) Örnek verileri yükle   0) Çıkış
================================================
Seçimin: 2

  #5 1984 - George Orwell (1949) [Rafta]
  #6 Clean Code - Robert C. Martin (2008) [Rafta]
  #2 İnce Memed - Yaşar Kemal (1955) [Rafta]
  #1 Kürk Mantolu Madonna - Sabahattin Ali (1943) [Ödünçte]
  ...
```

## 🏗️ Proje Yapısı

```
kutuphane-yonetim-sistemi/
├── main.py            # Menü ve kullanıcı arayüzü
├── kutuphane.py       # İş kuralları ve veritabanı işlemleri (Kutuphane sınıfı)
├── modeller.py        # Veri sınıfları: Kitap, Uye, Odunc
└── test_kutuphane.py  # Birim testleri
```

Arayüz (`main.py`) ile iş mantığı (`kutuphane.py`) birbirinden ayrıldı. Böylece iş kuralları, arayüzden bağımsız olarak test edilebiliyor.

### Veritabanı Şeması

```
kitaplar                uyeler                  oduncler
─────────               ──────                  ────────
id (PK)                 id (PK)                 id (PK)
baslik                  ad_soyad                kitap_id (FK -> kitaplar)
yazar                   telefon                 uye_id   (FK -> uyeler)
yil                     kayit_tarihi            verilis_tarihi
isbn (UNIQUE)                                   son_teslim_tarihi
                                                iade_tarihi (NULL = hâlâ ödünçte)
```

## 🧪 Testler

Testler, gerçek veritabanını etkilememek için bellek içi (`:memory:`) SQLite kullanır.

```bash
python -m unittest -v
```

## 📚 Bu Projede Öğrendiklerim

- Sınıflar, `@dataclass` ve `@staticmethod` ile nesne yönelimli tasarım
- `sqlite3` ile tablo oluşturma, `JOIN`, `GROUP BY`, alt sorgu (`EXISTS`)
- SQL injection'a karşı parametreli sorgular (`?`)
- Transaction yönetimi (`with baglanti:`)
- Özel hata sınıfı (`KutuphaneHatasi`) ile iş kuralı ihlallerini yönetme
- Context manager (`__enter__` / `__exit__`)
- Türkçe karakterlerde arama ve sıralama sorunlarının çözümü

## 📄 Lisans

[MIT](LICENSE)
