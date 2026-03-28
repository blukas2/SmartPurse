import pandas as pd

from globals.logger import get_logger
from backend.organizer import DataOrganizer

logger = get_logger(__name__)


class ChartDataProvider:
    """Provides pre-computed chart data for line visualizations."""

    GRANULARITY_MONTHLY = "Monthly"
    GRANULARITY_YEARLY = "Yearly"
    CALC_NOMINAL = "Nominal"
    CALC_YOY = "YoY%"
    CALC_PCT_OF_INCOME = "% of total income"

    def __init__(self, data_organizer: DataOrganizer):
        self._data_organizer = data_organizer
        self._datasets = {}
        self._prepare_all_datasets()

    def get_chart_data(self, granularity: str, calculation_type: str) -> pd.DataFrame:
        """Return a DataFrame with Category as rows and time periods as columns."""
        return self._datasets[(granularity, calculation_type)]

    def get_categories(self) -> list[str]:
        """Return sorted list of all available category labels."""
        nominal_monthly = self._datasets[(self.GRANULARITY_MONTHLY, self.CALC_NOMINAL)]
        return sorted(nominal_monthly["Category"].tolist())

    def _prepare_all_datasets(self):
        logger.info("Preparing chart datasets")
        monthly_nominal = self._negate_expenditure_values(
            self._data_organizer.accounts_data_cost_breakdown["all"].copy()
        )
        yearly_nominal = self._negate_expenditure_values(
            self._data_organizer.accounts_data_yearly_breakdown["all"].copy()
        )
        yearly_yoy = self._data_organizer.accounts_data_yearly_breakdown_yoy["all"].copy()

        self._datasets[(self.GRANULARITY_MONTHLY, self.CALC_NOMINAL)] = monthly_nominal
        self._datasets[(self.GRANULARITY_MONTHLY, self.CALC_YOY)] = self._calculate_monthly_yoy(monthly_nominal)
        self._datasets[(self.GRANULARITY_MONTHLY, self.CALC_PCT_OF_INCOME)] = self._calculate_pct_of_income(monthly_nominal)
        self._datasets[(self.GRANULARITY_YEARLY, self.CALC_NOMINAL)] = yearly_nominal
        self._datasets[(self.GRANULARITY_YEARLY, self.CALC_YOY)] = yearly_yoy
        self._datasets[(self.GRANULARITY_YEARLY, self.CALC_PCT_OF_INCOME)] = self._calculate_pct_of_income(yearly_nominal)
        logger.info("Chart datasets ready")

    def _calculate_monthly_yoy(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compare each month to the same month in the previous year."""
        result = df.copy()
        date_columns = self._get_date_columns(result)
        date_columns_sorted = sorted(date_columns, reverse=True)
        for col in date_columns_sorted:
            prev_col = self._get_previous_year_column(col, date_columns)
            if prev_col:
                result[col] = (result[col] / result[prev_col] * 100 - 100).round(2)
            else:
                result[col] = None
        return result

    def _get_previous_year_column(self, column: str, all_columns: list[str]) -> str | None:
        """Return the column name for the same month in the previous year."""
        year = str(int(column[:4]) - 1)
        prev_col = year + column[4:]
        return prev_col if prev_col in all_columns else None

    def _calculate_pct_of_income(self, df: pd.DataFrame) -> pd.DataFrame:
        """Divide each row by the INCOME row and multiply by 100."""
        result = df.copy()
        date_columns = self._get_date_columns(result)
        income_row = result[result["Category"] == "INCOME"]
        if income_row.empty:
            return result
        for col in date_columns:
            income_value = income_row[col].values[0]
            if income_value != 0:
                result[col] = (result[col] / income_value * 100).round(2)
            else:
                result[col] = None
        return result

    @staticmethod
    def _negate_expenditure_values(df: pd.DataFrame) -> pd.DataFrame:
        """Make expenditure values positive for chart display."""
        mask = df["Category"].str.startswith("EXPENDITURE")
        date_columns = ChartDataProvider._get_date_columns(df)
        df.loc[mask, date_columns] = df.loc[mask, date_columns] * -1
        return df

    @staticmethod
    def _get_date_columns(df: pd.DataFrame) -> list[str]:
        """Return all columns except 'Category'."""
        return [col for col in df.columns if col != "Category"]
