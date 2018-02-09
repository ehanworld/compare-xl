from compare_xl import CompareXl
from sql_to_xl import SqlToXl
from compare_sql_xl import CompareSqlInXl

import unittest, os

PROD_CONN = (
    r"DRIVER=SQL Server Native Client 10.0;SERVER=vagsosqla01\nvision;" +
    "DATABASE=nVisionHistorical;Trusted_Connection=Yes;APP=GSOSaveSql")

QA_CONN = (
    r"DRIVER=SQL Server Native Client 10.0;SERVER=vagsosqlp01\nvision;" +
    "DATABASE=nVisionHistorical;Trusted_Connection=Yes;APP=GSOSaveSql")

class Utility():
    @staticmethod
    def remove_file_if_exists(file):
        try:
            os.remove(file)
        except OSError:
            pass

class TestCompare(unittest.TestCase):


    def setUp(self):

        self.left_db = PROD_CONN
        self.right_db = QA_CONN

        self.sheet1 = "Sheet1"
        self.assets_sheet = "Assets"
        self.default_sheet = "output"

        self.output_directory = r"C:\RussC\SqlToFile" + '\\'
        self.diff_index_file = self.output_directory + "diff_test.xlsx"
        self.db_diff_file = self.output_directory + "qa_to_prod_diff.xlsx"
        self.prod_file = self.output_directory + "prod.xlsx"
        self.qa_file = self.output_directory + "qa.xlsx"
        self.diff_file = self.output_directory + 'diffs.xlsx'
        self.left_file = self.output_directory + 'left.xlsx'
        self.right_file = self.output_directory + 'right.xlsx'
        self.existing_left = self.output_directory + "res1.xlsx"  # not generated by tetss
        self.existing_right = self.output_directory + "res2.xlsx"  # not generated by tests
        self.save_file = self.output_directory + "test.xlsx"
        self.proc_file = self.output_directory + "proc.xlsx"
        self.diff_prod_file = self.output_directory + "diff_prod.xlsx"
        self.holdings_file = self.output_directory + "Holdings_20180207.xlsx"
        self.sql_holdings_file = self.output_directory + "prod_test.xlsx"

        Utility.remove_file_if_exists(self.diff_index_file)
        Utility.remove_file_if_exists(self.db_diff_file)
        Utility.remove_file_if_exists(self.prod_file)
        Utility.remove_file_if_exists(self.qa_file)
        Utility.remove_file_if_exists(self.diff_file)
        Utility.remove_file_if_exists(self.save_file)
        Utility.remove_file_if_exists(self.proc_file)
        Utility.remove_file_if_exists(self.diff_prod_file)
        Utility.remove_file_if_exists(self.sql_holdings_file)

    def test_compare_xl(self):
        Utility.remove_file_if_exists(self.diff_file)
        cxl = CompareXl(self.existing_left, self.existing_right, self.sheet1, self.sheet1)
        diffs = cxl.compare()
        cxl.save_differences(self.diff_file, diffs)
        self.assertTrue(os.path.exists(self.diff_file))

    def test_save_sql(self):
        cstr = (QA_CONN)
        stx = SqlToXl(cstr)
        stx.save_sql("select assetid, assetname from asset", self.save_file, self.assets_sheet)
        self.assertTrue(os.path.exists(self.save_file))

    def test_save_stored_proc(self):
        cstr = QA_CONN
        stx = SqlToXl(cstr)
        stx.save_sql("exec dbo.spExportAggregatorClosedEnd", self.proc_file, "proc results")
        self.assertTrue(os.path.exists(self.proc_file))

    def test_run_and_compare(self):

        sql_str = "exec dbo.spExportAggregatorClosedEnd '10/27/17'"
        sql_run_qa = SqlToXl(self.left_db)
        sql_run_qa.save_sql(sql_str, self.qa_file, self.default_sheet)
        sql_run_prod = SqlToXl(self.right_db)
        sql_run_prod.save_sql(sql_str, self.prod_file, self.default_sheet)

        compare = CompareXl(self.qa_file, self.prod_file, self.default_sheet, self.default_sheet)
        compare.save_differences(self.db_diff_file, compare.compare())

        self.assertTrue(os.path.exists(self.db_diff_file))

    def test_compare_index(self):
        compare = CompareXl(self.existing_left, self.existing_right, self.sheet1, self.sheet1)
        diffs = compare.compare_index(6)
        self.assertTrue(len(diffs) > 1)

    def test_compare_index_save(self):
        Utility.remove_file_if_exists(self.diff_file)
        compare = CompareXl(self.existing_left, self.right_file, self.sheet1, self.sheet1)
        diffs = compare.compare_index(6)
        compare.save_differences(self.diff_file, diffs)
        self.assertTrue(os.path.exists(self.diff_file))

    def test_run_and_compare_index(self):
        compare = CompareSqlInXl(PROD_CONN, QA_CONN)
        compare.run_index(self.existing_left, self.existing_right,
                          self.diff_index_file, self.default_sheet, 6,
                          "exec dbo.spExportAggregatorClosedEnd '2/5/18'")
        self.assertTrue(os.path.exists(self.diff_index_file))

    def test_compare_only(self):
        CompareSqlInXl.compare_only(self.sql_holdings_file,
                                    self.holdings_file,
                                    self.diff_prod_file,
                                    self.default_sheet,
                                    index=6
                                    )
        self.assertTrue(os.path.exists(self.diff_prod_file))


if __name__ == '__main__':
    unittest.main()
