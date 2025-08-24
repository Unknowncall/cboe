import sqlite3

conn = sqlite3.connect('trails.db')
cursor = conn.cursor()

print('Current AI query (≤ 5 miles):')
cursor.execute('SELECT name, distance_km FROM trails WHERE distance_km <= 8.04672 ORDER BY distance_km ASC LIMIT 5')
for row in cursor.fetchall():
    name, distance_km = row
    miles = distance_km * 0.621371
    print(f'  {name}: {miles:.1f} miles')

print()
print('Better query (around 5 miles, 4-6 mile range):')
cursor.execute('SELECT name, distance_km FROM trails WHERE distance_km BETWEEN 6.4 AND 9.6 ORDER BY ABS(distance_km - 8.0) LIMIT 5')
for row in cursor.fetchall():
    name, distance_km = row
    miles = distance_km * 0.621371
    print(f'  {name}: {miles:.1f} miles')

conn.close()
