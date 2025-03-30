import pandas as pd
from dataclasses import dataclass


@dataclass
class CountPercent:
    value_name: str
    count: int
    percent: float


@dataclass
class ColumnResults:
    result_as_df: pd.DataFrame
    result_as_count_percent_list: list[CountPercent]


def count_percent_specific_value(series: pd.Series, row_value: str, print_results: bool) -> CountPercent:
    """
    calculate the total number of entries in the series that match to the given row value
    calculate the number in percent to matching entries to the wohle series
    :param series: the Series for calculation
    :param row_value: the row value that will use for comparing to the series row values
    """
    matching_series: pd.Series = series[series == row_value]
    percent: float = (100 / series.size) * matching_series.size
    if print_results:
        print(
            f'{row_value}: total in Series: {matching_series.size}, percent: {percent}')
    return CountPercent(value_name=row_value, count=matching_series.size, percent=percent)


def count_percent_series(column_to_calculate: pd.Series, number_of_inspected_values: int, column_name: str, print_results: bool) -> ColumnResults:
    """
    calculate the top highest row values und call for each value count_percent_specific_value
    :param column_to_calculate: the column (Series) for which rows values the total count and percent value should be calculated
    :param number_of_inspected_values: how many (different) row values should be inspected (highest descending)
    :param column_name: the name of the colum (Series)
    """
    if number_of_inspected_values == -1:
        row_values: pd.Series = column_to_calculate.value_counts()
    else:
        row_values: pd.Series = column_to_calculate.value_counts().head(number_of_inspected_values)

    count_percent_list: list[CountPercent] = []
    result_as_dataframe: pd.DataFrame = pd.DataFrame(columns=[f'{column_name}', 'total', 'percent'])

    for row_value_name in row_values.index.tolist():
        new_count_percent: CountPercent = count_percent_specific_value(column_to_calculate, row_value_name, print_results)
        result_as_dataframe.loc[len(result_as_dataframe)] = [f'{new_count_percent.value_name}', new_count_percent.count, new_count_percent.percent]
        count_percent_list.append(new_count_percent)

    total_inspected_rows: int = len(result_as_dataframe)
    total_count: int = result_as_dataframe['total'].sum()
    total_percent: int = result_as_dataframe['percent'].sum()
    header_row: dict[str, str] = {f'{column_name}': f'{total_inspected_rows}', 'total': total_count, 'percent': total_percent}
    result_as_dataframe = pd.concat([pd.DataFrame([header_row]), result_as_dataframe], ignore_index=True)
    return ColumnResults(result_as_dataframe, count_percent_list)


def column_calculation(dataframe: pd.DataFrame, inspected_columns: dict[str, int], print_results: bool) -> list[ColumnResults]:
    """
    loop throw the inspected columns and call count_percent_series
    :param dataframe: dataframe for which columns the total count and percent should be calculated
    :param inspected_columns: which columns of the dataframe should be inspected and for echt column the maximum number of different rows values that should involve in calculation
           if the maximum number is set to -1 then there is no limit for different row values
    :param print_results: true -> print total count and percent for echt inspected row in console
    :return: list that contains an entry for each inspected column; each entry contains the results as dataframe and list[CountPercent]
    """
    column_result_list: list[ColumnResults] = []

    for index, column in enumerate(inspected_columns.keys()):
        if print_results:
            print(f'{column}:')
        column_result: ColumnResults = count_percent_series(dataframe[column], inspected_columns[column], column, print_results)
        column_result_list.append(column_result)
    return column_result_list

