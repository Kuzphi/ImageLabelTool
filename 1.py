import os
import cv2
import sys
import json
import matplotlib
from numpy import zeros
matplotlib.use("Qt5Agg")
import PyQt5
from PyQt5 import QtCore
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QGridLayout,QCheckBox, QWidget, QMainWindow, QApplication, QLineEdit, QLabel, QPushButton, QListWidget



class Joint(QWidget):
	def __init__(self, center, color, parent, Edit, idx, label, r = 4):
		super(Joint, self).__init__(parent = parent)
		self.label = label
		self.color = color
		self.idx = str(idx)
		self.r = r
		x = center[0]
		y = center[1]
		self.Edit = Edit
		self.setGeometry(x - r, y - r, 2 * r, 4 * r)
		self.Edit.setText(str(self.x() + self.width())  + " , " + str(self.y() + self.height()))
		# print (self.pos().x(), self.pos().y(), self.width(), self.height())

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.setBrush(QColor(*self.color))
		painter.drawEllipse(0, 0, self.width(), self.height() / 2)


		painter.setPen(QColor(*self.color[::-1]))
		painter.setFont(QFont("Arial", 7));
		painter.drawText(0, self.height() / 2., self.width(), self.height() / 2. , QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter, self.idx)
		painter.end()
		event.accept()

	def move(self, pos):
		super(Joint, self).move(pos)
		self.Edit.setText(str(pos.x() + self.r)  + " , " + str(pos.y() + self.r))

	def move_center(self, x, y):
		self.move(QPoint(x - self.r, y - self.r))
	
	def mousePressEvent(self, event):
		self.__mousePressPos = None
		self.__mouseMovePos = None
		if event.button() == QtCore.Qt.LeftButton:
			self.__mousePressPos = event.globalPos()
			self.__mouseMovePos = event.globalPos()

		super(Joint, self).mousePressEvent(event)
		event.accept()

	def mouseMoveEvent(self, event):
		if event.buttons() == QtCore.Qt.LeftButton:
			# adjust offset from clicked point to origin of widget
			currPos = self.mapToGlobal(self.pos())
			globalPos = event.globalPos()
			diff = globalPos - self.__mouseMovePos
			newPos = self.mapFromGlobal(currPos + diff)
			self.move(newPos)

			self.__mouseMovePos = globalPos

		super(Joint, self).mouseMoveEvent(event)
		event.accept()

	def mouseReleaseEvent(self, event):
		if self.__mousePressPos is not None:
			moved = event.globalPos() - self.__mousePressPos 
			if moved.manhattanLength() > 3:
				event.ignore()
				return

		super(Joint, self).mouseReleaseEvent(event)
		event.accept()

Name = 	["Wrist"] + \
		["Thumb 0", "Thumb 1", "Thumb 2","Thumb 3"] + \
		["Index 0", "Index 1", "Index 2","Index 3"] + \
		["Middle 0", "Middle 1", "Middle 2","Middle 3"] + \
		["Ring 0" , "Ring 1", "Ring 2","Ring 3"] + \
		["Little 0", "Little 1", "Little 2","Little 3"];

colors = [
		[100.,  100.,  100.], 
		[100.,    0.,    0.],
		[150.,    0.,    0.],
		[200.,    0.,    0.],
		[255.,    0.,    0.],
		[100.,  100.,    0.],
		[150.,  125.,    0.],
		[200.,  150.,    0.],
		[255.,  200.,    0.],
		[  0.,  100.,   50.],
		[  0.,  150.,   75.],
		[  0.,  200.,  100.],
		[  0.,  255.,  125.],
		[  0.,   50.,  100.],
		[  0.,   75.,  150.],
		[  0.,  100.,  200.],
		[  0.,  125.,  255.],
		[100.,    0.,  100.],
		[150.,    0.,  150.],
		[200.,    0.,  200.],
		[255.,    0.,  255.]]

LineSz = 15

def cmp(a, b):
	x, y = a[:-4], b[:-4]
	if x[-1] != y[-1]:
		return ord(x[-1]) - ord(y[-1]);
	return int(x[:-1]) - int(y[:-1])

