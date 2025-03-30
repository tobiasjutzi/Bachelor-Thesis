import pandas as pd


def switch_two_columns(dataframe: pd.DataFrame, column_name_one: str, column_name_two: str) -> pd.DataFrame:
    all_columns: list[str] = list(dataframe.columns)
    index_frist_column: int = all_columns.index(column_name_one)
    index_second_column: int = all_columns.index(column_name_two)
    all_columns[index_frist_column], all_columns[index_second_column] = all_columns[index_second_column], all_columns[index_frist_column]
    return dataframe[all_columns]

