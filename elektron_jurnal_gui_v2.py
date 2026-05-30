#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elektron Jurnal - GUI versiya (Tkinter + SQLite)
Yangi menyu tuzilishi bilan
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
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
        
        # Fanlar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fanlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_nomi TEXT NOT NULL UNIQUE,
                tavsif TEXT
            )
        ''')
        
        # Majburiyatlar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS majburiyatlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kursant_id INTEGER NOT NULL,
                majburiyat_nomi TEXT NOT NULL,
                muddat DATE,
                bajarildi BOOLEAN DEFAULT 0,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE
            )
        ''')

        
        # Baholar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS baholar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kursant_id INTEGER NOT NULL,
                fan_id INTEGER NOT NULL,
                baho INTEGER NOT NULL CHECK(baho >= 1 AND baho <= 5),
                sana DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE,
                FOREIGN KEY (fan_id) REFERENCES fanlar(id) ON DELETE CASCADE
            )
        ''')
        
        # Musobaqalar jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS musobaqalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musobaqa_nomi TEXT NOT NULL,
                sana DATE NOT NULL,
                joy TEXT,
                tavsif TEXT
            )
        ''')
        
        # Musobaqa natijalari
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS musobaqa_natijalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musobaqa_id INTEGER NOT NULL,
                kursant_id INTEGER NOT NULL,
                daraja TEXT,
                ball INTEGER,
                FOREIGN KEY (musobaqa_id) REFERENCES musobaqalar(id) ON DELETE CASCADE,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE
            )
        ''')
        
        # Amaliy mashqlar
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS amaliy_mashqlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mashq_nomi TEXT NOT NULL,
                tavsif TEXT,
                max_ball INTEGER DEFAULT 100
            )
        ''')
        
        # Amaliy mashq natijalari
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS amaliy_natijalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mashq_id INTEGER NOT NULL,
                kursant_id INTEGER NOT NULL,
                ball INTEGER,
                sana DATE DEFAULT CURRENT_DATE,
                izoh TEXT,
                FOREIGN KEY (mashq_id) REFERENCES amaliy_mashqlar(id) ON DELETE CASCADE,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE
            )
        ''')
        
        # Yugurish tayyorgarligi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS yugurish (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kursant_id INTEGER NOT NULL,
                masofa REAL NOT NULL,
                vaqt TEXT NOT NULL,
                sana DATE DEFAULT CURRENT_DATE,
                izoh TEXT,
                FOREIGN KEY (kursant_id) REFERENCES kursantlar(id) ON DELETE CASCADE
            )
        ''')
        
        self.connection.commit()
    
    # Kursantlar metodlari
    def kursant_qoshish(self, ism: str, familiya: str, guruh: str) -> int:
        self.cursor.execute(
            "INSERT INTO kursantlar (ism, familiya, guruh) VALUES (?, ?, ?)",
            (ism, familiya, guruh)
        )
        self.connection.commit()
        return self.cursor.lastrowid
    
    def barcha_kursantlar(self) -> List[Tuple]:
        self.cursor.execute("SELECT * FROM kursantlar ORDER BY guruh, familiya, ism")
        return self.cursor.fetchall()
    
    def kursant_topish(self, id: int) -> Optional[Tuple]:
        self.cursor.execute("SELECT * FROM kursantlar WHERE id = ?", (id,))
        return self.cursor.fetchone()
    
    def kursant_ochirish(self, id: int):
        self.cursor.execute("DELETE FROM kursantlar WHERE id = ?", (id,))
        self.connection.commit()
    
    # Fanlar metodlari
    def fan_qoshish(self, fan_nomi: str, tavsif: str = ""):
        self.cursor.execute(
            "INSERT INTO fanlar (fan_nomi, tavsif) VALUES (?, ?)",
            (fan_nomi, tavsif)
        )
        self.connection.commit()
        return self.cursor.lastrowid
    
    def barcha_fanlar(self) -> List[Tuple]:
        self.cursor.execute("SELECT * FROM fanlar ORDER BY fan_nomi")
        return self.cursor.fetchall()
    
    def fan_ochirish(self, id: int):
        self.cursor.execute("DELETE FROM fanlar WHERE id = ?", (id,))
        self.connection.commit()
    
    def yopish(self):
        if self.connection:
            self.connection.close()


