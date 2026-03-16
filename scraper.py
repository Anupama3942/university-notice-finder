import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import schedule
import time

load_dotenv()
email = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASSWORD")
receiver_email = "anupamaaluthge@gmail.com"

def message_fomat(title, link):
    msg = EmailMessage()
    msg['Subject'] = f"🎓 New University Notice: {title[:30]}..."
    msg['From'] = f"University Alert System {email}"
    msg['To'] = receiver_email
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
                <h2 style="color: #004a99;">New University Notice Found!</h2>
                <p>Hello,</p>
                <p>A new notice has been posted on the university website:</p>
                <div style="background: white; padding: 15px; border-left: 5px solid #004a99; margin: 10px 0;">
                    <strong>{title}</strong>
                </div>
                <p>You can view the full details by clicking the button below:</p>
                <a href="{link}" style="display: inline-block; padding: 10px 20px; background-color: #004a99; color: white; text-decoration: none; border-radius: 5px;">View Notice</a>
                <p style="font-size: 0.8em; color: #777; margin-top: 20px;">
                    This is an automated alert from your Notice Scraper.
                </p>
            </div>
        </body>
    </html>
    """
    
    msg.set_content(f"New Notice: {title}\nView here: {link}")
    msg.add_alternative(html_content, subtype='html')
    
    return msg

def init_db():
    conn = sqlite3.connect('notices.db')
    cursor = conn.cursor()
    
    cursor.execute ("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        university TEXT NOT NULL,
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL
    )
    """)
    
    conn.commit()
    return conn,cursor
    
def save_notice(conn, cursor, university, title, link):
    
    cursor.execute("SELECT * FROM notices WHERE link=?", (link,))
    result = cursor.fetchone()
    
    if result is None:
        cursor.execute("INSERT INTO notices(university, title, link) VALUES(?,?,?)", (university, title, link))
        conn.commit()
        print(f"New Notice found {title}")
        send_email(title, link)
    else:
        print("Notice already exist")
        
def send_email(title, link):
    
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    # server.starttls()
    server.login(email, password)
    message = message_fomat(title, link)
    server.send_message(message)
    
    server.quit()

def scrape_RUSL(conn, cursor):
    
    url = "https://www.rjt.ac.lk/notice/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    headingContainer = soup.find_all('h3', class_='blog-title')
    
    for titles in headingContainer:
        title = titles.text.strip()
        noticeTag = titles.find('a')
        
        if noticeTag:
            link = noticeTag['href']
            save_notice(conn, cursor, "RUSL", title, link)

def scrape_UOM(conn, cursor):
    
    url = "https://uom.lk/university_news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    headingContainer = soup.find_all('h2', class_='node__title')
    
    for titles in headingContainer:
        title = titles.text.strip()
        noticeTag = titles.find('a')
        
        if noticeTag:
            link = noticeTag['href']
            save_notice(conn, cursor, "UOM", title, link)

def scrape_UOV(conn, cursor):
    
    url = "https://www.vau.ac.lk/category/news/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    headingContainer = soup.find_all('h2', class_='entry-title')
    
    for titles in headingContainer:
        title = titles.text.strip()
        noticeTag = titles.find('a')
        
        if noticeTag:
            link = noticeTag['href']
            save_notice(conn, cursor, "UOV", title, link)
    
def scrape_UOK(conn, cursor):
    
    url = "https://news.kln.ac.lk/index.php/updates/notices"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    headingContainer = soup.find_all('h2', itemprop='name')
    
    for titles in headingContainer:
        title = titles.text.strip()
        noticeTag = titles.find('a')
        
        if noticeTag:
            link = noticeTag['href']
            save_notice(conn, cursor, "UOK", title, link)
    

def check_notices():
    
    db_conn, db_cursor = init_db()
    
    scrape_RUSL(db_conn, db_cursor)
    scrape_UOM(db_conn, db_cursor)
    scrape_UOV(db_conn, db_cursor)
    scrape_UOK(db_conn, db_cursor)
    
    db_conn.close();

    print("Checking...")
    
schedule.every(1).second.do(check_notices)

while True:
    schedule.run_pending()
    time.sleep(1)
    
