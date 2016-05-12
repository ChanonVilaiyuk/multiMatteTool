#Import python modules
import os, sys
import sqlite3
from collections import Counter

#Import GUI
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from shiboken import wrapInstance

# Import Maya module
import maya.OpenMayaUI as mui
import maya.cmds as mc
import maya.mel as mm

# Import setting
import setting 
reload(setting)

import customWidget
reload(customWidget)

moduleFile = sys.modules[__name__].__file__
moduleDir = os.path.dirname(moduleFile)
sys.path.append(moduleDir)


def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    if ptr is not  None:
        # ptr = mui.MQtUtil.mainWindow()
        return wrapInstance(long(ptr), QtGui.QMainWindow)

class MyForm(QtGui.QMainWindow):

    def __init__(self, parent=None):
        self.count = 0
        #Setup Window
        super(MyForm, self).__init__(parent)

        self.mayaUI = 'multiMatteWin'
        deleteUI(self.mayaUI)

        # read .ui directly
        loader = QtUiTools.QUiLoader()
        loader.setWorkingDirectory(moduleDir)

        f = QtCore.QFile("%s/multiMatteUI.ui" % moduleDir)
        f.open(QtCore.QFile.ReadOnly)

        self.myWidget = loader.load(f, self)
        self.ui = self.myWidget

        f.close()

        self.ui.show()
        self.ui.setWindowTitle('MultiMatte Tool v.1.0')

        self.initFunctions()
        self.initSignals()

    def initFunctions(self) : 
        # set ui 
        self.ui.material_listWidget.setAlternatingRowColors(True)
        self.ui.multiMatte_listWidget.setAlternatingRowColors(True)

        # set default values
        self.setDefaultValue()

        # list all material
        self.listVrayMtlNodeUI()
        self.listVrayMultiMatteUI()


    def initSignals(self) : 
        # button 
        self.ui.refresh1_pushButton.clicked.connect(self.listVrayMtlNodeUI)
        self.ui.refresh2_pushButton.clicked.connect(self.listVrayMultiMatteUI)
        self.ui.assign_puhsButton.clicked.connect(self.assignMatteID)
        self.ui.createMultiMatte_pushButton.clicked.connect(self.createMultiMatte)

        # listWidget 
        self.ui.material_listWidget.itemSelectionChanged.connect(self.materialSelect)
        self.ui.multiMatte_listWidget.itemSelectionChanged.connect(self.materialSelect)

        # lineEdit 
        self.ui.id_lineEdit.returnPressed.connect(self.setMaterialID)


    def listVrayMtlNodeUI(self) : 
        nodes = listVrayMtlNode()
        self.ui.material_listWidget.clear()

        if nodes : 
            for each in nodes : 
                mId = nodes[each]
                self.addMaterialWidget(text1 = each, text2 = str(mId), bgColor = [0, 0, 0], iconPath = '', size = 16)


    def listVrayMultiMatteUI(self) : 
        renderElement = 'MultiMatteElement'
        mmNodes = listVrayRenderElement(renderElement)
        self.ui.multiMatte_listWidget.clear()

        for each in mmNodes : 
            mm = each 
            redid = mc.getAttr('%s.vray_redid_multimatte' % mm)
            greenid = mc.getAttr('%s.vray_greenid_multimatte' % mm)
            blueid = mc.getAttr('%s.vray_blueid_multimatte' % mm)
            self.addMultiMatteWidget(text1 = mm, text2 = str(redid), text3 = str(greenid), text4 = str(blueid), bgColor = [0, 0, 0], iconPath = '', size = 16)


    def setDefaultValue(self) : 
        start = 1
        increment = 1
        self.ui.start_lineEdit.setText(str(start))
        self.ui.increment_lineEdit.setText(str(increment))

        prefix = 'mm' 
        name = 'character'
        self.ui.prefix_lineEdit.setText(prefix)
        self.ui.name_lineEdit.setText(name)


    def materialSelect(self) : 
        value = self.getSelectedItem()

        # UI set focus
        if value : 
            materials = value[0]
            ids = value[1]

            if len(ids) == 1 : 
                self.ui.id_lineEdit.setText(ids[0])

            else : 
                self.ui.id_lineEdit.setText('Multi')

            self.ui.id_lineEdit.setFocus()
            self.ui.id_lineEdit.selectAll()

            # select scene objects 
            if self.ui.selectMtr_checkBox.isChecked() : 
                mc.select(materials)




    def setMaterialID(self) : 
        setID = str(self.ui.id_lineEdit.text())
        items = self.getSelectedItem()

        if items : 
            mms = items[0]

            for i in range(len(mms)) : 
                mm = mms[i]
                mc.setAttr('%s.vrayMaterialId' % mm, int(setID))

            self.listVrayMtlNodeUI()

    
    def assignMatteID(self) : 
        start = int(self.ui.start_lineEdit.text())
        increment = int(self.ui.increment_lineEdit.text())

        items = self.getSelectedItem()

        if self.ui.assignAll_checkBox.isChecked() : 
            items = self.getAllItems()

        if items : 
            mms = items[0]
            setId = start 

            for i in range(len(mms)) : 
                mm = mms[i]
                mc.setAttr('%s.vrayMaterialId' % mm, int(setId))

                setId += increment

            self.listVrayMtlNodeUI()


    def createMultiMatte(self) : 
        prefix = str(self.ui.prefix_lineEdit.text())
        name = str(self.ui.name_lineEdit.text())
        
        if not name : 
            name = 'character' 

        mmName = name

        if prefix : 
            mmName = ('_').join([prefix, name])
            
        items = self.getSelectedItem()
        mmNode = str()

        if self.ui.createAll_checkBox.isChecked() : 
            items = self.getAllItems()

        if items : 
            mms = items[0]
            ids = items[1]
            countIndex = 1

            for i in range(len(mms)) : 
                mm = mms[i]
                setId = ids[i]
                index = i%3

                # index == 0 mean create 
                if index == 0 : 
                    assignName = ('%s_%02d' % (mmName, countIndex))
                    tmpNode = createMultiMatte()[0]
                    mmNode = mc.rename(tmpNode, assignName)
                    mc.setAttr('%s.vray_redid_multimatte' % mmNode, int(setId))
                    countIndex += 1 

                if index == 1 : 
                    mc.setAttr('%s.vray_greenid_multimatte' % mmNode, int(setId))

                if index == 2 : 
                    mc.setAttr('%s.vray_blueid_multimatte' % mmNode, int(setId))

            self.listVrayMultiMatteUI()



    def getAllItems(self) : 
        count = self.ui.material_listWidget.count()
        itemWidgets = []
        items1 = []
        items2 = []


        for i in range(count) : 
            item = self.ui.material_listWidget.item(i)

            customWidget = self.ui.material_listWidget.itemWidget(item)
            text1 = customWidget.text1()
            text2 = customWidget.text2()


            items1.append(text1)
            items2.append(text2)
            itemWidgets.append(customWidget)


        return [items1, items2, itemWidgets]


    def getSelectedItem(self) : 
        items = self.ui.material_listWidget.selectedItems()
        text1List = []
        text2List = []

        if items : 
            for item in items : 
                customWidget = self.ui.material_listWidget.itemWidget(item)
                text1 = customWidget.text1()
                text2 = customWidget.text2()
                text1List.append(text1)
                text2List.append(text2)

            return [text1List, text2List]


    def addMaterialWidget(self, text1 = '', text2 = '', bgColor = [0, 0, 0], iconPath = '', size = 16) : 
        myCustomWidget = customWidget.customQWidgetItem()
        myCustomWidget.setText1(text1)
        myCustomWidget.setText2(text2)

        myCustomWidget.setTextColor1([240, 240, 240])
        myCustomWidget.setTextColor2([100, 160, 200])

        myCustomWidget.setIcon(iconPath, size)

        item = QtGui.QListWidgetItem(self.ui.material_listWidget)
        item.setSizeHint(myCustomWidget.sizeHint())
        # item.setBackground(QtGui.QColor(bgColor[0], bgColor[1], bgColor[2]))

        self.ui.material_listWidget.addItem(item)
        self.ui.material_listWidget.setItemWidget(item, myCustomWidget)


    def addMultiMatteWidget(self, text1 = '', text2 = '', text3 = '', text4 = '', bgColor = [0, 0, 0], iconPath = '', size = 16) : 
        myCustomWidget = customWidget.customQWidgetItem2()
        myCustomWidget.setText1(text1)
        myCustomWidget.setText2(text2)
        myCustomWidget.setText3(text3)
        myCustomWidget.setText4(text4)

        myCustomWidget.setTextColor1([240, 240, 240])
        myCustomWidget.setTextColor2([200, 100, 100])
        myCustomWidget.setTextColor3([100, 200, 100])
        myCustomWidget.setTextColor4([100, 100, 200])

        myCustomWidget.setIcon(iconPath, size)

        item = QtGui.QListWidgetItem(self.ui.multiMatte_listWidget)
        item.setSizeHint(myCustomWidget.sizeHint())
        # item.setBackground(QtGui.QColor(bgColor[0], bgColor[1], bgColor[2]))

        self.ui.multiMatte_listWidget.addItem(item)
        self.ui.multiMatte_listWidget.setItemWidget(item, myCustomWidget)



    
