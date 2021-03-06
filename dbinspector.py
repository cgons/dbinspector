import sqlalchemy as sa


class DBInspector(object):
    """Use as a context manager inspect the queries executed + query count.

    Note: DBInspector even works with queires issued via. the ORM: `session.query()`

    Usage:
        with DBInspector(conn) as inspector:
            conn.execute("SELECT 1")
            conn.execute("SELECT 1")

            # Get query count
            assert inspector.get_count() == 2

            # Print queries issued
            inspector.print_queries(pretty=True)
    """

    def __init__(self, conn: sa.engine.Connection):
        """Initialize the DBInspector

        Params:
            conn: Instance of <sqlalchemy.engine.Connection>
        """
        self.conn = conn
        self.count = 0
        self.queries = []

    def __enter__(self):
        sa.event.listen(self.conn, "after_execute", self.callback)
        return self

    def __exit__(self, *args):
        sa.event.remove(self.conn, "after_execute", self.callback)

    def get_count(self) -> int:
        """Returns a count of the number of queries executed."""
        return self.count

    def print_queries(self, pretty=False):
        """Prints all queries issused to stdout."""
        if pretty:
            for i, q in enumerate(self.queries, 1):
                to_print = q

                if type(q) is not str:
                    to_print = q.compile(self.conn.engine)

                print(f"\nQUERY #{i}\n----------")
                print(to_print)
        else:
            for q in self.queries:
                print(str(q))

    def callback(self, conn, query, *args):
        self.queries.append(query)
        self.count += 1
