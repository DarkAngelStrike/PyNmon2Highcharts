#!/usr/bin/env python

import argparse, csv, operator, random, re, webbrowser, os, inspect

from PyHighcharts.chart import Highchart
from functools          import reduce

run_date  = ""
host_name = ""

LINEZOOM_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "min": 0, "title_text": " "},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

LINEZOOM100_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "min": 0, "max": 100, "title_text": "%"},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

LINEZOOMMB_CONFIG = {
    "xAxis": {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
              "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis": {"gridLineWidth": 1, "title_text": "MB", "min": 0},
    "chart": {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

LINEZOOMNOLEGEND_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "min": 0, "title_text": " "},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"enabled": False}}

AREAZOOM_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "title_text": " ", "min": 0},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

AREAZOOMMB_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "title_text": "MB", "min": 0},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

AREAZOOM100_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1, "tickInterval": 7,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "title_text": "%", "min": 0, "max": 100},
    "chart":  {"zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

COLUMNSTACKED_CONFIG = {
    "xAxis" : {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis" : {"gridLineWidth": 1, "title_text": "%", "min": 0 },
    "chart" : {"type": 'column', "zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}

COLUMNSTACKEDHD_CONFIG = {
    "xAxis":  {"gridLineWidth": 1, "lineWidth": 1, "tickLength": 1,
               "labels": {"rotation": 270, "align": "right"}, "minRange": 1},
    "yAxis":  {"gridLineWidth": 1, "title_text": " ", "min": 0},
    "chart":  {"type": 'column', "zoomType": 'x', "borderWidth": 3},
    "legend": {"verticalAlign": 'top', "y": 25}}


################################################################################

def ParseNmonFileParam(): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    parser = argparse.ArgumentParser(description='pynmon2highchart.py')
    parser.add_argument('-i', '--input', help='Input file name', required=True)
    args = parser.parse_args()
    return args.input


def DividePageRatio(x, y): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    if y > 0:
        return abs(round(x / y, 1))
    else:
        return 0


def GetAverageFromDict(dct): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return {key: round((reduce(lambda x, y: x + y, dct[key]) / len(dct[key])), 2) \
            for key in dct.keys()}


def GetAverageFromList(lst):
    """"""
    return round(reduce(lambda x, y: x + y, lst) / len(lst), 2)


def GetWAverageFromDict(dct, dct_avg): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    dict_wavg = {}
    for key in dct.keys():
        if dct_avg[key] > 0:
            dict_wavg.update({key: round(max(sum(reduce(operator.mul, data) \
                for data in zip(dct[key], dct[key])) / sum(dct[key]) - dct_avg[key], 0), 2)})
        else:
            dict_wavg.update({key: 0})
    return dict_wavg


def GetWAverageFromList(lst, val_avg): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    if val_avg > 0:
        return round(max(sum(reduce(operator.mul, data) \
               for data in zip(lst, lst)) / sum(lst)-val_avg, 0), 2)
    else:
        return 0


def GetMaxFromDict(dct, dct_avg, dct_wavg): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return {key: round(abs(max(dct[key])-dct_wavg[key]-dct_avg[key]), 2) \
            for key in dct.keys()}


def GetMaxFromList(lst, val_avg, val_wavg): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return round(abs(max(lst)-val_wavg-val_avg), 2)


def GetNmonCSVData(nmon_file_name): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return sorted(csv.reader(open(nmon_file_name)))


def GetTitleRow(nmon_data, tag_data, pos_data=[]):
    """"""
    for row in nmon_data:
        if row[:1] == [tag_data] and not re.findall(r"\bT\d+", str(row[1])):
            if pos_data != []:
               return [j for i, j in enumerate(row) if i in pos_data]
            else:
               return row


def SetTemplateDefaultxAxis(interval_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    global LINEZOOM_CONFIG
    global LINEZOOMMB_CONFIG
    global AREAZOOM_CONFIG
    global AREAZOOM100_CONFIG

    LINEZOOM_CONFIG["xAxis"].update({"categories": interval_data})
    LINEZOOMMB_CONFIG["xAxis"].update({"categories": interval_data})
    AREAZOOM_CONFIG["xAxis"].update({"categories": interval_data})
    AREAZOOM100_CONFIG["xAxis"].update({"categories": interval_data})


def GetInterval(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    interval_data = []

    for row in nmon_data:
        if row[:1] == ["ZZZZ"]:
            interval_data.append(row[2])

    SetTemplateDefaultxAxis(interval_data)


def Feed(row, title, data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    if re.findall(r"\bT\d+", str(row[1])):
        for idx, val in enumerate(row[2:]):
            if val == "": val = "0"
            try:
                data[title[idx+2]].append(float(val))
            except KeyError:
                data.update({title[idx+2]: [float(val)]})

    return title, data


def FeedWithSumm(row, title, data, summ=[]): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    if re.findall(r"\bT\d+", str(row[1])):
        summ.append(round(sum(list(float(val) for val in row[2:])), 1))
        for idx, val in enumerate(row[2:]):
            try:
                data[title[idx+2]].append(float(val))
            except KeyError:
                data.update({title[idx+2]: [float(val)]})

    return title, data, summ


def GetDATA(title, data, renderTo, chart_type="line", stack=None): #~~~~~~~~~~~~
    """"""
    highchart = ""

    if title != None:

        chart = Highchart(renderTo=renderTo)
        chart.title(title[1] + " " + run_date)
        for key in sorted(data.keys()):
            chart.add_data_set(data[key], series_type=chart_type, name=key, stacking=stack)
        chart.set_options(LINEZOOM_CONFIG)

        highchart = chart.generate()

    return highchart


def GetDATAAVG(title, data, renderTo): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    if title != None:

        data_avg  = GetAverageFromDict(data)
        data_wavg = GetWAverageFromDict(data, data_avg)
        data_max  = GetMaxFromDict(data, data_avg, data_wavg)

        COLUMNSTACKEDHD_CONFIG["xAxis"].update({"categories": sorted(data.keys())}) # TODO: Sort by disk_read_avg + disk_read_wavg DESC

        chart_avg_wavg_max = Highchart(renderTo=renderTo)
        chart_avg_wavg_max.title(title[1] + " " + run_date)
        chart_avg_wavg_max.add_data_set(list(value for key, value in sorted(data_max.items())),  series_type="column", name="Max.",  stacking="normal", legendIndex=3)
        chart_avg_wavg_max.add_data_set(list(value for key, value in sorted(data_wavg.items())), series_type="column", name="WAvg.", stacking="normal", legendIndex=2)
        chart_avg_wavg_max.add_data_set(list(value for key, value in sorted(data_avg.items())),  series_type="column", name="Avg.",  stacking="normal", legendIndex=1)
        chart_avg_wavg_max.set_options(COLUMNSTACKEDHD_CONFIG)

        highchart = chart_avg_wavg_max.generate()

    return highchart


def GetCPU_SUMM(cpu_all_titl, cpu_user, cpu_syst, cpu_wait): #~~~~~~~~~~~~~~~~~~
    """"""
    cpu_user_tread_avg = {key: round((reduce(lambda x, y: x + y, cpu_user[key]) / len(cpu_user[key])), 1) for key in cpu_user.keys()}
    cpu_syst_tread_avg = {key: round((reduce(lambda x, y: x + y, cpu_syst[key]) / len(cpu_syst[key])), 1) for key in cpu_syst.keys()}
    cpu_wait_tread_avg = {key: round((reduce(lambda x, y: x + y, cpu_wait[key]) / len(cpu_wait[key])), 1) for key in cpu_wait.keys()}

    COLUMNSTACKED_CONFIG["xAxis"].update({"categories": sorted(cpu_user_tread_avg.keys())})

    cpu_summ = Highchart(renderTo="cpu_summ")
    cpu_summ.title("CPU by Thread" + " " + host_name + " " + run_date)
    cpu_summ.add_data_set(list(value for key, value in sorted(cpu_wait_tread_avg.items())), series_type="column", name=cpu_all_titl[4], stacking="normal")
    cpu_summ.add_data_set(list(value for key, value in sorted(cpu_syst_tread_avg.items())), series_type="column", name=cpu_all_titl[3], stacking="normal")
    cpu_summ.add_data_set(list(value for key, value in sorted(cpu_user_tread_avg.items())), series_type="column", name=cpu_all_titl[2], stacking="normal")
    cpu_summ.set_options(COLUMNSTACKED_CONFIG)

    return cpu_summ.generate()


def GetNmonInfo(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    global run_date
    global host_name

    for row in nmon_data:
        if row[:1] == ["AAA"]:
            if row[1] == "host": host_name = row[2]
            if row[1] == "date": run_date  = row[2]


def GetCPU_ALL(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    cpu_all_wait = []
    cpu_all_syst = []
    cpu_all_user = []
    cpu_all_lcpu = []

    cpu_all_titl = GetTitleRow(nmon_data, "CPU_ALL")

    if cpu_all_titl != None:

        for row in nmon_data:
            if row[:1] == ["CPU_ALL"] and re.findall(r"\bT\d+", str(row[1])):
                cpu_all_user.append(float(row[2]))
                cpu_all_syst.append(float(row[3]))
                cpu_all_wait.append(float(row[4]))
                cpu_all_lcpu.append(float(row[7]))

        cpu_all = Highchart(renderTo="cpu_all")
        cpu_all.title(cpu_all_titl[1] + " " + run_date)
        cpu_all.add_data_set(cpu_all_wait, series_type="area", name=cpu_all_titl[4], stacking="normal", legendIndex=3)
        cpu_all.add_data_set(cpu_all_syst, series_type="area", name=cpu_all_titl[3], stacking="normal", legendIndex=2)
        cpu_all.add_data_set(cpu_all_user, series_type="area", name=cpu_all_titl[2], stacking="normal", legendIndex=1)
        cpu_all.set_options(AREAZOOM100_CONFIG)

        highchart += cpu_all.generate()

        cpu_lcpu = Highchart(renderTo="cpu_lcpu")
        cpu_lcpu.title(cpu_all_titl[1] + " " + run_date)
        cpu_lcpu.add_data_set(cpu_all_lcpu, series_type="area", name=cpu_all_titl[7])
        cpu_lcpu.set_options(AREAZOOM_CONFIG)

        highchart += cpu_lcpu.generate()

    return highchart


def GetCPU00(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    cpu_line  = 0
    cpu_titl  = []
    cpu_user  = {}
    cpu_syst  = {}
    cpu_wait  = {}

    for row in nmon_data:
        if re.findall(r"\bCPU\d+", str(row[:1])):
            if re.findall(r"\bCPU ", str(row[:2])): cpu_titl.append(row)
            else:
                try:
                   cpu_user[row[0]].append(float(row[2]))
                   cpu_syst[row[0]].append(float(row[3]))
                   cpu_wait[row[0]].append(float(row[4]))
                except KeyError:
                   cpu_user.update({row[0]: [float(row[2])]})
                   cpu_syst.update({row[0]: [float(row[3])]})
                   cpu_wait.update({row[0]: [float(row[4])]})

    cpu = dict((name, Highchart(renderTo=name)) for name in list(cpu_user.keys()))
    for name in sorted(cpu):
       cpu[name].title(cpu_titl[cpu_line][1] + " " + run_date)
       cpu[name].add_data_set(cpu_wait[name], series_type="area", name=cpu_titl[cpu_line][4], stacking="normal", legendIndex=3)
       cpu[name].add_data_set(cpu_syst[name], series_type="area", name=cpu_titl[cpu_line][3], stacking="normal", legendIndex=2)
       cpu[name].add_data_set(cpu_user[name], series_type="area", name=cpu_titl[cpu_line][2], stacking="normal", legendIndex=1)
       cpu[name].set_options(AREAZOOM100_CONFIG)
       highchart += cpu[name].generate()
       cpu_line += 1

    highchart += GetCPU_SUMM(cpu_titl[0], cpu_user, cpu_syst, cpu_wait)

    return highchart


def GetCPU(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    highchart += GetCPU_ALL(nmon_data)
    highchart += GetCPU00(nmon_data)

    return highchart


def  GetMEM(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    mem_real  = []
    mem_total = []

    mem_new_syst = []
    mem_new_proc = []
    mem_new_fsca = []

    mem_use_nump = []
    mem_use_minp = []
    mem_use_maxp = []
    mem_use_comp = []

    mem_titl     = GetTitleRow(nmon_data, "MEM")
    mem_new_titl = GetTitleRow(nmon_data, "MEMNEW")
    mem_use_titl = GetTitleRow(nmon_data, "MEMUSE")

    for row in nmon_data:
        if row[:1] == ["MEM"] and re.findall(r"\bT\d+", str(row[1])):
            mem_real.append(float(row[4]))
            mem_total.append(float(row[6]))

        if row[:1] == ["MEMNEW"] and re.findall(r"\bT\d+", str(row[1])):
            mem_new_syst.append(float(row[4]))
            mem_new_proc.append(float(row[2]))
            mem_new_fsca.append(float(row[3]))

        if row[:1] == ["MEMUSE"] and re.findall(r"\bT\d+", str(row[1])):
            mem_use_nump.append(float(row[2]))
            mem_use_minp.append(float(row[3]))
            mem_use_maxp.append(float(row[4]))
            mem_use_comp.append(100-float(row[2]))

    if mem_titl != None:
        memory_real = Highchart(renderTo="mem_real")
        memory_real.title(mem_titl[1] + " " + run_date)
        memory_real.add_data_set(mem_real, series_type="line", name=mem_titl[4])
        memory_real.set_options(LINEZOOMMB_CONFIG)
        highchart += memory_real.generate()

        memory_total = Highchart(renderTo="mem_total")
        memory_total.title(mem_titl[1] + " " + run_date)
        memory_total.add_data_set(mem_total, series_type="area", name=mem_titl[6])
        memory_total.set_options(AREAZOOMMB_CONFIG)
        highchart += memory_total.generate()

    if mem_new_titl != None:
        mem_new = Highchart(renderTo="mem_new")
        mem_new.title(mem_use_titl[1] + " " + run_date)
        mem_new.add_data_set(mem_new_fsca, series_type="area", name=mem_new_titl[3], stacking="normal", legendIndex=3)
        mem_new.add_data_set(mem_new_proc, series_type="area", name=mem_new_titl[2], stacking="normal", legendIndex=2)
        mem_new.add_data_set(mem_new_syst, series_type="area", name=mem_new_titl[4], stacking="normal", legendIndex=1)
        mem_new.set_options(AREAZOOM100_CONFIG)
        highchart += mem_new.generate()

    if mem_use_titl != None:
        mem_use = Highchart(renderTo="mem_use")
        mem_use.title("VMTUNE Parameters" + " " + host_name + " " + run_date)
        mem_use.add_data_set(mem_use_nump, series_type="line", name=mem_use_titl[2])
        mem_use.add_data_set(mem_use_minp, series_type="line", name=mem_use_titl[3])
        mem_use.add_data_set(mem_use_maxp, series_type="line", name=mem_use_titl[4])
        mem_use.add_data_set(mem_use_comp, series_type="line", name="%comp")
        mem_use.set_options(LINEZOOM100_CONFIG)
        highchart += mem_use.generate()

    return highchart


def GetPAGE(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    page_pgin  = []; page_pgsout   = [];
    page_pgout = []; page_reclaims = [];
    page_pgsin = []; page_scans    = [];

    page_title = GetTitleRow(nmon_data, "PAGE")

    if page_title != None:

        for row in nmon_data:
            if row[:1] == ["PAGE"] and re.findall(r"\bT\d+", str(row[1])):
                page_pgin.append(float(row[3]))
                page_pgout.append(float(row[4]))
                page_pgsin.append(float(row[5]))
                page_pgsout.append(float(row[6]))
                page_reclaims.append(float(row[7]))
                page_scans.append(float(row[8]))

        page_pgs = Highchart(renderTo="page_pgs")
        page_pgs.title(page_title[1] + " " + "(pgspace)" + " " + run_date)
        page_pgs.add_data_set(page_pgsin,  series_type="line", name=page_title[5])
        page_pgs.add_data_set(page_pgsout, series_type="line", name=page_title[6])
        page_pgs.set_options(LINEZOOM_CONFIG)
        highchart += page_pgs.generate()

        page_pg = Highchart(renderTo="page_pg")
        page_pg.title(page_title[1] + " " + "(filesystem)" + " " + run_date)
        page_pg.add_data_set(page_pgout, series_type="area", name=page_title[4], stacking="normal")
        page_pg.add_data_set(page_pgin,  series_type="area", name=page_title[3], stacking="normal")
        page_pg.set_options(AREAZOOM_CONFIG)
        highchart += page_pg.generate()

        page_srfr = Highchart(renderTo="page_srfr")
        page_srfr.title(page_title[1] + " " + "(Page scan:free ratio)" + " " + run_date)
        page_srfr_zip = zip(page_scans, page_reclaims)
        page_srfr_ratio = [DividePageRatio(x, y) for x, y in (page_srfr_zip)]
        page_srfr.add_data_set(page_srfr_ratio, series_type="line")
        page_srfr.set_options(LINEZOOMNOLEGEND_CONFIG)
        highchart += page_srfr.generate()

    return highchart


def GetLPAR(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    lpar_physicalcpu = []; lpar_vp_sys      = [];
    lpar_entitled    = []; lpar_vp_user     = [];
    lpar_unfoldedvp  = []; lpar_otherlpar   = [];
    lpar_vp_wait     = []; lpar_pool_idle   = [];

    lpar_title = GetTitleRow(nmon_data, "LPAR")

    if lpar_title != None:

        for row in nmon_data:
            if row[:1] == ["LPAR"] and re.findall(r"\bT\d+", str(row[1])):
                lpar_physicalcpu.append(float(row[2]))
                lpar_entitled.append(float(row[6]))
                lpar_unfoldedvp.append(float(row[3]))
                lpar_vp_wait.append(float(row[19]))
                lpar_vp_sys.append(float(row[18]))
                lpar_vp_user.append(float(row[17]))
                lpar_otherlpar.append(float(row[5]) - float(row[2]) - float(row[8]))
                lpar_pool_idle.append(float(row[8]))

        lpar_cpu_ent = Highchart(renderTo="lpar_cpu_ent")
        lpar_cpu_ent.title("Physical CPU vs Entitlement" + " - " + host_name + " " + run_date)
        lpar_cpu_ent.add_data_set(lpar_physicalcpu, series_type="line", name=lpar_title[2])
        lpar_cpu_ent.add_data_set(lpar_entitled,    series_type="line", name=lpar_title[6])
        lpar_cpu_ent.add_data_set(lpar_unfoldedvp,  series_type="line", name="Unfolded VPs")
        lpar_cpu_ent.set_options(LINEZOOM_CONFIG)
        highchart += lpar_cpu_ent.generate()

        lpar_cpu_vp = Highchart(renderTo="lpar_cpu_vp")
        lpar_cpu_vp.title("CPU% vs VPs" + " - " + host_name + " " + run_date)
        lpar_cpu_vp.add_data_set(lpar_vp_wait, series_type="area", name=lpar_title[19], stacking="normal", legendIndex=3)
        lpar_cpu_vp.add_data_set(lpar_vp_sys,  series_type="area", name=lpar_title[18], stacking="normal", legendIndex=2)
        lpar_cpu_vp.add_data_set(lpar_vp_user, series_type="area", name=lpar_title[17], stacking="normal", legendIndex=1)
        lpar_cpu_vp.set_options(AREAZOOM100_CONFIG)
        highchart += lpar_cpu_vp.generate()

        lpar_cpu_spool = Highchart(renderTo="lpar_cpu_spool")
        lpar_cpu_spool.title("Shared Pool Utilisation" + " - " + host_name + " " + run_date)
        lpar_cpu_spool.add_data_set(lpar_pool_idle,   series_type="area", name=lpar_title[8], stacking="normal", legendIndex=3)
        lpar_cpu_spool.add_data_set(lpar_otherlpar,   series_type="area", name="OtherLPARs",  stacking="normal", legendIndex=2)
        lpar_cpu_spool.add_data_set(lpar_physicalcpu, series_type="area", name=lpar_title[2], stacking="normal", legendIndex=1)
        lpar_cpu_spool.set_options(AREAZOOM_CONFIG)
        highchart += lpar_cpu_spool.generate()

    return highchart


def GetDISKREAD(disk_read_kbs_title, disk_read_kbs): #~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    disk_read = Highchart(renderTo="disk_read")
    disk_read.title(disk_read_kbs_title[1] + " " + run_date)
    for key in sorted(disk_read_kbs.keys()):
        disk_read.add_data_set(disk_read_kbs[key], series_type="line", name=key)
    disk_read.set_options(LINEZOOM_CONFIG)

    return disk_read.generate()


def GetDISKREADAVG(disk_read_kbs_title, disk_read_kbs): #~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    disk_read_avg  = GetAverageFromDict(disk_read_kbs)
    disk_read_wavg = GetWAverageFromDict(disk_read_kbs, disk_read_avg)
    disk_read_max  = GetMaxFromDict(disk_read_kbs, disk_read_avg, disk_read_wavg)

    COLUMNSTACKEDHD_CONFIG["xAxis"].update({"categories": sorted(disk_read_kbs.keys())}) # TODO: Sort by disk_read_avg + disk_read_wavg DESC

    disk_read_avg_wavg_max = Highchart(renderTo="disk_read_avg_wavg_max")
    disk_read_avg_wavg_max.title(disk_read_kbs_title[1] + " " + run_date)
    disk_read_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_read_max.items())),  series_type="column", name="Max.",  stacking="normal")
    disk_read_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_read_wavg.items())), series_type="column", name="WAvg.", stacking="normal")
    disk_read_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_read_avg.items())),  series_type="column", name="Avg.",  stacking="normal")
    disk_read_avg_wavg_max.set_options(COLUMNSTACKEDHD_CONFIG)

    return disk_read_avg_wavg_max.generate()


def GetDISKWRITE(disk_write_kbs_title, disk_write_kbs): #~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    disk_write = Highchart(renderTo="disk_write")
    disk_write.title(disk_write_kbs_title[1] + " " + run_date)
    for key in sorted(disk_write_kbs.keys()):
        disk_write.add_data_set(disk_write_kbs[key], series_type="line", name=key)
    disk_write.set_options(LINEZOOM_CONFIG)

    return disk_write.generate()


def GetDISKWRITEAVG(disk_write_kbs_title, disk_write_kbs): #~~~~~~~~~~~~~~~~~~~~
    """"""
    disk_write_avg  = GetAverageFromDict(disk_write_kbs)
    disk_write_wavg = GetWAverageFromDict(disk_write_kbs, disk_write_avg)
    disk_write_max  = GetMaxFromDict(disk_write_kbs, disk_write_avg, disk_write_wavg)

    COLUMNSTACKEDHD_CONFIG["xAxis"].update({"categories": sorted(disk_write_kbs.keys())}) # TODO: Sort by disk_write_avg + disk_write_wavg DESC

    disk_write_avg_wavg_max = Highchart(renderTo="disk_write_avg_wavg_max")
    disk_write_avg_wavg_max.title(disk_write_kbs_title[1] + " " + run_date)
    disk_write_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_write_max.items())),  series_type="column", name="Max.",  stacking="normal")
    disk_write_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_write_wavg.items())), series_type="column", name="WAvg.", stacking="normal")
    disk_write_avg_wavg_max.add_data_set(list(value for key, value in sorted(disk_write_avg.items())),  series_type="column", name="Avg.",  stacking="normal")
    disk_write_avg_wavg_max.set_options(COLUMNSTACKEDHD_CONFIG)

    return disk_write_avg_wavg_max.generate()


