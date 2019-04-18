from dbinspector import DBInspector


class TestDBInspector:
    def test_get_count(self, connection):
        """Ensure DBInspector.get_count() returns accurate count of queries executed"""
        with DBInspector(connection) as inspector:
            connection.execute("SELECT 1")
            connection.execute("SELECT 1")

            assert inspector.get_count() == 2

    def test_print_queries(self, capsys, connection):
        """Ensure DBInspector.print_queries() prints all queires executed"""
        with DBInspector(connection) as inspector:
            connection.execute("SELECT 1")
            connection.execute("SELECT 1")

            assert inspector.get_count() == 2
            inspector.print_queries()

            printed_output = capsys.readouterr().out
            assert printed_output == "SELECT 1\nSELECT 1\n"

    def test_print_queries_with_print_pretty_true(self, capsys, connection):
        """Ensure DBInspector.print_queries() pretty prints all queires executed"""
        with DBInspector(connection) as inspector:
            connection.execute("SELECT 1")
            connection.execute("SELECT 1")

            assert inspector.get_count() == 2
            inspector.print_queries(pretty=True)

            printed_output = capsys.readouterr().out
            assert printed_output == \
                "\nQUERY #1\n----------\nSELECT 1\n\nQUERY #2\n----------\nSELECT 1\n"
