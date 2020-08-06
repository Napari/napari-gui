"""print_property_table() function and RowTable class.
"""
from typing import List, Tuple, Union

from ._utils import highlight


def print_property_table(items: List[Tuple[str, str]]):
    """Print names and values.

    Example output:

    Layer ID: 0
        Name: numbered slices
      Levels: 1
       Shape: (20, 1024, 1024, 3)

    Parameters
    ----------
    items
    """
    width = max(len(heading) for heading, _ in items)
    for heading, value in items:
        aligned = f"{heading:>{width}}"
        print(f"{highlight(aligned)}: {value}")


class ColumnSpec:
    """Specification for one column in a RowTable.

    Parameters
    ----------
    spec : Union[str, dict]
        String column name, or a dict specification.
    """

    def __init__(self, spec: Union[str, dict]):

        if isinstance(spec, str):
            spec = {'name': spec}  # Spec is the name, then we use defaults.
        self.name = spec.get('name', "")
        self.align = spec.get('align', "right")
        self.width = spec.get('width')

    def format(self, value, width):
        """Return formatted value with alignment."""
        value_str = str(value)
        if self.align == "left":
            return f"{value_str:<{width}}"
        return f"{value_str:>{width}}"


class RowTable:
    """A printable text table with a header and rows.
    Usage:
        table = table(["NAME", "AGE"], [10, 5])
        table.add_row["Mary", "25"]
        table.add_row["Alice", "32"]
        table.print()
    Would print:
        NAME       AGE
        Mary       25
        Alice      32
    Parameters
    ----------
    headers : List[str]
        The column headers such as  ["NAME", "AGE"].
    widths: Optional[List[int]]
        Use these widths instead of automatic widths, 0 means auto for that column.
    """

    # For auto-width columns, pad max width by this many columns to
    # leave a little room between columns.
    PADDING = 2

    def __init__(self, columns: List[Union[str, dict]]):
        self.columns = [ColumnSpec(x) for x in columns]
        self.rows: List[list] = []

    def add_row(self, row: List[str]) -> None:
        """Add one row of data to the table.

        Parameters
        ----------
        row : List[str]
            The row values such as ["Fred", "25"].
        """
        row_cols = len(row)
        header_cols = len(self.columns)
        if row_cols != header_cols:
            raise ValueError(
                f"Row with {row_cols} columns not compatible "
                f"with headers ({header_cols} columns)"
            )
        self.rows.append(row)

    def _get_max_data_width(self, index: int) -> int:
        """Return maximum width of this column in the data.

        Parameters
        ----------
        index : int
            Return width of this column.

        Returns
        -------
        int
            The maximum width of this column.
        """
        if self.rows:
            return max([len(str(row[index])) for row in self.rows])
        return 0

    def _get_widths(self) -> List[int]:
        """Return widths of all the columns."

        Returns
        -------
        List[int]
            The width of each column in order.
        """
        widths = []
        for i, spec in enumerate(self.columns):
            if spec.width is not None:
                width = spec.width  # A fixed width column.
            else:
                # Auto sized column so whichever is wider: data or header.
                data_width = self._get_max_data_width(i)
                width = max(data_width, len(self.columns[i].name))
            widths.append(width + self.PADDING)
        return widths

    def get_header_str(self, widths: List[int]) -> str:
        """Return header string with all the column names.

        Parameters
        ----------
        widths : List[int]
            The column widths.

        Returns
        -------
        str
            The header string.
        """
        header_str = ""
        for i, spec in enumerate(self.columns):
            width = widths[i]
            value = str(spec.name)
            header_str += f"{value:<{width}}"
        return header_str

    def get_row_str(self, row, widths: List[int]) -> str:
        """Get string depicting one row on the table."""
        row_str = ""
        for i, spec in enumerate(self.columns):
            row_str += spec.format(row[i], widths[i])
        return row_str

    def print(self):
        """Print the entire table both header and rows."""
        widths = self._get_widths()
        print(highlight(self.get_header_str(widths)))
        for row in self.rows:
            print(self.get_row_str(row, widths))
