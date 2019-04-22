# DBInspector

A Python context manager for use with SQLAlchemy.

### Features
- Count the number of queires issued.
- Capture/print the number of queries issued.

---

### Installation
```
pip install dbinspector
```

### Usage

```
with DBInspector(conn) as inspector:
    conn.execute("SELECT 1")
    conn.execute("SELECT 1")

    # Get query count
    assert inspector.get_count() == 2
    
    # Print queries issued
    inspector.print_queries(pretty=True)
```

### API
```
DBInspector.get_count() -> int

DBInspector.print_queries(pretty=False)
```
