import sqlite3

conn = sqlite3.connect('backend/edu.db')
cursor = conn.cursor()

# Get all tables
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tables:', tables)

for table in tables:
    table_name = table[0]
    print(f'\n=== {table_name.upper()} TABLE ===')

    # Get column info
    cursor.execute(f'PRAGMA table_info({table_name})')
    cols = cursor.fetchall()
    print('Columns:', [col[1] for col in cols])

    # Get data
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()
    print('Data:')
    for row in rows:
        print(' ', row)

conn.close()
