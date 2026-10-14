"""M1: Larik (array) dan rantai (linked list).

Data pesanan yang sama disimpan pada dua struktur buatan sendiri yang
melayani lima operasi yang persis sama:

    Operasi            Letak                 Array               Linked List
    lihat(i)           pesanan ke-i          O(1)                O(n)
    tambah_reguler     paling belakang       O(1) amortized      O(1)  (tail)
    tambah_prioritas   tengah barisan (n/2)  O(n) geser          O(n) telusur
    tambah_vip         paling depan          O(n) geser          O(1)  (head)
    hapus(i)           pesanan ke-i          O(n) geser          O(n) telusur

``langkah_terakhir`` mencatat biaya operasi terakhir: elemen digeser (Array)
atau simpul ditelusuri (LinkedList). Array juga mencatat ``salin_terakhir``.

Aturan tugas: tanpa dict, set, sorted, .sort(), heapq, bisect, collections.*.
List Python hanya dipakai sebagai larik primitif ``[None] * kapasitas``.
"""

import csv
import time

PRIORITAS_VIP, PRIORITAS_PRIORITAS, PRIORITAS_REGULER = 1, 2, 3
LABEL_PRIORITAS = ("-", "VIP", "PRIORITAS", "REGULER")  # indeks = kode prioritas


class Pesanan:
    """Satu baris pesanan. ``__slots__`` dipakai agar objek tidak membawa dict."""

    __slots__ = ("oid", "pelanggan", "resto", "menu", "harga", "prioritas",
                 "t_masuk_detik", "t_selesai_detik", "status")

    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas,
                 t_masuk_detik, t_selesai_detik=None, status="ANTRE"):
        if prioritas not in (1, 2, 3):
            raise ValueError("prioritas harus 1 (VIP), 2 (PRIORITAS), atau 3 (REGULER)")
        if harga < 0:
            raise ValueError("harga tidak boleh negatif")
        self.oid, self.pelanggan, self.resto, self.menu = oid, pelanggan, resto, menu
        self.harga, self.prioritas, self.status = harga, prioritas, status
        self.t_masuk_detik, self.t_selesai_detik = t_masuk_detik, t_selesai_detik

    @property
    def label_prioritas(self):
        return LABEL_PRIORITAS[self.prioritas]


class _Barisan:
    """Lima operasi M1, dibangun di atas get/append/insert/remove_at."""

    def __getitem__(self, i):
        return self.get(i)

    def _cek_indeks(self, i):
        if i < 0 or i >= self._ukuran:
            raise IndexError(f"indeks {i} di luar rentang 0..{self._ukuran - 1}")

    def __len__(self):
        return self._ukuran

    def lihat(self, i):
        return self.get(i)

    def tambah_reguler(self, pesanan):
        """REGULER: masuk barisan paling belakang."""
        self.append(pesanan)
        return self._ukuran - 1

    def tambah_prioritas(self, pesanan):
        """PRIORITAS: menyerobot ke tengah barisan (indeks n // 2)."""
        tengah = self._ukuran // 2
        self.insert(tengah, pesanan)
        return tengah

    def tambah_vip(self, pesanan):
        """VIP: langsung ke urutan pertama."""
        self.insert(0, pesanan)
        return 0

    def hapus(self, i):
        return self.remove_at(i)


class Array(_Barisan):
    """Larik dinamis: saat penuh, siapkan petak 2x lalu salin seluruh isi."""

    def __init__(self, kapasitas_awal=4):
        self.kapasitas = max(kapasitas_awal, 1)
        self._data = [None] * self.kapasitas
        self._ukuran = 0
        self.langkah_terakhir = 0  # elemen digeser
        self.salin_terakhir = 0    # elemen disalin karena resize

    def _siapkan_slot(self):
        self.langkah_terakhir = self.salin_terakhir = 0
        if self._ukuran == self.kapasitas:
            self.kapasitas *= 2
            baru = [None] * self.kapasitas
            for j in range(self._ukuran):
                baru[j] = self._data[j]
            self._data = baru
            self.salin_terakhir = self._ukuran

    def get(self, i):
        """O(1): alamat slot ke-i langsung dihitung."""
        self._cek_indeks(i)
        self.langkah_terakhir = self.salin_terakhir = 0
        return self._data[i]

    def append(self, v):
        """O(1) amortized: resize hanya sesekali."""
        self._siapkan_slot()
        self._data[self._ukuran] = v
        self._ukuran += 1

    def insert(self, i, v):
        """O(n): geser elemen [i..akhir] satu slot ke kanan."""
        if i < 0 or i > self._ukuran:
            raise IndexError(f"indeks sisip {i} di luar rentang 0..{self._ukuran}")
        self._siapkan_slot()
        for j in range(self._ukuran, i, -1):
            self._data[j] = self._data[j - 1]
        self.langkah_terakhir = self._ukuran - i
        self._data[i] = v
        self._ukuran += 1

    def remove_at(self, i):
        """O(n): geser sisa elemen satu slot ke kiri."""
        self._cek_indeks(i)
        item = self._data[i]
        for j in range(i, self._ukuran - 1):
            self._data[j] = self._data[j + 1]
        self.langkah_terakhir, self.salin_terakhir = self._ukuran - 1 - i, 0
        self._ukuran -= 1
        self._data[self._ukuran] = None
        return item

    def rentang(self, mulai, jumlah):
        """Elemen [mulai, mulai+jumlah): langsung lompat ke ``mulai``."""
        for j in range(mulai, min(mulai + jumlah, self._ukuran)):
            yield self._data[j]

    def __iter__(self):
        return self.rentang(0, self._ukuran)


