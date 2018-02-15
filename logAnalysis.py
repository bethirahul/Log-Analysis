#!/usr/bin/env python3

import psycopg2
import http.server
import os


# custom python basic server to handle HTTP requests
class LogAnalysis(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Queries are sent and answers are printed in HTML format"""

        # Sending 200 OK response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

        output_text = ''

        # Connecting to database and creating cursor
        dbNews = psycopg2.connect("dbname=news")
        cursor = dbNews.cursor()

        # 1st Query and capturing response
        cursor.execute("""SELECT articles.title, count(log.path) AS views
            FROM articles LEFT JOIN log
                ON log.path LIKE concat('%',articles.slug,'%')
            GROUP BY articles.title
            ORDER BY views DESC
            limit 3
        """)
        ans = cursor.fetchall()

        # Formatting 1st query output
        output_text += "Top three most popular articles:\n"
        output_text += "-------------------------------\n"
        for key, value in ans:
            output_text += "{0} -- {1} views\n".format(key, str(value))
        output_text += "\n\n"

        # 2nd Query and capturing response
        cursor.execute("""SELECT authors.name, subq2.views
            FROM (SELECT articles.author, sum(subq.views) AS views
                    FROM articles LEFT JOIN
                        (SELECT articles.slug, count(log.path) AS views
                            FROM articles LEFT JOIN log
                                ON log.path LIKE concat('%',articles.slug,'%')
                            GROUP BY articles.slug
                        ) AS subq
                        ON articles.slug = subq.slug
                    GROUP BY articles.author
                    ORDER BY views DESC
                ) AS subq2
                RIGHT JOIN authors
                ON subq2.author = authors.id
        """)
        ans = cursor.fetchall()

        # Formatting 2nd query output
        output_text += "Most popular Authors:\n"
        output_text += "--------------------\n"
        for key, value in ans:
            output_text += "{0} -- {1} views\n".format(key, str(value))
        output_text += "\n\n"

        # 3rd Query and capturing response
        cursor.execute("""
            SELECT
                to_char(d, 'FMMonth DD, YYYY') AS dt,
                round(e_rate::numeric, 2) AS error_rate
            FROM (
                    SELECT
                        t_errors.d AS d,
                        ((cast(t_errors.errors AS real) /
                            cast(t_hits.hits AS real)) * 100) AS e_rate
                    FROM (SELECT date(time) AS d, count(*) AS errors
                            FROM log
                            where status LIKE '%404 NOT FOUND%'
                            GROUP BY d
                            ) AS t_errors
                        JOIN (SELECT date(time) AS d, count(*) AS hits
                            FROM log
                            where status LIKE '%200 OK%'
                            GROUP BY d
                            ) AS t_hits
                        ON t_errors.d = t_hits.d
                ) AS subq
            where e_rate > 1
            ORDER BY e_rate DESC;
        """)
        ans = cursor.fetchall()

        # Formatting 3rd query output
        output_text += "On the following days, more than 1% of requests lead "
        output_text += "to errors:\n-----------------------------------------"
        output_text += "---------------------\n"
        for key, value in ans:
            output_text += "{0} -- {1}% errors\n".format(key, str(value))
        output_text += "\n\n"

        # Close database connection
        dbNews.close()

        # Writing all answers as plain text
        self.wfile.write(output_text.encode())


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, LogAnalysis)
    print("Server is up and running at http://localhost:8000")
    httpd.serve_forever()
