import psycopg2
import http.server
import os

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Queries are sent and answers are printed in HTML format"""
        # Sending 200 OK response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write("Page Working!".encode())

        # Connecting to database and creating cursor
        dbNews = psycopg2.connect("dbname=news")
        cursor = dbNews.cursor()

        # 1st Query and capturing response
        cursor.execute("")
        ans1 = cursor.fetchall()

        # 2nd Query and capturing response
        cursor.execute("")
        ans2 = cursor.fetchall()

        # 3rd Query and capturing response
        cursor.execute("")
        ans3 = cursor.fetchall()

        # Close database connection
        dbNews.close()

if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, Shortener)
    httpd.serve_forever()
