"""Kütüphane Yönetim Sistemi - menü tabanlı konsol arayüzü."""

from pathlib import Path

from kutuphane import ODUNC_SURESI_GUN, Kutuphane, KutuphaneHatasi

VERITABANI = Path(__file__).with_name("kutuphane.db")

ORNEK_KITAPLAR = [
    ("Kürk Mantolu Madonna", "Sabahattin Ali", 1943),
    ("İnce Memed", "Yaşar Kemal", 1955),
    ("Saatleri Ayarlama Enstitüsü", "Ahmet Hamdi Tanpınar", 1961),
    ("Tutunamayanlar", "Oğuz Atay", 1972),
    ("1984", "George Orwell", 1949),
    ("Clean Code", "Robert C. Martin", 2008),
    ("Introduction to Algorithms", "Thomas H. Cormen", 1990),
    ("The C Programming Language", "Brian W. Kernighan", 1978),
]

ORNEK_UYELER = ["Ayşe Yılmaz", "Mehmet Demir", "Zeynep Kaya"]

MENU = """
========== KÜTÜPHANE YÖNETİM SİSTEMİ ==========
 KİTAP                ÜYE                ÖDÜNÇ
 1) Kitap ekle        5) Üye ekle        7) Ödünç ver
 2) Kitapları listele 6) Üyeleri listele 8) İade al
 3) Kitap ara                            9) Ödünçteki kitaplar
 4) Kitap sil                           10) Geciken kitaplar

11) İstatistikler   12) Örnek verileri yükle   0) Çıkış
================================================"""


def metin_al(soru, zorunlu=True):
    while True:
        cevap = input(f"{soru}: ").strip()
        if cevap or not zorunlu:
            return cevap
        print("Bu alan boş bırakılamaz.")


def sayi_al(soru, zorunlu=True):
    while True:
        cevap = input(f"{soru}: ").strip()
        if not cevap and not zorunlu:
            return None
        if cevap.isdigit():
            return int(cevap)
        print("Lütfen geçerli bir sayı gir.")


def listeyi_yazdir(ogeler, bos_mesaj):
    if not ogeler:
        print(bos_mesaj)
    for oge in ogeler:
        print(f"  {oge}")


def kitap_ekle(kutuphane):
    baslik = metin_al("Kitap adı")
    yazar = metin_al("Yazar")
    yil = sayi_al("Yayın yılı (boş geçilebilir)", zorunlu=False)
    isbn = metin_al("ISBN (boş geçilebilir)", zorunlu=False)
    kitap = kutuphane.kitap_ekle(baslik, yazar, yil, isbn)
    print(f"Kitap eklendi: {kitap}")


def kitap_ara(kutuphane):
    aranan = metin_al("Aranacak kitap adı veya yazar")
    listeyi_yazdir(kutuphane.kitap_ara(aranan), "Eşleşen kitap bulunamadı.")


def kitap_sil(kutuphane):
    kitap = kutuphane.kitap_sil(sayi_al("Silinecek kitap no"))
    print(f"Silindi: {kitap.baslik}")


def uye_ekle(kutuphane):
    ad = metin_al("Ad soyad")
    telefon = metin_al("Telefon (boş geçilebilir)", zorunlu=False)
    print(f"Üye eklendi: {kutuphane.uye_ekle(ad, telefon)}")


def uyeleri_listele(kutuphane):
    uyeler = kutuphane.uyeleri_listele()
    if not uyeler:
        print("Kayıtlı üye yok.")
    for uye in uyeler:
        kitap_sayisi = len(kutuphane.uyenin_kitaplari(uye.id))
        print(f"  {uye}  (elindeki kitap: {kitap_sayisi})")


def odunc_ver(kutuphane):
    kitap_id = sayi_al("Kitap no")
    uye_id = sayi_al("Üye no")
    odunc = kutuphane.odunc_ver(kitap_id, uye_id)
    print(f"Ödünç verildi: {odunc}")
    print(f"Ödünç süresi {ODUNC_SURESI_GUN} gündür.")


def iade_al(kutuphane):
    odunc = kutuphane.iade_al(sayi_al("İade edilen kitap no"))
    print(f"İade alındı: '{odunc.kitap_basligi}' ({odunc.uye_adi})")
    if odunc.gecikme_gunu():
        print(f"Dikkat: Kitap {odunc.gecikme_gunu()} gün gecikmeyle iade edildi.")


def gecikenleri_listele(kutuphane):
    gecikenler = kutuphane.geciken_oduncler()
    if not gecikenler:
        print("Geciken kitap yok.")
    for odunc in gecikenler:
        print(f"  {odunc}  -> {odunc.gecikme_gunu()} gün gecikti")


def istatistikleri_goster(kutuphane):
    ist = kutuphane.istatistikler()
    print(f"  Toplam kitap       : {ist['kitap_sayisi']}")
    print(f"  Toplam üye         : {ist['uye_sayisi']}")
    print(f"  Ödünçteki kitap    : {ist['oduncteki_kitap']}")
    print(f"  Geciken kitap      : {ist['geciken']}")
    print(f"  Toplam ödünç işlemi: {ist['toplam_odunc']}")
    if ist["en_cok_okunan"]:
        baslik, adet = ist["en_cok_okunan"]
        print(f"  En çok okunan      : {baslik} ({adet} kez)")


def ornek_verileri_yukle(kutuphane):
    for baslik, yazar, yil in ORNEK_KITAPLAR:
        kutuphane.kitap_ekle(baslik, yazar, yil)
    for ad in ORNEK_UYELER:
        kutuphane.uye_ekle(ad)
    print(f"{len(ORNEK_KITAPLAR)} kitap ve {len(ORNEK_UYELER)} üye eklendi.")


ISLEMLER = {
    "1": kitap_ekle,
    "2": lambda k: listeyi_yazdir(k.kitaplari_listele(), "Kütüphanede kitap yok."),
    "3": kitap_ara,
    "4": kitap_sil,
    "5": uye_ekle,
    "6": uyeleri_listele,
    "7": odunc_ver,
    "8": iade_al,
    "9": lambda k: listeyi_yazdir(k.aktif_oduncler(), "Ödünçte kitap yok."),
    "10": gecikenleri_listele,
    "11": istatistikleri_goster,
    "12": ornek_verileri_yukle,
}


def main():
    with Kutuphane(VERITABANI) as kutuphane:
        while True:
            print(MENU)
            secim = input("Seçimin: ").strip()
            if secim == "0":
                print("Görüşmek üzere!")
                break

            islem = ISLEMLER.get(secim)
            if islem is None:
                print("Geçersiz seçim.")
                continue

            print()
            try:
                islem(kutuphane)
            except KutuphaneHatasi as hata:
                print(f"Hata: {hata}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nÇıkıldı.")
