__author__ = 'ritzhang'

from pandas import ExcelWriter

# Save DataFrame into Excel Sheets
def saveExcel(dfList, excelPath):
    writer = ExcelWriter(excelPath)
    for n, df in enumerate(dfList):
        df.to_excel(writer, 'Sheet%s' % n)

    writer.save()
