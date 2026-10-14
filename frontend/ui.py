"""Frontend 2EZ4U APP: satu jendela Tkinter.

Tata letak (sesuai dokumen proyek):
- kiri  : daftar menu per milestone,
- kanan : form parameter menu terpilih + hasil,
- bawah : panel COMMAND yang mencatat perintah, modul, dan waktunya.

Menu milestone berikutnya cukup ditambahkan ke ``DAFTAR_GRUP``.
Frontend hanya memanggil backend; seluruh struktur data ada di ``backend/``.
"""

import os
import threading
import time
import tkinter as tk
from tkinter import ttk

from backend.m1_pesanan import (PRIORITAS_PRIORITAS, PRIORITAS_REGULER, PRIORITAS_VIP,
                                LayananPesanan)
from backend.m2_antrean import LayananM2, hitung, ke_postfix, langkah_kasir

PATH_PESANAN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "data", "pesanan.csv")

# Palet warna & huruf
BG, KARTU, SIDEBAR, SIDEBAR_TEKS, REDUP = "#f4f5f9", "#ffffff", "#1b1f2b", "#c3c9d8", "#596075"
AKSEN, AKSEN_GELAP, TEKS, ABU, GARIS = "#ff6b35", "#e4561f", "#1b1f2b", "#6b7280", "#e3e6ee"
CMD_BG, CMD_TEKS, HIJAU, KUNING, MERAH = "#11141c", "#d5d9e2", "#3ecf8e", "#f5b942", "#ef4444"
HURUF, MONO = "Segoe UI", "Consolas"


def angka(n):
    return f"{n:,}".replace(",", ".")


def rupiah(n):
    return "Rp" + angka(n)


def durasi(detik):
    nilai, satuan = (detik, "s") if detik >= 1 else (detik * 1000, "ms")
    return f"{nilai:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") + " " + satuan


class Menu:
    """Satu menu: ``params`` = tuple (nama, label, jenis "int"/"teks", bawaan)."""

    __slots__ = ("kode", "label", "modul", "deskripsi", "params", "aksi", "struktur")

    def __init__(self, kode, label, modul, deskripsi, params, aksi, struktur=None):
        self.kode, self.label, self.modul, self.deskripsi = kode, label, modul, deskripsi
        self.params, self.aksi, self.struktur = params, aksi, struktur


class Hasil:
    """Keluaran satu aksi: judul, keterangan, baris tabel, baris sorot, waktu, ringkasan."""

    __slots__ = ("judul", "keterangan", "baris", "sorot", "waktu", "ringkas", "kolom", "lebar")

    def __init__(self, judul, keterangan, baris, sorot, waktu, ringkas, kolom=None, lebar=None):
        self.judul, self.keterangan, self.baris = judul, keterangan, baris
        self.sorot, self.waktu, self.ringkas = sorot, waktu, ringkas
        self.kolom, self.lebar = kolom, lebar


KOLOM_KASIR = ("Langkah", "Token", "Tindakan", "Stack", "Keluaran / Total")
LEBAR_KASIR = (80, 80, 360, 160, 240)


# ---------------------------------------------------------------------------
# Menu M1: Array vs Linked List
# ---------------------------------------------------------------------------
KOLOM_PESANAN = ("#", "OID", "Pelanggan", "Resto", "Menu", "Harga", "Prioritas", "Status")
LEBAR_KOLOM = (70, 90, 230, 130, 130, 90, 90, 80)
PARAM_INDEKS = ("indeks", "Indeks ke-i", "int", "0")
PARAM_PESANAN = (("pelanggan", "Nama pelanggan", "teks", "Pelanggan Baru"),
                 ("resto", "Resto", "teks", "kedai-kopi"),
                 ("menu", "Menu", "teks", "roti-bakar"),
                 ("harga", "Harga (Rp)", "int", "15000"))
JENIS_TAMBAH = (  # (prioritas, nama, letak)
    (PRIORITAS_REGULER, "REGULER", "masuk barisan paling belakang"),
    (PRIORITAS_PRIORITAS, "PRIORITAS", "menyerobot ke tengah barisan (indeks n/2)"),
    (PRIORITAS_VIP, "VIP", "langsung ke urutan pertama (indeks 0)"),
)