def GetDISKXFER(disk_xfer_psec_title, disk_xfer_psec): #~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    disk_xfer = Highchart(renderTo="disk_xfer")
    disk_xfer.title(disk_xfer_psec_title[1] + " " + run_date)
    for key in sorted(disk_xfer_psec.keys()):
        disk_xfer.add_data_set(disk_xfer_psec[key], series_type="line", name=key)
    disk_xfer.set_options(LINEZOOM_CONFIG)

    return disk_xfer.generate()


def GetDISK_SUMM(disk_write_kbs_title, disk_read_kbs_summ, disk_write_kbs_summ):
    """"""
    highchart = ""

    disk_summ_area = Highchart(renderTo="disk_summ_area")
    disk_summ_area.title("Disk total KB/s" + " " + host_name + " " + run_date)
    disk_summ_area.add_data_set(disk_write_kbs_summ, series_type="area", name="Disk Write KB/s", stacking="normal")
    disk_summ_area.add_data_set(disk_read_kbs_summ,  series_type="area", name="Disk Read KB/s",  stacking="normal")
    #disk_summ_area.add_data_set(disk_xfer_psec_summ,  series_type="line", name="I/O Sec") # TODO: Add with yAxis=1 (left side) and opposite:True
    disk_summ_area.set_options(AREAZOOM_CONFIG)
    highchart += disk_summ_area.generate()

    disk_read_kbs_summ_avg   = GetAverageFromList(disk_read_kbs_summ)
    disk_read_kbs_summ_wavg  = GetWAverageFromList(disk_read_kbs_summ, disk_read_kbs_summ_avg)
    disk_read_kbs_summ_max   = GetMaxFromList(disk_read_kbs_summ, disk_read_kbs_summ_wavg, disk_read_kbs_summ_avg)
    disk_write_kbs_summ_avg  = GetAverageFromList(disk_write_kbs_summ)
    disk_write_kbs_summ_wavg = GetWAverageFromList(disk_write_kbs_summ, disk_write_kbs_summ_avg)
    disk_write_kbs_summ_max  = GetMaxFromList(disk_write_kbs_summ, disk_write_kbs_summ_wavg, disk_write_kbs_summ_avg)

    COLUMNSTACKEDHD_CONFIG["xAxis"].update({"categories": ["Disk Read KB/s","Disk Write KB/s"]})

    disk_summ_column = Highchart(renderTo="disk_summ_column")
    disk_summ_column.title("Disk total KB/s" + " " + host_name + " " + run_date)
    disk_summ_column.add_data_set([disk_read_kbs_summ_max,  disk_write_kbs_summ_max],  series_type="column", name="Max.",  stacking="normal")
    disk_summ_column.add_data_set([disk_read_kbs_summ_wavg, disk_write_kbs_summ_wavg], series_type="column", name="WAvg.", stacking="normal")
    disk_summ_column.add_data_set([disk_read_kbs_summ_avg,  disk_write_kbs_summ_avg],  series_type="column", name="Avg.",  stacking="normal")
    disk_summ_column.set_options(COLUMNSTACKEDHD_CONFIG)
    highchart += disk_summ_column.generate()

    return highchart


