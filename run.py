#!/usr/bin/python
# -*- coding: utf-8 -*-

from Tkinter import Frame, Tk, BOTH, Menu, RAISED, Label, W, N, E, S, Button, Entry, Listbox, END, DISABLED, VERTICAL, \
    Message, \
    StringVar, Text
from PIL import ImageTk
import tkMessageBox as mbox

import numpy
import tkFileDialog
import pickle
from test2 import *
import ttk


class Example(Frame):
    def __init__(self, parent):
        self.catFactors = {}
        Frame.__init__(self, parent)

        self.parent = parent
        self.initUI()

    def initUI(self):
        if hasattr(self, 'frame0'):
            self.frame0.destroy()
        self.initUIRoot()
        self.initUIFrame()

    def initUIRoot(self):
        self.parent.title("集总模型")
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        self.frame0 = Frame(self, relief=RAISED)
        self.frame0.pack(fill=BOTH, expand=True)

        fileMenu = Menu(menubar)
        fileMenu.add_command(label=u"新建催化剂", command=self.onNewCata)
        fileMenu.add_command(label=u"精确预测", command=self.onNewPre)
        fileMenu.add_command(label=u"趋势预测", command=self.onNewGraph)
        fileMenu.add_command(label=u"最优条件预测", command=self.onNewBest)
        helpMenu = Menu(menubar)
        helpMenu.add_command(label=u"关于", command=self.onHelp)

        mainPageMenu = Menu(menubar)
        mainPageMenu.add_command(label=u"主页", command=self.initUI)
        menubar.add_cascade(label="主页", menu=mainPageMenu)
        menubar.add_cascade(label="操作", menu=fileMenu)
        menubar.add_cascade(label="帮助", menu=helpMenu)

    def initUIFrame(self):
        self.frame0.columnconfigure(0, pad=5, weight=1)
        self.frame0.columnconfigure(1, pad=5, weight=1)
        self.frame0.columnconfigure(2, pad=5, weight=1)
        self.frame0.columnconfigure(3, pad=5, weight=1)
        self.frame0.columnconfigure(4, pad=5, weight=1)
        self.frame0.columnconfigure(5, pad=5, weight=1)
        self.frame0.rowconfigure(0, pad=37)
        self.frame0.rowconfigure(1, pad=7)
        self.frame0.rowconfigure(2, pad=7, weight=1)
        titleImg = ImageTk.PhotoImage(file="./imgs/title.png")
        catImg = ImageTk.PhotoImage(file="./imgs/cat.png")
        preImg = ImageTk.PhotoImage(file="./imgs/pre.png")
        chartImg = ImageTk.PhotoImage(file="./imgs/chart.png")
        bestImg = ImageTk.PhotoImage(file="./imgs/bestPoint.png")
        rareImg = ImageTk.PhotoImage(file="./imgs/rare.png")

        lbl = Label(self.frame0, image=titleImg)
        lbl.grid(row=0, column=1,columnspan=5,sticky=S+W)
        lbl.image = titleImg
        lbl = Label(self.frame0, image=rareImg)
        lbl.grid(row=3, column=1,columnspan=5,sticky=S)
        lbl.image = rareImg
        preButton = Button(self.frame0, command=self.onNewPre)
        preButton.config(image=preImg)
        preButton.image = preImg
        preButton.grid(row=1, column=2)
        cateButton = Button(self.frame0, command=self.onNewCata)
        cateButton.config(image=catImg)
        cateButton.image = catImg
        cateButton.grid(row=1, column=1)
        chartButton = Button(self.frame0, command=self.onNewGraph)
        chartButton.config(image=chartImg)
        chartButton.image = chartImg
        chartButton.grid(row=1, column=3)
        chartButton = Button(self.frame0, command=self.onNewBest)
        chartButton.config(image=bestImg)
        chartButton.image = bestImg
        chartButton.grid(row=1, column=4)

        lbl = Label(self.frame0, text="新建催化剂")
        lbl.grid(row=2, column=1, sticky=N)
        lbl = Label(self.frame0, text="精确预测")
        lbl.grid(row=2, column=2, sticky=N)
        lbl = Label(self.frame0, text="趋势预测")
        lbl.grid(row=2, column=3, sticky=N)
        lbl = Label(self.frame0, text="最优条件预测")
        lbl.grid(row=2, column=4, sticky=N)
    def bestUI(self):
        self.frame0.destroy()
        self.initUIRoot()
        frame1 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame1.pack(fill=BOTH, expand=False)

        frame2 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame2.pack(fill=BOTH, expand=True)

        frame1.columnconfigure(1, weight=1)
        # frame1.columnconfigure(9, weight=1)
        frame1.columnconfigure(10, pad=7)
        frame1.rowconfigure(5, weight=1)
        frame1.rowconfigure(5, pad=7)

        frame2.columnconfigure(11, pad=7, weight=1)
        frame2.rowconfigure(8, pad=7)

        lbl = Label(frame1, text="催化剂性质")
        lbl.grid(row=0, column=0, columnspan=8, rowspan=1, sticky=W, pady=4, padx=5)
        # K_Mat_Tree = ttk.Treeview(frame1)
        # K_Mat_Tree['show'] = 'headings'
        # K_Mat_Tree = self.makeMatrixUI(7, K_Mat_Tree, sourceDate.K_model)
        # K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=5, sticky=E + W + S + N, pady=4, padx=5)
        K_Mat_Tree = Text(frame1, height=18)
        self.makeMatrixUI(K_Mat_Tree, self.catObj)
        K_Mat_Tree.configure(state='normal')
        K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=6, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="优化方法:")
        lbl.grid(row=0, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.optMethod)
        txt.configure(state='readonly')
        txt.grid(row=0, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="集总数:")
        lbl.grid(row=1, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.n)
        txt.configure(state='readonly')
        txt.grid(row=1, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="精确度:")
        lbl.grid(row=2, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.tol)
        txt.configure(state='readonly')
        txt.grid(row=2, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        cateDetailButton = Button(frame1, text="查看催化剂详情")
        cateDetailButton.grid(row=3, column=8)
        # ________________________________________
        lbl = Label(frame2, text="待预测条件")
        lbl.grid(row=0, column=0, sticky=W, columnspan=5, rowspan=1, pady=4, padx=5)

        lbl = Label(frame2, text="初始组成（<1 英文逗号分割）:")
        lbl.grid(row=1, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.Y0_input = Entry(frame2)
        self.Y0_input.grid(row=1, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="温度范围（K 英文逗号分割 ）")
        lbl.grid(row=2, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.T_input = Entry(frame2)
        if not self.catObj.withTemp:
            self.T_input.insert(0, '%f,%f'%(self.catObj.t,self.catObj.t))
            self.T_input.configure(state='readonly')
        self.T_input.grid(row=2, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="压力范围（KPa 英文逗号分割）")
        lbl.grid(row=3, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.p_input = Entry(frame2)
        self.p_input.grid(row=3, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="剂油比范围 （英文逗号分割）")
        lbl.grid(row=4, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.roil_input = Entry(frame2)
        self.roil_input.grid(row=4, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="停留时间范围（英文逗号分割s）")
        lbl.grid(row=5, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.t_input = Entry(frame2)
        self.t_input.grid(row=5, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="碱氮含量（<1）")
        lbl.grid(row=6, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.yn_input = Entry(frame2)
        self.yn_input.insert(0, 0.0)
        self.yn_input.grid(row=6, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="重芳烃含量（<1）")
        lbl.grid(row=7, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.ya_input = Entry(frame2)
        self.ya_input.grid(row=7, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="微分方程步长")
        lbl.grid(row=8, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.step_input = Entry(frame2)
        self.step_input.insert(0, 0.1)
        self.step_input.grid(row=8, column=2, columnspan=3, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="待预测组分编号（，）")
        lbl.grid(row=9, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.target = Entry(frame2)
        self.target.insert(0, '5,6,7')
        self.target.grid(row=9, column=2, columnspan=3, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="结果组成")
        lbl.grid(row=0, column=7, columnspan=2, rowspan=1, pady=4, padx=5, sticky=W)
        self.preResult_LB = Listbox(frame2)
        self.preResult_LB.grid(row=1, column=7, columnspan=2, rowspan=8, pady=4, padx=5, sticky=W)

        lbl = Label(frame2, text="最优温度：")
        lbl.grid(row=0, column=9, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.bestT = Entry(frame2)
        self.bestT.delete(0, 'end')
        self.bestT.configure(state='readonly')
        self.bestT.grid(row=0, column=11, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)
        lbl = Label(frame2, text="最优压力：")
        lbl.grid(row=1, column=9, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.bestP = Entry(frame2)
        self.bestP.delete(0, 'end')
        self.bestP.configure(state='readonly')
        self.bestP.grid(row=1, column=11, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)
        lbl = Label(frame2, text="最优剂油比：")
        lbl.grid(row=2, column=9, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.bestR = Entry(frame2)
        self.bestR.delete(0, 'end')
        self.bestR.configure(state='readonly')
        self.bestR.grid(row=2, column=11, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)
        lbl = Label(frame2, text="最优反应时间：")
        lbl.grid(row=3, column=9, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.bestTime = Entry(frame2)
        self.bestTime.delete(0, 'end')
        self.bestTime.configure(state='readonly')
        self.bestTime.grid(row=3, column=11, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)
        lbl = Label(frame2, text="目标结果：")
        lbl.grid(row=4, column=9, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.bestSum = Entry(frame2)
        self.bestSum.delete(0, 'end')
        self.bestSum.configure(state='readonly')
        self.bestSum.grid(row=4, column=11, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)
        cateDetailButton = Button(frame2, text="预测", command=self.doBest)
        cateDetailButton.grid(row=9, column=6, columnspan=2)

    def preUI(self):
        self.frame0.destroy()
        self.initUIRoot()
        frame1 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame1.pack(fill=BOTH, expand=False)

        frame2 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame2.pack(fill=BOTH, expand=True)

        frame1.columnconfigure(1, weight=1)
        # frame1.columnconfigure(9, weight=1)
        frame1.columnconfigure(10, pad=7)
        frame1.rowconfigure(5, weight=1)
        frame1.rowconfigure(5, pad=7)

        frame2.columnconfigure(8, pad=7, weight=1)
        frame2.rowconfigure(8, pad=7)

        lbl = Label(frame1, text="催化剂性质")
        lbl.grid(row=0, column=0, columnspan=8, rowspan=1, sticky=W, pady=4, padx=5)
        # K_Mat_Tree = ttk.Treeview(frame1)
        # K_Mat_Tree['show'] = 'headings'
        # K_Mat_Tree = self.makeMatrixUI(7, K_Mat_Tree, sourceDate.K_model)
        # K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=5, sticky=E + W + S + N, pady=4, padx=5)
        K_Mat_Tree = Text(frame1, height=18)
        self.makeMatrixUI(K_Mat_Tree, self.catObj)
        K_Mat_Tree.configure(state='normal')
        K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=6, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="优化方法:")
        lbl.grid(row=0, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.optMethod)
        txt.configure(state='readonly')
        txt.grid(row=0, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="集总数:")
        lbl.grid(row=1, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.n)
        txt.configure(state='readonly')
        txt.grid(row=1, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="精确度:")
        lbl.grid(row=2, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.tol)
        txt.configure(state='readonly')
        txt.grid(row=2, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        cateDetailButton = Button(frame1, text="查看催化剂详情")
        cateDetailButton.grid(row=3, column=8)
        # ________________________________________
        lbl = Label(frame2, text="待预测条件")
        lbl.grid(row=0, column=0, sticky=W, columnspan=5, rowspan=1, pady=4, padx=5)

        lbl = Label(frame2, text="初始组成（<1 英文逗号分割）:")
        lbl.grid(row=1, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.Y0_input = Entry(frame2)
        self.Y0_input.grid(row=1, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="温度（K）")
        lbl.grid(row=2, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.T_input = Entry(frame2)
        if not self.catObj.withTemp:
            self.T_input.insert(0, self.catObj.t)
            self.T_input.configure(state='readonly')
        self.T_input.grid(row=2, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="压力（KPa）")
        lbl.grid(row=3, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.p_input = Entry(frame2)
        self.p_input.grid(row=3, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="剂油比")
        lbl.grid(row=4, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.roil_input = Entry(frame2)
        self.roil_input.grid(row=4, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="停留时间（s）")
        lbl.grid(row=5, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.t_input = Entry(frame2)
        self.t_input.grid(row=5, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="碱氮含量（<1）")
        lbl.grid(row=6, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.yn_input = Entry(frame2)
        self.yn_input.insert(0, 0.0)
        self.yn_input.grid(row=6, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="重芳烃含量（<1）")
        lbl.grid(row=7, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.ya_input = Entry(frame2)
        self.ya_input.grid(row=7, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="微分方程步长")
        lbl.grid(row=8, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.step_input = Entry(frame2)
        self.step_input.insert(0, 0.1)
        self.step_input.grid(row=8, column=2, columnspan=3, rowspan=1, sticky=E, pady=4, padx=5)
        self.preResult_LB = Listbox(frame2)
        self.preResult_LB.grid(row=1, column=7, columnspan=2, rowspan=6, pady=4, padx=5)

        cateDetailButton = Button(frame2, text="预测", command=self.doPre)
        cateDetailButton.grid(row=8, column=7, columnspan=2)

    def cateUI(self):
        self.frame0.destroy()
        self.initUIRoot()
        frame4 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame4.pack(fill=BOTH)

        frame1 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame1.pack(fill=BOTH, expand=True)

        frame1.columnconfigure(0, weight=1)
        # frame1.columnconfigure(9, weight=1)
        frame1.rowconfigure(0, weight=1)

        lbl = Label(frame4, text="已输入温度组数")
        lbl.grid(row=0, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.varCountT = StringVar()
        self.countT = Message(frame4, textvariable=self.varCountT)
        self.varCountT.set('0')

        self.countT.grid(row=0, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        factor_Tree = ttk.Treeview(frame1)
        factor_Tree['show'] = 'headings'
        factor_Tree["columns"] = ['t_resid', 't', 'r_oil', 'p', 'Y0', 'Y_results', 'w_aro', 'w_nitro']
        #
        factor_Tree.heading("t", text="温度")
        factor_Tree.column("t", width=self.winfo_width() / 8)
        factor_Tree.heading("r_oil", text="剂油比")
        factor_Tree.column("r_oil", width=self.winfo_width() / 8)
        factor_Tree.heading("p", text="压力")
        factor_Tree.column("p", width=self.winfo_width() / 8)
        factor_Tree.heading("Y0", text="初始组成")
        factor_Tree.column("Y0", width=self.winfo_width() / 8)
        factor_Tree.heading("Y_results", text="产物组成")
        factor_Tree.column("Y_results", width=self.winfo_width() / 8)
        factor_Tree.heading("w_aro", text="重芳烃含量")
        factor_Tree.column("w_aro", width=self.winfo_width() / 8)
        factor_Tree.heading("w_nitro", text="碱氮含量")
        factor_Tree.column("w_nitro", width=self.winfo_width() / 8)
        factor_Tree.heading("t_resid", text="停留时间")
        factor_Tree.column("t_resid", width=self.winfo_width() / 8)
        factor_Tree.grid(row=0, column=0, pady=4, padx=5)
        self.factor_Tree = factor_Tree

        frame2 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame2.pack(fill=BOTH, expand=True)

        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(8, weight=1)

        lbl = Label(frame2, text="停留时间（s）")
        lbl.grid(row=0, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.t_input = Entry(frame2)
        self.t_input.grid(row=0, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="温度（K）")
        lbl.grid(row=1, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.T_input = Entry(frame2)
        self.T_input.grid(row=1, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="剂油比")
        lbl.grid(row=2, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.roil_input = Entry(frame2)
        self.roil_input.grid(row=2, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="压力（KPa）")
        lbl.grid(row=3, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.p_input = Entry(frame2)
        self.p_input.grid(row=3, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="初始组成（<1 英文逗号分割）:")
        lbl.grid(row=0, column=4, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.Y0_input = Entry(frame2)
        self.Y0_input.grid(row=0, column=6, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="产物组成（<1 英文逗号分割）:")
        lbl.grid(row=1, column=4, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.Y_results_input = Entry(frame2)
        self.Y_results_input.grid(row=1, column=6, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="碱氮含量（<1）")
        lbl.grid(row=2, column=4, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.yn_input = Entry(frame2)
        self.yn_input.insert(0, 0.0)
        self.yn_input.grid(row=2, column=6, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="重芳烃含量（<1）")
        lbl.grid(row=3, column=4, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.ya_input = Entry(frame2)
        self.ya_input.grid(row=3, column=6, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="分子质量（逗号分割）")
        lbl.grid(row=4, column=4, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.Molmasses_input = Entry(frame2)
        self.Molmasses_input.grid(row=4, column=6, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)
        self.Molmasses_input.insert(0,'0.8,1.1,1.8,0.2,0.2,0.2,0.11,0.016,0.042,0.056,0.05,0.012')
        addButton = Button(frame2, command=self.addFactors, text="添加条件")
        addButton.grid(row=9, column=2, sticky=E)

        self.newCatButton = Button(frame2, command=self.newCata, text="开始计算", state=DISABLED)
        self.newCatButton.grid(row=9, column=6, sticky=E)

    def graphUI(self):
        self.frame0.destroy()
        self.initUIRoot()
        frame1 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame1.pack(fill=BOTH, expand=False)

        frame2 = Frame(self.frame0, relief=RAISED, borderwidth=1)
        frame2.pack(fill=BOTH, expand=True)

        frame1.columnconfigure(1, weight=1)
        # frame1.columnconfigure(9, weight=1)
        frame1.columnconfigure(10, pad=7)
        frame1.rowconfigure(5, weight=1)
        frame1.rowconfigure(5, pad=7)

        frame2.columnconfigure(8, pad=7, weight=1)
        frame2.columnconfigure(1, weight=1)
        frame2.columnconfigure(6, weight=1)
        frame2.rowconfigure(8, pad=7)

        lbl = Label(frame1, text="催化剂性质")
        lbl.grid(row=0, column=0, columnspan=8, rowspan=1, sticky=W, pady=4, padx=5)
        # K_Mat_Tree = ttk.Treeview(frame1)
        # K_Mat_Tree['show'] = 'headings'
        # K_Mat_Tree = self.makeMatrixUI(7, K_Mat_Tree, sourceDate.K_model)
        # K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=5, sticky=E + W + S + N, pady=4, padx=5)
        K_Mat_Tree = Text(frame1, height=18)
        self.makeMatrixUI(K_Mat_Tree, self.catObj)
        K_Mat_Tree.configure(state='normal')
        K_Mat_Tree.grid(row=1, column=0, columnspan=6, rowspan=6, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="优化方法:")
        lbl.grid(row=0, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.optMethod)
        txt.configure(state='readonly')
        txt.grid(row=0, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="集总数:")
        lbl.grid(row=1, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.n)
        txt.configure(state='readonly')
        txt.grid(row=1, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        lbl = Label(frame1, text="精确度:")
        lbl.grid(row=2, column=6, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)
        txt = Entry(frame1)
        txt.insert(0, self.catObj.tol)
        txt.configure(state='readonly')
        txt.grid(row=2, column=8, columnspan=2, rowspan=1, sticky=E + W + S + N, pady=4, padx=5)

        cateDetailButton = Button(frame1, text="查看催化剂详情")
        cateDetailButton.grid(row=3, column=8)
        # ________________________________________
        lbl = Label(frame2, text="待预测条件")
        lbl.grid(row=0, column=0, columnspan=5, rowspan=1, pady=4, padx=5)

        lbl = Label(frame2, text="初始组成（<1 英文逗号分割）:")
        lbl.grid(row=1, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.Y0_input = Entry(frame2)
        self.Y0_input.grid(row=1, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="温度（K）")
        lbl.grid(row=2, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.T_input = Entry(frame2)

        self.T_input.grid(row=2, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="压力（KPa）")
        lbl.grid(row=3, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.p_input = Entry(frame2)
        self.p_input.grid(row=3, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="剂油比")
        lbl.grid(row=4, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.roil_input = Entry(frame2)
        self.roil_input.grid(row=4, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="停留时间（s）")
        lbl.grid(row=5, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.t_input = Entry(frame2)
        self.t_input.grid(row=5, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="碱氮含量（<1）")
        lbl.grid(row=6, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.yn_input = Entry(frame2)
        self.yn_input.insert(0, 0.0)
        self.yn_input.grid(row=6, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="重芳烃含量（<1）")
        lbl.grid(row=7, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.ya_input = Entry(frame2)
        self.ya_input.grid(row=7, column=2, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="微分方程步长")
        lbl.grid(row=8, column=0, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)

        self.step_input = Entry(frame2)
        self.step_input.insert(0, 0.1)
        self.step_input.grid(row=8, column=2, columnspan=3, rowspan=1, sticky=E, pady=4, padx=5)

        lbl = Label(frame2, text="图表设置")
        lbl.grid(row=0, column=6, columnspan=5, rowspan=1, pady=4, padx=5)

        lbl = Label(frame2, text="条件变量")
        lbl.grid(row=1, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.var = ttk.Combobox(frame2, textvariable=StringVar())
        if not self.catObj.withTemp:
            self.var['values'] = (u'压力', u'剂油比', u'停留时间')
            self.p_input.insert(0, 0)
            self.T_input.insert(0, self.catObj.t)
            self.T_input.configure(state='readonly')
            self.p_input.configure(state='readonly')
            self.lastVar = u'压力'
        else:
            self.T_input.delete(0, 'end')
            self.T_input.insert(0, 0)
            self.T_input.configure(state='readonly')
            self.var['values'] = (u'温度', u'压力', u'剂油比', u'停留时间', u'温度+压力',u'温度+剂油比',u'剂油比+压力')
            self.lastVar = u'温度'
        self.var.bind('<<ComboboxSelected>>', self.onSelecetedVar)
        self.var.current(0)
        self.var.grid(row=1, column=8, columnspan=2, rowspan=1, sticky=W, pady=4, padx=5)

        self.rangeLbl = Label(frame2, text="条件范围")
        self.rangeLbl.grid(row=2, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        lbl = Label(frame2, text="上限")
        lbl.grid(row=3, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        lbl = Label(frame2, text="下限")
        lbl.grid(row=4, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.rangeMin = Entry(frame2)
        self.rangeMax = Entry(frame2)

        self.rangeMin.grid(row=3, column=8, columnspan=1, sticky=W, rowspan=1, pady=4, padx=5)
        self.rangeMax.grid(row=4, column=8, columnspan=1, sticky=W, rowspan=1, pady=4, padx=5)

        lbl = Label(frame2, text="结果集（英文逗号分割）")
        lbl.grid(row=5, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.chartResultId = Entry(frame2)
        self.chartResultId.insert(0, '1,2,3,4,5,6,7,8,9,10,11,12')
        self.chartResultId.grid(row=5, column=8, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="结果名（英文逗号分割\n尽量使用英文）")
        lbl.grid(row=6, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.chartResultName = Entry(frame2)
        #TODO,get the default value from lump model
        self.chartResultName.insert(0, 'HS,HA,HR,DIESEL,GS,GO,GA,DGAS,LO3,LO4,LPGD,COKE')
        self.chartResultName.grid(row=6, column=8, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)

        lbl = Label(frame2, text="点数")
        lbl.grid(row=7, column=6, columnspan=2, rowspan=1, sticky=E, pady=4, padx=5)
        self.stepNum = Entry(frame2)
        self.stepNum.grid(row=7, column=8, columnspan=3, rowspan=1, sticky=W, pady=4, padx=5)

        cateDetailButton = Button(frame2, text="预测趋势", command=self.doChart)
        cateDetailButton.grid(row=8, column=6, columnspan=2)

    def onSelecetedVar(self, event):
        varName = self.var.get()
        if self.lastVar == u'温度':
            # u'温度',,,u'停留时间'
            self.T_input.configure(state="normal")
        elif self.lastVar == u'压力':
            self.p_input.configure(state="normal")
        elif self.lastVar == u'剂油比':
            self.roil_input.configure(state="normal")
        elif self.lastVar == u'停留时间':
            self.t_input.configure(state="normal")
        elif self.lastVar == u'温度+压力':
            self.T_input.configure(state="normal")
            self.p_input.configure(state="normal")
        elif self.lastVar == u'温度+剂油比':
            self.roil_input.configure(state="normal")
            self.T_input.configure(state="normal")
        elif self.lastVar == u'剂油比+压力':
            self.roil_input.configure(state="normal")
            self.p_input.configure(state="normal")

        if varName == u'温度':
            self.rangeLbl.config(text='条件范围')

            self.T_input.delete(0, 'end')
            self.T_input.insert(0, 0)
            self.T_input.configure(state="readonly")
        elif varName == u'压力':
            self.rangeLbl.config(text='条件范围')

            self.p_input.delete(0, 'end')
            self.p_input.insert(0, 0)
            self.p_input.configure(state="readonly")
        elif varName == u'剂油比':
            self.rangeLbl.config(text='条件范围')

            self.roil_input.delete(0, 'end')
            self.roil_input.insert(0, 0)
            self.roil_input.configure(state="readonly")
        elif varName == u'停留时间':
            self.rangeLbl.config(text='条件范围')

            self.t_input.delete(0, 'end')
            self.t_input.insert(0, 0)
            self.t_input.configure(state="readonly")
        elif varName == u'温度+压力':
            self.rangeLbl.config(text='条件范围,格式：温度，压力')

            self.T_input.delete(0, 'end')
            self.T_input.insert(0, 0)
            self.T_input.configure(state="readonly")
            self.p_input.delete(0, 'end')
            self.p_input.insert(0, 0)
            self.p_input.configure(state="readonly")
        elif varName == u'温度+剂油比':
            self.rangeLbl.config(text='条件范围,格式：温度，剂油比')
            self.roil_input.delete(0, 'end')
            self.roil_input.insert(0, 0)
            self.roil_input.configure(state="readonly")
            self.T_input.delete(0, 'end')
            self.T_input.insert(0, 0)
            self.T_input.configure(state="readonly")

        elif varName == u'剂油比+压力':
            self.rangeLbl.config(text='条件范围,格式：剂油比，压力')
            self.roil_input.delete(0, 'end')
            self.roil_input.insert(0, 0)
            self.roil_input.configure(state="readonly")

            self.p_input.delete(0, 'end')
            self.p_input.insert(0, 0)
            self.p_input.configure(state="readonly")

        self.lastVar = varName

    def onNewCata(self):
        self.catFactors = {}
        ftypes = [('集总模型', '*.lp')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        # print flmakePreResultUI
        if fl != '':
            self.lumpObj = self.readFile(fl)
            print self.lumpObj
            self.cateUI()

    def onNewPre(self):
        ftypes = [('催化剂存档文件', '*.cat')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        print fl
        if fl != '':
            self.catObj = self.readFile(fl)
            self.preUI()
    def onNewBest(self):
        ftypes = [('催化剂存档文件', '*.cat')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        print fl
        if fl != '':
            self.catObj = self.readFile(fl)
            self.bestUI()
    def onNewGraph(self):
        ftypes = [('催化剂存档文件', '*.cat')]
        dlg = tkFileDialog.Open(self, filetypes=ftypes)
        fl = dlg.show()
        print fl
        if fl != '':
            self.catObj = self.readFile(fl)
            self.graphUI()

    def saveCate(self):
        ftypes = [('催化剂存档文件', '*.cat')]
        filename = tkFileDialog.asksaveasfilename(title='保存催化剂存档文件', defaultextension='.cat', filetypes=ftypes)
        return filename

    def onHelp(self):
        mbox.showinfo("集总模型软件", "中国石油\n兰州化工研究中心")

    def doPre(self):
        catObj = self.catObj
        t_resid = float(self.t_input.get())
        p = float(self.p_input.get())
        Y0 = numpy.mat(self.Y0_input.get().split(',')).astype(numpy.float)
        const_r = 8.3145
        w_aro = float(self.ya_input.get())
        w_nitro = float(self.yn_input.get())
        t = float(self.T_input.get())
        r_oil = float(self.roil_input.get())
        stepLength = float(self.step_input.get())
        n = catObj.n
        print [t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n]
        result = newPre(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n, stepLength).tolist()[0]
        self.makePreResultUI(self.preResult_LB, result)
    def doBest(self):
        catObj = self.catObj
        t_resid = [float(self.t_input.get().split(',')[0]),float(self.t_input.get().split(',')[1])]
        p = [float(self.p_input.get().split(',')[0]),float(self.p_input.get().split(',')[1])]
        Y0 = numpy.mat(self.Y0_input.get().split(',')).astype(numpy.float)
        const_r = 8.3145
        w_aro = float(self.ya_input.get())
        w_nitro = float(self.yn_input.get())
        t = [float(self.T_input.get().split(',')[0]),float(self.T_input.get().split(',')[1])]
        r_oil = [float(self.roil_input.get().split(',')[0]),float(self.roil_input.get().split(',')[1])]
        stepLength = float(self.step_input.get())
        n = catObj.n
        target = self.target.get().split(',')
        print [t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n,target]
        result = newBest(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n, stepLength,target)
        self.bestP.configure(state='normal')
        self.bestT.configure(state='normal')
        self.bestR.configure(state='normal')
        self.bestTime.configure(state='normal')
        self.bestSum.configure(state='normal')
        self.bestP.insert('end',round(result['bestP'], 4))
        self.bestT.insert('end',round(result['bestT'], 4))
        self.bestR.insert('end',round(result['bestR'], 4))
        self.bestTime.insert('end',round(result['bestTime'], 4))
        self.bestSum.insert('end',round(result['sum'], 4))
        self.makePreResultUI(self.preResult_LB, result['Y'])
    def doChart(self):
        catObj = self.catObj
        t_resid = float(self.t_input.get())
        p = float(self.p_input.get())
        Y0 = numpy.mat(self.Y0_input.get().split(',')).astype(numpy.float)
        const_r = 8.3145
        w_aro = float(self.ya_input.get())
        w_nitro = float(self.yn_input.get())
        t = float(self.T_input.get())
        r_oil = float(self.roil_input.get())
        stepNum = int(self.stepNum.get())
        resultId = self.chartResultId.get()
        resultName = self.chartResultName.get()

        stepLength = float(self.step_input.get())
        n = catObj.n
        varName = ''
        if self.lastVar == u'温度':
            varName = 't'
            varMin = float(self.rangeMin.get())
            varMax = float(self.rangeMax.get())
        elif self.lastVar == u'压力':
            varName = 'p'
            varMin = float(self.rangeMin.get())
            varMax = float(self.rangeMax.get())
        elif self.lastVar == u'剂油比':
            varName = 'r'
            varMin = float(self.rangeMin.get())
            varMax = float(self.rangeMax.get())
        elif self.lastVar == u'停留时间':
            varName = 'time'
            varMin = float(self.rangeMin.get())
            varMax = float(self.rangeMax.get())
        elif self.lastVar == u'温度+压力':
            varName = 't,p'.split(',')
            varMin = self.rangeMin.get().split(',')
            varMax = self.rangeMax.get().split(',')
        elif self.lastVar == u'温度+剂油比':
            varName = 't,r'.split(',')
            varMin = self.rangeMin.get().split(',')
            varMax = self.rangeMax.get().split(',')
        elif self.lastVar == u'剂油比+压力':
            varName = 'r,p'.split(',')
            varMin = self.rangeMin.get().split(',')
            varMax = self.rangeMax.get().split(',')
        chartConfig = {}
        chartConfig['varName'] = varName
        chartConfig['stepNum'] = stepNum

        chartConfig['varMin'] = varMin
        chartConfig['varMax'] = varMax
        chartConfig['resultId'] = resultId
        chartConfig['resultName'] = resultName
        # t_resid=3
        # p=175
        # const_r=8.3145
        # Y0=mat([0.481,0.472,0.047,0,0,0,0])
        # w_aro=0.472
        # w_nitro=0
        # t=685
        # n=7
        # r_oil=8.79
        # chartConfig={'varName': 'time', 'varMax': 0.001, 'varMin': 15.0, 'resultId': '1,2,3,4,5,6,7', 'stepNum': 100,'resultName':u'Hs,Ha,Hr,柴油,汽油,气体,焦炭'}

        print chartConfig
        print [catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n, chartConfig]
        if len(varName)>1:
            result = new3dChart(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n, chartConfig, stepLength)

        else:
            result = new2dChart(catObj, t_resid, p, Y0, const_r, w_aro, w_nitro, t, r_oil, n, chartConfig, stepLength)

    def addFactors(self):
        t_resid = float(self.t_input.get())
        p = float(self.p_input.get())
        Y0_raw = self.Y0_input.get()
        Y0 = numpy.mat(Y0_raw.split(',')).astype(numpy.float)
        Y_results_raw = self.Y_results_input.get()
        Y_results = numpy.mat(Y_results_raw.split(',')).astype(numpy.float)
        w_aro = float(self.ya_input.get())
        w_nitro = float(self.yn_input.get())
        t = float(self.T_input.get())
        r_oil = float(self.roil_input.get())
        self.Molmasses = numpy.mat(self.Molmasses_input.get().split(',')).astype(numpy.float)
        self.factor_Tree.insert('', END, values=[t_resid, t, r_oil, p, Y0_raw, Y_results_raw, w_aro, w_nitro])
        if self.catFactors.has_key(t):
            self.catFactors[t].append(
                {'t_resid': t_resid, 't': t, 'r_oil': r_oil, 'p': p, 'Y0': Y0, 'Y_results': Y_results, 'w_aro': w_aro,
                 'w_nitro': w_nitro})
        else:
            self.catFactors[t] = [
                {'t_resid': t_resid, 't': t, 'r_oil': r_oil, 'p': p, 'Y0': Y0, 'Y_results': Y_results, 'w_aro': w_aro,
                 'w_nitro': w_nitro}]
        print self.catFactors
        self.varCountT.set(len(self.catFactors))
        self.Molmasses_input.configure(state='readonly')
        self.newCatButton.configure(state='active')

    def newCata(self):
        filename = self.saveCate()
        print filename
        if len(self.catFactors) == 1:
            newCatNoKa(filename, self.lumpObj, 1, 0, 1, self.lumpObj, self.Molmasses, self.catFactors.values()[0],
                       'L-BFGS-B',
                       1e-5, self.lumpObj.shape[0])
        else:
            newCatWithKa(filename, self.lumpObj, 1, 0, 1, self.lumpObj, self.Molmasses, self.catFactors, 'L-BFGS-B',
                         1e-5,
                         self.lumpObj.shape[0])

    def makeMatrixUI(self, targetTree, catObj):
        n = catObj.n
        if not catObj.withTemp:
            targetTree.insert('end', '催化剂模型是在同一温度下，只能计算K\n------------------\nK=\n')
            K = numpy.around(self.makeMatrixByResult(catObj.K_model, catObj.X0_result, catObj.n)['K_result'], 4)
            self.makeMatrixOutput(n, targetTree, K)
            targetTree.insert('end', '\n------------------\n重芳烃影响因数：\n')
            targetTree.insert('end', self.makeMatrixByResult(catObj.K_model, catObj.X0_result, catObj.n)['Ka'])
            targetTree.insert('end', '\n------------------\n碱氮影响因数：\n')
            targetTree.insert('end', self.makeMatrixByResult(catObj.K_model, catObj.X0_result, catObj.n)['Kn'])
            targetTree.insert('end', '\n------------------\n')

        else:
            K = self.makeMatrixByResult(catObj.K_model, catObj.X0_result, catObj.n)['K_result']
            print catObj.X0_result
            Ka = numpy.around(self.makeMatrixByResult(catObj.K_model, catObj.Ka, catObj.n)['K_result'], 4)
            print catObj.Ka
            Ea = numpy.around(self.makeMatrixByResult(catObj.K_model, catObj.Ea, catObj.n)['K_result'], 4)
            print catObj.Ea
            targetTree.insert('end', '\n------------------\nK=\n')
            print len(K)
            for i in K:
                self.makeMatrixOutput(n, targetTree, numpy.round(i, 4))
                targetTree.insert('end', '\n------------------\n')
            targetTree.insert('end', '\n------------------\nKa=\n')
            self.makeMatrixOutput(n, targetTree, Ka)
            targetTree.insert('end', '\n------------------\n')
            targetTree.insert('end', '\n------------------\nEa=\n')
            self.makeMatrixOutput(n, targetTree, Ea)
            targetTree.insert('end', '\n------------------\n')

    def makeMatrixOutput(self, n, targetTree, mat):
        for i in range(n):
            targetTree.insert('end', ','.join(mat[i].astype(numpy.string_).tolist()))
            targetTree.insert('end', '\n')
        return targetTree

    def makeMatrixByResult(self, K_model, result, n):
        if type(result) != type([]):
            K = result[:-3].tolist()
            args = result[-3:]
            K_raw_result = []
            for i in K_model.T.flat:
                if i:
                    K_raw_result.append(K.pop(0))
                else:
                    K_raw_result.append(0)
            K_result = reshape(K_raw_result, (n, n)).T.T.T
            ka_result, kn_result, cata_result = args
            return {'K_result': K_result, 'ka_result': ka_result, 'kn_result': kn_result, 'cata_result': cata_result}
        else:
            K_results = []

            args = result[0][-3:]
            for i in result:
                K = i[:-3].tolist()
                K_raw_result = []
                for i in K_model.T.flat:
                    if i:
                        K_raw_result.append(K.pop(0))
                    else:
                        K_raw_result.append(0)
                K_result = reshape(K_raw_result, (n, n)).T.T.T
                K_results.append(K_result)
            ka_result, kn_result, cata_result = args
            return {'K_result': K_results, 'ka_result': ka_result, 'kn_result': kn_result,
                    'cata_result': cata_result}

    def makePreResultUI(self, target, result):
        target.delete(0, END)
        if type(result)!=type([]):
            result=result.tolist()[0]
        for i in result:
            target.insert(END, round(i, 3))
        return target

    def readFile(self, filename):
        f = open(filename, "r")
        obj = pickle.load(f)
        return obj


def main():
    root = Tk()
    ex = Example(root)
    root.geometry("800x640+300+300")
    root.iconbitmap('./imgs/logo.ico')
    root.mainloop()


if __name__ == '__main__':
    main()
