"""M2: Stack kasir/undo dan dua antrean untuk dibandingkan."""

from backend.m1_pesanan import Array


class Tumpukan:
    """Stack LIFO sederhana di atas Array M1."""

    def __init__(self):
        self._data = Array()

    def __len__(self):
        return len(self._data)

    def kosong(self):
        return len(self) == 0

    def is_empty(self):
        return self.kosong()

    def push(self, nilai):
        self._data.append(nilai)

    def pop(self):
        if self.kosong():
            raise IndexError("tumpukan kosong")
        return self._data.remove_at(len(self) - 1)

    def peek(self):
        if self.kosong():
            raise IndexError("tumpukan kosong")
        return self._data.get(len(self) - 1)

    def kosongkan(self):
        self._data = Array()

    def __iter__(self):
        for i in range(len(self._data)):
            yield self._data.get(i)


def pecah_token(ekspresi):
    """Pecah angka multi-digit dan operator + - * / ( )."""
    hasil, angka = [], ""
    for karakter in ekspresi:
        if karakter.isdigit():
            angka += karakter
        else:
            if angka:
                hasil.append(angka)
                angka = ""
            if karakter in "+-*/()":
                hasil.append(karakter)
            elif not karakter.isspace():
                raise ValueError("karakter kasir tidak dikenal: " + karakter)
    if angka:
        hasil.append(angka)
    if not hasil:
        raise ValueError("ekspresi kasir kosong")
    return hasil


