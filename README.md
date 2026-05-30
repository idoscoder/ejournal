# 📚 Elektron Jurnal - Kursantlar Boshqaruvi Tizimi

Python tilida yaratilgan zamonaviy elektron jurnal dasturi. Tkinter kutubxonasi bilan grafik interfeys va SQLite ma'lumotlar bazasi ishlatilgan.

## ✨ Imkoniyatlar

### 👥 Kursantlar Boshqaruvi
- ➕ Yangi kursant qo'shish
- ✏️ Kursant ma'lumotlarini tahrirlash
- 🗑️ Kursantni o'chirish
- 🔍 Kursantlarni qidirish
- 📋 Barcha kursantlarni ko'rish

### 📅 Davomat Tizimi
- Kunlik davomat belgilash
- Davomat tarixini ko'rish
- Davomat foizini avtomatik hisoblash
- Sana bo'yicha davomat qo'shish

### 📝 Baholar Tizimi
- Turli fanlar bo'yicha baho qo'yish
- Baholar tarixini ko'rish
- Har bir fan uchun o'rtacha bahoni hisoblash
- Umumiy o'rtacha bahoni aniqlash

### 📊 Statistika va Hisobotlar
- Har bir kursant uchun individual statistika
- Umumiy statistika (barcha kursantlar)
- Guruhlar bo'yicha taqsimot
- O'rtacha baholar va davomat foizi

### 🔍 Filtr va Qidiruv
- Ism, familiya yoki guruh bo'yicha qidirish
- Guruh bo'yicha filtrlash
- Real-time qidiruv

## 🛠️ Texnologiyalar

- **Python 3.x** - Dasturlash tili
- **Tkinter** - Grafik interfeys kutubxonasi
- **SQLite** - Ma'lumotlar bazasi

## 📦 O'rnatish

### 1. Python o'rnatish
Python 3.6 yoki undan yuqori versiyasi talab qilinadi:
```bash
python --version
```

### 2. Kerakli kutubxonalar
Tkinter va SQLite Python bilan birga keladi, qo'shimcha o'rnatish shart emas.

### 3. Dasturni yuklab olish
```bash
git clone [repository_url]
cd elektron_jurnal
```

## 🚀 Ishga Tushirish

```bash
python elektron_jurnal_gui.py
```

## 📖 Foydalanish Qo'llanmasi

### Yangi Kursant Qo'shish
1. "➕ Yangi Kursant" tugmasini bosing
2. Ism, familiya va guruhni kiriting
3. "💾 Saqlash" tugmasini bosing

### Davomat Belgilash
1. Jadvaldan kursantni tanlang
2. "📅 Davomat" tugmasini bosing
3. Sanani kiriting (yoki bugungi kun avtomatik qo'yiladi)
4. "Keldi" checkboxini belgilang yoki bo'shatib qoldiring
5. "💾 Saqlash" tugmasini bosing

### Baho Qo'yish
1. Jadvaldan kursantni tanlang
2. "📝 Baho Qo'yish" tugmasini bosing
3. Fan nomini kiriting
4. Bahoni tanlang (1 dan 5 gacha)
5. "💾 Saqlash" tugmasini bosing

### Statistika Ko'rish
- **Kursant statistikasi:** Kursantni tanlab, "📊 Statistika" tugmasini bosing
- **Umumiy statistika:** "📈 Umumiy Statistika" tugmasini bosing

### Qidiruv va Filtr
- Qidiruv maydoniga matn kiriting (ism, familiya yoki guruh)
- "🔍 Filtr" tugmasi orqali guruh bo'yicha filtrlash

## 📁 Fayl Tuzilmasi

```
elektron_jurnal/
│
├── elektron_jurnal_gui.py    # Asosiy GUI dastur
├── elektron_jurnal.py         # Konsol versiya (eski)
├── elektron_jurnal.db         # SQLite ma'lumotlar bazasi (avtomatik yaratiladi)
└── README.md                  # Dokumentatsiya
```

## 🗄️ Ma'lumotlar Bazasi Tuzilmasi

### Jadvallar

#### kursantlar
| Ustun    | Turi    | Tavsif                  |
|----------|---------|-------------------------|
| id       | INTEGER | Asosiy kalit (PRIMARY KEY) |
| ism      | TEXT    | Kursant ismi            |
| familiya | TEXT    | Kursant familiyasi      |
| guruh    | TEXT    | Guruh nomi              |

#### davomat
| Ustun       | Turi    | Tavsif                     |
|-------------|---------|----------------------------|
| id          | INTEGER | Asosiy kalit               |
| kursant_id  | INTEGER | Kursant ID (FOREIGN KEY)   |
| sana        | DATE    | Davomat sanasi             |
| keldi       | BOOLEAN | Keldi (1) yoki Kelmadi (0) |

#### baholar
| Ustun       | Turi    | Tavsif                   |
|-------------|---------|--------------------------|
| id          | INTEGER | Asosiy kalit             |
| kursant_id  | INTEGER | Kursant ID (FOREIGN KEY) |
| fan         | TEXT    | Fan nomi                 |
| baho        | INTEGER | Baho (1-5)               |
| sana        | DATE    | Baho qo'yilgan sana      |

## 🎨 Interfeys Ranglari

- **Yashil (#27ae60)** - Qo'shish va saqlash
- **Ko'k (#3498db)** - Tahrirlash
- **Qizil (#e74c3c)** - O'chirish va bekor qilish
- **To'q sariq (#f39c12)** - Davomat
- **Binafsha (#9b59b6)** - Baho qo'yish
- **Yashil-ko'k (#1abc9c, #16a085)** - Statistika
- **Kulrang (#34495e)** - Filtr

## ⚙️ Xususiyatlar

- ✅ Grafik interfeys (GUI)
- ✅ SQLite ma'lumotlar bazasi
- ✅ Avtomatik ma'lumotlarni saqlash
- ✅ Real-time qidiruv
- ✅ Rang-barang interfeys
- ✅ O'zbek tilida
- ✅ O'chirish orqali CASCADE (bog'liq ma'lumotlar ham o'chadi)
- ✅ Validatsiya (baho 1-5, majburiy maydonlar)

## 🔒 Xavfsizlik

- Ma'lumotlar mahalliy SQLite bazasida saqlanadi
- CASCADE o'chirish - kursant o'chirilganda barcha bog'liq ma'lumotlar ham o'chadi
- UNIQUE constraint - bir kursantga bir kunda faqat bitta davomat yozuvi

## 🐛 Muammolarni Hal Qilish

### Dastur ishga tushmayapti
```bash
# Python versiyasini tekshiring
python --version

# Tkinter o'rnatilganini tekshiring
python -c "import tkinter"
```

### Ma'lumotlar bazasi xatosi
Agar ma'lumotlar bazasi buzilgan bo'lsa, `elektron_jurnal.db` faylini o'chiring va dasturni qayta ishga tushiring.

## 📝 Litsenziya

Bu dastur o'quv maqsadlari uchun yaratilgan va erkin foydalanish uchun ochiq.

## 👨‍💻 Muallif

Python dasturlash kursi loyihasi

## 🤝 Hissa Qo'shish

Takliflar va xatolarni bildirish uchun issue yarating yoki pull request yuboring.

---

**Dastur haqida savollaringiz bo'lsa, murojaat qiling!** 📧
