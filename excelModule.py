# -*- coding: utf-8 -*-
import xlrd


def readEXCELFile(filename):
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)
    return sheet

factorStruct={'t': 0,
                'p': 0,
                't_resid': 0,
                'Y0_raw': [],
                'Y_results_raw': [],
                'w_aro': 0,
                'w_nitro': 0,
                'r_oil': 0}
factorStructTwelve = {'t': 0,
                'p': 0,
                't_resid': 0,
                'Y0_raw': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'Y_results_raw': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                'w_aro': 0,
                'w_nitro': 0,
                'r_oil': 0}
factorStructEight = {'t': 0,
                'p': 0,
                't_resid': 0,
                'Y0_raw': [0, 0, 0, 0, 0, 0, 0, 0],
                'Y_results_raw': [0, 0, 0, 0, 0, 0, 0, 0],
                'w_aro': 0,
                'w_nitro': 0,
                'r_oil': 0}


def getFactorsFromRealExcel(sheet, t_resid, w_nitro,w_aro, Y0_raw):
    resultArray = []
    for col_index in range(1, sheet.ncols):
        result = factorStructTwelve
        gasoline = 0
        GO = 0
        GA = 0
        LO3 = 0
        LO4 = 0
        LPG = 0

        for row_index in range(sheet.nrows):

            if "Rx Exit Temp" in sheet.cell(row_index, 0).value:
                result['t'] = float(sheet.cell(row_index, col_index).value)+273.15
            elif "C/O RATIO" in sheet.cell(row_index, 0).value:
                result['r_oil'] = float(sheet.cell(row_index, col_index).value)
            elif "Pressure" in sheet.cell(row_index, 0).value:
                result['p'] = float(sheet.cell(row_index, col_index).value)+101.35
            elif "C/O RATIO" in sheet.cell(row_index, 0).value:
                result['r_oil'] = float(sheet.cell(row_index, col_index).value)
            elif "BOTTOMS" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][0] = float(sheet.cell(row_index, col_index).value) * 0.2 / 100
                result['Y_results_raw'][1] = float(sheet.cell(row_index, col_index).value) * 0.4 / 100
                result['Y_results_raw'][2] = float(sheet.cell(row_index, col_index).value) * 0.4 / 100
            elif "LCO wt%" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][3] = float(sheet.cell(row_index, col_index).value) / 100
            elif "GASOLINE" in sheet.cell(row_index, 0).value:
                gasoline = float(sheet.cell(row_index, col_index).value)
            elif "G-Con O" in sheet.cell(row_index, 0).value:
                GO = float(sheet.cell(row_index, col_index).value)
            elif "G-Con A" in sheet.cell(row_index, 0).value:
                GA = float(sheet.cell(row_index, col_index).value)
            elif "Dry Gas" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][7] = float(sheet.cell(row_index, col_index).value) / 100
            elif "LPG wt%" in sheet.cell(row_index, 0).value:
                LPG = float(sheet.cell(row_index, col_index).value)
            elif "C3= wt%" in sheet.cell(row_index, 0).value:
                LO3 = float(sheet.cell(row_index, col_index).value)
            elif "Total C4= wt%" in sheet.cell(row_index, 0).value:
                LO4 = float(sheet.cell(row_index, col_index).value)
            elif "Coke wt%" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][11] = float(sheet.cell(row_index, col_index).value)/100
        result['Y_results_raw'][5] = gasoline * GO / 10000
        result['Y_results_raw'][6] = gasoline * GA / 10000
        result['Y_results_raw'][4] = gasoline / 100 - result['Y_results_raw'][5] - result['Y_results_raw'][6]
        result['Y_results_raw'][8] = LO3 / 100
        result['Y_results_raw'][9] = LO4 / 100
        result['Y_results_raw'][10] = LPG / 100 - result['Y_results_raw'][8] - result['Y_results_raw'][9]
        result["t_redis"] = t_resid
        result["w_nitro"] = w_nitro
        result["w_aro"] = w_aro
        result["Y0_raw"] = Y0_raw
        resultArray.append(result)
    return resultArray

def getFactorsFromExcelEight(sheet, t_resid, w_nitro,w_aro, Y0_raw):
    resultArray = []
    for col_index in range(1, sheet.ncols):
        result = factorStructEight
        gasoline = 0
        LO3 = 0
        LPG = 0
        COKE = 0
        for row_index in range(sheet.nrows):

            if "Rx Exit Temp" in sheet.cell(row_index, 0).value:
                result['t'] = float(sheet.cell(row_index, col_index).value)+273.15
            elif "C/O RATIO" in sheet.cell(row_index, 0).value:
                result['r_oil'] = float(sheet.cell(row_index, col_index).value)
            elif "Pressure" in sheet.cell(row_index, 0).value:
                result['p'] = float(sheet.cell(row_index, col_index).value)+101.35
            elif "C/O RATIO" in sheet.cell(row_index, 0).value:
                result['r_oil'] = float(sheet.cell(row_index, col_index).value)
            elif "BOTTOMS" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][0] = float(sheet.cell(row_index, col_index).value) * 0.2 / 100
                result['Y_results_raw'][1] = float(sheet.cell(row_index, col_index).value) * 0.4 / 100
                result['Y_results_raw'][2] = float(sheet.cell(row_index, col_index).value) * 0.4 / 100
            elif "LCO wt%" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][3] = float(sheet.cell(row_index, col_index).value) / 100
            elif "GASOLINE" in sheet.cell(row_index, 0).value:
                gasoline = float(sheet.cell(row_index, col_index).value)
            elif "G-Con O" in sheet.cell(row_index, 0).value:
                GO = float(sheet.cell(row_index, col_index).value)
            elif "G-Con A" in sheet.cell(row_index, 0).value:
                GA = float(sheet.cell(row_index, col_index).value)
            elif "Dry Gas" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][7] = float(sheet.cell(row_index, col_index).value) / 100
            elif "LPG wt%" in sheet.cell(row_index, 0).value:
                LPG = float(sheet.cell(row_index, col_index).value)
            elif "C3= wt%" in sheet.cell(row_index, 0).value:
                LO3 = float(sheet.cell(row_index, col_index).value)
            elif "Total C4= wt%" in sheet.cell(row_index, 0).value:
                LO4 = float(sheet.cell(row_index, col_index).value)
            elif "Coke wt%" in sheet.cell(row_index, 0).value:
                result['Y_results_raw'][11] = float(sheet.cell(row_index, col_index).value)/100
        result['Y_results_raw'][5] = gasoline * GO / 10000
        result['Y_results_raw'][6] = gasoline * GA / 10000
        result['Y_results_raw'][4] = gasoline / 100 - result['Y_results_raw'][5] - result['Y_results_raw'][6]
        result['Y_results_raw'][8] = LO3 / 100
        result['Y_results_raw'][9] = LO4 / 100
        result['Y_results_raw'][10] = LPG / 100 - result['Y_results_raw'][8] - result['Y_results_raw'][9]
        result["t_redis"] = t_resid
        result["w_nitro"] = w_nitro
        result["w_aro"] = w_aro
        result["Y0_raw"] = Y0_raw
        resultArray.append(result)
    return resultArray
# def getFactorsFromExcel(sheet, t_resid, w_nitro,w_aro, Y0_raw):
#     resultArray = []
#
#     for row_index in range(sheet.nrows):
#         for col_index in range(sheet.ncols):
#             if row_index <
#     return resultArray
