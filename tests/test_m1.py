"""Pengujian M1: Array, LinkedList, dan tiga letak penyisipan.

Jalankan dari akar proyek:  python -m unittest discover -s tests -v
"""

import os
import sys
import unittest

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, AKAR)

from backend.m1_pesanan import (  # noqa: E402
    Array,
    LayananPesanan,
    LinkList,
    LinkedList,
    Node,
    Pesanan,
    Simpul,
)

PATH_PESANAN = os.path.join(AKAR, "data", "pesanan.csv")


def buat(oid, prioritas=3):
    return Pesanan(oid, "uji", "resto", "menu", 10000, prioritas, 0)


def daftar_oid(struktur):
    hasil = []
    for p in struktur:
        hasil.append(p.oid)
    return hasil


def isi(struktur, n):
    for i in range(n):
        struktur.append(buat(f"O-{i}"))
    return struktur


class TestArray(unittest.TestCase):
    def test_resize_berlipat_dua_dan_menyalin(self):
        arr = Array(kapasitas_awal=4)
        isi(arr, 4)
        self.assertEqual(arr.kapasitas, 4)
        arr.append(buat("O-4"))                 # penuh -> petak baru 8, salin 4
        self.assertEqual(arr.kapasitas, 8)
        self.assertEqual(arr.salin_terakhir, 4)
        arr.append(buat("O-5"))                 # ada ruang cadangan -> gratis
        self.assertEqual(arr.salin_terakhir, 0)
        self.assertEqual(daftar_oid(arr), ["O-0", "O-1", "O-2", "O-3", "O-4", "O-5"])

    def test_get_O1(self):
        arr = isi(Array(), 10)
        self.assertEqual(arr.get(7).oid, "O-7")
        self.assertEqual(arr[7].oid, "O-7")
        self.assertEqual(arr.langkah_terakhir, 0)

    def test_insert_dan_remove_menggeser(self):
        arr = isi(Array(kapasitas_awal=8), 4)
        arr.insert(1, buat("X"))
        self.assertEqual(arr.langkah_terakhir, 3)
        self.assertEqual(daftar_oid(arr), ["O-0", "X", "O-1", "O-2", "O-3"])
        self.assertEqual(arr.remove_at(0).oid, "O-0")
        self.assertEqual(arr.langkah_terakhir, 4)
        self.assertEqual(arr.remove_at(3).oid, "O-3")   # elemen terakhir: 0 geser
        self.assertEqual(arr.langkah_terakhir, 0)

    def test_indeks_tidak_valid(self):
        arr = isi(Array(), 3)
        with self.assertRaises(IndexError):
            arr.get(3)
        with self.assertRaises(IndexError):
            arr.remove_at(-1)
        with self.assertRaises(IndexError):
            Array().get(0)


class TestLinkedList(unittest.TestCase):
    def test_get_menelusuri(self):
        ll = isi(LinkedList(), 10)
        self.assertEqual(ll.get(7).oid, "O-7")
        self.assertEqual(ll[7].oid, "O-7")
        self.assertEqual(ll.langkah_terakhir, 7)

    def test_head_tail_terjaga(self):
        ll = LinkedList()
        ll.append(buat("A"))
        ll.append(buat("B"))
        ll.prepend(buat("Z"))
        self.assertEqual((ll.head.nilai.oid, ll.tail.nilai.oid), ("Z", "B"))
        self.assertEqual(ll.remove_at(2).oid, "B")
        self.assertEqual(ll.tail.nilai.oid, "A")
        ll.insert(2, buat("C"))                 # sisip di ujung -> tail baru
        self.assertEqual(ll.tail.nilai.oid, "C")
        ll.remove_at(0)
        ll.remove_at(0)
        ll.remove_at(0)
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)
        self.assertEqual(len(ll), 0)

    def test_alias_sesuai_panduan(self):
        self.assertIs(LinkList, LinkedList)
        self.assertIs(Node, Simpul)


class TestTigaLetakPenyisipan(unittest.TestCase):
    def _uji(self, struktur):
        isi(struktur, 6)                         # O-0 .. O-5
        self.assertEqual(struktur.tambah_reguler(buat("R", 3)), 6)
        self.assertEqual(struktur.tambah_prioritas(buat("P", 2)), 3)   # 7 // 2
        self.assertEqual(struktur.tambah_vip(buat("V", 1)), 0)
        self.assertEqual(daftar_oid(struktur),
                         ["V", "O-0", "O-1", "O-2", "P", "O-3", "O-4", "O-5", "R"])
        self.assertEqual(struktur.hapus(4).oid, "P")
        self.assertEqual(struktur.lihat(0).oid, "V")

    def test_array(self):
        self._uji(Array())

    def test_linked_list(self):
        self._uji(LinkedList())

    def test_biaya_sesuai_teori(self):
        arr = isi(Array(kapasitas_awal=64), 40)
        ll = isi(LinkedList(), 40)
        arr.tambah_vip(buat("V", 1))
        ll.tambah_vip(buat("V", 1))
        self.assertEqual((arr.langkah_terakhir, ll.langkah_terakhir), (40, 0))
        arr.tambah_prioritas(buat("P", 2))       # tengah = 41 // 2 = 20
        ll.tambah_prioritas(buat("P", 2))
        self.assertEqual(arr.langkah_terakhir, 21)  # geser 41 - 20 elemen
        self.assertEqual(ll.langkah_terakhir, 19)   # telusur ke simpul ke-19
        arr.tambah_reguler(buat("R", 3))
        ll.tambah_reguler(buat("R", 3))
        self.assertEqual((arr.langkah_terakhir, ll.langkah_terakhir), (0, 0))
        self.assertEqual(daftar_oid(arr), daftar_oid(ll))


class TestLayanan(unittest.TestCase):
    def test_muat_csv_dan_oid_otomatis(self):
        layanan = LayananPesanan()
        jumlah, _ = layanan.muat_csv(PATH_PESANAN, batas=500)
        self.assertEqual(jumlah, 500)
        self.assertEqual(len(layanan.array), 500)
        self.assertEqual(len(layanan.linked), 500)
        self.assertEqual(daftar_oid(layanan.array), daftar_oid(layanan.linked))
        self.assertEqual(layanan.oid_berikutnya(), "O-000501")
        baru = layanan.buat_pesanan("Tes", "kedai-kopi", "kopi", 15000, 1)
        self.assertEqual(baru.oid, "O-000501")
        self.assertEqual(baru.status, "ANTRE")
        self.assertEqual(layanan.oid_berikutnya(), "O-000502")


if __name__ == "__main__":
    unittest.main()