def _tabel(s, mulai, jumlah, pusat=-1):
    """Baris tabel [mulai, mulai+jumlah) dan posisi baris ``pusat`` di tabel."""
    mulai = max(mulai, 0)
    baris = []
    for i, p in enumerate(s.rentang(mulai, jumlah), mulai):
        baris.append((angka(i), p.oid, p.pelanggan, p.resto, p.menu, rupiah(p.harga),
                      p.label_prioritas, p.status))
    return baris, pusat - mulai


def _biaya(kode, s):
    if kode == "linked":
        return f"{angka(s.langkah_terakhir)} simpul ditelusuri"
    teks = f"{angka(s.langkah_terakhir)} elemen digeser"
    if s.salin_terakhir:
        teks += (f" + resize ke kapasitas {angka(s.kapasitas)} "
                 f"({angka(s.salin_terakhir)} elemen disalin)")
    return teks


def _ukur(fungsi, *argumen):
    mulai = time.perf_counter()
    hasil = fungsi(*argumen)
    return hasil, time.perf_counter() - mulai


def aksi_lihat(kode):
    def aksi(layanan, indeks, jumlah):
        if not 1 <= jumlah <= 500:
            raise ValueError("jumlah baris harus 1 – 500")
        s = layanan.struktur(kode)
        p, waktu = _ukur(s.lihat, indeks)
        cara = ("akses langsung, alamat slot dihitung → O(1)" if kode == "array" else
                f"{angka(s.langkah_terakhir)} simpul ditelusuri dari head → O(n)")
        baris, _ = _tabel(s, indeks, jumlah)
        return Hasil(f"Pesanan ke-{angka(indeks)}: {p.oid} · {p.pelanggan}",
                     (f"{p.resto} / {p.menu} · {rupiah(p.harga)} · {p.label_prioritas} · "
                      f"{p.status}", cara[0].upper() + cara[1:] + ".",
                      f"Menampilkan {angka(len(baris))} dari {angka(len(s))} pesanan."),
                     baris, 0, waktu, f"pesanan ke-{angka(indeks)} = {p.oid} | {cara}")
    return aksi


def aksi_tambah(kode, prioritas, letak):
    def aksi(layanan, pelanggan, resto, menu, harga):
        s = layanan.struktur(kode)
        pesanan = layanan.buat_pesanan(pelanggan, resto, menu, harga, prioritas)
        fungsi = (s.tambah_reguler, s.tambah_prioritas, s.tambah_vip)[3 - prioritas]
        indeks, waktu = _ukur(fungsi, pesanan)
        biaya = _biaya(kode, s)
        baris, sorot = _tabel(s, indeks - 3, 10, indeks)
        return Hasil(f"✓ {pesanan.oid} ({pesanan.label_prioritas}) masuk di indeks "
                     f"{angka(indeks)}, {letak}.",
                     (biaya + ".", f"Panjang sekarang {angka(len(s))}."),
                     baris, sorot, waktu,
                     f"{pesanan.oid} masuk di indeks {angka(indeks)} | {biaya}")
    return aksi


def aksi_hapus(kode):
    def aksi(layanan, indeks):
        s = layanan.struktur(kode)
        p, waktu = _ukur(s.hapus, indeks)
        biaya = _biaya(kode, s)
        pusat = min(indeks, len(s) - 1)
        baris, sorot = _tabel(s, pusat - 3, 10, pusat)
        return Hasil(f"✓ Pesanan ke-{angka(indeks)} ({p.oid} · {p.pelanggan}) dihapus.",
                     (biaya + ".", f"Panjang sekarang {angka(len(s))}."),
                     baris, sorot, waktu,
                     f"{p.oid} dihapus dari indeks {angka(indeks)} | {biaya}")
    return aksi


def _menu_m1():
    daftar = []
    for kode, nama in (("array", "Array"), ("linked", "Linked List")):
        modul, awalan = f"M1 - {nama.lower()}", nama.upper()
        daftar.append(Menu(f"{kode}_lihat", f"{awalan} - LIHAT PESANAN", modul,
                           f"Membuka detail pesanan ke-i pada {nama}.",
                           (PARAM_INDEKS, ("jumlah", "Jumlah baris", "int", "20")),
                           aksi_lihat(kode), kode))
        for prioritas, jenis, letak in JENIS_TAMBAH:
            daftar.append(Menu(f"{kode}_tambah_{jenis.lower()}",
                               f"{awalan} - TAMBAH PESANAN {jenis}", modul,
                               f"Pesanan {jenis} ({prioritas}) {letak}.", PARAM_PESANAN,
                               aksi_tambah(kode, prioritas, letak), kode))
        daftar.append(Menu(f"{kode}_hapus", f"{awalan} - HAPUS PESANAN", modul,
                           f"Mencabut pesanan ke-i dari barisan {nama}.", (PARAM_INDEKS,),
                           aksi_hapus(kode), kode))
    return tuple(daftar)


