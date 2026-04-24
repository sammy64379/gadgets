import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(r'c:\Users\sammy\OneDrive\Desktop\electronics e commerce\app\test.db')
c = conn.cursor()

# Search for cameras
c.execute("SELECT id, name, category, price, image FROM items WHERE category LIKE '%camera%' OR name LIKE '%camera%' OR name LIKE '%canon%' OR name LIKE '%nikon%' OR name LIKE '%fujifilm%' OR name LIKE '%EOS%' OR name LIKE '%sony alpha%'")
rows = c.fetchall()
if rows:
    print("=== Cameras in DB ===")
    for r in rows:
        print(f'ID={r[0]} | {r[1]} | cat={r[2]} | price={r[3]} | img={r[4]}')
else:
    print('No cameras found.')

print("\n=== All categories ===")
c.execute('SELECT DISTINCT category FROM items')
for r in c.fetchall():
    print(f'  {r[0]}')

print("\n=== All items ===")
c.execute('SELECT id, name, category, price, image FROM items ORDER BY id')
for r in c.fetchall():
    print(f'ID={r[0]} | {r[1]} | cat={r[2]} | price={r[3]}')

conn.close()
