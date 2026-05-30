#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elektron Jurnal - GUI versiya (Tkinter + SQLite)
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from typing import List, Tuple, Optional


class Database:
    """SQLite ma'lumotlar bazasi bilan ishlash"""
    
    def __init__(self, db_name: str = "elektron_jurnal.db"):
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.ulanish()
        self.jadvallar_yaratish()
    
    def ulanish(self):
        """Ma'lumotlar bazasiga ulanish"""
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
    
    def jadvallar_yaratish(self):
        """Jadvallarni yaratish"""
        # Kursantlar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS kursantlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ism TEXT NOT NULL,
                familiya TEXT NOT NULL,
                guruh TEXT NOT NULL
            )
        ''')
        
        # Davomat jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS davomat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kursant_id INTEGER NOT NULL,
                sana DATE NOT NULL,
                keldi BOOLEAN NOT NULL,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE,
                UNIQUE(kursant_id, sana)
            )
        ''')

        
        # Baholar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS baholar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kursant_id INTEGER NOT NULL,
                fan TEXT NOT NULL,
                baho INTEGER NOT NULL CHECK(baho >= 1 AND baho <= 5),
                sana DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE
            )
        ''')
        
        self.connection.commit()
    
    def kursant_qoshish(self, ism: str, familiya: str, guruh: str) -> int:
        """Yangi kursant qo'shish"""
        self.cursor.execute(
            "INSERT INTO kursantlar (ism, familiya, guruh) VALUES (?, ?, ?)",
            (ism, familiya, guruh)
        )
        self.connection.commit()
        return self.cursor.lastrowid
    
    def barcha_kursantlar(self) -> List[Tuple]:
        """Barcha kursantlarni olish"""
        self.cursor.execute("SELECT * FROM kursantlar ORDER BY guruh, familiya, ism")
        return self.cursor.fetchall()
    
    def kursant_topish(self, id: int) -> Optional[Tuple]:
        """ID bo'yicha kursant topish"""
        self.cursor.execute("SELECT * FROM kursantlar WHERE id = ?", (id,))
        return self.cursor.fetchone()
    
    def kursant_yangilash(self, id: int, ism: str, familiya: str, guruh: str):
        """Kursant ma'lumotlarini yangilash"""
        self.cursor.execute(
            "UPDATE kursantlar SET ism = ?, familiya = ?, guruh = ? WHERE id = ?",
            (ism, familiya, guruh, id)
        )
        self.connection.commit()
    
    def kursant_ochirish(self, id: int):
        """Kursantni o'chirish"""
        self.cursor.execute("DELETE FROM kursantlar WHERE id = ?", (id,))
        self.connection.commit()

    
    def davomat_belgilash(self, kursant_id: int, sana: str, keldi: bool):
        """Davomat belgilash yoki yangilash"""
        self.cursor.execute(
            "INSERT OR REPLACE INTO davomat (kursant_id, sana, keldi) VALUES (?, ?, ?)",
            (kursant_id, sana, 1 if keldi else 0)
        )
        self.connection.commit()
    
    def kursant_davomati(self, kursant_id: int) -> List[Tuple]:
        """Kursant davomat tarixini olish"""
        self.cursor.execute(
            "SELECT sana, keldi FROM davomat WHERE kursant_id = ? ORDER BY sana DESC",
            (kursant_id,)
        )
        return self.cursor.fetchall()
    
    def davomat_foizi(self, kursant_id: int) -> float:
        """Kursant davomat foizini hisoblash"""
        self.cursor.execute(
            "SELECT COUNT(*) as jami, SUM(keldi) as kelgan FROM davomat WHERE kursant_id = ?",
            (kursant_id,)
        )
        result = self.cursor.fetchone()
        if result and result[0] > 0:
            return (result[1] / result[0]) * 100
        return 0.0
    
    def baho_qoshish(self, kursant_id: int, fan: str, baho: int):
        """Baho qo'shish"""
        self.cursor.execute(
            "INSERT INTO baholar (kursant_id, fan, baho) VALUES (?, ?, ?)",
            (kursant_id, fan, baho)
        )
        self.connection.commit()
    
    def kursant_baholari(self, kursant_id: int) -> List[Tuple]:
        """Kursant baholarini olish"""
        self.cursor.execute(
            "SELECT fan, baho, sana FROM baholar WHERE kursant_id = ? ORDER BY sana DESC",
            (kursant_id,)
        )
        return self.cursor.fetchall()
    
    def ortacha_baho(self, kursant_id: int, fan: Optional[str] = None) -> float:
        """O'rtacha bahoni hisoblash"""
        if fan:
            self.cursor.execute(
                "SELECT AVG(baho) FROM baholar WHERE kursant_id = ? AND fan = ?",
                (kursant_id, fan)
            )
        else:
            self.cursor.execute(
                "SELECT AVG(baho) FROM baholar WHERE kursant_id = ?",
                (kursant_id,)
            )
        result = self.cursor.fetchone()
        return result[0] if result[0] else 0.0

    
    def guruh_boyicha_kursantlar(self, guruh: str) -> List[Tuple]:
        """Guruh bo'yicha kursantlarni olish"""
        self.cursor.execute(
            "SELECT * FROM kursantlar WHERE guruh = ? ORDER BY familiya, ism",
            (guruh,)
        )
        return self.cursor.fetchall()
    
    def barcha_guruhlar(self) -> List[str]:
        """Barcha guruhlar ro'yxati"""
        self.cursor.execute("SELECT DISTINCT guruh FROM kursantlar ORDER BY guruh")
        return [row[0] for row in self.cursor.fetchall()]
    
    def umumiy_statistika(self) -> dict:
        """Umumiy statistika"""
        stats = {}
        
        # Jami kursantlar
        self.cursor.execute("SELECT COUNT(*) FROM kursantlar")
        stats['jami_kursantlar'] = self.cursor.fetchone()[0]
        
        # Guruhlar soni
        self.cursor.execute("SELECT COUNT(DISTINCT guruh) FROM kursantlar")
        stats['guruhlar_soni'] = self.cursor.fetchone()[0]
        
        # O'rtacha baho
        self.cursor.execute("SELECT AVG(baho) FROM baholar")
        result = self.cursor.fetchone()[0]
        stats['ortacha_baho'] = result if result else 0.0
        
        # O'rtacha davomat
        self.cursor.execute("SELECT AVG(keldi) * 100 FROM davomat")
        result = self.cursor.fetchone()[0]
        stats['ortacha_davomat'] = result if result else 0.0
        
        return stats
    
    def yopish(self):
        """Ma'lumotlar bazasini yopish"""
        if self.connection:
            self.connection.close()




class ElektronJurnalGUI:
    """Asosiy GUI dastur"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Elektron Jurnal - Kursantlar Boshqaruvi")
        self.root.geometry("1200x700")
        
        # Ma'lumotlar bazasi
        self.db = Database()
        
        # Asosiy interfeys
        self.interfeys_yaratish()
        self.kursantlar_yangilash()
    
    def interfeys_yaratish(self):
        """Interfeys elementlarini yaratish"""
        # Yuqori panel - Tugmalar
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        # Sarlavha
        title_label = tk.Label(
            top_frame, 
            text="📚 ELEKTRON JURNAL", 
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Tugmalar paneli
        button_frame = tk.Frame(self.root, bg="#ecf0f1", height=100)
        button_frame.pack(fill=tk.X, pady=10)
        button_frame.pack_propagate(False)
        
        buttons = [
            ("➕ Yangi Kursant", self.yangi_kursant_dialog, "#27ae60"),
            ("✏️ Tahrirlash", self.kursant_tahrirlash, "#3498db"),
            ("🗑️ O'chirish", self.kursant_ochirish, "#e74c3c"),
            ("📅 Davomat", self.davomat_dialog, "#f39c12"),
            ("📝 Baho Qo'yish", self.baho_dialog, "#9b59b6"),
            ("📊 Statistika", self.kursant_statistika, "#1abc9c"),
            ("📈 Umumiy Statistika", self.umumiy_statistika_dialog, "#16a085"),
            ("🔍 Filtr", self.filtr_dialog, "#34495e"),
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                command=command,
                font=("Arial", 10, "bold"),
                bg=color,
                fg="white",
                width=15,
                height=2,
                cursor="hand2",
                relief=tk.RAISED,
                bd=2
            )
            btn.pack(side=tk.LEFT, padx=5, pady=10)

        
        # Qidiruv paneli
        search_frame = tk.Frame(self.root, bg="#ecf0f1")
        search_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(search_frame, text="🔍 Qidiruv:", font=("Arial", 10), bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.kursantlar_yangilash())
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 11), width=30)
        search_entry.pack(side=tk.LEFT, padx=5, pady=10)
        
        tk.Button(
            search_frame,
            text="♻️ Yangilash",
            command=self.kursantlar_yangilash,
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        # Jadval
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ("ID", "Ism", "Familiya", "Guruh", "O'rtacha Baho", "Davomat %")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set,
            height=20
        )
        
        scrollbar_y.config(command=self.tree.yview)
        scrollbar_x.config(command=self.tree.xview)
        
        # Ustun sarlavhalari
        widths = [50, 150, 150, 100, 120, 120]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col, anchor=tk.CENTER)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # Joylash
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Jadval ranglari
        self.tree.tag_configure("oddrow", background="#ecf0f1")
        self.tree.tag_configure("evenrow", background="white")

        
        # Pastki status bar
        status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = tk.Label(
            status_frame,
            text="✓ Tayyor",
            font=("Arial", 9),
            bg="#34495e",
            fg="white",
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def kursantlar_yangilash(self):
        """Kursantlar jadvalini yangilash"""
        # Avvalgi ma'lumotlarni tozalash
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Qidiruv matnini olish
        search_text = self.search_var.get().lower()
        
        # Kursantlarni olish
        kursantlar = self.db.barcha_kursantlar()
        
        # Filtrlash va ko'rsatish
        count = 0
        for k in kursantlar:
            id, ism, familiya, guruh = k
            
            # Qidiruv filtri
            if search_text:
                if search_text not in ism.lower() and \
                   search_text not in familiya.lower() and \
                   search_text not in guruh.lower():
                    continue
            
            # Statistika
            ortacha = self.db.ortacha_baho(id)
            davomat = self.db.davomat_foizi(id)
            
            # Qatorga qo'shish
            tag = "evenrow" if count % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(id, ism, familiya, guruh, f"{ortacha:.2f}", f"{davomat:.1f}%"),
                tags=(tag,)
            )
            count += 1
        
        self.status_label.config(text=f"✓ {count} ta kursant ko'rsatilmoqda")

    
    def tanlangan_kursant_id(self) -> Optional[int]:
        """Tanlangan kursant ID sini qaytarish"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ogohlantirish", "Iltimos, kursantni tanlang!")
            return None
        
        item = self.tree.item(selected[0])
        return int(item['values'][0])
    
    def yangi_kursant_dialog(self):
        """Yangi kursant qo'shish dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Yangi Kursant Qo'shish")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Markazga joylashtirish
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form
        tk.Label(dialog, text="Ism:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        ism_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        ism_entry.grid(row=0, column=1, padx=20, pady=10)
        ism_entry.focus()
        
        tk.Label(dialog, text="Familiya:", font=("Arial", 11)).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        familiya_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        familiya_entry.grid(row=1, column=1, padx=20, pady=10)
        
        tk.Label(dialog, text="Guruh:", font=("Arial", 11)).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        guruh_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        guruh_entry.grid(row=2, column=1, padx=20, pady=10)
        
        def saqlash():
            ism = ism_entry.get().strip()
            familiya = familiya_entry.get().strip()
            guruh = guruh_entry.get().strip()
            
            if not ism or not familiya or not guruh:
                messagebox.showerror("Xato", "Barcha maydonlarni to'ldiring!")
                return
            
            self.db.kursant_qoshish(ism, familiya, guruh)
            messagebox.showinfo("Muvaffaqiyat", f"{ism} {familiya} qo'shildi!")
            dialog.destroy()
            self.kursantlar_yangilash()
        
        # Tugmalar
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Saqlash", command=saqlash, font=("Arial", 11), 
                  bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Bekor qilish", command=dialog.destroy, font=("Arial", 11),
                  bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    
    def kursant_tahrirlash(self):
        """Kursant ma'lumotlarini tahrirlash"""
        kursant_id = self.tanlangan_kursant_id()
        if not kursant_id:
            return
        
        kursant = self.db.kursant_topish(kursant_id)
        if not kursant:
            messagebox.showerror("Xato", "Kursant topilmadi!")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Kursant Ma'lumotlarini Tahrirlash")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        _, ism, familiya, guruh = kursant
        
        # Form
        tk.Label(dialog, text="Ism:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        ism_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        ism_entry.insert(0, ism)
        ism_entry.grid(row=0, column=1, padx=20, pady=10)
        
        tk.Label(dialog, text="Familiya:", font=("Arial", 11)).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        familiya_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        familiya_entry.insert(0, familiya)
        familiya_entry.grid(row=1, column=1, padx=20, pady=10)
        
        tk.Label(dialog, text="Guruh:", font=("Arial", 11)).grid(row=2, column=0, padx=20, pady=10, sticky=tk.W)
        guruh_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        guruh_entry.insert(0, guruh)
        guruh_entry.grid(row=2, column=1, padx=20, pady=10)
        
        def yangilash():
            yangi_ism = ism_entry.get().strip()
            yangi_familiya = familiya_entry.get().strip()
            yangi_guruh = guruh_entry.get().strip()
            
            if not yangi_ism or not yangi_familiya or not yangi_guruh:
                messagebox.showerror("Xato", "Barcha maydonlarni to'ldiring!")
                return
            
            self.db.kursant_yangilash(kursant_id, yangi_ism, yangi_familiya, yangi_guruh)
            messagebox.showinfo("Muvaffaqiyat", "Ma'lumotlar yangilandi!")
            dialog.destroy()
            self.kursantlar_yangilash()
        
        # Tugmalar
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Saqlash", command=yangilash, font=("Arial", 11),
                  bg="#3498db", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Bekor qilish", command=dialog.destroy, font=("Arial", 11),
                  bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    
    def kursant_ochirish(self):
        """Kursantni o'chirish"""
        kursant_id = self.tanlangan_kursant_id()
        if not kursant_id:
            return
        
        kursant = self.db.kursant_topish(kursant_id)
        if not kursant:
            return
        
        _, ism, familiya, guruh = kursant
        
        javob = messagebox.askyesno(
            "Tasdiqlash",
            f"'{ism} {familiya}' ni o'chirishni tasdiqlaysizmi?\n\n"
            f"Diqqat: Barcha davomat va baho ma'lumotlari ham o'chiriladi!"
        )
        
        if javob:
            self.db.kursant_ochirish(kursant_id)
            messagebox.showinfo("Muvaffaqiyat", "Kursant o'chirildi!")
            self.kursantlar_yangilash()
    
    def davomat_dialog(self):
        """Davomat belgilash dialog"""
        kursant_id = self.tanlangan_kursant_id()
        if not kursant_id:
            return
        
        kursant = self.db.kursant_topish(kursant_id)
        if not kursant:
            return
        
        _, ism, familiya, guruh = kursant
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📅 Davomat - {ism} {familiya}")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Info
        info_frame = tk.Frame(dialog, bg="#3498db", height=60)
        info_frame.pack(fill=tk.X)
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame,
            text=f"Kursant: {ism} {familiya} ({guruh})",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        # Yangi davomat qo'shish
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(form_frame, text="Sana:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        bugun = datetime.now().strftime("%Y-%m-%d")
        sana_entry = tk.Entry(form_frame, font=("Arial", 10), width=15)
        sana_entry.insert(0, bugun)
        sana_entry.grid(row=0, column=1, padx=10, pady=5)
        
        keldi_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form_frame, text="Keldi", variable=keldi_var, font=("Arial", 10)).grid(row=0, column=2, padx=10)
        
        def davomat_saqlash():
            sana = sana_entry.get().strip()
            if not sana:
                messagebox.showerror("Xato", "Sanani kiriting!")
                return
            
            self.db.davomat_belgilash(kursant_id, sana, keldi_var.get())
            messagebox.showinfo("Muvaffaqiyat", "Davomat belgilandi!")
            sana_entry.delete(0, tk.END)
            sana_entry.insert(0, bugun)
            davomat_yangilash()
            self.kursantlar_yangilash()
        
        tk.Button(form_frame, text="💾 Saqlash", command=davomat_saqlash, font=("Arial", 10),
                  bg="#27ae60", fg="white", width=10).grid(row=0, column=3, padx=10)

        
        # Davomat tarixi
        tk.Label(dialog, text="Davomat Tarixi:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        davomat_list = tk.Listbox(list_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        davomat_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=davomat_list.yview)
        
        def davomat_yangilash():
            davomat_list.delete(0, tk.END)
            davomat_data = self.db.kursant_davomati(kursant_id)
            
            if not davomat_data:
                davomat_list.insert(tk.END, "Hozircha davomat yo'q")
            else:
                for sana, keldi in davomat_data:
                    holat = "✓ Keldi  " if keldi else "✗ Kelmadi"
                    davomat_list.insert(tk.END, f"{sana}  →  {holat}")
        
        davomat_yangilash()
    
    def baho_dialog(self):
        """Baho qo'yish dialog"""
        kursant_id = self.tanlangan_kursant_id()
        if not kursant_id:
            return
        
        kursant = self.db.kursant_topish(kursant_id)
        if not kursant:
            return
        
        _, ism, familiya, guruh = kursant
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📝 Baho Qo'yish - {ism} {familiya}")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Info
        info_frame = tk.Frame(dialog, bg="#9b59b6", height=60)
        info_frame.pack(fill=tk.X)
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame,
            text=f"Kursant: {ism} {familiya} ({guruh})",
            font=("Arial", 12, "bold"),
            bg="#9b59b6",
            fg="white"
        ).pack(pady=15)
        
        # Yangi baho qo'shish
        form_frame = tk.Frame(dialog)
        form_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(form_frame, text="Fan:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        fan_entry = tk.Entry(form_frame, font=("Arial", 10), width=20)
        fan_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(form_frame, text="Baho:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.W, pady=5)
        baho_var = tk.IntVar(value=5)
        baho_spinbox = tk.Spinbox(form_frame, from_=1, to=5, textvariable=baho_var, font=("Arial", 10), width=5)
        baho_spinbox.grid(row=0, column=3, padx=10, pady=5)

        
        def baho_saqlash():
            fan = fan_entry.get().strip()
            baho = baho_var.get()
            
            if not fan:
                messagebox.showerror("Xato", "Fan nomini kiriting!")
                return
            
            if not (1 <= baho <= 5):
                messagebox.showerror("Xato", "Baho 1 dan 5 gacha bo'lishi kerak!")
                return
            
            self.db.baho_qoshish(kursant_id, fan, baho)
            messagebox.showinfo("Muvaffaqiyat", f"{fan} fanidan {baho} baho qo'shildi!")
            fan_entry.delete(0, tk.END)
            baho_var.set(5)
            baholar_yangilash()
            self.kursantlar_yangilash()
        
        tk.Button(form_frame, text="💾 Saqlash", command=baho_saqlash, font=("Arial", 10),
                  bg="#27ae60", fg="white", width=10).grid(row=0, column=4, padx=10)
        
        # Baholar tarixi
        tk.Label(dialog, text="Baholar Tarixi:", font=("Arial", 11, "bold")).pack(pady=(10, 5))
        
        list_frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        baholar_list = tk.Listbox(list_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        baholar_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=baholar_list.yview)
        
        def baholar_yangilash():
            baholar_list.delete(0, tk.END)
            baholar_data = self.db.kursant_baholari(kursant_id)
            
            if not baholar_data:
                baholar_list.insert(tk.END, "Hozircha baholar yo'q")
            else:
                for fan, baho, sana in baholar_data:
                    baholar_list.insert(tk.END, f"{sana}  →  {fan:<20}  Baho: {baho}")
        
        baholar_yangilash()

    
    def kursant_statistika(self):
        """Kursant statistikasi dialog"""
        kursant_id = self.tanlangan_kursant_id()
        if not kursant_id:
            return
        
        kursant = self.db.kursant_topish(kursant_id)
        if not kursant:
            return
        
        _, ism, familiya, guruh = kursant
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📊 Statistika - {ism} {familiya}")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        
        # Header
        header_frame = tk.Frame(dialog, bg="#1abc9c", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text=f"📊 {ism} {familiya}",
            font=("Arial", 16, "bold"),
            bg="#1abc9c",
            fg="white"
        ).pack(pady=10)
        
        tk.Label(
            header_frame,
            text=f"Guruh: {guruh}",
            font=("Arial", 11),
            bg="#1abc9c",
            fg="white"
        ).pack()
        
        # Statistika
        stats_frame = tk.Frame(dialog, bg="white")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # O'rtacha baho
        ortacha_baho = self.db.ortacha_baho(kursant_id)
        davomat_foizi = self.db.davomat_foizi(kursant_id)
        
        tk.Label(
            stats_frame,
            text="UMUMIY STATISTIKA",
            font=("Arial", 13, "bold"),
            bg="white"
        ).pack(pady=(10, 20))
        
        stats_text = f"""
        📚 O'rtacha Baho: {ortacha_baho:.2f}
        
        📅 Davomat Foizi: {davomat_foizi:.1f}%
        
        """
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=("Arial", 12),
            bg="white",
            justify=tk.LEFT
        ).pack()
        
        # Fanlar bo'yicha baholar
        baholar_data = self.db.kursant_baholari(kursant_id)
        
        if baholar_data:
            tk.Label(
                stats_frame,
                text="FANLAR BO'YICHA",
                font=("Arial", 13, "bold"),
                bg="white"
            ).pack(pady=(20, 10))
            
            # Fanlar bo'yicha guruhlash
            fanlar = {}
            for fan, baho, _ in baholar_data:
                if fan not in fanlar:
                    fanlar[fan] = []
                fanlar[fan].append(baho)
            
            fan_text = ""
            for fan, baholar in fanlar.items():
                ortacha = sum(baholar) / len(baholar)
                fan_text += f"\n  • {fan}: {ortacha:.2f} (Baholar: {len(baholar)})\n"
            
            tk.Label(
                stats_frame,
                text=fan_text,
                font=("Arial", 11),
                bg="white",
                justify=tk.LEFT
            ).pack()

    
    def umumiy_statistika_dialog(self):
        """Umumiy statistika dialog"""
        stats = self.db.umumiy_statistika()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("📈 Umumiy Statistika")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        
        # Header
        header_frame = tk.Frame(dialog, bg="#16a085", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="📈 UMUMIY STATISTIKA",
            font=("Arial", 16, "bold"),
            bg="#16a085",
            fg="white"
        ).pack(pady=20)
        
        # Stats
        stats_frame = tk.Frame(dialog, bg="white")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        stats_text = f"""
        👥 Jami Kursantlar: {stats['jami_kursantlar']}
        
        🏫 Guruhlar Soni: {stats['guruhlar_soni']}
        
        📚 O'rtacha Baho: {stats['ortacha_baho']:.2f}
        
        📅 O'rtacha Davomat: {stats['ortacha_davomat']:.1f}%
        
        """
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=("Arial", 14),
            bg="white",
            justify=tk.LEFT
        ).pack(pady=20)
        
        # Guruhlar bo'yicha taqsimot
        guruhlar = self.db.barcha_guruhlar()
        
        if guruhlar:
            tk.Label(
                stats_frame,
                text="GURUHLAR BO'YICHA",
                font=("Arial", 13, "bold"),
                bg="white"
            ).pack(pady=(20, 10))
            
            for guruh in guruhlar:
                kursantlar = self.db.guruh_boyicha_kursantlar(guruh)
                tk.Label(
                    stats_frame,
                    text=f"  • {guruh}: {len(kursantlar)} ta kursant",
                    font=("Arial", 11),
                    bg="white",
                    justify=tk.LEFT
                ).pack()
    
    def filtr_dialog(self):
        """Filtr dialog - guruh bo'yicha filtrlash"""
        guruhlar = self.db.barcha_guruhlar()
        
        if not guruhlar:
            messagebox.showinfo("Ma'lumot", "Hozircha guruhlar yo'q")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("🔍 Guruh Bo'yicha Filtrlash")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Guruhni tanlang:", font=("Arial", 12, "bold")).pack(pady=15)
        
        listbox = tk.Listbox(dialog, font=("Arial", 11), height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox.insert(tk.END, "BARCHA KURSANTLAR")
        for guruh in guruhlar:
            kursantlar = self.db.guruh_boyicha_kursantlar(guruh)
            listbox.insert(tk.END, f"{guruh} ({len(kursantlar)} ta)")

        
        def filtr_qollash():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Ogohlantirish", "Guruhni tanlang!")
                return
            
            tanlangan = listbox.get(selection[0])
            
            if tanlangan == "BARCHA KURSANTLAR":
                self.search_var.set("")
            else:
                guruh = tanlangan.split(" (")[0]
                self.search_var.set(guruh)
            
            dialog.destroy()
            self.kursantlar_yangilash()
        
        tk.Button(
            dialog,
            text="✓ Qo'llash",
            command=filtr_qollash,
            font=("Arial", 11),
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(pady=10)


def main():
    """Dasturni ishga tushirish"""
    root = tk.Tk()
    app = ElektronJurnalGUI(root)
    
    # Dasturni yopishda ma'lumotlar bazasini yopish
    def on_closing():
        app.db.yopish()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
