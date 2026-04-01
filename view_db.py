#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("notices.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*80)
print("USERS TABLE")
print("="*80)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
if users:
    for user in users:
        print(f"ID: {user['id']} | Name: {user['name']} | University: {user['university']} | Email: {user['email']} | Telegram ID: {user['telegram_id']}")
else:
    print("(No users registered yet)")

print("\n" + "="*80)
print("NOTICES TABLE")
print("="*80)
cursor.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 20")
notices = cursor.fetchall()
if notices:
    for notice in notices:
        print(f"\nID: {notice['id']}")
        print(f"  University: {notice['university']}")
        print(f"  Title: {notice['title']}")
        print(f"  Link: {notice['link']}")
else:
    print("(No notices found)")

print("\n" + "="*80)
print(f"SUMMARY: {len(users) if users else 0} users | {len(notices) if notices else 0} notices")
print("="*80 + "\n")

conn.close()
