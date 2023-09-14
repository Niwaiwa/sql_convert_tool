import sys
import json
import hashlib
import sqlparse
from sqlparse.tokens import Keyword
from sqlparse.sql import Identifier, Token

def is_sql_function(string):
    SQL_FUNCTIONS = set([
        "AVG", "COUNT", "SUM", "MAX", "MIN",
        "UPPER", "LOWER", "INITCAP",
        "SUBSTRING", "TRIM", "LENGTH", "TO_DATE",
        "SYSDATE", "CURRENT_TIMESTAMP",
        "COALESCE", "NULLIF", "CASE",
        "ROUND", "FLOOR", "CEIL", "ABS", 
        "SQRT", "LOG", "EXP",
        "SIN", "COS", "TAN", 
        "CAST", "CONVERT", "IF",
        "CONCAT", "CONCAT_WS", "SUBSTR", "REPLACE",
        "STR_TO_DATE", "DATE_FORMAT",
        "DATE", "DATETIME", "TIMESTAMP", "TIME",
        "YEAR", "MONTH", "DAY", "HOUR", "MINUTE", "SECOND",
        "EXTRACT", "TO_CHAR", "TO_NUMBER", 
        "TO_NUMBER", "TO_TIMESTAMP",
        "NOW", "DATE_PART", "DATE_TRUNC", "DATE_ADD",
        # ... You can add more functions as needed
    ])
    return string.upper() in SQL_FUNCTIONS

def hash_column(column_name):
    return hashlib.md5(column_name.encode()).hexdigest()

def check_and_get_hashed_name(col_name, column_hash_map):
    if col_name not in column_hash_map:
        hashed_name = hash_column(col_name)
        column_hash_map[col_name] = hashed_name
        return hashed_name
    else:
        hashed_name = column_hash_map[col_name]
        return hashed_name
    

def process_tokens(tokens, column_hash_map, after_from=False, group_token_alias=False):
    new_tokens = []
    for token in tokens:
        if token.ttype is Keyword and token.value.upper() == 'FROM':
            after_from = True

        if isinstance(token, Identifier):
            col_name = token.get_real_name()
            table = token.get_parent_name()
            alias = token.get_alias()
            if group_token_alias:
                if token is tokens[-1]:
                    new_tokens.append(token)
            elif after_from:
                new_tokens.append(token)
            elif is_sql_function(col_name):
                if token.is_group and token.has_alias():
                    new_tokens.extend(process_tokens(token.tokens, column_hash_map, after_from, True))
                else:
                    new_tokens.append(token)
            else:
                hashed_name = check_and_get_hashed_name(col_name, column_hash_map)
                if '.' in token.value and token.has_alias():
                    new_ident = Token(sqlparse.tokens.Name, f'{table}.{hashed_name} as {alias}')
                elif '.' in token.value:
                    new_ident = Token(sqlparse.tokens.Name, f'{table}.{hashed_name}')
                elif token.has_alias():
                    new_ident = Token(sqlparse.tokens.Name, f'{hashed_name} as {alias}')
                else:
                    new_ident = Token(sqlparse.tokens.Name, hashed_name)
                new_tokens.append(new_ident)
        elif token.is_group:
            new_tokens.extend(process_tokens(token.tokens, column_hash_map, after_from))
        else:
            new_tokens.append(token)

        # Once we've passed the 'FROM', we turn off the after_from flag for the remaining tokens.
        if after_from and token.ttype is Keyword and token.value.upper() in ['WHERE', 'GROUP BY', 'ORDER BY']:
            after_from = False

    return new_tokens

def process_query(sql):
    if not sql:
        return sql, {}
    sqls = sqlparse.split(sql)
    if len(sqls) > 1:
        return sql, {}
    parsed = sqlparse.parse(sql)
    if not parsed:
        return sql, {}
    stmt = parsed[0]
    column_hash_map = {}
    new_tokens = process_tokens(stmt.tokens, column_hash_map)
    stmt.tokens = new_tokens
    return str(stmt), column_hash_map


if __name__ == '__main__':
    argv = sys.argv
    sql = argv[1]

    new_sql, column_map = process_query(sql)
    print("Input SQL: " + sql)
    print("Modified SQL: " + new_sql)
    print("MAP: " + json.dumps(column_map))