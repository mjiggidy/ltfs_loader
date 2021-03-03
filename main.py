from PySide2  import QtWidgets, QtGui, QtCore
import sys, pathlib

class DriveMonitor(QtWidgets.QWidget):
	"""GUI monitor for a tape drive"""

	def __init__(self, device, mount, density):
		super().__init__()

		self.device = device
		self.mount = mount
		self.density = density

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		self.setupWidgets()
		self.setupSignals()

	def setupWidgets(self):

		grp_device = QtWidgets.QGroupBox(f"[LTO-{self.density}] " + self.device)
		grp_device.setLayout(QtWidgets.QVBoxLayout())
		
		lay_controls = QtWidgets.QHBoxLayout()

		self.txt_mountpoint = QtWidgets.QLineEdit(self.mount)
		self.btn_mount = QtWidgets.QPushButton("Mount")
		self.btn_eject = QtWidgets.QPushButton("Eject")
		
		self.prog_status = QtWidgets.QProgressBar()
		self.prog_status.setRange(0,1)
		self.prog_status.setValue(0)
		self.prog_status.setTextVisible(True)
		self.prog_status.setFormat("Ready")
		#self.btn_eject.setDisabled(True)

		self.txt_log = QtWidgets.QTextEdit()
		self.txt_log.setReadOnly(True)
		self.txt_log.setDocument(QtGui.QTextDocument("Ready"))
		self.txt_log.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)	
		self.txt_log.setFont(QtGui.QFont("monospace", 7))

		lay_controls.addWidget(self.txt_mountpoint)
		lay_controls.addWidget(self.btn_mount)
		lay_controls.addWidget(self.btn_eject)

		grp_device.layout().addLayout(lay_controls)
		grp_device.layout().addWidget(self.prog_status)
		grp_device.layout().addWidget(QtWidgets.QLabel("Details"))
		grp_device.layout().addWidget(self.txt_log)

		self.layout().addWidget(grp_device)
	
	def setupSignals(self):
		self.btn_mount.clicked.connect(self.mountDrive)
		self.btn_eject.clicked.connect(lambda: self.unmountDrive(eject=True))
	
	def mountDrive(self):
		self.btn_mount.setDisabled(True)
		self.btn_eject.setDisabled(True)
		self.txt_mountpoint.setDisabled(True)
		self.proc_mount = QtCore.QProcess()


		self.prog_status.setFormat("Mounting drive...")
		self.prog_status.setMaximum(0)
		self.txt_log.setText(f"Mounting {self.device} to {self.txt_mountpoint.text()}...\n")
		
		self.proc_mount.finished.connect(self.mountSuccess)
		self.proc_mount.start("ltfs", [self.txt_mountpoint.text()])
	
	def mountSuccess(self):
		self.btn_mount.setText("Unmount")
		self.btn_mount.clicked.disconnect()
		self.btn_mount.clicked.connect(self.unmountDrive)
		self.btn_mount.setEnabled(True)
		
		self.btn_eject.setEnabled(True)
		
		self.prog_status.setFormat("Mounted successfully")
		self.prog_status.setMaximum(1)
		self.txt_log.insertPlainText("Complete\n")
	
	def unmountDrive(self, eject=False):
		self.btn_mount.setDisabled(True)
		self.btn_eject.setDisabled(True)
		self.prog_status.setFormat("Unmounting...")
		self.prog_status.setMaximum(0)
		self.txt_log.insertPlainText(f"Unmounting {self.device} from {self.txt_mountpoint.text()}...\n")

		self.proc_dismount = QtCore.QProcess()
		self.proc_dismount.finished.connect(lambda: self.unmountSuccess(eject))
		self.proc_dismount.start("umount", [self.txt_mountpoint.text()])
	
	def unmountSuccess(self, eject):
		self.txt_mountpoint.setEnabled(True)
		self.btn_mount.setText("Mount")
		self.btn_mount.clicked.disconnect()
		self.btn_mount.clicked.connect(self.mountDrive)
		self.btn_mount.setEnabled(True)
		self.btn_eject.setEnabled(True)

		self.prog_status.setFormat("Unmounted successfully")
		self.prog_status.setMaximum(1)

		self.txt_log.insertPlainText("Unmount complete\n")
		if(eject):
			self.ejectTape()
	
	def ejectTape(self):
		self.btn_mount.setDisabled(True)
		self.btn_eject.setDisabled(True)
		
		self.prog_status.setFormat("Ejecting tape...")
		self.prog_status.setMaximum(0)

		self.txt_log.insertPlainText("Ejecting tape\n")
		self.proc_eject = QtCore.QProcess()
		self.proc_eject.finished.connect(self.ejectSuccess)
		self.proc_eject.start("mt",["-f",self.device,"eject"])
	
	def ejectSuccess(self):
		self.btn_mount.setEnabled(True)
		self.btn_eject.setEnabled(True)
		
		self.prog_status.setFormat("Tape ejected")
		self.prog_status.setMaximum(1)

		self.txt_log.insertPlainText("Complete")



		


		


