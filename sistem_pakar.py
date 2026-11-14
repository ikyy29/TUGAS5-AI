"""Sistem pakar hama padi dengan Forward Chaining.
Jalankan:  python sistem_pakar.py
Mode cepat: python sistem_pakar.py --fakta "daun menguning, tanaman mengering cepat seperti terbakar"
"""
import argparse
import json


def muat_kb(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fakta_dasar(kb):
    """Fakta yang tidak pernah menjadi hasil aturan -> ditanyakan ke user."""
    hasil = {r["maka"] for r in kb["aturan"]}
    dasar = []
    for r in kb["aturan"]:
        for j in r["jika"]:
            if j not in hasil and j not in dasar:
                dasar.append(j)
    return dasar


def terpenuhi(r, memori):
    if r["mode"] == "atau":
        return any(j in memori for j in r["jika"])
    return all(j in memori for j in r["jika"])


def forward_chaining(kb, fakta_awal):
    memori = set(fakta_awal)
    asal = {}   # kesimpulan -> aturan yang menghasilkannya
    log = []
    siklus = 0
    while True:
        siklus += 1
        cocok = [r for r in kb["aturan"]
                 if r["maka"] not in memori and terpenuhi(r, memori)]
        if not cocok:
            log.append(f"Siklus {siklus}: tidak ada aturan baru, berhenti")
            break
        r = cocok[0]                      # ambil aturan pertama
        memori.add(r["maka"])
        asal[r["maka"]] = r
        log.append(f"Siklus {siklus}: {r['id']} -> {r['maka']}")
    return memori, asal, log


def syarat_terpakai(r, memori):
    return [j for j in r["jika"] if j in memori]


def kesimpulan_akhir(asal, memori):
    """Hasil yang tidak dipakai sebagai syarat oleh aturan lain yang terpakai."""
    dipakai = set()
    for r in asal.values():
        dipakai.update(syarat_terpakai(r, memori))
    return [k for k in asal if k not in dipakai]


def cetak_alasan(k, asal, memori, tingkat=1):
    r = asal[k]
    pakai = syarat_terpakai(r, memori)
    print("  " * tingkat + f"{k}  <- {r['id']} ({', '.join(pakai)})")
    for j in pakai:
        if j in asal:
            cetak_alasan(j, asal, memori, tingkat + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default="kb_padi.json", help="file aturan (JSON)")
    ap.add_argument("--fakta", help="fakta 'ya' dipisah koma, tanpa tanya jawab")
    a = ap.parse_args()

    kb = muat_kb(a.kb)
    dasar = fakta_dasar(kb)
    print(kb["judul"])

    if a.fakta is not None:
        ya = [f.strip() for f in a.fakta.split(",") if f.strip()]
        asing = [f for f in ya if f not in dasar]
        if asing:
            print("Fakta tidak dikenal:", "; ".join(asing))
            print("Fakta yang tersedia:")
            for f in dasar:
                print("  -", f)
            return
    else:
        print("Jawab y/t.")
        ya = []
        for i, f in enumerate(dasar, 1):
            while True:
                j = input(f"{i}. Apakah {f}? (y/t) > ").strip().lower()
                if j in ("y", "t"):
                    break
            if j == "y":
                ya.append(f)

    print("\nFakta awal:", ", ".join(ya) if ya else "(tidak ada)")
    print()
    memori, asal, log = forward_chaining(kb, ya)
    for baris in log:
        print(baris)

    print()
    if not asal:
        print("Kesimpulan: tidak ada kesimpulan yang dapat ditarik dari fakta tersebut.")
    else:
        akhir = kesimpulan_akhir(asal, memori)
        print("Kesimpulan:")
        for k in akhir:
            print(f"- {k}")
            if k in kb.get("keterangan", {}):
                print(f"  {kb['keterangan'][k]}")
        print("\nAlasan:")
        for k in akhir:
            cetak_alasan(k, asal, memori)

    print("\nCatatan:", kb["batas"])


if __name__ == "__main__":
    main()
