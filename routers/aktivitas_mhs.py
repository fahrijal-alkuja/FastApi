from datetime import date, timedelta
from difflib import SequenceMatcher
from itertools import combinations
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from config.condb import get_db
from models.model import AktivitasMhs
from schemas.am import AddAktivitas, UpdateAktivitas, Analisis
import aiohttp
from config.auth_bearer import get_current_active_user

Aktivitas = APIRouter()


def similarity(a: str, b: str) -> float:
    """Returns the percentage of similarity between two strings."""
    matcher = SequenceMatcher(None, a, b)
    return matcher.ratio() * 100


def get_all_judul(db: Session) -> List[str]:
    """Returns a list of all the 'judul' values from the database."""
    return [row.judul for row in db.query(AktivitasMhs.judul).all()]


def get_judul_by_id_prodi_judul(db: Session, id_prodi: int) -> List[str]:
    """Returns a list of judul values based on id_prodi and judul."""
    # Query database untuk mengambil data judul yang sesuai dengan id_prodi dan judul
    juduls = db.query(AktivitasMhs.judul).filter_by(
        id_prodi=id_prodi).all()
    # Kembalikan hasil dalam bentuk list
    return [row.judul for row in juduls]


def hitung_jadwal_seminar(tanggal_sk_tugas: date, jangka_waktu: Optional[int] = 3) -> date:
    return tanggal_sk_tugas + timedelta(days=30 * jangka_waktu)


def hitung_jadwal_ujian(tanggal_seminar: date, jangka_waktu: Optional[int] = 3) -> date:
    return tanggal_seminar + timedelta(days=30 * jangka_waktu)


