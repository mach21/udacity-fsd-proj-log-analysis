#! /usr/bin/python3

import psycopg2
import traceback


class LogAnalyzerResource(object):
    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        class LogAnalyzer(object):
            def __init__(self, db_name):
                self.db_name = db_name
                self.db_conn = self.__get_db_conn()
                self.db_cursor = self.__get_db_cursor()

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                self._close_db_conn()

            def __get_db_conn(self):
                '''
                Establish a db connection.

                :returns: connection object
                :raises psycopg2.OperationalError: for db operations errors
                '''
                try:
                    return psycopg2.connect('dbname={}'.format(self.db_name))
                except psycopg2.OperationalError as op_err:
                    print('DB Operational error! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise op_err
                except Exception as ex:
                    print('Undefined exception! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise ex

            def __get_db_cursor(self):
                '''
                Obtain a cursor object.

                :returns: cursor object
                :raises psycopg2.OperationalError: for db operations errors
                '''
                try:
                    return self.db_conn.cursor()
                except psycopg2.OperationalError as op_err:
                    print('DB Operational error! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise op_err
                except Exception as ex:
                    print('Undefined exception! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise ex

            def __db_exec_and_fetchall(self, query):
                '''
                Convenience method. Run a db query and fetch all the results.

                @param query: the command string to execute
                :returns: list of results tuples
                :raises psycopg2.OperationalError: for db operations errors
                '''
                try:
                    self.db_cursor.execute(query)
                    return self.db_cursor.fetchall()
                except psycopg2.OperationalError as op_err:
                    print('DB Operational error! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise op_err
                except Exception as ex:
                    print('Undefined exception! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise ex

            def _close_db_conn(self):
                '''
                Close the db connection

                :returns: None
                :raises psycopg2.OperationalError: for db operations errors
                '''
                try:
                    self.db_conn.close()
                except psycopg2.OperationalError as op_err:
                    print('DB Operational error! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise op_err
                except Exception as ex:
                    print('Undefined exception! traceback: {}'.format(
                        traceback.format_exc())
                    )
                    raise ex

            def __get_3_most_popular_articles(self):
                '''
                Fetch the 3 most popular articles from the db.

                :returns: list of (article, views) tuples
                '''
                return self.__db_exec_and_fetchall(
                    '''
                        SELECT title, count
                        FROM articles
                        JOIN
                            (
                                SELECT path, COUNT(path)
                                FROM log
                                WHERE path LIKE '/article/%'
                                GROUP BY path
                            ) AS path_counts
                        ON path_counts.path = CONCAT(
                            '/article/', articles.slug
                        )
                        ORDER BY count DESC
                        LIMIT 3
                        ;
                    '''
                )

            def __get_most_popular_authors(self):
                '''
                Fetch the most popular authors from the db.

                :returns: list of (article, views) tuples
                '''
                return self.__db_exec_and_fetchall(
                    '''
                        SELECT name, sum
                        FROM
                            (
                                SELECT author, SUM(count) FROM
                                    (
                                        SELECT title, author, count
                                        FROM articles
                                        JOIN
                                            (
                                                SELECT path, COUNT(path)
                                                FROM log
                                                WHERE path LIKE '/article/%'
                                                GROUP BY path
                                            ) AS path_counts
                                        ON path_counts.path = CONCAT(
                                            '/article/', articles.slug)
                                    ) AS subs1
                                GROUP BY author
                            ) AS subs2
                        JOIN authors ON subs2.author = authors.id
                        ORDER BY sum DESC
                        ;
                    '''
                )

            def __get_bad_days(self):
                '''
                Fetch the days when more than 1% of requests lead to errors.
                Definition of error:
                    - status code != 200 OK
                    AND
                        - status code in the 4xx (client err) class
                        OR
                        - sttus code in the 5xx (server err) class

                :returns: list of (day, percent) tuples
                :raises psycopg2.OperationalError: for db operations errors
                '''
                return self.__db_exec_and_fetchall(
                    '''
                        SELECT day, pcent
                        FROM
                        (
                            SELECT
                                sub1.day as day,
                                sub1.total,
                                sub2.errs,
                                ((sub2.errs/sub1.total::float)*100.0) AS pcent
                            FROM
                                (
                                    SELECT
                                        date_trunc('day', log.time) as day,
                                        COUNT(1) AS total
                                    FROM log
                                    GROUP BY day
                                ) AS sub1
                            LEFT JOIN
                                (
                                    SELECT
                                        date_trunc('day', log.time) as day,
                                        COUNT(1) AS errs
                                    FROM log
                                    WHERE
                                        status != '200 OK'
                                        AND (
                                            -- client error
                                            status LIKE '4%' OR
                                            -- server error
                                            status LIKE '5%'
                                        )
                                    GROUP BY day
                                ) AS sub2
                            ON sub1.day::TIMESTAMP = sub2.day::TIMESTAMP
                        ) AS sub3
                        WHERE pcent > 1.0
                        ;
                    '''
                )

            def print_popular_article_data(self):
                '''
                Pretty prints most popular article data.

                :returns: None
                :raises Exception: when there is no data to parse
                '''
                articles = self.__get_3_most_popular_articles()

                if articles == [] or articles is None:
                    raise Exception('No article data to display!')

                print(self.__format_message(
                    'The 3 most popular articles of all time are:')
                )
                for item in articles:
                    print(
                        '"{title}" - {views} views'.format(
                            title=item[0], views=str(item[1])
                        )
                    )

            def print_popular_author_data(self):
                '''
                Pretty prints most popular author data.

                :returns: None
                :raises Exception: when there is no data to parse
                '''
                authors = self.__get_most_popular_authors()

                if authors == [] or authors is None:
                    raise Exception('No author data to display!')

                print(self.__format_message(
                    'The most popular authors of all time are:')
                )
                for item in authors:
                    print(
                        '"{author}" - {views} views'.format(
                            author=item[0], views=str(item[1])
                        )
                    )

            def print_bad_days_data(self):
                '''
                Pretty prints bad days data.

                :returns: None
                :raises Exception: when there is no data to parse
                '''
                days = self.__get_bad_days()

                if days == [] or days is None:
                    raise Exception('No bad days data to display!')

                print(self.__format_message('Bad days are:'))
                for item in days:
                    print(
                        '"{day}" - {percent}% errors'.format(
                            # Day format is like: July 29, 2016
                            day=item[0].strftime('%B %d, %Y'),
                            # Percent format is like: 2.5% errors
                            percent=str(round(item[1], 1))
                        )
                    )

            def __format_message(self, message):
                '''
                Utility method to surround messages with pretty stars.

                @Param message: message string to be formatted
                :returns: Formatted message string
                '''

                return ('\n{stars}\n{message}\n{stars}\n'.format(
                    stars='*' * len(message), message=message)
                )

        self.log_analyzer_object = LogAnalyzer(self.db_name)
        return self.log_analyzer_object

    def __exit__(self, exc_type, exc_value, traceback):
        self.log_analyzer_object._close_db_conn()


if __name__ == '__main__':
    with LogAnalyzerResource(db_name='news') as log_analyzer:
        log_analyzer.print_popular_article_data()
        log_analyzer.print_popular_author_data()
        log_analyzer.print_bad_days_data()
