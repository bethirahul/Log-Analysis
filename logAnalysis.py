# Python 3.6.4

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
        cursor.execute("""select articles.title, count(log.path) as views
            from articles left join log
                on log.path like concat('%',articles.slug,'%')
            group by articles.title
            order by views desc
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
        cursor.execute("""select authors.name, subq2.views
            from (select articles.author, sum(subq.views) as views
                    from articles left join
                        (select articles.slug, count(log.path) as views
                            from articles left join log
                                on log.path like concat('%',articles.slug,'%')
                            group by articles.slug
                        ) as subq
                        on articles.slug = subq.slug
                    group by articles.author
                    order by views desc
                ) as subq2
                right join authors
                on subq2.author = authors.id
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
            select
                to_char(d, 'FMMonth DD, YYYY') as dt,
                round(e_rate::numeric, 2) as error_rate
            from (
                    select
                        t_errors.d as d,
                        ((cast(t_errors.errors as real) /
                            cast(t_hits.hits as real)) * 100) as e_rate
                    from (select date(time) as d, count(*) as errors
                            from log
                            where status like '%404 NOT FOUND%'
                            group by d
                            ) as t_errors
                        join (select date(time) as d, count(*) as hits
                            from log
                            where status like '%200 OK%'
                            group by d
                            ) as t_hits
                        on t_errors.d = t_hits.d
                ) as subq
            where e_rate > 1
            order by e_rate desc;
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
    httpd.serve_forever()