class Main(QWidget):
	def __init__(self, name, data_path):
		super(Main, self).__init__()
		self.NextImg = QPushButton(self)
		self.AppPre = QPushButton(self)
		self.FileList = QListWidget(self)
		self.MousePosEdit  = QLineEdit(self)
		self.MousePosLabel = QLabel(self)
		self.finger = QWidget(self)
		self.Layout = QGridLayout(self.finger)
		self.canvas = QLabel(self)
		self.path = data_path
		self.name = name
		self.NewPosPath = "./" + name + ".js"
		self.OriPos = json.load(open(data_path + "annotation.json",'r'))
		if os.path.exists(self.NewPosPath):
			self.NewPos = json.load(open(self.NewPosPath,"r"))
		else:
			self.NewPos = {}
		ImgList = os.listdir(data_path)
		# print sorted(ImgList)
		Img = []
		for idx, ImgName in enumerate(ImgList):
			if ImgName.endswith(".jpg"):
				Img.append(ImgName)
		Img = sorted(Img, cmp = cmp)
		# print Img
		count = 0
		for idx, ImgName in enumerate(Img):
			if self.OriPos.has_key(ImgName[:-4]):
				self.FileList.addItem(ImgName)
				if self.NewPos.has_key(ImgName[:-4]):					
					self.FileList.item(count).setForeground(QColor(255,0,0))
				count += 1

		self.FileList.itemClicked.connect(self.ItemSelect)
		self.NextImg.clicked.connect(self.SaveNext)
		self.AppPre.clicked.connect(self.applyPreviousResult)
		self.Edits  = [QLineEdit() for i in range(21)]
		self.Labels = [QLabel() for i in range(21)]
		self.Joints = [Joint([0,0], colors[i], parent = self.canvas, Edit = self.Edits[i], \
								idx = i, label = self.Labels[i]) for i in range(21)]

		for idx, label in enumerate(self.Labels):
			label.setText(str(idx) +".\t" +Name[idx])
			self.Layout.addWidget(label, idx % LineSz, idx // LineSz * 2)
			label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			palette = label.palette()
			palette.setColor(label.foregroundRole(),QColor(*colors[idx]))
			label.setPalette(palette)

		CheckBoxName = ["Wrist", "Thumb", "Index", "Middle", "Ring", "Little"]
		self.CheckBox = [QCheckBox("Show %s"%(name)) for name in CheckBoxName]
		self.CheckBoxAll = QCheckBox("All")

		self.SetupUI()

	def SetupUI(self):
		self.resize(1200,500)
		self.FileList.setGeometry(0,0,200,500)
		# self.Layout.setContentsMargins(0, 0, 0, 0)
		self.canvas.setGeometry(200,0,500, 500)
		self.finger.setGeometry(700, 0, 500, 400)
		# print self.canvas.width(), self.canvas.height()
		# self.Layout.addWidget(self.canvas, 0, 0, 21 , 1)

		self.AppPre.setText("Apply Previous Result")
		self.MousePosLabel.setText("Mouse Position")
		self.NextImg.setText("Save && Next Image(n)")
		self.Layout.addWidget(self.MousePosLabel, LineSz, 0)
		self.Layout.addWidget(self.MousePosEdit , LineSz, 1)
		self.Layout.addWidget(self.CheckBoxAll, 6, 3)
		self.CheckBoxAll.stateChanged.connect(self.AllChange)
		self.CheckBoxAll.setChecked(True)
		for idx, checkbox in enumerate(self.CheckBox):
			self.Layout.addWidget(checkbox, 7 + idx, 3)
			checkbox.setChecked(True)
			checkbox.stateChanged.connect(self.CheckBoxStateChange)

		self.Layout.addWidget(self.NextImg, 13, 3)
		self.Layout.addWidget(self.AppPre, 14, 3)
		for idx, edit in enumerate(self.Edits):
			self.Layout.addWidget(edit, idx % LineSz, idx // LineSz * 2 + 1)

		self.FileList.setCurrentRow(0)
		self.ItemSelect(self.FileList.item(0))
		
	def keyPressEvent(self, event):		
		if event.key() == QtCore.Qt.Key_N:
			self.SaveNext()
		event.accept()

	def applyPreviousResult(self):
		PreRow = self.FileList.currentRow() - 1
		if PreRow < 0:
			return False
		PreName = self.FileList.item(PreRow).text()[:-4]
		if self.NewPos.has_key(PreName):
			Jposes = self.NewPos[PreName]['Joint']
			Ipos = self.NewPos[PreName]['Pos']
			for Jpos, Joint in zip(Jposes, self.Joints):
				nx, ny = Jpos[0] - Ipos[2], Jpos[1] - Ipos[0]
				nx, ny= float(nx) * self.ratio[0], float(ny) * self.ratio[1]
				if nx <= 5 or nx >= 495 or ny <= 5 or ny >= 495:
					nx = ny = 10
				# print nx, ny
				# pos.append([int(nx), int(ny)])
				Joint.move_center(nx, ny)

	def mouseMoveEvent(self, event):
		# currPos = self.mapToGlobal(self.pos())
		pos = event.localPos()
		# pos =  currPos - globalPos
		self.MousePosEdit.setText(str(pos.x() - 200)  + " , " + str(pos.y()))
		super(Main, self).mouseMoveEvent(event)

	def Collect(self):
		Name = self.FileList.currentItem().text()[:-4]
		dy, dx = self.OriPos[Name]["Pos"][0], self.OriPos[Name]["Pos"][2]
		pos = []
		for Edit in self.Edits:
			x, y = Edit.text().split(" , ")
			nx, ny = dx + float(x) / self.ratio[0], dy + float(y) / self.ratio[1]
			pos.append([nx, ny])
		self.NewPos[Name] = {}
		self.NewPos[Name]["Joint"] = pos
		self.NewPos[Name]["Pos"] = self.OriPos[Name]["Pos"]
		self.Save()

	def Save(self):
		json.dump(self.NewPos,open(self.NewPosPath,"w"));

	def SaveNext(self):
		self.Collect()
		self.FileList.currentItem().setForeground(QColor(255,0,0))
		row  = self.FileList.currentRow()  + 1
		row %= self.FileList.count()
		self.FileList.setCurrentRow(row)
		self.ItemSelect(self.FileList.item(row))

	def ItemSelect(self, item):
		# print item.text()
		img = cv2.imread(self.path + item.text())
		self.ratio = [500. / img.shape[0], 500./ img.shape[1]]
		img = cv2.resize(img, (500,500))
		canvas = zeros((500,500,3))
		canvas[:,:,:] = 255
		w, h = img.shape[0], img.shape[1]
		canvas[:w , :h, :] = img
		cv2.imwrite("./tmp.jpg", canvas)
		pixmap = QPixmap("./tmp.jpg")

		# print (pixmap.width(), pixmap.height())
		self.canvas.setPixmap(pixmap)
		self.canvas.setAlignment(QtCore.Qt.AlignTop|QtCore.Qt.AlignLeft)
		if not self.OriPos.has_key(item.text()[:-4]):
			raise EnvironmentError("Can not find %s_%s coordination\n" %(self.name, item.text()))

		thisItem = self.OriPos[item.text()[:-4]]
		if self.NewPos.has_key(item.text()[:-4]):
			thisItem = self.NewPos[item.text()[:-4]]
		pos = []
		# print thisItem
		# print "=============="
		for coor in thisItem["Joint"]:
			if coor == -1:
				pos.append([10,10])
			else:
				nx, ny = coor[0] - thisItem['Pos'][2], coor[1] - thisItem['Pos'][0]
				nx, ny= float(nx) * self.ratio[0], float(ny) * self.ratio[1]
				if nx <= 5 or nx >= 495 or ny <= 5 or ny >= 495:
					nx = ny = 10
				print nx, ny
				pos.append([int(nx), int(ny)])

		# print len(pos), len(self.Joints)

		for coor, Joint in zip(pos, self.Joints):
			Joint.move_center(coor[0] , coor[1])

	def CheckBoxStateChange(self):
		for checkbox in self.CheckBox:
			name = checkbox.text()[5:]
			for joint in self.Joints:
				if name in joint.label.text():
					joint.setVisible(checkbox.checkState())

	def AllChange(self):
		for checkbox in self.CheckBox:
			checkbox.setChecked(self.CheckBoxAll.checkState())
		self.CheckBoxStateChange()

	def closeEvent(self, event):
		self.Save();
		event.accept()

if __name__ == '__main__':
	ID = [0,0]
	if os.path.exists("./user.txt"):
		with open("user.txt","r") as f:
			ID[0] = f.readline()[:-1]
			ID[1] = f.readline()[:-1]
		while True:
			ans = raw_input("Is your name Initial %s, Student ID %s (y/n) ?: "%(ID[0],ID[1]))
			ans = ans.lower()
			if ans == "yes" or ans == "y":
				break
			elif ans == 'no' or ans == 'n':
				ID[0] = raw_input("Input your name initial: ")
				ID[1] = raw_input("Input your student id: ")
				break
	else:
		ID[0] = raw_input("Input your name initial: ")
		ID[1] = raw_input("Input your student id: ")

	name = ID[0] +"_" + ID[1]
	data_path = "./" + name + "/"
	f = open("user.txt","w")
	f.write(str(ID[0]) + "\n")
	f.write(str(ID[1]) + "\n")
	f.close()
	if not os.path.exists(data_path):
		raise EnvironmentError("folder %s Not Found" % (name))

	app = QApplication(sys.argv)
	mytest = Main(name, data_path)
	mytest.show()
	app.exec_()