from sql_convert_tool.main import process_query, hash_column
import pytest

def test_basic_column_hashing():
    sql = "SELECT col1, col2 FROM table_name"
    hashed_sql, column_map = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") in hashed_sql
    assert len(column_map) == 2
    assert "col1" in column_map
    assert "col2" in column_map
    assert hashed_sql == "SELECT " + hash_column("col1") + ", " + hash_column("col2") + " FROM table_name"

def test_table_names_unchanged():
    sql = "SELECT col1 FROM test_table"
    hashed_sql, _ = process_query(sql)
    assert "test_table" in hashed_sql

def test_column_with_dot_notation():
    sql = "SELECT test_table.col1 FROM test_table"
    hashed_sql, _ = process_query(sql)
    assert "test_table." + hash_column("col1") in hashed_sql

def test_where_clause_hashing():
    sql = "SELECT col1 FROM test_table WHERE col2 = 'value'"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col2") in hashed_sql

def test_no_change_on_non_column_tokens():
    sql = "SELECT 'test' FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert hashed_sql == sql

def test_alias_unchanged():
    sql = "SELECT col1 as alias_name FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "alias_name" in hashed_sql

def test_column_with_dot_notation_and_alias():
    sql = "SELECT table_name.col1 as alias_name FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "table_name." + hash_column("col1") + " as alias_name" in hashed_sql
    assert hashed_sql == "SELECT table_name." + hash_column("col1") + " as alias_name FROM table_name"

def test_column_with_dot_notation_and_alias_and_function():
    sql = "SELECT table_name.col1 as alias_name, COUNT(table_name.col2) as alias_name2 FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "table_name." + hash_column("col1") + " as alias_name" in hashed_sql
    assert "COUNT(table_name." + hash_column("col2") + ") as alias_name2" in hashed_sql
    assert hashed_sql == "SELECT table_name." + hash_column("col1") + " as alias_name, COUNT(table_name." + \
        hash_column("col2") + ") as alias_name2 FROM table_name"

def test_edge_case_empty_sql():
    sql = ""
    hashed_sql, column_map = process_query(sql)
    assert hashed_sql == ""
    assert len(column_map) == 0

def test_edge_case_all_spaces():
    sql = "     "
    hashed_sql, column_map = process_query(sql)
    assert hashed_sql == "     "
    assert len(column_map) == 0

def test_edge_case_no_columns():
    sql = "SELECT 1 + 2 FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert hashed_sql == sql

def test_edge_case_multiple_tables():
    sql = "SELECT a.col1, b.col2 FROM table_a as a, table_b as b WHERE a.col3 = b.col3"
    hashed_sql, column_map = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") in hashed_sql
    assert hash_column("col3") in hashed_sql
    assert len(column_map) == 3
    assert "col1" in column_map
    assert "col2" in column_map
    assert "col3" in column_map
    assert 'a.' + hash_column('col1') in hashed_sql
    assert 'b.' + hash_column('col2') in hashed_sql
    assert 'a.' + hash_column('col3') in hashed_sql
    assert 'b.' + hash_column('col3') in hashed_sql

def test_subquery_hashing():
    sql = "SELECT col1 FROM (SELECT col2 FROM test_table) as subquery"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") not in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + " FROM (SELECT col2 FROM test_table) as subquery"

def test_complex_conditions_hashing():
    sql = "SELECT col1 FROM test_table WHERE col2 = 'value' AND col3 > 10 OR col4 LIKE '%test%'"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col2") in hashed_sql
    assert hash_column("col3") in hashed_sql
    assert hash_column("col4") in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + " FROM test_table WHERE " \
    + hash_column("col2") + " = 'value' AND " + hash_column("col3") + " > 10 OR " + hash_column("col4") + " LIKE '%test%'"

def test_function_call():
    sql = "SELECT AVG(col1), MAX(col2) FROM test_table"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") in hashed_sql
    assert hashed_sql == "SELECT AVG(" + hash_column("col1") + "), MAX(" + hash_column("col2") + ") FROM test_table"

def test_distinct_keyword():
    sql = "SELECT DISTINCT col1 FROM test_table"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hashed_sql == "SELECT DISTINCT " + hash_column("col1") + " FROM test_table"

def test_multiple_statements():
    sql = "SELECT col1 FROM table1; SELECT col2 FROM table2"
    hashed_sql, _ = process_query(sql)
    assert sql == hashed_sql

def test_nested_subqueries():
    sql = "SELECT col1 FROM (SELECT col2 FROM (SELECT col3 FROM test_table) as sub1) as sub2"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") not in hashed_sql
    assert hash_column("col3") not in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + " FROM (SELECT col2 FROM (SELECT col3 FROM test_table) as sub1) as sub2"

def test_order_by_and_group_by():
    sql = "SELECT col1, COUNT(col2) FROM test_table GROUP BY col1 ORDER BY col2"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + ", COUNT(" + hash_column("col2") + \
        ") FROM test_table GROUP BY " + hash_column("col1") + " ORDER BY " + hash_column("col2")

def test_limit_and_offset():
    sql = "SELECT col1 FROM test_table LIMIT 10 OFFSET 5"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert "LIMIT" in hashed_sql
    assert "OFFSET" in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + " FROM test_table LIMIT 10 OFFSET 5"

def test_literal_strings():
    sql = "SELECT 'test' FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "test" in hashed_sql

def test_literal_numbers():
    sql = "SELECT 1, 2.5 FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "1" in hashed_sql
    assert "2.5" in hashed_sql

def test_in_keyword_hashing():
    sql = "SELECT col1 FROM test_table WHERE col2 IN ('value1', 'value2')"
    hashed_sql, _ = process_query(sql)
    assert hash_column("col1") in hashed_sql
    assert hash_column("col2") in hashed_sql
    assert hashed_sql == "SELECT " + hash_column("col1") + " FROM test_table WHERE " + hash_column("col2") + " IN ('value1', 'value2')"

def test_DATE_and_NOW_functions_without_hashing():
    sql = "SELECT DATE(NOW()) FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "DATE(NOW())" in hashed_sql

def test_placeholder():
    sql = "SELECT * FROM foo where user = ?"
    hashed_sql, _ = process_query(sql)
    assert "?" in hashed_sql
    sql = "SELECT * FROM foo where user = :name"
    hashed_sql, _ = process_query(sql)
    assert ":name" in hashed_sql

def test_float():
    sql = "SELECT 1.0 FROM table_name"
    hashed_sql, _ = process_query(sql)
    assert "1.0" in hashed_sql