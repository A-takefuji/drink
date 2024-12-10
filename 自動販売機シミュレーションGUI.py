import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk  # Pillowライブラリを使用
import sqlite3


class VendingMachineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自動販売機")

        # データベース接続
        self.conn = sqlite3.connect("drink.db")
        self.cursor = self.conn.cursor()

        # パスワード取得
        self.cursor.execute("SELECT * FROM admins")
        row = self.cursor.fetchone()
        self.PASS = row[0] if row else ""

        # メインメニュー画面
        self.main_menu()

        # アプリ終了時の処理
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def main_menu(self):
        """メインメニューの描画"""
        self.clear_window()

        tk.Label(self.root, text="【メニュー一覧】", font=("Arial", 16)).pack(pady=10)

        menu_buttons = [
            ("商品の一覧表示", self.show_items),
            ("商品の購入", self.purchase_item),
            ("在庫の確認", self.check_stock),
            ("在庫の追加・削除", self.edit_stock),
            ("アプリの終了", self.close_app),
        ]

        for text, command in menu_buttons:
            tk.Button(self.root, text=text, font=("Arial", 14), command=command).pack(pady=5, fill="x")

    def show_items(self):
        """商品の一覧を表示する"""
        self.clear_window()
        tk.Label(self.root, text="【商品一覧】", font=("Arial", 16)).pack(pady=10)

        self.cursor.execute("SELECT id, name, price FROM items")
        rows = self.cursor.fetchall()

        for row in rows:
            tk.Label(self.root, text=f"ID: {row[0]} | 商品: {row[1]} | 価格: {row[2]}円").pack()

        tk.Button(self.root, text="メニューに戻る", command=self.main_menu).pack(pady=10)

    def purchase_item(self):
        """商品を画像付きで購入する"""
        self.clear_window()
        tk.Label(self.root, text="【商品の購入】", font=("Arial", 16)).pack(pady=10)

        # 商品情報を取得
        self.cursor.execute("SELECT id, name, price, image_path FROM items")
        items = self.cursor.fetchall()

        # 商品一覧を自動販売機風に表示
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        for item in items:
            item_id, name, price, image_path = item

            # 画像の読み込み
            try:
                image = Image.open(image_path)
                image = image.resize((60, 100))  # 画像をリサイズ
                photo = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"画像の読み込みに失敗しました: {e}")
                photo = None

            # 商品ボタン（画像付き）
            btn_frame = tk.Frame(frame)
            btn_frame.pack(side="left", padx=5, pady=5)

            if photo:
                img_button = tk.Button(btn_frame, image=photo, command=lambda i=item_id: self.confirm_purchase(i))
                img_button.image = photo  # 画像参照を保持
                img_button.pack()
            else:
                tk.Label(btn_frame, text="画像なし").pack()

            # 商品名と価格
            tk.Label(btn_frame, text=f"{name}\n{price}円", font=("Arial", 10)).pack()

        tk.Button(self.root, text="メニューに戻る", command=self.main_menu).pack(pady=10)

    def confirm_purchase(self, item_id):
        """商品の購入確認と処理"""
        self.cursor.execute("SELECT name, price, count FROM items WHERE id=?", (item_id,))
        item = self.cursor.fetchone()

        if not item:
            messagebox.showerror("エラー", "商品が見つかりません。")
            return

        name, price, stock = item

        if stock <= 0:
            messagebox.showerror("エラー", f"{name} は在庫切れです。")
            return

        quantity = simpledialog.askinteger("購入数", f"{name} を何個購入しますか？\n(在庫: {stock}個)", minvalue=1, maxvalue=stock)
        if not quantity:
            return  # ユーザーが購入数を入力しなかった場合は終了

        total_price = price * quantity
        money = simpledialog.askinteger("支払い", f"合計金額: {total_price}円\nお金を入れてください:")

        if not money or money < total_price:
            messagebox.showerror("エラー", "お金が不足しています。")
            return

        # 在庫とお釣りの計算
        new_stock = stock - quantity
        self.cursor.execute("UPDATE items SET count=? WHERE id=?", (new_stock, item_id))
        self.conn.commit()

        change = money - total_price
        messagebox.showinfo("購入完了", f"{name} を {quantity} 個購入しました。\nお釣り: {change}円")

    def check_stock(self):
        """在庫の確認"""
        self.clear_window()
        tk.Label(self.root, text="【在庫の確認】", font=("Arial", 16)).pack(pady=10)

        self.cursor.execute("SELECT id, name, count FROM items")
        rows = self.cursor.fetchall()

        for row in rows:
            tk.Label(self.root, text=f"ID: {row[0]} | 商品: {row[1]} | 在庫: {row[2]}個").pack()

        tk.Button(self.root, text="メニューに戻る", command=self.main_menu).pack(pady=10)

    def edit_stock(self):
        """在庫の追加・削除"""
        self.clear_window()
        tk.Label(self.root, text="【在庫の追加・削除】", font=("Arial", 16)).pack(pady=10)

        password = simpledialog.askstring("認証", "パスワードを入力してください:", show="*")
        if password != self.PASS:
            messagebox.showerror("エラー", "パスワードが違います。")
            self.main_menu()
            return

        tk.Label(self.root, text="商品ID:").pack()
        item_id_entry = tk.Entry(self.root)
        item_id_entry.pack()

        tk.Label(self.root, text="変更数 (+追加 / -削除):").pack()
        change_entry = tk.Entry(self.root)
        change_entry.pack()

        def confirm_edit():
            try:
                item_id = item_id_entry.get()
                change = int(change_entry.get())
                self.cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
                item = self.cursor.fetchone()

                if not item:
                    messagebox.showerror("エラー", "商品が見つかりません。")
                    return

                new_stock = max(0, item[3] + change)
                self.cursor.execute("UPDATE items SET count=? WHERE id=?", (new_stock, item_id))
                self.conn.commit()
                messagebox.showinfo("完了", f"{item[1]} の在庫を {new_stock} 個に更新しました。")
            except ValueError:
                messagebox.showerror("エラー", "変更数は整数で入力してください。")

        tk.Button(self.root, text="変更する", command=confirm_edit).pack(pady=10)
        tk.Button(self.root, text="メニューに戻る", command=self.main_menu).pack(pady=10)

    def clear_window(self):
        """現在のウィジェットを削除"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def close_app(self):
        """アプリ終了時の処理"""
        if messagebox.askyesno("確認", "本当に終了しますか？"):
            self.conn.close()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VendingMachineApp(root)
    root.mainloop()