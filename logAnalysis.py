#!/usr/bin/env python3

import psycopg2
import http.server
import os
import sys


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
        dbNews = connect_db("news")
        cursor = dbNews.cursor()

        # 1st Query and capturing response
        output_text += get_top_three_articles(cursor)
        output_text += "\n\n"

        # 2nd Query and capturing response
        output_text += get_top_authors(cursor)
        output_text += "\n\n"

        # 3rd Query and capturing response
        output_text += get_errors_over_one(cursor)
        output_text += "\n\n"

        # Close database connection
        dbNews.close()

        # Writing all answers as plain text
        self.wfile.write(output_text.encode())


def connect_db(database_name):
    """Connect to the database. Returns a database connection."""
    try:
        db = psycopg2.connect(dbname=database_name)
        return db

    except:
        print ("Unable to connect to database")
        sys.exit(1)


def get_top_three_articles(cursor):
    """Prints out the top 3 articles of all time."""
    query = """SELECT articles.title, count(log.path) AS views
        FROM articles LEFT JOIN log
            ON log.path = concat('/article/',articles.slug)
        GROUP BY articles.title
        ORDER BY views DESC
        limit 3"""
    cursor.execute(query)
    ans = cursor.fetchall()
    result = "Most popular Authors:\n"
    result += "--------------------\n"
    for key, value in ans:
        result += "{0} -- {1} views\n".format(key, str(value))
    return result


def get_top_authors(cursor):
    """Prints a list of authors ranked by article views."""
    query = """SELECT authors.name, subq2.views
        FROM (SELECT articles.author, sum(subq.views) AS views
                FROM articles LEFT JOIN
                    (SELECT articles.slug, count(log.path) AS views
                        FROM articles LEFT JOIN log
                            ON log.path =
                                concat('/article/',articles.slug)
                        GROUP BY articles.slug
                    ) AS subq
                    ON articles.slug = subq.slug
                GROUP BY articles.author
                ORDER BY views DESC
            ) AS subq2
            RIGHT JOIN authors
            ON subq2.author = authors.id"""
    cursor.execute(query)
    ans = cursor.fetchall()
    result = "Most popular Authors:\n"
    result += "--------------------\n"
    for key, value in ans:
        result += "{0} -- {1} views\n".format(key, str(value))
    return result


def get_errors_over_one(cursor):
    """Prints out the days where more than 1% of logged access requests
    were errors."""
    query = """SELECT
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
        ORDER BY e_rate DESC"""
    cursor.execute(query)
    ans = cursor.fetchall()
    result = "Most popular Authors:\n"
    result += "--------------------\n"
    for key, value in ans:
        result += "{0} -- {1} views\n".format(key, str(value))
    return result


if __name__ == '__main__':
    server_address = ('', 8000)
    httpd = http.server.HTTPServer(server_address, LogAnalysis)
    print("Server is up and running at http://localhost:8000")
    httpd.serve_forever()