class Simpul:
    """Satu simpul: nilai dan alamat simpul berikutnya."""

    __slots__ = ("nilai", "berikut")

    def __init__(self, nilai, berikut=None):
        self.nilai, self.berikut = nilai, berikut


class LinkedList(_Barisan):
    """Singly linked list dengan penunjuk head dan tail."""

    def __init__(self):
        self.head = self.tail = None
        self._ukuran = 0
        self.langkah_terakhir = 0  # simpul ditelusuri

    def _simpul_ke(self, i):
        """Telusuri i langkah dari head."""
        simpul = self.head
        for _ in range(i):
            simpul = simpul.berikut
        self.langkah_terakhir = i
        return simpul

    def get(self, i):
        """O(n): harus menelusuri dari head."""
        self._cek_indeks(i)
        return self._simpul_ke(i).nilai

    def prepend(self, v):
        """O(1): simpul baru menjadi head."""
        self.head = Simpul(v, self.head)
        if self.tail is None:
            self.tail = self.head
        self._ukuran += 1
        self.langkah_terakhir = 0

    def append(self, v):
        """O(1): berkat penunjuk tail."""
        if self.tail is None:
            self.prepend(v)
            return
        simpul = Simpul(v)
        self.tail.berikut = simpul
        self.tail = simpul
        self._ukuran += 1
        self.langkah_terakhir = 0

    def insert(self, i, v):
        """O(n) telusur ke simpul ke-(i-1), lalu sambung sekali."""
        if i < 0 or i > self._ukuran:
            raise IndexError(f"indeks sisip {i} di luar rentang 0..{self._ukuran}")
        if i == 0:
            return self.prepend(v)
        sebelum = self._simpul_ke(i - 1)
        sebelum.berikut = Simpul(v, sebelum.berikut)
        if sebelum is self.tail:
            self.tail = sebelum.berikut
        self._ukuran += 1

    def remove_at(self, i):
        """O(n) telusur ke simpul ke-(i-1), lalu lepas simpul ke-i."""
        self._cek_indeks(i)
        if i == 0:
            sebelum, target = None, self.head
            self.head = target.berikut
            self.langkah_terakhir = 0
        else:
            sebelum = self._simpul_ke(i - 1)
            target = sebelum.berikut
            sebelum.berikut = target.berikut
        if target is self.tail:
            self.tail = sebelum
        self._ukuran -= 1
        return target.nilai

    def rentang(self, mulai, jumlah):
        """Elemen [mulai, mulai+jumlah): harus menelusuri dari head dulu."""
        if mulai >= self._ukuran:
            return
        simpul = self._simpul_ke(mulai)
        while simpul is not None and jumlah > 0:
            yield simpul.nilai
            simpul, jumlah = simpul.berikut, jumlah - 1

    def __iter__(self):
        return self.rentang(0, self._ukuran)


class LayananPesanan:
    """Titik akses frontend: pesanan yang sama di Array dan LinkedList."""

    def __init__(self):
        self.array = Array()
        self.linked = LinkedList()
        self._oid_terbesar = 0

    def struktur(self, nama):
        """``nama``: "array" atau "linked"."""
        if nama in ("array", "linked"):
            return getattr(self, nama)
        raise ValueError(f"struktur tidak dikenal: {nama}")

    def _catat_oid(self, oid):
        if oid.startswith("O-") and oid[2:].isdigit():
            self._oid_terbesar = max(self._oid_terbesar, int(oid[2:]))

    def muat_csv(self, path, batas=None):
        """Muat CSV ke belakang KEDUA struktur (append, total O(n)).

        Mengembalikan (jumlah, durasi_detik).
        """
        mulai = time.perf_counter()
        jumlah = 0
        with open(path, encoding="utf-8", newline="") as berkas:
            pembaca = csv.reader(berkas)
            next(pembaca)  # lewati header
            for b in pembaca:
                if batas is not None and jumlah >= batas:
                    break
                p = Pesanan(b[0], b[1], b[2], b[3], int(b[4]), int(b[5]), int(b[6]),
                            int(b[7]) if b[7] else None, b[8])
                self.array.append(p)
                self.linked.append(p)
                self._catat_oid(p.oid)
                jumlah += 1
        return jumlah, time.perf_counter() - mulai

    def oid_berikutnya(self):
        return f"O-{self._oid_terbesar + 1:06d}"

    def buat_pesanan(self, pelanggan, resto, menu, harga, prioritas):
        """Pesanan baru: OID otomatis, status ANTRE, t_masuk = jam sekarang."""
        t = time.localtime()
        pesanan = Pesanan(self.oid_berikutnya(), pelanggan, resto, menu, harga, prioritas,
                          t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec)
        self._catat_oid(pesanan.oid)
        return pesanan


# Alias sesuai penamaan di dokumen panduan
LinkList = LinkedList
Node = Simpul