# ---------------------------------------------------------------------------
# Menu M2: Stack & Queue
# ---------------------------------------------------------------------------
PARAM_EKSPRESI = (("ekspresi", "Ekspresi infix", "teks", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"),)
PARAM_JUMLAH = (("jumlah", "Jumlah pesanan", "int", "1"),)


def _baris_antrean(m2):
    baris = []
    for i, p in enumerate(m2.melingkar.daftar()):
        baris.append((angka(i), p.oid, p.pelanggan, p.resto, p.menu, rupiah(p.harga),
                      p.label_prioritas, p.status))
    return baris


def _status_m2(m2):
    naif, circular, kapasitas, geser, undo, redo = m2.stats()
    return (f"Naif {angka(naif)} · Circular {angka(circular)} "
            f"(front {m2.melingkar.front}, rear {m2.melingkar.rear}, kap. {angka(kapasitas)}) · "
            f"total geser {angka(geser)} · undo {undo} · redo {redo}")


def aksi_postfix(layanan, ekspresi):
    (postfix, total, baris), waktu = _ukur(langkah_kasir, ekspresi)
    return Hasil("TOTAL " + rupiah(total),
                 ("Postfix: " + " ".join(postfix),
                  "Tahap 1 (1.x): Konversi infix ke postfix memakai stack operator.",
                  "Tahap 2 (2.x): Evaluasi postfix ke total memakai stack nilai."),
                 baris, len(baris) - 1, waktu, "postfix → total " + rupiah(total),
                 KOLOM_KASIR, LEBAR_KASIR)


def aksi_enqueue(layanan, pelanggan, resto, menu, harga):
    m2 = layanan.m2
    p = layanan.buat_pesanan(pelanggan, resto, menu, harga, PRIORITAS_REGULER)
    _, waktu = _ukur(m2.enqueue, p)
    return Hasil("✓ " + p.oid + " masuk ke belakang kedua antrean.",
                 ("Enqueue O(1) pada kedua versi.", _status_m2(m2)),
                 _baris_antrean(m2), -1, waktu, p.oid + " enqueue ke dua antrean")


def aksi_dequeue(judul):
    def aksi(layanan, jumlah):
        m2 = layanan.m2
        keluar, waktu = _ukur(m2.dequeue, jumlah)
        geser = m2.naif.geser_terakhir if len(keluar) == 1 else "lihat total"
        if judul == "naif vs circular":
            detil = (f"Naif: {angka(m2.naif.geser_terakhir)} elemen digeser "
                     f"(total {angka(m2.naif.total_geser)}); Circular: 0 elemen digeser.")
        else:
            detil = (f"Circular: 0 elemen digeser (front maju ke {m2.melingkar.front}); "
                     f"Naif: {angka(m2.naif.total_geser)} total elemen digeser.")
        return Hasil("✓ " + angka(len(keluar)) + " pesanan dilayani (" + judul + ").",
                     (detil, _status_m2(m2)),
                     _baris_antrean(m2), -1, waktu,
                     f"dequeue {angka(len(keluar))} | naif {geser} geser | circular 0")
    return aksi


def aksi_undo(layanan):
    aksi, waktu = _ukur(layanan.m2.undo_last)
    if aksi is None:
        return Hasil("Tidak ada aksi untuk dibatalkan.", (_status_m2(layanan.m2),), (), -1,
                     waktu, "undo kosong")
    teks = "dikembalikan ke depan" if aksi.jenis == "dequeue" else "dikeluarkan dari belakang"
    return Hasil("✓ Undo " + aksi.jenis + ": data " + teks + ".",
                 (_status_m2(layanan.m2),), _baris_antrean(layanan.m2), -1, waktu,
                 "undo " + aksi.jenis)


def aksi_redo(layanan):
    aksi, waktu = _ukur(layanan.m2.redo_last)
    if aksi is None:
        return Hasil("Tidak ada aksi untuk diulang.", (_status_m2(layanan.m2),), (), -1,
                     waktu, "redo kosong")
    return Hasil("✓ Redo " + aksi.jenis + ": aksi asli dikerjakan ulang.",
                 (_status_m2(layanan.m2),), _baris_antrean(layanan.m2), -1, waktu,
                 "redo " + aksi.jenis)


def _menu_m2():
    return (
        Menu("stack_postfix", "STACK - POSTFIX (MESIN KASIR)", "M2 - stack",
             "Ubah infix menjadi postfix, lalu hitung total dengan stack.", PARAM_EKSPRESI,
             aksi_postfix),
        Menu("stack_undo", "STACK - UNDO", "M2 - stack",
             "Batalkan aksi antrean terakhir dan pindahkan catatannya ke redo.", (), aksi_undo),
        Menu("stack_redo", "STACK - REDO", "M2 - stack",
             "Kerjakan ulang aksi yang terakhir dibatalkan.", (), aksi_redo),
        Menu("queue_enqueue", "QUEUE - ENQUEUE", "M2 - queue",
             "Masukkan pesanan yang sama ke belakang antrean naif dan circular.", PARAM_PESANAN,
             aksi_enqueue),
        Menu("queue_dequeue_naif", "QUEUE - DEQUEUE NAIF", "M2 - queue naif",
             "Layani data yang sama; biaya versi naif adalah pergeseran larik.", PARAM_JUMLAH,
             aksi_dequeue("naif vs circular")),
        Menu("queue_dequeue_circular", "QUEUE - DEQUEUE CIRCULAR", "M2 - queue circular",
             "Layani data yang sama; circular hanya menggeser penunjuk front.", PARAM_JUMLAH,
             aksi_dequeue("circular vs naif")),
    )


# (judul grup, tuple Menu). Grup tanpa menu tampil sebagai "segera".
DAFTAR_GRUP = (
    ("M1 · Array vs Linked List", _menu_m1()),
    ("M2 · Stack & Queue", _menu_m2()),
    ("M3 · Sort & Search", ()),
    ("M4 · Hash & Pencarian", ()),
    ("M5 · Katalog BST & Heap", ()),
    ("M6 · Peta & Rute", ()),
)


# ---------------------------------------------------------------------------
# Jendela utama
# ---------------------------------------------------------------------------
class Aplikasi:
    def __init__(self, root):
        self.root = root
        self.layanan = None
        self.menu_aktif = None
        self.isian = []          # list (param, StringVar)
        self.lbl_rentang = None
        self._muat = None        # (layanan, jumlah, lama) atau Exception

        root.title("2EZ4U APP — Struktur Data & Analisa Algoritma")
        root.geometry("1280x820")
        root.minsize(1040, 680)
        root.configure(bg=BG)
        self._atur_gaya()
        self._bangun()
        root.bind("<Return>", lambda _e: self.jalankan())
        root.after(80, self._mulai_muat)

    def _atur_gaya(self):
        g = ttk.Style(self.root)
        g.theme_use("clam")
        g.configure(".", font=(HURUF, 10), background=BG, foreground=TEKS)
        g.configure("Kartu.TFrame", background=KARTU)
        for nama, opsi in (("Judul", (TEKS, (HURUF, 15, "bold"))),
                           ("Modul", (AKSEN, (HURUF, 9, "bold"))),
                           ("Redup", (ABU, (HURUF, 10))),
                           ("Hint", (ABU, (HURUF, 9)))):
            g.configure(f"{nama}.TLabel", background=KARTU, foreground=opsi[0], font=opsi[1])
        g.configure("TEntry", fieldbackground="#fafbfd", bordercolor=GARIS, padding=6)
        g.map("TEntry", bordercolor=(("focus", AKSEN),))
        g.configure("Aksen.TButton", background=AKSEN, foreground="#ffffff",
                    font=(HURUF, 10, "bold"), padding=(22, 9), borderwidth=0)
        g.map("Aksen.TButton", background=(("disabled", "#f3b8a2"), ("active", AKSEN_GELAP)))
        g.configure("Sidebar.Treeview", background=SIDEBAR, fieldbackground=SIDEBAR,
                    foreground=SIDEBAR_TEKS, borderwidth=0, rowheight=30)
        g.map("Sidebar.Treeview", background=(("selected", AKSEN),),
              foreground=(("selected", "#ffffff"),))
        g.configure("Tabel.Treeview", background=KARTU, fieldbackground=KARTU,
                    rowheight=26, borderwidth=0, font=(HURUF, 9))
        g.configure("Tabel.Treeview.Heading", background="#eef0f5", foreground=ABU,
                    font=(HURUF, 9, "bold"), borderwidth=0, padding=6)

    def _bangun(self):
        # Header
        header = tk.Frame(self.root, bg=SIDEBAR, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)
        for teks, warna, jarak in (("2EZ4U", AKSEN, (20, 0)), ("APP", "#ffffff", (4, 14))):
            tk.Label(header, text=teks, bg=SIDEBAR, fg=warna,
                     font=(HURUF, 18, "bold")).pack(side="left", padx=jarak)
        tk.Label(header, text="engine backend layanan antar makanan · EC234303",
                 bg=SIDEBAR, fg=REDUP).pack(side="left")
        self.lbl_data = tk.Label(header, text="memuat data…", bg=SIDEBAR, fg=SIDEBAR_TEKS,
                                 font=(MONO, 10))
        self.lbl_data.pack(side="right", padx=20)

        # Status bar
        self.lbl_status = tk.Label(self.root, text="Siap", bg="#e9ebf2", fg=ABU,
                                   font=(HURUF, 9), anchor="w", padx=12, pady=4)
        self.lbl_status.pack(fill="x", side="bottom")

        vertikal = ttk.PanedWindow(self.root, orient="vertical")
        vertikal.pack(fill="both", expand=True)
        horizontal = ttk.PanedWindow(vertikal, orient="horizontal")
        vertikal.add(horizontal, weight=4)

        # Kiri: daftar menu
        kiri = tk.Frame(horizontal, bg=SIDEBAR, width=300)
        horizontal.add(kiri, weight=0)
        tk.Label(kiri, text="MENU", bg=SIDEBAR, fg=REDUP, font=(HURUF, 9, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(14, 4))
        self.pohon = ttk.Treeview(kiri, style="Sidebar.Treeview", show="tree",
                                  selectmode="browse")
        self.pohon.pack(fill="both", expand=True, padx=(6, 0), pady=(0, 8))
        self.pohon.column("#0", width=290)
        self.pohon.tag_configure("grup", foreground="#ffffff", font=(HURUF, 10, "bold"))
        self.pohon.tag_configure("segera", foreground=REDUP, font=(HURUF, 10, "italic"))
        for no, (judul, daftar) in enumerate(DAFTAR_GRUP):
            iid = f"grup{no}"
            self.pohon.insert("", "end", iid=iid, text=judul if daftar else f"{judul}  (segera)",
                              open=True, tags=("grup" if daftar else "segera",))
            for menu in daftar:
                self.pohon.insert(iid, "end", iid=menu.kode, text=menu.label)
        self.pohon.bind("<<TreeviewSelect>>", self._pilih_menu)

        # Kanan: form + hasil
        kanan = ttk.Frame(horizontal, padding=16)
        horizontal.add(kanan, weight=1)
        kartu = ttk.Frame(kanan, style="Kartu.TFrame", padding=(20, 16))
        kartu.pack(fill="both", expand=True)
        self.lbl_modul = ttk.Label(kartu, style="Modul.TLabel")
        self.lbl_modul.pack(anchor="w")
        self.lbl_judul = ttk.Label(kartu, text="Pilih menu di kiri", style="Judul.TLabel")
        self.lbl_judul.pack(anchor="w")
        self.lbl_desk = ttk.Label(kartu, style="Redup.TLabel", wraplength=820)
        self.lbl_desk.pack(anchor="w", pady=(2, 12))

        baris_form = ttk.Frame(kartu, style="Kartu.TFrame")
        baris_form.pack(fill="x")
        self.form = ttk.Frame(baris_form, style="Kartu.TFrame")
        self.form.pack(side="left", anchor="n")
        self.btn = ttk.Button(baris_form, text="▶  Jalankan", style="Aksen.TButton",
                              command=self.jalankan, state="disabled")
        self.btn.pack(side="left", anchor="s", padx=(18, 0))
        tk.Frame(kartu, bg=GARIS, height=1).pack(fill="x", pady=14)

        self.txt_hasil = tk.Text(kartu, height=4, bg=KARTU, fg=ABU, relief="flat",
                                 font=(HURUF, 10), wrap="word", highlightthickness=0,
                                 cursor="arrow", state="disabled")
        self.txt_hasil.pack(fill="x")
        self.txt_hasil.tag_configure("judul", foreground=TEKS, font=(HURUF, 11, "bold"))
        self.txt_hasil.tag_configure("galat", foreground=MERAH, font=(HURUF, 11, "bold"))

        bingkai = ttk.Frame(kartu, style="Kartu.TFrame")
        bingkai.pack(fill="both", expand=True, pady=(10, 0))
        self.tabel = ttk.Treeview(bingkai, style="Tabel.Treeview", show="headings",
                                  columns=KOLOM_PESANAN)
        for nama, lebar in zip(KOLOM_PESANAN, LEBAR_KOLOM):
            self.tabel.heading(nama, text=nama, anchor="w")
            self.tabel.column(nama, width=lebar, minwidth=50, stretch=nama == "Pelanggan")
        gulir = ttk.Scrollbar(bingkai, orient="vertical", command=self.tabel.yview)
        self.tabel.configure(yscrollcommand=gulir.set)
        self.tabel.pack(side="left", fill="both", expand=True)
        gulir.pack(side="right", fill="y")
        self.tabel.tag_configure("sorot", background="#fff1ea", font=(HURUF, 9, "bold"))
        self.tabel.tag_configure("genap", background="#fafbfd")

        # Bawah: panel COMMAND
        bawah = tk.Frame(vertikal, bg=CMD_BG)
        vertikal.add(bawah, weight=1)
        tk.Label(bawah, text="COMMAND  ", bg=CMD_BG, fg=AKSEN, font=(MONO, 10, "bold"),
                 anchor="w", padx=14, pady=6).pack(fill="x")
        self.txt_cmd = tk.Text(bawah, height=9, bg=CMD_BG, fg=CMD_TEKS, relief="flat",
                               font=(MONO, 10), highlightthickness=0, padx=14,
                               state="disabled")
        self.txt_cmd.pack(fill="both", expand=True)
        for tag, warna in (("prompt", AKSEN), ("perintah", "#ffffff"), ("modul", HIJAU),
                           ("waktu", KUNING), ("galat", MERAH)):
            self.txt_cmd.tag_configure(tag, foreground=warna)

    # -- pemuatan data (thread terpisah agar jendela tidak membeku) ------------
    def _mulai_muat(self):
        self.lbl_status.configure(text="Memuat data/pesanan.csv ke Array dan Linked List…")

        def kerja():
            try:
                layanan = LayananPesanan()
                self._muat = (layanan,) + layanan.muat_csv(PATH_PESANAN)
            except Exception as galat:  # ditampilkan di UI
                self._muat = galat

        threading.Thread(target=kerja, daemon=True).start()
        self._cek_muat()

    def _cek_muat(self):
        if self._muat is None:
            self.root.after(100, self._cek_muat)
            return
        if isinstance(self._muat, Exception):
            self._log("muat_data", (("  GALAT: " + str(self._muat) + "\n", "galat"),))
            self.lbl_status.configure(text="Gagal memuat data.")
            return
        self.layanan, jumlah, lama = self._muat
        self.layanan.m2 = LayananM2(self.layanan.array)
        self._log("muat_data data/pesanan.csv",
                  ((f"  {angka(jumlah)} pesanan dimuat ke Array dan Linked List   ", ""),
                   ("[M1 - data] ", "modul"), (durasi(lama) + "\n", "waktu")))
        self._perbarui_info()
        self.btn.configure(state="normal")
        self.lbl_status.configure(text=f"Siap · {angka(jumlah)} pesanan dimuat")
        pertama = DAFTAR_GRUP[0][1][0].kode
        self.pohon.selection_set(pertama)
        self.pohon.focus(pertama)

    # -- interaksi ------------------------------------------------------------
    def _pilih_menu(self, _event=None):
        pilihan = self.pohon.selection()
        menu = None
        for _, daftar in DAFTAR_GRUP:
            for m in daftar:
                if pilihan and m.kode == pilihan[0]:
                    menu = m
        if menu is None:
            return
        self.menu_aktif = menu
        self.lbl_modul.configure(text=menu.modul.upper())
        self.lbl_judul.configure(text=menu.label)
        self.lbl_desk.configure(text=menu.deskripsi)
        for anak in self.form.winfo_children():
            anak.destroy()
        self.isian, self.lbl_rentang = [], None
        for kolom, param in enumerate(menu.params):
            nama, label, jenis, bawaan = param
            ttk.Label(self.form, text=label, style="Hint.TLabel").grid(
                row=0, column=kolom, sticky="w", padx=(0, 12))
            var = tk.StringVar(value=bawaan)
            ttk.Entry(self.form, textvariable=var, width=10 if jenis == "int" else 18,
                      font=(HURUF, 10)).grid(row=1, column=kolom, sticky="w", padx=(0, 12))
            if nama == "indeks":
                self.lbl_rentang = ttk.Label(self.form, style="Hint.TLabel")
                self.lbl_rentang.grid(row=2, column=kolom, sticky="w")
            self.isian.append((param, var))
        self._perbarui_rentang()

    def jalankan(self):
        menu = self.menu_aktif
        if menu is None or self.layanan is None:
            return
        argumen, teks = [], menu.kode
        for (nama, label, jenis, _), var in self.isian:
            mentah = var.get().strip()
            teks += f" {nama}={mentah}"
            if jenis == "int":
                try:
                    argumen.append(int(mentah.replace(".", "")))
                except ValueError:
                    return self._galat(teks, f"{label} harus berupa angka bulat.")
            elif mentah:
                argumen.append(mentah)
            else:
                return self._galat(teks, f"{label} tidak boleh kosong.")
        try:
            h = menu.aksi(self.layanan, *argumen)
        except (IndexError, ValueError, RuntimeError) as galat:
            return self._galat(teks, str(galat))

        kolom_target = h.kolom if h.kolom is not None else KOLOM_PESANAN
        lebar_target = h.lebar if h.lebar is not None else LEBAR_KOLOM
        if tuple(self.tabel["columns"]) != tuple(kolom_target):
            self.tabel.configure(columns=kolom_target)
            for nama, lebar in zip(kolom_target, lebar_target):
                self.tabel.heading(nama, text=nama, anchor="w")
                self.tabel.column(nama, width=lebar, minwidth=50,
                                  stretch=(nama in ("Pelanggan", "Tindakan", "Keluaran / Total")))

        self._tulis_hasil(((h.judul + "\n", "judul"),)
                          + tuple((k + "\n", "") for k in h.keterangan))
        self.tabel.delete(*self.tabel.get_children())
        for k, baris in enumerate(h.baris):
            tag = "sorot" if k == h.sorot else ("genap" if k % 2 == 0 else "")
            self.tabel.insert("", "end", values=baris, tags=(tag,) if tag else ())
        self._log(teks, ((f"  {h.ringkas}   ", ""), (f"[{menu.modul}] ", "modul"),
                         (durasi(h.waktu) + "\n", "waktu")))
        self.lbl_status.configure(text=f"{menu.label} · {durasi(h.waktu)}")
        self._perbarui_info()
        self._perbarui_rentang()

    # -- render ---------------------------------------------------------------
    def _tulis_hasil(self, potongan):
        self.txt_hasil.configure(state="normal")
        self.txt_hasil.delete("1.0", "end")
        for teks, tag in potongan:
            self.txt_hasil.insert("end", teks, tag)
        self.txt_hasil.configure(state="disabled")

    def _galat(self, perintah, pesan):
        self._tulis_hasil((("✗ " + pesan, "galat"),))
        self._log(perintah, (("  GALAT: " + pesan + "\n", "galat"),))
        self.lbl_status.configure(text="Galat: " + pesan)

    def _log(self, perintah, potongan):
        t = self.txt_cmd
        t.configure(state="normal")
        t.insert("end", "> ", "prompt")
        t.insert("end", perintah + "\n", "perintah")
        for teks, tag in potongan:
            t.insert("end", teks, tag)
        t.configure(state="disabled")
        t.see("end")

    def _perbarui_rentang(self):
        if self.lbl_rentang is not None and self.layanan is not None:
            n = len(self.layanan.struktur(self.menu_aktif.struktur))
            self.lbl_rentang.configure(text=f"0 – {angka(n - 1)}")

    def _perbarui_info(self):
        a, ll = self.layanan.array, self.layanan.linked
        self.lbl_data.configure(text=f"Array {angka(len(a))} / kap {angka(a.kapasitas)}   ·   "
                                     f"Linked List {angka(len(ll))} simpul")


def jalankan():
    try:  # tampilan tajam pada layar Windows ber-DPI tinggi
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    Aplikasi(root)
    root.mainloop()
