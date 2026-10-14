"""Pengujian M2: postfix, circular queue, serta undo/redo."""

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)

from backend.m1_pesanan import Pesanan
from backend.m2_antrean import (AntreanMelingkar, AntreanNaif, LayananM2,
                                Tumpukan, hitung, ke_postfix, langkah_kasir,
                                queue, stack)


def pesanan(oid):
    return Pesanan(oid, "uji", "resto", "menu", 10000, 3, 0)


class TestKasir(unittest.TestCase):
    def test_postfix_dan_total_contoh_pdf(self):
        postfix = ke_postfix("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        self.assertEqual(postfix, ["3", "12000", "*", "2", "8500", "*", "+", "5000", "-"])
        self.assertEqual(hitung(postfix), 48000)

    def test_kurung_dan_urutan_pengurangan_pembagian(self):
        self.assertEqual(hitung(ke_postfix("20 - 8 - 3")), 9)
        self.assertEqual(hitung(ke_postfix("20 / ( 3 + 2 )")), 4)

    def test_langkah_kasir_sesuai_transkrip_pdf(self):
        postfix, total, baris = langkah_kasir("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        self.assertEqual(total, 48000)
        self.assertEqual(postfix, ["3", "12000", "*", "2", "8500", "*", "+", "5000", "-"])
        # Tahap 1: 14 langkah (1.1 sampai 1.14)
        tahap1 = [b for b in baris if b[0].startswith("1.")]
        self.assertEqual(len(tahap1), 14)
        self.assertEqual(tahap1[0], ("1.1", "(", "push (", "(", ""))
        self.assertEqual(tahap1[-1][0:3], ("1.14", "akhir", "pop sisa stack"))
        # Tahap 2: 9 langkah (2.1 sampai 2.9)
        tahap2 = [b for b in baris if b[0].startswith("2.")]
        self.assertEqual(len(tahap2), 9)
        self.assertEqual(tahap2[-1][4], "Rp48.000")


class TestAntrean(unittest.TestCase):
    def test_naif_menggeser_sedangkan_circular_tidak(self):
        naif, circular = AntreanNaif(), AntreanMelingkar(4)
        for nilai in ("A", "B", "C"):
            naif.enqueue(nilai)
            circular.enqueue(nilai)
        self.assertEqual((naif.dequeue(), circular.dequeue()), ("A", "A"))
        self.assertEqual((naif.geser_terakhir, circular.geser_terakhir), (2, 0))

    def test_circular_berputar_dan_tumbuh(self):
        q = AntreanMelingkar(4)
        for nilai in ("A", "B", "C"):
            q.enqueue(nilai)
        self.assertEqual((q.dequeue(), q.dequeue()), ("A", "B"))
        for nilai in ("D", "E", "F"):
            q.enqueue(nilai)
        self.assertEqual(q.daftar(), ["C", "D", "E", "F"])

    def test_kosong_dan_is_empty(self):
        q = AntreanMelingkar(4)
        self.assertTrue(q.kosong())
        self.assertTrue(q.is_empty())
        q.enqueue("A")
        self.assertFalse(q.kosong())
        self.assertFalse(q.is_empty())
        q.dequeue()
        self.assertTrue(q.is_empty())


class TestUndoRedo(unittest.TestCase):
    def test_undo_redo_dan_cabang_baru(self):
        layanan = LayananM2([pesanan("A"), pesanan("B"), pesanan("C")])
        layanan.enqueue(pesanan("D"))
        self.assertEqual(layanan.stats()[0:2], (4, 4))
        self.assertEqual(len(layanan.history()), 1)
        layanan.undo_last()
        self.assertEqual(layanan.stats()[0:2], (3, 3))
        layanan.redo_last()
        self.assertEqual(layanan.stats()[0:2], (4, 4))
        keluar = layanan.dequeue(2)
        self.assertEqual([p.oid for p in keluar], ["A", "B"])
        layanan.undo_last()
        self.assertEqual([p.oid for p in layanan.melingkar.daftar()], ["A", "B", "C", "D"])
        layanan.enqueue(pesanan("E"))
        self.assertIsNone(layanan.redo_last())


class TestPanduanAlias(unittest.TestCase):
    def test_alias(self):
        self.assertIs(stack, Tumpukan)
        self.assertIs(queue, AntreanMelingkar)


if __name__ == "__main__":
    unittest.main()