class AddDriveWindow(QtWidgets.QDialog):
	"""Add drives setup menu"""

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.setWindowTitle("Add Drive")
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.setupWidgets()
	
	def setupWidgets(self):

		grp_addnew = QtWidgets.QGroupBox()

		grp_addnew.setLayout(QtWidgets.QFormLayout())

		self.combo_density = QtWidgets.QComboBox()
		for x in range(5,9):
			self.combo_density.insertItem(x,f"LTO-{x}", x)
		self.combo_density.setCurrentIndex(self.combo_density.count() - 1)
		
		self.combo_devices = QtWidgets.QComboBox()
		self.combo_devices.insertItems(0, [str(x) for x in pathlib.Path("/dev/").glob("nst?")])
		self.combo_devices.setCurrentIndex(self.combo_devices.count() - 1)

		self.num_buffer = QtWidgets.QSpinBox()
		self.num_buffer.setRange(512000, 5120000)
		self.num_buffer.setSuffix(" KB")
		self.txt_mount = QtWidgets.QLineEdit()

		grp_addnew.layout().addRow("Device:", self.combo_devices)
		grp_addnew.layout().addRow("Drive Density:", self.combo_density)
		grp_addnew.layout().addRow("Drive Buffer:", self.num_buffer)
		grp_addnew.layout().addRow("Mount Point:", self.txt_mount)
		
		self.layout().addWidget(grp_addnew)

		btns_actions = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Cancel)
		self.layout().addWidget(btns_actions)
	


class AppWindow(QtWidgets.QMainWindow):
	"""Main application window"""

	def __init__(self, title):
		super().__init__()
		
		self.setWindowTitle(title)
		self.setMinimumWidth(400)
		
		self.setCentralWidget(QtWidgets.QWidget())
		self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
		
		self.setupWidgets()
		self.setupSignals()
	
	def setupWidgets(self):
		self.centralWidget().layout().addWidget(DriveMonitor("/dev/nst0", "/mnt/ltfs0", 8))
	#	self.centralWidget().layout().addWidget(DriveMonitor("/dev/nst1"))
	#	self.centralWidget().layout().addWidget(DriveMonitor("/dev/nst2"))

		
		lay_btns = QtWidgets.QHBoxLayout()
		
		self.btn_add = QtWidgets.QPushButton("Add Drive...")
		self.btn_add.setIcon(QtGui.QIcon.fromTheme("list-add"))
		self.btn_save = QtWidgets.QPushButton("Save Config")
		self.btn_save.setIcon(QtGui.QIcon.fromTheme("document-save"))
		
		lay_btns.addWidget(self.btn_add)
		lay_btns.addWidget(self.btn_save)
		lay_btns.addStretch()
		lay_btns.addWidget(QtWidgets.QLabel("v0.1 by Michael Jordan"))
		
		self.centralWidget().layout().addLayout(lay_btns)
	
	def setupSignals(self):
		self.btn_add.clicked.connect(self.showAddDrive)
	
	def showAddDrive(self):
		wnd_adddrive = AddDriveWindow(self)
		wnd_adddrive.show()
	

if __name__=="__main__":

	app = QtWidgets.QApplication(sys.argv)
	
	wnd_main = AppWindow(title="LTFS Mounter ExXxtreme")
	
	wnd_main.show()
	
	sys.exit(app.exec_())

