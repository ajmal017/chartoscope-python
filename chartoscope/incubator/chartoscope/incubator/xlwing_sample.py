import xlwings as xw
wb = xw.Book()  # this will create a new workbook
wb = xw.Book('chart_stock.xlsx')  # connect to an existing file in the current working directory