@Aktivitas.get("/api/am", tags=["Aktivitas_mhs"], response_model=List[Analisis])
async def get_aktivitas(db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    aktivitas = db.query(AktivitasMhs).all()

    for am in aktivitas:
        # hitung lama tugas
        am.lama_tugas = hitung_lama_tugas(am.tanggal_sk_tugas)
        # check if seminar date or ujian date has passed
        today = date.today()
        if am.tanggal_seminar and am.tanggal_seminar < today:
            am.pesan_seminar = "Target seminar tidak terpenuhi."
        else:
            am.pesan_seminar = "Dalam Proses Bimbingan"

        if am.tanggal_ujian and am.tanggal_ujian < today:
            am.pesan_ujian = "Target ujian tidak terpenuhi."
        else:
            am.pesan_ujian = "Dalam Proses Bimbingan"

    return aktivitas


@Aktivitas.get("/api/am/{id_prodi}", tags=["Aktivitas_mhs"], response_model=List[Analisis])
async def get_aktivitas_by_prodi(id_prodi: int, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    aktivitas = db.query(AktivitasMhs).filter(
        AktivitasMhs.id_prodi == id_prodi).all()
    if not aktivitas:
        raise HTTPException(
            status_code=404, detail=f"Aktivitas mahasiswa dengan id_prodi {id_prodi} tidak ditemukan")

    for am in aktivitas:
        # hitung lama tugas
        am.lama_tugas = hitung_lama_tugas(am.tanggal_sk_tugas)
        # check if seminar date or ujian date has passed
        today = date.today()
        if am.tanggal_seminar and am.tanggal_seminar < today:
            am.pesan_seminar = "Target seminar tidak terpenuhi."
        else:
            am.pesan_seminar = "Dalam Proses Bimbingan"

        if am.tanggal_ujian and am.tanggal_ujian < today:
            am.pesan_ujian = "Target ujian tidak terpenuhi."
        else:
            am.pesan_ujian = "Dalam Proses Bimbingan"

    return aktivitas


@Aktivitas.get("/api/am/byid/{id}", tags=["Aktivitas_mhs"], response_model=List[Analisis])
async def get_aktivitas_by_id(id: int, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    aktivitas = db.query(AktivitasMhs).filter(AktivitasMhs.id == id).all()
    if not aktivitas:
        raise HTTPException(
            status_code=404, detail=f"Aktivitas mahasiswa dengan id {id} tidak ditemukan")
    for am in aktivitas:
        # hitung lama tugas
        am.lama_tugas = hitung_lama_tugas(am.tanggal_sk_tugas)
        # check if seminar date or ujian date has passed
        today = date.today()
        if am.tanggal_seminar and am.tanggal_seminar < today:
            am.pesan_seminar = "Target seminar tidak terpenuhi."
        else:
            am.pesan_seminar = "Dalam Proses Bimbingan"

        if am.tanggal_ujian and am.tanggal_ujian < today:
            am.pesan_ujian = "Target ujian tidak terpenuhi."
        else:
            am.pesan_ujian = "Dalam Proses Bimbingan"

    return aktivitas


def hitung_lama_tugas(tanggal_sk_tugas: date) -> str:
    today = date.today()
    delta = today - tanggal_sk_tugas
    total_days = delta.days
    total_months = int(total_days / 30.44)  # Average number of days per month

    if total_months >= 12:
        years = int(total_months / 12)
        months = total_months % 12
        if years == 1:
            year_string = "1 year"
        else:
            year_string = f"{years} years"
        if months == 1:
            month_string = "1 month"
        else:
            month_string = f"{months} months"
        return f"{year_string}, {month_string}"
    else:
        if total_months == 1:
            return "1 month"
        elif total_days == 1:
            return "1 day"
        else:
            return f"{total_days} days"


@Aktivitas.get("/api/judul", tags=["Aktivitas_mhs"])
async def cek_judul(judul: str, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    juduls = get_all_judul(db)
    similarity_matrix = []
    for judul_db in juduls:
        sim = similarity(judul.lower(), judul_db.lower())
        similarity_matrix.append(
            {'judul_input': judul, 'judul_db': judul_db, 'similarity': round(sim, 2)})
    similarity_matrix = [
        similarity_item for similarity_item in similarity_matrix if similarity_item['similarity'] > 85]

    # return similarity_matrix
    if len(similarity_matrix) == 0:
        return {"message": "Judul masih original"}
    else:
        return similarity_matrix


@Aktivitas.get("/api/judul/{id_prodi}", tags=["Aktivitas_mhs"])
async def get_judul_by_id_prodi(id_prodi: int, judul: str, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")
    juduls = get_judul_by_id_prodi_judul(db, id_prodi=id_prodi)
    similarity_matrix = []
    for judul_db in juduls:
        sim = similarity(judul.lower(), judul_db.lower())

        similarity_matrix.append(
            {'judul_input': judul, 'judul_db': judul_db, 'similarity': round(sim, 2)})
    similarity_matrix = [
        similarity_item for similarity_item in similarity_matrix if similarity_item['similarity'] > 85]

    # return similarity_matrix
    if len(similarity_matrix) == 0:
        return {"message": "Judul masih original"}
    else:
        return similarity_matrix


@Aktivitas.post("/api/am", tags=["Aktivitas_mhs"], response_model=AddAktivitas)
async def add_aktivitas(am: AddAktivitas, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    data = AktivitasMhs(**am.dict())
    # hitung tanggal seminar dan tanggal ujian
    data.tanggal_seminar = hitung_jadwal_seminar(data.tanggal_sk_tugas)
    data.tanggal_ujian = hitung_jadwal_ujian(data.tanggal_seminar)

    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@Aktivitas.put("/api/am/{id}", tags=["Aktivitas_mhs"], response_model=UpdateAktivitas)
async def update_aktivitas(id: int, aktivitas: UpdateAktivitas, db: Session = Depends(get_db), IsAktiv=Depends(get_current_active_user)):
    if not IsAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    db_am = db.query(AktivitasMhs).filter(AktivitasMhs.id == id)

    if not db_am.first():
        raise HTTPException(
            status_code=404, detail="Aktivitas tidak ditemukan")

    db_am.update(aktivitas.dict(exclude_unset=True))
    db.commit()
    db.refresh(db_am.first())

    return db_am.first()


@Aktivitas.delete("/api/am/{id}", tags=["Aktivitas_mhs"], response_class=JSONResponse)
async def delete_Aktivitas_mahasiswa(id: int, db: Session = Depends(get_db), isAktiv: bool = Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat menghapus user, akun tidak aktif")
    try:
        prodi = db.query(AktivitasMhs).filter(AktivitasMhs.id == id).first()
        if not prodi:
            raise HTTPException(
                status_code=404, detail=f"User dengan id {id} tidak ditemukan")
        db.delete(prodi)
        db.commit()
        return {f"Prodi dengan Id {id} berhasil dihapus": True}
    except:
        raise HTTPException(
            status_code=500, detail="Terjadi kesalahan saat menghapus user")


@Aktivitas.get("/api/evaluasi", tags=["Aktivitas_mhs"])
async def analisis_Ipk(prodi: str, tahun: int, isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

    # Call external API to perform analysis
    url = f"https://api.unikarta.ac.id/api/ipk?prodi={prodi}&tahun={tahun}"
    headers = {'API-KEY': 'alkuja07'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()

    # return data
    filtered_data = list(filter(
        lambda x: x['status_mahasiswa'] == 'A' or x['status_mahasiswa'] == 'C', data))
    mahasiswa_dgn_peringatan = 0
    mahasiswa_dgn_warning = 0
    # Perform analysis and return data
    mahasiswa_dgn_peringatan = []
    for mahasiswa in filtered_data:
        sks_total = mahasiswa["sks_total"]
        if sks_total is not None:
            sks_total = int(sks_total)
            ipk = float(mahasiswa["ipk"])
            semester = int(mahasiswa["semester"])

            if semester == 1:
                if sks_total is not None and sks_total < 15:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Peringatan Pertama"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 2:
                if sks_total is not None and sks_total < 30:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Peringatan Pertama"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 3:
                if sks_total is not None and sks_total < 45:
                    mahasiswa['peringatan'] = " Evaluasi Kedua Pertama Prodi Memberikan Peringatan Tertulis"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 4:
                if sks_total is not None and sks_total < 60:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Surat Peringatan Kedua"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 5:
                if sks_total is not None and sks_total < 75:
                    mahasiswa['peringatan'] = " Ketua Prodi Memberikan Surat Peringatan Kedua"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 6:
                if sks_total is not None and sks_total < 90:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Surat Peringatan Kedua"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 7:
                if sks_total is not None and sks_total < 115:
                    mahasiswa['peringatan'] = "Evaluasi Kedua Ketua Prodi Memberikan Surat Peringatan Terakhir"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester == 8:
                if sks_total is not None and sks_total < 130:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Usulan DO"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"
            elif semester > 8:
                if sks_total is not None and sks_total < 145:
                    mahasiswa['peringatan'] = "Ketua Prodi Memberikan Usulan DO"
                    mahasiswa_dgn_peringatan.append(mahasiswa)
                if ipk is not None and ipk < 2.50:
                    mahasiswa['warning'] = "IPK Tidak Memeneuhi Standar Evaluasi"

    # return filtered_data
    # Calculate percentage of students with warning
    persentase_peringatan = (
        len(mahasiswa_dgn_peringatan) / len(filtered_data)) * 100

    # Return data
    output_data = {'persentase_peringatan': f"{persentase_peringatan:.2f}%",
                   'data': filtered_data}
    return output_data


@Aktivitas.get("/api/reg", tags=["Aktivitas_mhs"])
async def analisis_Ipk(tahun: str, kodeAkun: str,  prodi: str, isAktiv=Depends(get_current_active_user)):
    if not isAktiv:
        raise HTTPException(
            status_code=401, detail="Tidak dapat mengakses data user, akun tidak aktif")

       # Call external API to perform analysis
    # url = f"http://api.unikarta.ac.id/api/tunggakan?tahun=2022&kodeAkun=04&prodi=61201"
    url = f"http://api.unikarta.ac.id/api/tunggakan?tahun={tahun}&kodeAkun={kodeAkun}&prodi={prodi}"
    headers = {'API-KEY': 'alkuja07'}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
    # return data
    # Process the data
    results = process_data(data)

    return results


def process_data(data):
    results = {}
    for item in data:
        nim = item['nim']
        if nim not in results:
            results[nim] = {
                'nim': nim,
                'nama_mahasiswa': item['nama_mahasiswa'],
                'jumlah_tunggakan': 0,
                'jumlah_tagihan': 0,
                'tunggakan': []
            }

        tagihan = int(item['tagihan'])
        results[nim]['jumlah_tagihan'] += tagihan

        if tagihan > 0:
            results[nim]['jumlah_tunggakan'] += 1
            results[nim]['tunggakan'].append({
                'tagihan': item['tagihan'],
                'deskripsi_pendek': item['deskripsi_pendek'],
                'periode': item['periode'],
                'tahun_akademik': item['tahun_akademik']
            })

    # Remove students with no outstanding payment
    results = [result for result in results.values(
    ) if result['jumlah_tunggakan'] > 0]

    # Sort the results by NIM
    results = sorted(results, key=lambda x: x['nim'])

    # Format the results
    for result in results:
        tunggakan = result['tunggakan']
        if len(tunggakan) == 1 and tunggakan[0]['tagihan'] == '':
            tunggakan = []
        result['tunggakan'] = tunggakan

    return results
