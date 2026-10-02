"""Kütüphane iş kuralları ve SQLite veritabanı işlemleri."""

import sqlite3
from datetime import date, timedelta

from modeller import Kitap, Odunc, Uye

ODUNC_SURESI_GUN = 14
UYE_BASINA_MAX_KITAP = 3

TABLOLAR = """
CREATE TABLE IF NOT EXISTS kitaplar (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik  TEXT NOT NULL,
    yazar   TEXT NOT NULL,
    yil     INTEGER,
    isbn    TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS uyeler (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_soyad      TEXT NOT NULL,
    telefon       TEXT,
    kayit_tarihi  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS oduncler (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    kitap_id           INTEGER NOT NULL REFERENCES kitaplar(id),
    uye_id             INTEGER NOT NULL REFERENCES uyeler(id),
    verilis_tarihi     TEXT NOT NULL,
    son_teslim_tarihi  TEXT NOT NULL,
    iade_tarihi        TEXT
);
"""

# Türkçe "İ, I, ı" harflerini "i" yaparak aramayı harf duyarsız hale getirir
I_HARFLERI = str.maketrans({"İ": "i", "I": "i", "ı": "i"})

ODUNC_SORGUSU = """
SELECT o.id, o.kitap_id, k.baslik AS kitap_basligi, o.uye_id, u.ad_soyad AS uye_adi,
       o.verilis_tarihi, o.son_teslim_tarihi, o.iade_tarihi
FROM oduncler o
JOIN kitaplar k ON k.id = o.kitap_id
JOIN uyeler u ON u.id = o.uye_id
"""


TURK_ALFABESI = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"


def turkce_sirala_anahtari(metin):
    """Metinleri Türk alfabesine göre (ç, ğ, ı, ö, ş, ü doğru yerde) sıralamak için anahtar."""
    kucuk = metin.replace("I", "ı").replace("İ", "i").lower()
    return [TURK_ALFABESI.find(h) if h in TURK_ALFABESI else 100 + ord(h) for h in kucuk]


def sadelestir(metin):
    """Arama için metni küçük harfe çevirir ve Türkçe i harflerini birleştirir."""
    return metin.translate(I_HARFLERI).casefold()


class KutuphaneHatasi(Exception):
    """İş kuralı ihlallerinde fırlatılan hata (ör. kitap zaten ödünçte)."""


