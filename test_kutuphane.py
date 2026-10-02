import unittest
from datetime import date, timedelta

from kutuphane import ODUNC_SURESI_GUN, UYE_BASINA_MAX_KITAP, Kutuphane, KutuphaneHatasi

BUGUN = date(2026, 10, 1)


class KutuphaneTesti(unittest.TestCase):
    def setUp(self):
        self.k = Kutuphane(":memory:")
        self.kitap = self.k.kitap_ekle("Kürk Mantolu Madonna", "Sabahattin Ali", 1943)
        self.uye = self.k.uye_ekle("Ayşe Yılmaz")

    def tearDown(self):
        self.k.kapat()

    def test_kitap_ekle_ve_listele(self):
        self.k.kitap_ekle("1984", "George Orwell", 1949)
        basliklar = [kitap.baslik for kitap in self.k.kitaplari_listele()]
        self.assertEqual(basliklar, ["1984", "Kürk Mantolu Madonna"])

    def test_bos_baslik_eklenemez(self):
        with self.assertRaises(KutuphaneHatasi):
            self.k.kitap_ekle("  ", "Yazar")

    def test_ayni_isbn_iki_kez_eklenemez(self):
        self.k.kitap_ekle("A", "Yazar", isbn="123")
        with self.assertRaises(KutuphaneHatasi):
            self.k.kitap_ekle("B", "Yazar", isbn="123")

    def test_kitap_ara_buyuk_kucuk_harf_duyarsiz(self):
        self.assertEqual(len(self.k.kitap_ara("madonna")), 1)
        self.assertEqual(len(self.k.kitap_ara("SABAHATTİN")), 1)
        self.assertEqual(len(self.k.kitap_ara("sabahattin")), 1)
        self.assertEqual(len(self.k.kitap_ara("kurk")), 0)
        self.assertEqual(len(self.k.kitap_ara("orwell")), 0)

    def test_odunc_ver_kitabi_musait_olmaktan_cikarir(self):
        odunc = self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        self.assertEqual(odunc.son_teslim_tarihi, BUGUN + timedelta(days=ODUNC_SURESI_GUN))
        self.assertFalse(self.k.kitap_getir(self.kitap.id).musait)

    def test_oduncteki_kitap_tekrar_verilemez(self):
        ikinci_uye = self.k.uye_ekle("Mehmet Demir")
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        with self.assertRaises(KutuphaneHatasi):
            self.k.odunc_ver(self.kitap.id, ikinci_uye.id, BUGUN)

    def test_uye_kitap_limiti(self):
        for i in range(UYE_BASINA_MAX_KITAP - 1):
            kitap = self.k.kitap_ekle(f"Kitap {i}", "Yazar")
            self.k.odunc_ver(kitap.id, self.uye.id, BUGUN)
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)

        fazladan = self.k.kitap_ekle("Fazladan", "Yazar")
        with self.assertRaises(KutuphaneHatasi):
            self.k.odunc_ver(fazladan.id, self.uye.id, BUGUN)

    def test_gecikmesi_olan_uye_yeni_kitap_alamaz(self):
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        yeni = self.k.kitap_ekle("Yeni", "Yazar")
        gelecek = BUGUN + timedelta(days=ODUNC_SURESI_GUN + 1)
        with self.assertRaises(KutuphaneHatasi):
            self.k.odunc_ver(yeni.id, self.uye.id, gelecek)

    def test_iade_ve_gecikme_hesabi(self):
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        iade_gunu = BUGUN + timedelta(days=ODUNC_SURESI_GUN + 3)
        odunc = self.k.iade_al(self.kitap.id, iade_gunu)
        self.assertEqual(odunc.gecikme_gunu(), 3)
        self.assertTrue(self.k.kitap_getir(self.kitap.id).musait)

    def test_oduncte_olmayan_kitap_iade_edilemez(self):
        with self.assertRaises(KutuphaneHatasi):
            self.k.iade_al(self.kitap.id)

    def test_geciken_oduncler(self):
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        self.assertEqual(self.k.geciken_oduncler(BUGUN), [])
        gec = BUGUN + timedelta(days=ODUNC_SURESI_GUN + 1)
        self.assertEqual(len(self.k.geciken_oduncler(gec)), 1)

    def test_oduncteki_kitap_silinemez(self):
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        with self.assertRaises(KutuphaneHatasi):
            self.k.kitap_sil(self.kitap.id)

    def test_istatistikler(self):
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        self.k.iade_al(self.kitap.id, BUGUN)
        self.k.odunc_ver(self.kitap.id, self.uye.id, BUGUN)
        ist = self.k.istatistikler(BUGUN)
        self.assertEqual(ist["kitap_sayisi"], 1)
        self.assertEqual(ist["oduncteki_kitap"], 1)
        self.assertEqual(ist["toplam_odunc"], 2)
        self.assertEqual(ist["en_cok_okunan"], ("Kürk Mantolu Madonna", 2))


if __name__ == "__main__":
    unittest.main()
