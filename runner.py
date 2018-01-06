# -*- coding: utf-8 -*-
# @Time    : 2017/12/22 下午5:35
# @Author  : Lincvic
# @Email   : lincvic@yahoo.com
# @File    : runner.py
# @SoftwareName: PyCharm

import sys
import mainwindow
from PyQt5 import QtWidgets

#定义
MEM_TOTAL = 600  # 总共的用户内存
MEM_REM_TOTAL = 600  # 剩余的用户可用的内存
MEM_ALLO = []  # 定义一个列表用来保存所有的内存分配情况，每一个元素都是一个列表（包括可用与已分）
MEM_ID = 0  # 索引分区ID
MEM_ADDR = 1  # 索引分区始地址
MEM_SIZE = 2  # 索引分区大小
MEM_STATE = 3  # 索引分区的状态 0(可用) 1(已分配)
NEXT_FIT_NEXT = 0  # 循环首次适应算法的指针。
JOB_LIST = []  # 所用正在进行的作业
CUR_ALLO_METHOD = "FF"  # 默认为首次适应算法

#PyQT窗口初始化
class mainApp(QtWidgets.QMainWindow, mainwindow.Ui_Form):

    #初始化QT页面
    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        mainwindow.Ui_Form.__init__(self)
        self.setupUi(self)

        # 连接槽
        self.depart_btn.clicked.connect(self.allocate)
        self.refresh_btn.clicked.connect(self.showProgress)
        self.saveSimDisk_btn.clicked.connect(self.showProgress)
        self.mkdir_btn.clicked.connect(self.showProgress)
        self.touch_btn.clicked.connect(self.showProgress)
        self.rm_btn.clicked.connect(self.showProgress)
        self.move_btn.clicked.connect(self.showProgress)
        self.drawBack_btn.clicked.connect(self.recover)

        #初始化
        self.systemInit()

    #进度条
    def showProgress(self):
        i = 0
        while i < 100:
            i += 0.0001
            self.progressBar.setValue(i)

    # 函数：systemInit()
    # 功能： 系统初始化
    def systemInit(self):
        global MEM_ALLO
        MEM_ALLO.insert(0, [
            0,  # 分区的id 0
            0,  # 分区的始址 0
            MEM_TOTAL,  # 分区的大小
            0  # 分区的状态 0
        ])
        self.warn_textBrowser.setText(str("内存容量为600"))

    # 函数：existJobName()
    # 参数：job_name: 作业的名字
    # 返回：Boolean
    def existJobName(self, job_name):
        for name in JOB_LIST:
            if name == job_name:
                print('nmae' + name)
                return True  # 存在名字则返回真
        return False  # 不存在名字则返回假

    # 函数：memShow()内存的情况
    # 参数：str : 附加的信息
    def memShow(self, show_str):
        rem_str = '分区序号\t分区起始地址\t分区大小\t分区状态\n'  # 空余的内存的情况字符串
        allo_str = '分区序号\t分区起始地址\t分区大小\t作业的名字\n'  # 已经分配。。。。

        for one_mem in MEM_ALLO:
            temp_str = str(one_mem[MEM_ID]) +'\t' \
                       + str(one_mem[MEM_ADDR]) + '\t' \
                       + str(one_mem[MEM_SIZE]) + '\t' \
                       + str(one_mem[MEM_STATE]) + '\t' \
                       + '\n'
            if one_mem[MEM_STATE] == 0:
                rem_str += temp_str
            else:
                allo_str += temp_str

        all_str = show_str + '\n\n空余分区\n\n' + rem_str + '\n\n\n已经分配分区\n\n' + allo_str

        # 显示内存全部情况
        self.all_textBrowser.setText(all_str)

    # 函数：fixMemId()  调整分区的id
    # 参数： index: 要调整的分区的id
    def fixMemId(self, index):
        global MEM_ALLO
        mem_len = len(MEM_ALLO)  # 分区块的总数
        while index < mem_len:
            MEM_ALLO[index][MEM_ID] = index
            index += 1

    # 函数：splitMem() 拆分分区块
    # 参数： job_name: 作业名
    # job_size: 作业的大小
    # index:  分区块的ifen qud
    def splitMem(self, job_name, job_size, index):
        global MEM_ALLO
        # 分区块的大小刚好是作业的大小
        if MEM_ALLO[index][MEM_SIZE] == job_size:
            MEM_ALLO[index][MEM_STATE] = job_name
            return True  # 退出返回
        # 要分配的内存块
        allo_one = [MEM_ALLO[index][MEM_ID],
                    MEM_ALLO[index][MEM_ADDR],
                    job_size,
                    job_name
                    ]
        MEM_ALLO.insert(index + 1, allo_one)

        # 剩余的内存块
        allo_one = [MEM_ALLO[index][MEM_ID] + 1,
                    MEM_ALLO[index][MEM_ADDR] + job_size,
                    MEM_ALLO[index][MEM_SIZE] - job_size,  # 总的大小减去已经分配了的分区的大小
                    0
                    ]
        MEM_ALLO.insert(index + 2, allo_one)
        del MEM_ALLO[index]  # 删掉这个分区块index

        self.fixMemId(index + 2)  # 从index+2开始调整分区的id

    # 函数：uniMem()合并分区块
    # 参数：index要合并的分区id
    def uniMem(self, index):
        print ('index' + str(index))
        global MEM_ALLO
        mem_len = len(MEM_ALLO)  # 分区块的个数
        ##释放区上下都跟空闲区相邻
        if index != 0 and \
                (index + 1) != mem_len and \
                MEM_ALLO[index - 1][MEM_STATE] == 0 and \
                MEM_ALLO[index + 1][MEM_STATE] == 0:

            MEM_ALLO[index - 1] = [MEM_ALLO[index - 1][MEM_ID],
                                   MEM_ALLO[index - 1][MEM_ADDR],
                                   MEM_ALLO[index - 1][MEM_SIZE] + MEM_ALLO[index][MEM_SIZE] + MEM_ALLO[index + 1][
                                       MEM_SIZE],
                                   0]
            del MEM_ALLO[index]  # 删除掉id 为index的分区块
            del MEM_ALLO[index]
            self.fixMemId(index)  # 调整分区块的id


        #释放区下跟空闲区相邻
        elif (index == 0 or MEM_ALLO[index - 1][MEM_STATE] != 0) and \
                (index + 1) != mem_len and \
                MEM_ALLO[index + 1][MEM_STATE] == 0:

            MEM_ALLO[index] = [MEM_ALLO[index][MEM_ID],
                               MEM_ALLO[index][MEM_ADDR],
                               MEM_ALLO[index][MEM_SIZE] + MEM_ALLO[index + 1][MEM_SIZE],
                               0]
            del MEM_ALLO[index + 1]  # 删除掉id + 1为index的分区块
            self.fixMemId(index + 1)  # 调整分区块的id

            ###释放区上跟空闲区相邻
        elif index != 0 and \
                MEM_ALLO[index - 1][MEM_STATE] == 0 and \
                (index + 1) != mem_len and \
                MEM_ALLO[index + 1][MEM_STATE] != 0:

            MEM_ALLO[index - 1] = [MEM_ALLO[index - 1][MEM_ID],
                                   MEM_ALLO[index - 1][MEM_ADDR],
                                   MEM_ALLO[index - 1][MEM_SIZE] + MEM_ALLO[index][MEM_SIZE],
                                   0]
            del MEM_ALLO[index]  # 删除掉id + 1为index的分区块
            self.fixMemId(index)  # 调整分区块的id

        #上下都不邻空闲区
        else:
            MEM_ALLO[index][MEM_STATE] = 0

    # 函数：allocate
    # 功能： 分配的过程
    def allocate(self):

        global CUR_ALLO_METHOD  # 当前的分配方法
        global MEM_REM_TOTAL  # 空闲内存的大小
        job_name = self.workName_box.toPlainText() # 作业的名字
        job_size = int(self.workSize_box.toPlainText()) # 作业的大小

        # 判断作业名是否存在
        if self.existJobName(job_name):
            self.warn_textBrowser.setText(str("作业名字已存在"))
            return False

        # 判断作业的大小是否正确
        print (MEM_REM_TOTAL, job_size)
        if MEM_REM_TOTAL < job_size:
            self.warn_textBrowser.setText(str("内存空间不足"))
            return False
        MEM_REM_TOTAL -= job_size  # 内存的余量变化

        JOB_LIST.append(job_name)  # 追加到list的最后

        if self.FF_radioBtn.isChecked():
            self.firstFit(job_name, job_size)
        elif self.BF_radioBtn.isChecked():
            self.bestFit(job_name, job_size)

        show_str = '系统已经为作业' + job_name + ' 分配了' + str(job_size) + '大小的空间 还剩下' + str(MEM_REM_TOTAL)  # 分配的信息
        self.warn_textBrowser.setText(str("分配完成"))
        self.memShow(show_str)

    # 函数： recover
    # 功能： 内存的回收
    def recover(self):
        global JOB_LIST, one_mem
        global MEM_REM_TOTAL
        job_name = self.workDrawbackName_box.toPlainText()
        print (job_name)
        if self.existJobName(job_name) == False:
            self.warn_textBrowser.setText(str("作业名不存在"))
            return False
        id = 0
        for job in JOB_LIST:
            if job == job_name:
                del JOB_LIST[id]
                break
            id += 1

        for one_mem in MEM_ALLO:
            if one_mem[MEM_STATE] == job_name:
                break

        MEM_REM_TOTAL += one_mem[MEM_SIZE]  # 空闲的内存空间增加
        self.uniMem(one_mem[MEM_ID])  # 合并分区
        self.warn_textBrowser.setText(str("回收成功"))
        show_str = '回收内存' + str(one_mem[MEM_SIZE]) + ' 空闲内存还剩' + str(MEM_REM_TOTAL) + '\n'
        self.memShow(show_str)

    # 函数：firstFit()  首次适应算法
    def firstFit(self, job_name, job_size):
        global NEXT_FIT_NEXT, one_mem
        # 循环找出首次适应的分区块
        for one_mem in MEM_ALLO:
            if one_mem[MEM_STATE] == 0 and one_mem[MEM_SIZE] > job_size:
                break

        NEXT_FIT_NEXT = one_mem[MEM_ID] + 1  # 循环首次适应算法的指针加1
        self.splitMem(job_name, job_size, one_mem[MEM_ID])  # 把one_mem[MEM_ID] 中得内存块分解

    # 函数： bestFit() 最佳适应算法
    def bestFit(self, job_name, job_size):
        global NEXT_FIT_NEXT
        min_rem = MEM_TOTAL  # 拆分后最小的剩余
        best_mem = []  # 最适合的分区
        for one_mem in MEM_ALLO:
            if one_mem[MEM_STATE] == 0 and \
                    one_mem[MEM_SIZE] > job_size and \
                    (one_mem[MEM_SIZE] - job_size < min_rem):
                best_mem = one_mem
                min_rem = one_mem[MEM_SIZE] - job_size

        NEXT_FIT_NEXT = best_mem[MEM_ID] + 1  # 循环首次适应算法指针加1
        self.splitMem(job_name, job_size, best_mem[MEM_ID])

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = mainApp()
    window.show()
    sys.exit(app.exec_())