class ElektronJurnalGUI:
    """Asosiy GUI dastur"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Elektron Jurnal - Harbiy Ta'lim Tizimi")
        self.root.geometry("1400x800")
        
        self.db = Database()
        self.joriy_sahifa = None
        
        self.interfeys_yaratish()
        self.kursantlar_sahifasini_korsatish()
    
    def interfeys_yaratish(self):
        """Asosiy interfeys yaratish"""
        # Sarlavha
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🎖️ ELEKTRON JURNAL - HARBIY TA'LIM TIZIMI",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=25)
        
        # Asosiy konteyner
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Chap menyu
        menu_frame = tk.Frame(main_container, bg="#34495e", width=250)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        menu_frame.pack_propagate(False)
        
        tk.Label(
            menu_frame,
            text="ASOSIY MENYU",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=20)
        
        # Menyu tugmalari
        menu_items = [
            ("👥 Kursantlar Ro'yxati", self.kursantlar_sahifasini_korsatish, "#27ae60"),
            ("📋 Majburiyatlar", self.majburiyatlar_sahifasini_korsatish, "#3498db"),
            ("📚 Fanlar", self.fanlar_sahifasini_korsatish, "#9b59b6"),
            ("📝 Baholash", self.baholash_sahifasini_korsatish, "#e67e22"),
            ("🏆 Musobaqalar", self.musobaqalar_sahifasini_korsatish, "#f39c12"),
            ("🎯 Amaliy Mashqlar", self.amaliy_mashqlar_sahifasini_korsatish, "#16a085"),
            ("🏃 Yugurish Tayyorgarligi", self.yugurish_sahifasini_korsatish, "#c0392b"),
        ]
        
        for text, command, color in menu_items:
            btn = tk.Button(
                menu_frame,
                text=text,
                command=command,
                font=("Arial", 11, "bold"),
                bg=color,
                fg="white",
                width=22,
                height=2,
                cursor="hand2",
                relief=tk.FLAT,
                anchor=tk.W,
                padx=15
            )
            btn.pack(pady=5, padx=10)
        
        # O'ng tomon - kontent maydoni
        self.content_frame = tk.Frame(main_container, bg="white")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
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

    
    def tozalash(self):
        """Kontent maydonini tozalash"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def kursantlar_sahifasini_korsatish(self):
        """Kursantlar ro'yxati sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "kursantlar"
        
        # Sarlavha
        title_frame = tk.Frame(self.content_frame, bg="#27ae60", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="👥 KURSANTLAR RO'YXATI",
            font=("Arial", 16, "bold"),
            bg="#27ae60",
            fg="white"
        ).pack(pady=15)
        
        # Tugmalar paneli
        btn_frame = tk.Frame(self.content_frame, bg="#ecf0f1", height=60)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_frame,
            text="➕ Yangi Kursant",
            command=self.yangi_kursant_dialog,
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="🗑️ O'chirish",
            command=self.kursant_ochirish,
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Jadval
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("ID", "Ism", "Familiya", "Guruh")
        self.kursantlar_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            height=20
        )
        
        scrollbar_y.config(command=self.kursantlar_tree.yview)
        
        for col in columns:
            self.kursantlar_tree.heading(col, text=col)
            self.kursantlar_tree.column(col, width=150, anchor=tk.CENTER)
        
        self.kursantlar_tree.pack(fill=tk.BOTH, expand=True)
        
        # Ma'lumotlarni yuklash
        self.kursantlar_yangilash()
    
    def kursantlar_yangilash(self):
        """Kursantlar jadvalini yangilash"""
        if hasattr(self, 'kursantlar_tree'):
            for item in self.kursantlar_tree.get_children():
                self.kursantlar_tree.delete(item)
            
            kursantlar = self.db.barcha_kursantlar()
            for k in kursantlar:
                self.kursantlar_tree.insert("", tk.END, values=k)
    
    def yangi_kursant_dialog(self):
        """Yangi kursant qo'shish dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Yangi Kursant")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Ism:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        ism_entry = tk.Entry(dialog, font=("Arial", 11), width=25)
        ism_entry.grid(row=0, column=1, padx=20, pady=10)
        
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
            
            if ism and familiya and guruh:
                self.db.kursant_qoshish(ism, familiya, guruh)
                messagebox.showinfo("Muvaffaqiyat", f"{ism} {familiya} qo'shildi!")
                dialog.destroy()
                self.kursantlar_yangilash()
            else:
                messagebox.showerror("Xato", "Barcha maydonlarni to'ldiring!")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Saqlash", command=saqlash, font=("Arial", 11),
                  bg="#27ae60", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Bekor qilish", command=dialog.destroy, font=("Arial", 11),
                  bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    
    def kursant_ochirish(self):
        """Kursantni o'chirish"""
        if hasattr(self, 'kursantlar_tree'):
            selected = self.kursantlar_tree.selection()
            if not selected:
                messagebox.showwarning("Ogohlantirish", "Kursantni tanlang!")
                return
            
            item = self.kursantlar_tree.item(selected[0])
            kursant_id = item['values'][0]
            ism = item['values'][1]
            familiya = item['values'][2]
            
            if messagebox.askyesno("Tasdiqlash", f"{ism} {familiya} ni o'chirishni tasdiqlaysizmi?"):
                self.db.kursant_ochirish(kursant_id)
                messagebox.showinfo("Muvaffaqiyat", "Kursant o'chirildi!")
                self.kursantlar_yangilash()
    
    def majburiyatlar_sahifasini_korsatish(self):
        """Majburiyatlar sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "majburiyatlar"
        
        title_frame = tk.Frame(self.content_frame, bg="#3498db", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="📋 MAJBURIYATLAR",
            font=("Arial", 16, "bold"),
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="Majburiyatlar bo'limi tez orada...",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=100)
    
    def fanlar_sahifasini_korsatish(self):
        """Fanlar sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "fanlar"
        
        title_frame = tk.Frame(self.content_frame, bg="#9b59b6", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="📚 FANLAR",
            font=("Arial", 16, "bold"),
            bg="#9b59b6",
            fg="white"
        ).pack(pady=15)
        
        # Tugmalar
        btn_frame = tk.Frame(self.content_frame, bg="#ecf0f1", height=60)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            btn_frame,
            text="➕ Yangi Fan",
            command=self.yangi_fan_dialog,
            font=("Arial", 10, "bold"),
            bg="#9b59b6",
            fg="white",
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Jadval
        table_frame = tk.Frame(self.content_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("ID", "Fan Nomi", "Tavsif")
        self.fanlar_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar_y.set,
            height=20
        )
        
        scrollbar_y.config(command=self.fanlar_tree.yview)
        
        for col in columns:
            self.fanlar_tree.heading(col, text=col)
        
        self.fanlar_tree.column("ID", width=50, anchor=tk.CENTER)
        self.fanlar_tree.column("Fan Nomi", width=200, anchor=tk.W)
        self.fanlar_tree.column("Tavsif", width=400, anchor=tk.W)
        
        self.fanlar_tree.pack(fill=tk.BOTH, expand=True)
        
        self.fanlar_yangilash()
    
    def fanlar_yangilash(self):
        """Fanlar jadvalini yangilash"""
        if hasattr(self, 'fanlar_tree'):
            for item in self.fanlar_tree.get_children():
                self.fanlar_tree.delete(item)
            
            fanlar = self.db.barcha_fanlar()
            for fan in fanlar:
                self.fanlar_tree.insert("", tk.END, values=fan)
    
    def yangi_fan_dialog(self):
        """Yangi fan qo'shish dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Yangi Fan")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Fan nomi:", font=("Arial", 11)).grid(row=0, column=0, padx=20, pady=10, sticky=tk.W)
        fan_entry = tk.Entry(dialog, font=("Arial", 11), width=30)
        fan_entry.grid(row=0, column=1, padx=20, pady=10)
        
        tk.Label(dialog, text="Tavsif:", font=("Arial", 11)).grid(row=1, column=0, padx=20, pady=10, sticky=tk.W)
        tavsif_entry = tk.Entry(dialog, font=("Arial", 11), width=30)
        tavsif_entry.grid(row=1, column=1, padx=20, pady=10)
        
        def saqlash():
            fan_nomi = fan_entry.get().strip()
            tavsif = tavsif_entry.get().strip()
            
            if fan_nomi:
                self.db.fan_qoshish(fan_nomi, tavsif)
                messagebox.showinfo("Muvaffaqiyat", f"{fan_nomi} fani qo'shildi!")
                dialog.destroy()
                self.fanlar_yangilash()
            else:
                messagebox.showerror("Xato", "Fan nomini kiriting!")
        
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Saqlash", command=saqlash, font=("Arial", 11),
                  bg="#9b59b6", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="❌ Bekor qilish", command=dialog.destroy, font=("Arial", 11),
                  bg="#e74c3c", fg="white", width=12).pack(side=tk.LEFT, padx=5)

    
    def baholash_sahifasini_korsatish(self):
        """Baholash sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "baholash"
        
        title_frame = tk.Frame(self.content_frame, bg="#e67e22", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="📝 BAHOLASH",
            font=("Arial", 16, "bold"),
            bg="#e67e22",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="Baholash bo'limi tez orada...",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=100)
    
    def musobaqalar_sahifasini_korsatish(self):
        """Musobaqalar sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "musobaqalar"
        
        title_frame = tk.Frame(self.content_frame, bg="#f39c12", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🏆 MUSOBAQALAR",
            font=("Arial", 16, "bold"),
            bg="#f39c12",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="Musobaqalar bo'limi tez orada...",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=100)
    
    def amaliy_mashqlar_sahifasini_korsatish(self):
        """Amaliy mashqlar sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "amaliy_mashqlar"
        
        title_frame = tk.Frame(self.content_frame, bg="#16a085", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🎯 AMALIY MASHQLAR",
            font=("Arial", 16, "bold"),
            bg="#16a085",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="Amaliy mashqlar bo'limi tez orada...",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=100)
    
    def yugurish_sahifasini_korsatish(self):
        """Yugurish tayyorgarligi sahifasi"""
        self.tozalash()
        self.joriy_sahifa = "yugurish"
        
        title_frame = tk.Frame(self.content_frame, bg="#c0392b", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🏃 YUGURISH TAYYORGARLIGI",
            font=("Arial", 16, "bold"),
            bg="#c0392b",
            fg="white"
        ).pack(pady=15)
        
        tk.Label(
            self.content_frame,
            text="Yugurish tayyorgarligi bo'limi tez orada...",
            font=("Arial", 14),
            fg="gray"
        ).pack(pady=100)


def main():
    """Dasturni ishga tushirish"""
    root = tk.Tk()
    app = ElektronJurnalGUI(root)
    
    def on_closing():
        app.db.yopish()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
