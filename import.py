import csv
import MySQLdb

conn = MySQLdb.connect("localhost","zahid","password","bookreviewapp")
cursor = conn.cursor()

cursor = conn.cursor()
with open('books.csv', newline='') as csvfile:
    customer_data = csv.reader(csvfile)
    next(customer_data)
    for row in customer_data:
    	#print(row[0])
    	isbn = row[0]
    	title = row[1]
    	author = row[2]
    	year = row[3]
    	cursor.execute("INSERT INTO books(isbn,title,author,year) VALUES(%s, %s,%s,%s)", (isbn , title , author , year))
    conn.commit()
conn.close()


