"""Kütüphane sistemindeki veri modelleri."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Kitap:
    id: int
    baslik: str
    yazar: str
    yil: Optional[int]
    isbn: Optional[str]
    musait: bool = True

    def __str__(self):
        yil = f" ({self.yil})" if self.yil else ""
        durum = "Rafta" if self.musait else "Ödünçte"
        return f"#{self.id} {self.baslik} - {self.yazar}{yil} [{durum}]"


@dataclass
class Uye:
    id: int
    ad_soyad: str
    telefon: Optional[str]
    kayit_tarihi: date

    def __str__(self):
        return f"#{self.id} {self.ad_soyad}"


@dataclass
class Odunc:
    id: int
    kitap_id: int
    kitap_basligi: str
    uye_id: int
    uye_adi: str
    verilis_tarihi: date
    son_teslim_tarihi: date
    iade_tarihi: Optional[date] = None

    def gecikme_gunu(self, bugun=None):
        """Teslim tarihi geçtiyse kaç gün geciktiğini döndürür."""
        bitis = self.iade_tarihi or bugun or date.today()
        return max(0, (bitis - self.son_teslim_tarihi).days)

    def __str__(self):
        return (f"#{self.id} '{self.kitap_basligi}' -> {self.uye_adi} "
                f"(Son teslim: {self.son_teslim_tarihi:%d.%m.%Y})")
