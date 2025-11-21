import json

# Load JSON data from file
with open("zus_kl_selangor_outlets.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Start building the SQL statement
sql = "INSERT INTO outlets (name, address, google_map) VALUES\n"

# Convert each JSON entry to a SQL value tuple
values = []
for outlet in data:
    name = outlet['name'].replace("'", "''")  # Escape single quotes
    address = outlet['address'].replace("'", "''")
    google_map = outlet['google_map'].replace("'", "''")
    values.append(f"('{name}', '{address}', '{google_map}')")

# Join all values with commas and add semicolon at the end
sql += ",\n".join(values) + ";"

# Save SQL to a file or print
with open("outlets.sql", "w", encoding="utf-8") as f:
    f.write(sql)

print("SQL file generated successfully!")