def listVrayMtlNode() : 
    """ list vray material """
    nodes = []

    for eachType in setting.VrayNodeType : 
        tmpNodes = mc.ls(type = eachType)

        if tmpNodes : 
            nodes = nodes + tmpNodes 

    vrayNode = dict()

    for eachNode in nodes : 
        attr = '%s.vrayMaterialId' % eachNode

        if mc.listConnections(eachNode, t = 'shadingEngine') : 
            if not mc.objExists(attr) : 
                mm.eval('vray addAttributesFromGroup %s vray_material_id 1' % eachNode)

            id = mc.getAttr('%s.vrayMaterialId' % eachNode)

            vrayNode[eachNode] = id

    return vrayNode


def listVrayRenderElement(type) : 
    nodes = mc.ls(type = 'VRayRenderElement')
    renderNodes = []
    
    for each in nodes : 
        classType = mc.getAttr('%s.vrayClassType' % each)
        
        if classType == type : 
            if not each in renderNodes : 
                renderNodes.append(each)
                
    return renderNodes

def createMultiMatte() : 
    currentNodes = listVrayRenderElement('MultiMatteElement')
    mm.eval('vrayAddRenderElement MultiMatteElement;')
    newNodes = listVrayRenderElement('MultiMatteElement')

    for each in currentNodes : 
        newNodes.remove(each)

    return newNodes


def renameMultiMatte(name) : 
    currentNodes = listVrayRenderElement('MultiMatteElement')

    if name in currentNodes : 
        num = name.split('_')[-1]


def deleteUI(ui) : 
    if mc.window(ui, exists = True) : 
        mc.deleteUI(ui)
        deleteUI(ui)