def GetDISK(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    disk_read_kbs_summ   = [];  disk_write_kbs_summ  = [];
    disk_read_kbs        = {};  disk_write_kbs       = {};
    disk_xfer_psec_summ  = [];  disk_bsize_summ      = [];
    disk_xfer_psec       = {};  disk_bsize           = {};
    disk_busy_summ       = [];  disk_serv_summ       = [];
    disk_busy            = {};  disk_serv            = {};
    disk_wait_summ       = [];  disk_rxfer_summ      = [];
    disk_wait            = {};  disk_rxfer           = {};

    disk_bsize_title      = GetTitleRow(nmon_data, "DISKBSIZE")
    disk_busy_title       = GetTitleRow(nmon_data, "DISKBUSY")
    disk_read_kbs_title   = GetTitleRow(nmon_data, "DISKREAD")
    disk_rxfer_title      = GetTitleRow(nmon_data, "DISKRXFER")
    disk_serv_title       = GetTitleRow(nmon_data, "DISKSERV")
    disk_wait_title       = GetTitleRow(nmon_data, "DISKWAIT")
    disk_write_kbs_title  = GetTitleRow(nmon_data, "DISKWRITE")
    disk_xfer_psec_title  = GetTitleRow(nmon_data, "DISKXFER")

    for row in nmon_data:
        if row[:1] == ["DISKBSIZE"]:
            disk_bsize_title, disk_bsize, disk_bsize_summ = \
            FeedWithSumm(row, disk_bsize_title, disk_bsize, disk_bsize_summ)

        if row[:1] == ["DISKBUSY"]:
            disk_busy_title, disk_busy, disk_busy_summ = \
            FeedWithSumm(row, disk_busy_title, disk_busy, disk_busy_summ)

        if row[:1] == ["DISKREAD"]:
            disk_read_kbs_title, disk_read_kbs, disk_read_kbs_summ = \
            FeedWithSumm(row, disk_read_kbs_title, disk_read_kbs, disk_read_kbs_summ)

        if row[:1] == ["DISKRXFER"]:
            disk_rxfer_title, disk_rxfer, disk_rxfer_summ = \
            FeedWithSumm(row, disk_rxfer_title, disk_rxfer, disk_rxfer_summ)

        if row[:1] == ["DISKSERV"]:
            disk_serv_title, disk_serv, disk_serv_summ = \
            FeedWithSumm(row, disk_serv_title, disk_serv, disk_serv_summ)

        if row[:1] == ["DISKWAIT"]:
            disk_wait_title, disk_wait, disk_wait_summ = \
            FeedWithSumm(row, disk_wait_title, disk_wait, disk_wait_summ)

        if row[:1] == ["DISKWRITE"]:
            disk_write_kbs_title, disk_write_kbs, disk_write_kbs_summ = \
            FeedWithSumm(row, disk_write_kbs_title, disk_write_kbs, disk_write_kbs_summ)

        if row[:1] == ["DISKXFER"]:
            disk_xfer_psec_title, disk_xfer_psec, disk_xfer_psec_summ = \
            FeedWithSumm(row, disk_xfer_psec_title, disk_xfer_psec, disk_xfer_psec_summ)

    highchart += GetDATA     (disk_busy_title,      disk_busy,      "disk_bsize")
    highchart += GetDATAAVG  (disk_busy_title,      disk_busy,      "disk_bsize_avg_wavg_max")
    highchart += GetDATA     (disk_bsize_title,     disk_bsize,     "disk_busy")
    highchart += GetDATAAVG  (disk_bsize_title,     disk_bsize,     "disk_busy_avg_wavg_max")
    highchart += GetDATA     (disk_read_kbs_title,  disk_read_kbs,  "disk_read")
    highchart += GetDATAAVG  (disk_read_kbs_title,  disk_read_kbs,  "disk_read_avg_wavg_max")
    highchart += GetDATA     (disk_rxfer_title,     disk_rxfer,     "disk_rxfer")
    highchart += GetDATAAVG  (disk_rxfer_title,     disk_rxfer,     "disk_rxfer_avg_wavg_max")
    highchart += GetDATA     (disk_serv_title,      disk_serv,      "disk_serv")
    highchart += GetDATAAVG  (disk_serv_title,      disk_serv,      "disk_serv_avg_wavg_max")
    highchart += GetDATA     (disk_wait_title,      disk_wait,      "disk_wait")
    highchart += GetDATAAVG  (disk_wait_title,      disk_wait,      "disk_wait_avg_wavg_max")
    highchart += GetDATA     (disk_write_kbs_title, disk_write_kbs, "disk_write")
    highchart += GetDATAAVG  (disk_write_kbs_title, disk_write_kbs, "disk_write_avg_wavg_max")
    highchart += GetDATA     (disk_xfer_psec_title, disk_xfer_psec, "disk_xfer")
    highchart += GetDATAAVG  (disk_xfer_psec_title, disk_xfer_psec, "disk_xfer_avg_wavg_max")

    highchart += GetDISK_SUMM(disk_write_kbs_title, disk_read_kbs_summ, disk_write_kbs_summ)

    return highchart


def GetFCHAN(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    fc_read   = {};  fc_write   = {};
    fc_xferin = {};  fc_xferout = {};

    fc_read_title    = GetTitleRow(nmon_data, "FCREAD")
    fc_write_title   = GetTitleRow(nmon_data, "FCWRITE")
    fc_xferin_title  = GetTitleRow(nmon_data, "FCXFERIN")
    fc_xferout_title = GetTitleRow(nmon_data, "FCXFEROUT")

    for row in nmon_data:
        if row[:1] == ["FCREAD"]:
            fc_read_title, fc_read       = Feed(row, fc_read_title, fc_read)
        if row[:1] == ["FCWRITE"]:
            fc_write_title, fc_write     = Feed(row, fc_write_title, fc_write)
        if row[:1] == ["FCXFERIN"]:
            fc_xferin_title, fc_xferin   = Feed(row, fc_xferin_title, fc_xferin)
        if row[:1] == ["FCXFEROUT"]:
            fc_xferout_title, fc_xferout = Feed(row, fc_xferout_title, fc_xferout)

    highchart += GetDATA     (fc_read_title,    fc_read,    "fcread")
    highchart += GetDATAAVG  (fc_read_title,    fc_read,    "fcread_avg_wavg_max")
    highchart += GetDATA     (fc_write_title,   fc_write,   "fcwrite")
    highchart += GetDATAAVG  (fc_write_title,   fc_write,   "fcwrite_avg_wavg_max")
    highchart += GetDATA     (fc_xferin_title,  fc_xferin,  "fcxferin")
    highchart += GetDATAAVG  (fc_xferin_title,  fc_xferin,  "fcxferin_avg_wavg_max")
    highchart += GetDATA     (fc_xferout_title, fc_xferout, "fcxferout")
    highchart += GetDATAAVG  (fc_xferout_title, fc_xferout, "fcxferout_avg_wavg_max")

    return highchart


def GetVOLGRP(nmon_data):
    """"""
    highchart = ""

    vg_busy = {};  vg_read  = {};
    vg_size = {};  vg_write = {};
    vg_xfer = {};

    vg_busy_title  = GetTitleRow(nmon_data, "VGBUSY")
    vg_read_title  = GetTitleRow(nmon_data, "VGREAD")
    vg_size_title  = GetTitleRow(nmon_data, "VGSIZE")
    vg_write_title = GetTitleRow(nmon_data, "VGWRITE")
    vg_xfer_title  = GetTitleRow(nmon_data, "VGXFER")

    for row in nmon_data:
        if row[:1] == ["VGBUSY"]:
            vg_busy_title, vg_busy   = Feed(row, vg_busy_title, vg_busy)
        if row[:1] == ["VGREAD"]:
            vg_read_title, vg_read   = Feed(row, vg_read_title, vg_read)
        if row[:1] == ["VGSIZE"]:
            vg_size_title, vg_size   = Feed(row, vg_size_title, vg_size)
        if row[:1] == ["VGWRITE"]:
            vg_write_title, vg_write = Feed(row, vg_write_title, vg_write)
        if row[:1] == ["VGXFER"]:
            vg_xfer_title, vg_xfer   = Feed(row, vg_xfer_title, vg_xfer)

    highchart += GetDATA     (vg_busy_title,  vg_busy,  "vg_busy")
    highchart += GetDATAAVG  (vg_busy_title,  vg_busy,  "vg_busy_avg_wavg_max")
    highchart += GetDATA     (vg_read_title,  vg_read,  "vg_read")
    highchart += GetDATAAVG  (vg_read_title,  vg_read,  "vg_read_avg_wavg_max")
    highchart += GetDATA     (vg_size_title,  vg_size,  "vg_size")
    highchart += GetDATAAVG  (vg_size_title,  vg_size,  "vg_size_avg_wavg_max")
    highchart += GetDATA     (vg_write_title, vg_write, "vg_write")
    highchart += GetDATAAVG  (vg_write_title, vg_write, "vg_write_avg_wavg_max")
    highchart += GetDATA     (vg_write_title, vg_xfer,  "vg_xfer")
    highchart += GetDATAAVG  (vg_write_title, vg_xfer,  "vg_xfer_avg_wavg_max")

    return highchart


def GetPAGING(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart    = ""

    paging       = {}

    paging_title = GetTitleRow(nmon_data, "PAGING")

    if paging_title != None:

        for row in nmon_data:
            if row[:1] == ["PAGING"]:
                paging_title, paging = Feed(row, paging_title, paging)

        highchart += GetDATA(paging_title, paging, "paging")

    return highchart


def GetPOOLS(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    max_pool_cap   = []
    ent_pool_cap   = []
    pool_busy_time = []

    pools_title = GetTitleRow(nmon_data, "POOLS")

    if pools_title != None:

        for row in nmon_data:
            if row[:1] == ["POOLS"] and re.findall(r"\bT\d+", str(row[1])):
                max_pool_cap.append(float(row[3]))
                ent_pool_cap.append(float(row[4]))
                pool_busy_time.append(float(row[6]))

        pools = Highchart(renderTo="pools")
        pools.title(pools_title[1] + " " + run_date)
        pools.add_data_set(max_pool_cap,   series_type="line", name=pools_title[3])
        pools.add_data_set(ent_pool_cap,   series_type="line", name=pools_title[4])
        pools.add_data_set(pool_busy_time, series_type="line", name=pools_title[6])
        pools.set_options(LINEZOOM_CONFIG)
        highchart += pools.generate()

    return highchart


def GetPROC(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    proc_run_queue = []
    proc_swapin    = []
    proc_switch    = []
    proc_syscall   = []
    proc_fork      = []
    proc_exec      = []

    proc_title = GetTitleRow(nmon_data, "PROC")

    if proc_title != None:

        for row in nmon_data:
            if row[:1] == ["PROC"] and re.findall(r"\bT\d+", str(row[1])):
                proc_run_queue.append(float(row[2]))
                proc_swapin.append(float(row[3]))
                proc_switch.append(float(row[4]))
                proc_syscall.append(float(row[5]))
                proc_fork.append(float(row[8]))
                proc_exec.append(float(row[9]))

        proc_1 = Highchart(renderTo="proc_1")
        proc_1.title(proc_title[1] + " " + run_date)
        proc_1.add_data_set(proc_run_queue, series_type="line", name="RunQueue")
        proc_1.add_data_set(proc_swapin,    series_type="line", name="Swap-in")
        proc_1.set_options(LINEZOOM_CONFIG)
        highchart += proc_1.generate()

        proc_2 = Highchart(renderTo="proc_2")
        proc_2.title(proc_title[1] + " " + run_date)
        proc_2.add_data_set(proc_switch,  series_type="line", name=proc_title[4]+"/sec")
        proc_2.add_data_set(proc_syscall, series_type="line", name=proc_title[5]+"s/sec")
        proc_2.set_options(LINEZOOM_CONFIG)
        highchart += proc_2.generate()

        proc_3 = Highchart(renderTo="proc_3")
        proc_3.title(proc_title[1] + " " + run_date)
        proc_3.add_data_set(proc_fork, series_type="line", name=proc_title[8]+"s/sec")
        proc_3.add_data_set(proc_exec, series_type="line", name=proc_title[9]+"s/sec")
        proc_3.set_options(LINEZOOM_CONFIG)
        highchart += proc_3.generate()

    return highchart


def GetFILE(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    file_readch  = []
    file_writech = []
    fileiget     = []
    file_namei   = []
    file_dirblk  = []

    file_title = GetTitleRow(nmon_data, "FILE")

    if file_title != None:

        for row in nmon_data:
            if row[:1] == ["FILE"] and re.findall(r"\bT\d+", str(row[1])):
                file_readch.append(float(row[5]))
                file_writech.append(float(row[6]))
                fileiget.append(float(row[2]))
                file_namei.append(float(row[3]))
                file_dirblk.append(float(row[4]))

        file_rwsyscalls = Highchart(renderTo="file_rwsyscalls")
        file_rwsyscalls.title("Kernel Read/Write System Calls" + " " + host_name + " " + run_date)
        file_rwsyscalls.add_data_set(file_readch,  series_type="line", name=file_title[5]+"/sec")
        file_rwsyscalls.add_data_set(file_writech, series_type="line", name=file_title[6]+"/sec")
        file_rwsyscalls.set_options(LINEZOOM_CONFIG)
        highchart += file_rwsyscalls.generate()

        file_fsfunc = Highchart(renderTo="file_fsfunc")
        file_fsfunc.title("Kernel Filesystem Functions" + " " + host_name + " " + run_date)
        file_fsfunc.add_data_set(fileiget,    series_type="line", name=file_title[2])
        file_fsfunc.add_data_set(file_namei,  series_type="line", name=file_title[3])
        file_fsfunc.add_data_set(file_dirblk, series_type="line", name=file_title[4])
        file_fsfunc.set_options(LINEZOOM_CONFIG)
        highchart += file_fsfunc.generate()

    return highchart


def GetIOADAPT(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    disk_adapt            = {}
    disk_adapt_read_write = {}
    disk_adapt_xfer_tps   = {}

    disk_adapt_title = GetTitleRow(nmon_data, "IOADAPT")

    if disk_adapt_title != None:

        for row in nmon_data:
            if row[:1] == ["IOADAPT"]:
                disk_adapt_title, disk_adapt = Feed(row, disk_adapt_title, disk_adapt)

        disk_adapt_read_write = ({k:disk_adapt[k] for k in [s for s in disk_adapt.keys() if "write" in s or "read" in s]})
        disk_adapt_xfer_tps   = ({k:disk_adapt[k] for k in [s for s in disk_adapt.keys() if "xfer-tps" in s]})

        highchart += GetDATA(disk_adapt_title,    disk_adapt_read_write, "ioadapt_read_write", "area", "normal")
        highchart += GetDATA(disk_adapt_title,    disk_adapt_xfer_tps,   "ioadapt_xfer_tps",   "area", "normal")
        highchart += GetDATAAVG(disk_adapt_title, disk_adapt_read_write, "ioadapt_avg_wavg_max")

    return highchart


def GetPROCAIO(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    procaio = {}
    procaio_asynch = {}
    procaio_asynch_avg = {}

    procaio_title = GetTitleRow(nmon_data, "PROCAIO")

    if procaio_title != None:

        for row in nmon_data:
            if row[:1] == ["PROCAIO"]:
                procaio_title, procaio = Feed(row, procaio_title, procaio)

        procaio_asynch     = ({k:procaio[k] for k in [s for s in procaio.keys() if "aiorunning" in s]}) # TODO: Add syscpu with yAxis=1 (left side) and opposite:True (aiocpu/LogicalCPUs)
        procaio_asynch_avg = ({k:procaio[k] for k in [s for s in procaio.keys() if "aioprocs" in s or "aiorunning" in s]})

        highchart += GetDATA(procaio_title,    procaio_asynch,     "procaio_asynch")
        highchart += GetDATAAVG(procaio_title, procaio_asynch_avg, "procaio_avg_wavg_max")

    return highchart


def GetNET(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    net = {}

    net_title = GetTitleRow(nmon_data, "NET")

    if net_title != None:

        for row in nmon_data:
            if row[:1] == ["NET"]:
                net_title, net = Feed(row, net_title, net)

    # TODO: Total-Read // Total-Write -ve
    highchart += GetDATA(net_title, net, "net", "area", "normal")
    highchart += GetDATAAVG(net_title, net, "net_avg_wavg_max")

    return highchart

def GetNETPACKET(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    netpacket = {}
    netpacket_avg = {}

    netpacket_title = GetTitleRow(nmon_data, "NETPACKET")

    if netpacket_title != None:

        for row in nmon_data:
            if row[:1] == ["NETPACKET"]:
                netpacket_title, netpacket = Feed(row, netpacket_title, netpacket)

        highchart += GetDATA(netpacket_title,    netpacket, "netpacket")
        highchart += GetDATAAVG(netpacket_title, netpacket, "netpacket_avg_wavg_max")

    return highchart


def GetNETSIZE(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    netsize = {}
    netsize_avg = {}

    netsize_title = GetTitleRow(nmon_data, "NETSIZE")

    if netsize_title != None:

        for row in nmon_data:
            if row[:1] == ["NETSIZE"]:
                netsize_title, netsize = Feed(row, netsize_title, netsize)

        highchart += GetDATA(netsize_title,    netsize, "netsize")
        highchart += GetDATAAVG(netsize_title, netsize, "netsize_avg_wavg_max")

    return highchart


def GetJFSFILE(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    jfsfile = {}

    jfsfile_title = GetTitleRow(nmon_data, "JFSFILE")

    if jfsfile_title != None:

        for row in nmon_data:
            if row[:1] == ["JFSFILE"]:
                jfsfile_title, jfsfile = Feed(row, jfsfile_title, jfsfile)

        highchart += GetDATAAVG(jfsfile_title, jfsfile, "jfsfile_avg_wavg_max")

    return highchart


def GetJFSINODE(nmon_data): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    jfsinode = {}

    jfsinode_title = GetTitleRow(nmon_data, "JFSINODE")

    if jfsinode_title != None:

        for row in nmon_data:
            if row[:1] == ["JFSINODE"]:
                jfsinode_title, jfsinode = Feed(row, jfsinode_title, jfsinode)

        highchart += GetDATAAVG(jfsinode_title, jfsinode, "jfsinode_avg_wavg_max")

    return highchart


def SetDefaultColors(highchart): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return highchart.replace("colors: [],",
                             """colors: ['#7EB5D6', '#2A75A9', '#274257',
                                         '#DFC184', '#8F6048', '#644436',
                                         '#E9B64D', '#E48743', '#9E3B33',
                                         '#601407'],""")


def SetDisableMarkers(highchart): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    return highchart.replace("plotOptions: {",
                             "plotOptions: {series: {marker: {enabled: false}},")


def GenHighcharts(nmon_file_name, highchart): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""

    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    new_fn = os.path.join(__location__, "%s.html" % (nmon_file_name))

    with open(os.path.dirname(inspect.getfile(Highchart))+"\\show_temp.tmp", 'r') as file_open:
        tmp = file_open.read()

    html = tmp.format(chart_data=highchart)

    with open(new_fn, 'w') as file_open:
        file_open.write(html)

    handle = webbrowser.get()
    handle.open("file://"+new_fn)


def PyNmon2Highcharts(): #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """"""
    highchart = ""

    nmon_file_name = ParseNmonFileParam()
    nmon_data = GetNmonCSVData(nmon_file_name)

    GetInterval(nmon_data)
    GetNmonInfo(nmon_data)

    highchart += GetCPU(nmon_data)
    highchart += GetMEM(nmon_data)
    highchart += GetPAGE(nmon_data)
    highchart += GetLPAR(nmon_data)
    highchart += GetDISK(nmon_data)
    highchart += GetFCHAN(nmon_data)
    highchart += GetVOLGRP(nmon_data)
    highchart += GetPAGING(nmon_data)
    highchart += GetPOOLS(nmon_data)
    highchart += GetPROC(nmon_data)
    highchart += GetFILE(nmon_data)
    highchart += GetIOADAPT(nmon_data)
    highchart += GetJFSFILE(nmon_data)
    highchart += GetJFSINODE(nmon_data)
    highchart += GetNET(nmon_data)
    highchart += GetNETPACKET(nmon_data)
    highchart += GetNETSIZE(nmon_data)
    highchart += GetPROCAIO(nmon_data)

    highchart = SetDefaultColors(highchart)
    highchart = SetDisableMarkers(highchart)

    GenHighcharts(nmon_file_name, highchart)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    PyNmon2Highcharts()