class Kutuphane:
    def __init__(self, veritabani="kutuphane.db"):
        self.baglanti = sqlite3.connect(veritabani)
        self.baglanti.row_factory = sqlite3.Row
        self.baglanti.execute("PRAGMA foreign_keys = ON")
        self.baglanti.executescript(TABLOLAR)

    def kapat(self):
        self.baglanti.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.kapat()

    # ---------- Kitap işlemleri ----------

    def kitap_ekle(self, baslik, yazar, yil=None, isbn=None):
        baslik, yazar = baslik.strip(), yazar.strip()
        if not baslik or not yazar:
            raise KutuphaneHatasi("Kitap başlığı ve yazar boş olamaz.")
        if yil is not None and not 0 < yil <= date.today().year:
            raise KutuphaneHatasi(f"Geçersiz yayın yılı: {yil}")

        try:
            with self.baglanti:
                imlec = self.baglanti.execute(
                    "INSERT INTO kitaplar (baslik, yazar, yil, isbn) VALUES (?, ?, ?, ?)",
                    (baslik, yazar, yil, isbn or None))
        except sqlite3.IntegrityError:
            raise KutuphaneHatasi(f"Bu ISBN ile kayıtlı bir kitap zaten var: {isbn}") from None
        return self.kitap_getir(imlec.lastrowid)

    def kitap_getir(self, kitap_id):
        satir = self.baglanti.execute(
            """SELECT k.*, NOT EXISTS (
                   SELECT 1 FROM oduncler o WHERE o.kitap_id = k.id AND o.iade_tarihi IS NULL
               ) AS musait
               FROM kitaplar k WHERE k.id = ?""", (kitap_id,)).fetchone()
        if satir is None:
            raise KutuphaneHatasi(f"{kitap_id} numaralı kitap bulunamadı.")
        return self._kitaba_cevir(satir)

    def kitaplari_listele(self):
        satirlar = self.baglanti.execute(
            """SELECT k.*, NOT EXISTS (
                   SELECT 1 FROM oduncler o WHERE o.kitap_id = k.id AND o.iade_tarihi IS NULL
               ) AS musait
               FROM kitaplar k""")
        kitaplar = [self._kitaba_cevir(s) for s in satirlar]
        return sorted(kitaplar, key=lambda k: turkce_sirala_anahtari(k.baslik))

    def kitap_ara(self, aranan):
        aranan = sadelestir(aranan.strip())
        return [k for k in self.kitaplari_listele()
                if aranan in sadelestir(k.baslik) or aranan in sadelestir(k.yazar)]

    def kitap_sil(self, kitap_id):
        kitap = self.kitap_getir(kitap_id)
        if not kitap.musait:
            raise KutuphaneHatasi("Ödünçteki bir kitap silinemez.")
        with self.baglanti:
            self.baglanti.execute("DELETE FROM oduncler WHERE kitap_id = ?", (kitap_id,))
            self.baglanti.execute("DELETE FROM kitaplar WHERE id = ?", (kitap_id,))
        return kitap

    # ---------- Üye işlemleri ----------

    def uye_ekle(self, ad_soyad, telefon=None, kayit_tarihi=None):
        ad_soyad = ad_soyad.strip()
        if not ad_soyad:
            raise KutuphaneHatasi("Üye adı boş olamaz.")
        kayit_tarihi = kayit_tarihi or date.today()
        with self.baglanti:
            imlec = self.baglanti.execute(
                "INSERT INTO uyeler (ad_soyad, telefon, kayit_tarihi) VALUES (?, ?, ?)",
                (ad_soyad, telefon or None, kayit_tarihi.isoformat()))
        return self.uye_getir(imlec.lastrowid)

    def uye_getir(self, uye_id):
        satir = self.baglanti.execute("SELECT * FROM uyeler WHERE id = ?", (uye_id,)).fetchone()
        if satir is None:
            raise KutuphaneHatasi(f"{uye_id} numaralı üye bulunamadı.")
        return Uye(satir["id"], satir["ad_soyad"], satir["telefon"],
                   date.fromisoformat(satir["kayit_tarihi"]))

    def uyeleri_listele(self):
        satirlar = self.baglanti.execute("SELECT id FROM uyeler")
        uyeler = [self.uye_getir(s["id"]) for s in satirlar]
        return sorted(uyeler, key=lambda u: turkce_sirala_anahtari(u.ad_soyad))

    # ---------- Ödünç işlemleri ----------

    def odunc_ver(self, kitap_id, uye_id, bugun=None):
        bugun = bugun or date.today()
        kitap = self.kitap_getir(kitap_id)
        uye = self.uye_getir(uye_id)

        if not kitap.musait:
            raise KutuphaneHatasi(f"'{kitap.baslik}' şu anda başka bir üyede.")

        uyedekiler = self.uyenin_kitaplari(uye_id)
        if len(uyedekiler) >= UYE_BASINA_MAX_KITAP:
            raise KutuphaneHatasi(
                f"{uye.ad_soyad} en fazla {UYE_BASINA_MAX_KITAP} kitap alabilir.")
        if any(o.gecikme_gunu(bugun) > 0 for o in uyedekiler):
            raise KutuphaneHatasi(
                f"{uye.ad_soyad} adlı üyenin teslim tarihi geçmiş kitabı var.")

        son_teslim = bugun + timedelta(days=ODUNC_SURESI_GUN)
        with self.baglanti:
            imlec = self.baglanti.execute(
                """INSERT INTO oduncler (kitap_id, uye_id, verilis_tarihi, son_teslim_tarihi)
                   VALUES (?, ?, ?, ?)""",
                (kitap_id, uye_id, bugun.isoformat(), son_teslim.isoformat()))
        return self._odunc_getir(imlec.lastrowid)

    def iade_al(self, kitap_id, bugun=None):
        bugun = bugun or date.today()
        satir = self.baglanti.execute(
            "SELECT id FROM oduncler WHERE kitap_id = ? AND iade_tarihi IS NULL",
            (kitap_id,)).fetchone()
        if satir is None:
            raise KutuphaneHatasi(f"{kitap_id} numaralı kitap ödünçte değil.")

        with self.baglanti:
            self.baglanti.execute("UPDATE oduncler SET iade_tarihi = ? WHERE id = ?",
                                  (bugun.isoformat(), satir["id"]))
        return self._odunc_getir(satir["id"])

    def aktif_oduncler(self):
        satirlar = self.baglanti.execute(
            ODUNC_SORGUSU + " WHERE o.iade_tarihi IS NULL ORDER BY o.son_teslim_tarihi")
        return [self._oduce_cevir(s) for s in satirlar]

    def geciken_oduncler(self, bugun=None):
        return [o for o in self.aktif_oduncler() if o.gecikme_gunu(bugun) > 0]

    def uyenin_kitaplari(self, uye_id):
        return [o for o in self.aktif_oduncler() if o.uye_id == uye_id]

    def istatistikler(self, bugun=None):
        def say(sorgu):
            return self.baglanti.execute(sorgu).fetchone()[0]

        en_cok_okunan = self.baglanti.execute(
            """SELECT k.baslik, COUNT(*) AS adet FROM oduncler o
               JOIN kitaplar k ON k.id = o.kitap_id
               GROUP BY o.kitap_id ORDER BY adet DESC, k.baslik LIMIT 1""").fetchone()

        return {
            "kitap_sayisi": say("SELECT COUNT(*) FROM kitaplar"),
            "uye_sayisi": say("SELECT COUNT(*) FROM uyeler"),
            "oduncteki_kitap": say("SELECT COUNT(*) FROM oduncler WHERE iade_tarihi IS NULL"),
            "toplam_odunc": say("SELECT COUNT(*) FROM oduncler"),
            "geciken": len(self.geciken_oduncler(bugun)),
            "en_cok_okunan": tuple(en_cok_okunan) if en_cok_okunan else None,
        }

    # ---------- Yardımcılar ----------

    def _odunc_getir(self, odunc_id):
        satir = self.baglanti.execute(ODUNC_SORGUSU + " WHERE o.id = ?", (odunc_id,)).fetchone()
        return self._oduce_cevir(satir)

    @staticmethod
    def _kitaba_cevir(satir):
        return Kitap(satir["id"], satir["baslik"], satir["yazar"], satir["yil"],
                     satir["isbn"], bool(satir["musait"]))

    @staticmethod
    def _oduce_cevir(satir):
        iade = satir["iade_tarihi"]
        return Odunc(
            id=satir["id"],
            kitap_id=satir["kitap_id"],
            kitap_basligi=satir["kitap_basligi"],
            uye_id=satir["uye_id"],
            uye_adi=satir["uye_adi"],
            verilis_tarihi=date.fromisoformat(satir["verilis_tarihi"]),
            son_teslim_tarihi=date.fromisoformat(satir["son_teslim_tarihi"]),
            iade_tarihi=date.fromisoformat(iade) if iade else None,
        )
