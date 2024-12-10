# 自動販売機シミュレーション初期設定
import sqlite3

if __name__ == '__main__':

    bl = True # メニュー終了判定変数
    
    # SQLiteデータベースへの接続
    conn = sqlite3.connect("drink.db")  # データベースファイル
    
    # クエリの実行
    cursor = conn.cursor()
    
    # テーブル作成
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER, name TEXT, price INTEGER, count INTEGER, image_path TEXT)")
    
    # 初期パスワードの設定
    password = input('初期パスワードを設定してください \n')
    cursor.execute("INSERT INTO admins VALUES ('" + password + "')")
    

    # 初期商品の登録
    cursor.execute("INSERT INTO items VALUES (1, 'お茶', 130, 10, 'C:\img\Tea.png')")
    cursor.execute("INSERT INTO items VALUES (2, '水', 100, 10, 'C:\img\water.png')")
    cursor.execute("INSERT INTO items VALUES (3, 'コーラ', 140, 10, 'C:\img\cola.png')")
    cursor.execute("INSERT INTO items VALUES (4, 'オレンジジュース', 120, 10, 'C:\img\orange.png')")
    cursor.execute("INSERT INTO items VALUES (5, 'コーヒー', 110, 10, 'C:\img\coffe.png')")
    
    # データベースに反映
    conn.commit()
    
    # 接続を閉じる
    cursor.close()
    conn.close()