def ke_postfix(ekspresi):
    """Konversi infix ke postfix memakai stack operator."""
    prioritas = "+-*/"  # +,- = 0; *,/ = 1 lewat pembagian indeks dua
    keluaran, operator = [], Tumpukan()
    perlu_angka = True
    for token in pecah_token(ekspresi):
        if token.isdigit():
            if not perlu_angka:
                raise ValueError("operator diperlukan sebelum angka")
            keluaran.append(token)
            perlu_angka = False
        elif token == "(":
            if not perlu_angka:
                raise ValueError("operator diperlukan sebelum '('")
            operator.push(token)
        elif token == ")":
            if perlu_angka:
                raise ValueError("angka diperlukan sebelum ')'")
            while not operator.kosong() and operator.peek() != "(":
                keluaran.append(operator.pop())
            if operator.kosong():
                raise ValueError("kurung buka tidak ditemukan")
            operator.pop()
        else:
            if perlu_angka:
                raise ValueError("angka diperlukan sebelum operator")
            while (not operator.kosong() and operator.peek() != "(" and
                   prioritas.index(operator.peek()) // 2 >= prioritas.index(token) // 2):
                keluaran.append(operator.pop())
            operator.push(token)
            perlu_angka = True
    if perlu_angka:
        raise ValueError("ekspresi berakhir tanpa angka")
    while not operator.kosong():
        token = operator.pop()
        if token == "(":
            raise ValueError("kurung tutup tidak ditemukan")
        keluaran.append(token)
    return keluaran


def hitung(postfix):
    """Evaluasi postfix; operand kanan selalu dipop terlebih dahulu."""
    nilai = Tumpukan()
    for token in postfix:
        if token.isdigit():
            nilai.push(int(token))
        else:
            if len(nilai) < 2:
                raise ValueError("operand tidak cukup")
            kanan, kiri = nilai.pop(), nilai.pop()
            if token == "+":
                nilai.push(kiri + kanan)
            elif token == "-":
                nilai.push(kiri - kanan)
            elif token == "*":
                nilai.push(kiri * kanan)
            elif token == "/":
                if kanan == 0:
                    raise ValueError("pembagian dengan nol")
                nilai.push(kiri // kanan)
            else:
                raise ValueError("operator postfix tidak dikenal")
    if len(nilai) != 1:
        raise ValueError("postfix tidak valid")
    return nilai.pop()


def langkah_kasir(ekspresi):
    """Menghasilkan jejak visual langkah per langkah kasir:
    Tahap 1: Infix -> Postfix (Baris 1.x)
    Tahap 2: Evaluasi Postfix -> Total (Baris 2.x)
    Sesuai transkrip implementasi acuan pada dokumen proyek.
    """
    prioritas = "+-*/"
    keluaran, operator = [], Tumpukan()
    baris = []
    tahap1 = 1
    perlu_angka = True

    def _stack_str(st):
        if st.kosong():
            return "kosong"
        isi = []
        for x in st:
            isi.append(str(x))
        return " ".join(isi)

    tokens = pecah_token(ekspresi)
    for token in tokens:
        if token.isdigit():
            if not perlu_angka:
                raise ValueError("operator diperlukan sebelum angka")
            keluaran.append(token)
            perlu_angka = False
            baris.append((f"1.{tahap1}", token, "angka, langsung keluar",
                          _stack_str(operator), " ".join(keluaran)))
            tahap1 += 1
        elif token == "(":
            if not perlu_angka:
                raise ValueError("operator diperlukan sebelum '('")
            operator.push(token)
            baris.append((f"1.{tahap1}", token, "push (",
                          _stack_str(operator), " ".join(keluaran)))
            tahap1 += 1
        elif token == ")":
            if perlu_angka:
                raise ValueError("angka diperlukan sebelum ')'")
            while not operator.kosong() and operator.peek() != "(":
                keluaran.append(operator.pop())
            if operator.kosong():
                raise ValueError("kurung buka tidak ditemukan")
            operator.pop()
            baris.append((f"1.{tahap1}", token, "pop sampai (, buang (",
                          _stack_str(operator), " ".join(keluaran)))
            tahap1 += 1
        else:
            if perlu_angka:
                raise ValueError("angka diperlukan sebelum operator")
            popped = []
            while (not operator.kosong() and operator.peek() != "(" and
                   prioritas.index(operator.peek()) // 2 >= prioritas.index(token) // 2):
                p = operator.pop()
                popped.append(p)
                keluaran.append(p)
            operator.push(token)
            if popped:
                gabung = " ".join(popped)
                tindakan = f"pop {gabung} (lebih/sama kuat), push {token}"
            else:
                tindakan = f"push {token}"
            baris.append((f"1.{tahap1}", token, tindakan,
                          _stack_str(operator), " ".join(keluaran)))
            tahap1 += 1
            perlu_angka = True

    if perlu_angka:
        raise ValueError("ekspresi berakhir tanpa angka")

    if not operator.kosong():
        while not operator.kosong():
            t = operator.pop()
            if t == "(":
                raise ValueError("kurung tutup tidak ditemukan")
            keluaran.append(t)
        baris.append((f"1.{tahap1}", "akhir", "pop sisa stack",
                      "kosong", " ".join(keluaran)))

    # Tahap 2: evaluasi postfix
    tahap2 = 1
    nilai = Tumpukan()
    for token in keluaran:
        if token.isdigit():
            nilai.push(int(token))
            baris.append((f"2.{tahap2}", token, f"push {token}",
                          _stack_str(nilai), ""))
            tahap2 += 1
        else:
            if len(nilai) < 2:
                raise ValueError("operand tidak cukup")
            kanan, kiri = nilai.pop(), nilai.pop()
            if token == "+":
                hasil = kiri + kanan
            elif token == "-":
                hasil = kiri - kanan
            elif token == "*":
                hasil = kiri * kanan
            elif token == "/":
                if kanan == 0:
                    raise ValueError("pembagian dengan nol")
                hasil = kiri // kanan
            else:
                raise ValueError("operator postfix tidak dikenal")
            nilai.push(hasil)
            tindakan = f"pop {kanan} dan {kiri} -> {kiri} {token} {kanan} = {hasil}"
            baris.append((f"2.{tahap2}", token, tindakan,
                          _stack_str(nilai), f"Rp{hasil:,}".replace(",", ".")))
            tahap2 += 1

    total = nilai.pop()
    return keluaran, total, baris


class AntreanNaif:
    """FIFO larik biasa; dequeue menggeser seluruh sisa elemen."""

    def __init__(self):
        self._data = Array()
        self.geser_terakhir = self.total_geser = 0

    def __len__(self):
        return len(self._data)

    def kosong(self):
        return len(self._data) == 0

    def is_empty(self):
        return self.kosong()

    def enqueue(self, nilai):
        self._data.append(nilai)
        self.geser_terakhir = 0

    def dequeue(self):
        if not len(self):
            return None
        nilai = self._data.remove_at(0)
        self.geser_terakhir = self._data.langkah_terakhir
        self.total_geser += self.geser_terakhir
        return nilai

    def keluarkan_belakang(self):
        return None if not len(self) else self._data.remove_at(len(self) - 1)

    def kembalikan_depan(self, daftar):
        for i in range(len(daftar) - 1, -1, -1):
            self._data.insert(0, daftar[i])

    def daftar(self, batas=10):
        hasil = []
        for i, nilai in enumerate(self._data):
            if i == batas:
                break
            hasil.append(nilai)
        return hasil


class AntreanMelingkar:
    """FIFO circular: front/rear/count, tumbuh saat penuh."""

    def __init__(self, kapasitas=4):
        self.kapasitas = max(kapasitas, 1)
        self.data = [None] * self.kapasitas
        self.front = self.rear = self.count = 0
        self.geser_terakhir = self.total_geser = 0

    def __len__(self):
        return self.count

    def kosong(self):
        return self.count == 0

    def is_empty(self):
        return self.kosong()

    def _tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.kapasitas]
        self.data, self.kapasitas = baru, self.kapasitas * 2
        self.front, self.rear = 0, self.count

    def enqueue(self, nilai):
        if self.count == self.kapasitas:
            self._tumbuh()
        self.data[self.rear] = nilai
        self.rear = (self.rear + 1) % self.kapasitas
        self.count += 1
        self.geser_terakhir = 0

    def dequeue(self):
        if not self.count:
            return None
        nilai = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas
        self.count -= 1
        self.geser_terakhir = 0
        return nilai

    def keluarkan_belakang(self):
        if not self.count:
            return None
        self.rear = (self.rear - 1) % self.kapasitas
        nilai = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return nilai

    def kembalikan_depan(self, daftar):
        while self.count + len(daftar) > self.kapasitas:
            self._tumbuh()
        for i in range(len(daftar) - 1, -1, -1):
            self.front = (self.front - 1) % self.kapasitas
            self.data[self.front] = daftar[i]
            self.count += 1

    def daftar(self, batas=10):
        hasil = []
        for i in range(min(self.count, batas)):
            hasil.append(self.data[(self.front + i) % self.kapasitas])
        return hasil


class Aksi:
    __slots__ = ("jenis", "data")

    def __init__(self, jenis, data):
        self.jenis, self.data = jenis, data


class LayananM2:
    """Menjaga dua antrean identik serta riwayat undo/redo."""

    def __init__(self, pesanan):
        self.naif, self.melingkar = AntreanNaif(), AntreanMelingkar()
        self.undo, self.redo = Tumpukan(), Tumpukan()
        for p in pesanan:
            if p.status == "ANTRE":
                self.naif.enqueue(p)
                self.melingkar.enqueue(p)

    def _catat_baru(self, aksi):
        self.undo.push(aksi)
        self.redo.kosongkan()

    def enqueue(self, pesanan):
        self.naif.enqueue(pesanan)
        self.melingkar.enqueue(pesanan)
        self._catat_baru(Aksi("enqueue", pesanan))

    def dequeue(self, jumlah):
        if jumlah < 1:
            raise ValueError("jumlah dequeue minimal 1")
        keluar = []
        for _ in range(jumlah):
            a, b = self.naif.dequeue(), self.melingkar.dequeue()
            if a is None or b is None:
                break
            if a.oid != b.oid:
                raise RuntimeError("dua antrean tidak konsisten")
            keluar.append(a)
        if not keluar:
            raise ValueError("antrean kosong")
        self._catat_baru(Aksi("dequeue", keluar))
        return keluar

    def undo_last(self):
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        if aksi.jenis == "enqueue":
            self.naif.keluarkan_belakang()
            self.melingkar.keluarkan_belakang()
        else:
            self.naif.kembalikan_depan(aksi.data)
            self.melingkar.kembalikan_depan(aksi.data)
        self.redo.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        if aksi.jenis == "enqueue":
            self.naif.enqueue(aksi.data)
            self.melingkar.enqueue(aksi.data)
        else:
            for _ in aksi.data:
                self.naif.dequeue()
                self.melingkar.dequeue()
        self.undo.push(aksi)
        return aksi

    def history(self):
        """Mengembalikan urutan rekaman aksi undo dari terlama hingga terbaru."""
        hasil = []
        for a in self.undo:
            hasil.append(a)
        return hasil

    def stats(self):
        return (len(self.naif), len(self.melingkar), self.melingkar.kapasitas,
                self.naif.total_geser, len(self.undo), len(self.redo))


# Alias sesuai penamaan di dokumen panduan
stack = Tumpukan
Stack = Tumpukan
queue = AntreanMelingkar
Queue = AntreanMelingkar

