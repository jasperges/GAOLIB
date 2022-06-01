#   Copyright (C) 2022 GAO SHAN PICTURES

#   This file is a part of GAOLIB.

#   GAOLIB is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>

__author__ = "Anne Beurard"

import json
import os
import shutil

import bpy
from PySide2 import QtCore, QtGui, QtWidgets

from gaolib.model.blenderutils import (
    getCurrentPose,
    getRefPoseFromLib,
    getSelectedBones,
    removeOrphans,
    selectBones,
    updateSelectionSet,
)
from gaolib.ui.infowidgetui import Ui_Form as InfoWidget
from gaolib.ui.yesnodialogui import Ui_Dialog as YesNoDialog


class GaoLibInfoWidget(QtWidgets.QWidget, InfoWidget):
    """Manage display of the selected list item informations"""

    def __init__(self, selectedItem, mainWin, parent=None):
        super(GaoLibInfoWidget, self).__init__(parent=parent)
        self.parent = parent
        self.setupUi(self)
        self.mainWindow = mainWin
        self.item = selectedItem
        self.thumbpath = self.item.thumbpath
        self.currentPose = None

        # For animation item use gif thumbnail
        self.movie = None
        if self.item.itemType == "ANIMATION":
            self.thumbpath = self.item.thumbpath.replace("png", "gif")
        self.showInfos()
        # Connect functions
        self.trashPushButton.released.connect(self.delete)
        self.selectBonesPushButton.released.connect(self.selectBones)
        self.addToSetPushButton.released.connect(
            lambda: updateSelectionSet(self, add=True)
        )
        self.rmFromSetPushButton.released.connect(
            lambda: updateSelectionSet(self, add=False)
        )
        self.blendPoseSlider.valueChanged.connect(
            lambda: self.blendSliderChanged(
                self.item.path, blend=self.blendPoseSlider.value() / 100
            )
        )

    def blendSliderChanged(self, poseDir, blend=1):
        self.blendPoseLabel.setText(
            "Blend Pose " + str(self.blendPoseSlider.value()) + "%"
        )

        selection = getSelectedBones()

        # Remember current pose
        if not self.currentPose:
            self.currentPose = getCurrentPose(selection)

        # Append pose object
        refPose = getRefPoseFromLib(poseDir, selection)
        pose = refPose.pose

        # Copy properties from ref bones current object
        for posebone in pose.bones:
            for selectedbone in selection:
                if posebone.name == selectedbone.name:
                    rotationMode = posebone.rotation_mode
                    selectedbone.rotation_mode = posebone.rotation_mode

                    for axis in range(3):
                        if not selectedbone.lock_location[axis]:
                            selectedbone.location[axis] = (
                                blend * posebone.location[axis]
                                + (1 - blend)
                                * self.currentPose[selectedbone]["location"][axis]
                            )
                        if rotationMode != "QUATERNION":
                            if not selectedbone.lock_rotation[axis]:
                                selectedbone.rotation_euler[axis] = (
                                    blend * posebone.rotation_euler[axis]
                                    + (1 - blend)
                                    * self.currentPose[selectedbone]["rotation"][axis]
                                )
                        if not selectedbone.lock_scale[axis]:
                            selectedbone.scale[axis] = (
                                blend * posebone.scale[axis]
                                + (1 - blend)
                                * self.currentPose[selectedbone]["scale"][axis]
                            )
                    if rotationMode == "QUATERNION":
                        if not selectedbone.lock_rotation[0]:
                            selectedbone.rotation_quaternion[0] = (
                                blend * posebone.rotation_quaternion[0]
                                + (1 - blend)
                                * self.currentPose[selectedbone]["rotation"][0]
                            )
                        for axis in range(3):
                            if not selectedbone.lock_rotation[axis]:
                                selectedbone.rotation_quaternion[axis + 1] = (
                                    blend * posebone.rotation_quaternion[axis + 1]
                                    + (1 - blend)
                                    * self.currentPose[selectedbone]["rotation"][
                                        axis + 1
                                    ]
                                )

                    # for key in posebone.keys():
                    #     try:
                    #         exec('selectedbone.' + key + ' = posebone.' + key)
                    #     except:
                    #         try:
                    #             exec('selectedbone[\"' + key + '\"] = posebone[\"' + key +'\"]')
                    #         except:
                    #             print('IMPOSSIBLE TO HANDLE PROPERTY ' + key + ' FOR ' + selectedbone.name)

                    # break

        # Delete pose
        bpy.context.scene.collection.objects.unlink(refPose)
        # Clean orphans
        removeOrphans()

    def delete(self):
        """Delete selected item"""
        # Confirm delete dialog
        path = self.item.path
        dialog = QtWidgets.QDialog(self)
        dialog.ui = YesNoDialog()
        dialog.ui.setupUi(dialog)
        message = (
            "Do you want to delete the "
            + self.item.itemType
            + " item "
            + self.item.name
            + " ?"
        )
        dialog.ui.label.setText(message)
        rsp = dialog.exec_()
        # if user clicks on 'ok'
        if rsp == QtWidgets.QDialog.Accepted:
            print(self.mainWindow.rootPath)
            trashPath = os.path.join(self.mainWindow.rootPath, "../trash")
            if not os.path.exists(trashPath):
                os.makedirs(trashPath)
            trashPath = os.path.join(trashPath, os.path.basename(path))

            # clean info widget
            if self.movie is not None:
                self.thumbnailLabel.removeEventFilter(self)
                self.movie.setFileName("")
            layout = self.mainWindow.verticalLayout_5
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().deleteLater()

            # delete files
            copied = False
            attempts = 0
            while not copied:
                try:
                    shutil.copytree(path, trashPath)
                    copied = True
                except FileExistsError:
                    attempts += 1
                    try:
                        trashPath = (
                            trashPath.split(" Copy (")[0]
                            + " Copy ("
                            + str(attempts)
                            + ")"
                        )
                        shutil.copytree(path, trashPath)
                        copied = True
                    except:
                        pass
                except WindowsError as e:
                    attempts += 1
                    if str(e).startswith("[Error 183]"):
                        try:
                            trashPath = (
                                trashPath.split(" Copy (")[0]
                                + " Copy ("
                                + str(attempts)
                                + ")"
                            )
                            shutil.copytree(path, trashPath)
                            copied = True
                        except:
                            pass
                    else:
                        raise
            try:
                if self.item.itemType == "ANIMATION":
                    os.remove(os.path.join(path, "thumbnail.gif"))
                elif self.item.itemType in ["POSE", "SELECTION SET"]:
                    os.remove(os.path.join(path, "thumbnail.png"))
            except Exception as e:
                if self.item.itemType == "ANIMATION":
                    QtWidgets.QMessageBox.about(
                        self,
                        "Abort action",
                        "Cannot remove "
                        + os.path.join(path, "thumbnail.gif")
                        + " : "
                        + str(e),
                    )
                elif self.item.itemType in ["POSE", "SELECTION SET"]:
                    os.remove(os.path.join(path, "thumbnail.png"))
                return
            shutil.rmtree(path)
            self.mainWindow.items = self.mainWindow.getListItems()
            self.mainWindow.currentTreeElement = None
            self.mainWindow.setTreeView()

    def selectBones(self):
        """Select bones listed in json file"""
        for file in os.listdir(self.item.path):
            if file.endswith(".json"):
                jsonPath = os.path.join(self.item.path, file)
        selectBones(jsonPath)

    def showInfos(self):
        """Display thumbnail and infos from json file"""
        self.parent.infoGroupBox.setTitle(self.item.itemType)
        self.nameLabel.setText(self.item.name)
        self.ownerLabel.setText(self.item.owner)
        self.dateLabel.setText(self.item.date)
        self.contentLabel.setText(self.item.content)

        self.thumbnailLabel.setPixmap((QtGui.QPixmap(self.thumbpath).scaled(200, 200)))
        self.frameRangeLabel.setText(self.item.frameRange)

        if not self.item.bonesSelection:
            self.selectBonesPushButton.setEnabled(False)

        if self.item.itemType == "POSE":
            self.animOptionsWidget.setVisible(False)
            # self.poseOptionsWidget.setVisible(False)
            self.optionsGroupBox.setVisible(True)
            self.selectionSetOptionsWidget.setVisible(False)
            self.flippedCheckBox.setVisible(False)
            self.flippedCheckBox.setEnabled(False)
            # for file in os.listdir(self.item.path):
            #     if file == 'flipped_pose.blend':
            #         self.flippedCheckBox.setEnabled(True)
            self.label_5.setVisible(False)
            self.frameRangeLabel.setVisible(False)

        if self.item.itemType == "SELECTION SET":
            self.applyPushButton.setVisible(False)
            self.poseOptionsWidget.setVisible(False)
            self.animOptionsWidget.setVisible(False)
            self.label_5.setVisible(False)
            self.frameRangeLabel.setVisible(False)

        if self.item.itemType == "FOLDER":
            self.applyPushButton.setVisible(False)
            self.optionsGroupBox.setVisible(False)
            self.ownerLabel.setVisible(False)
            self.dateLabel.setVisible(False)
            self.contentLabel.setVisible(False)
            self.frameRangeLabel.setVisible(False)
            self.label_2.setVisible(False)
            self.label_3.setVisible(False)
            self.label_4.setVisible(False)
            self.label_5.setVisible(False)
            self.selectBonesPushButton.setVisible(False)

        if self.item.itemType == "ANIMATION":
            self.selectionSetOptionsWidget.setVisible(False)
            self.poseOptionsWidget.setVisible(False)
            icon1 = QtGui.QIcon()
            icon1.addPixmap(
                QtGui.QPixmap("icons/anim2.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off
            )
            self.applyPushButton.setIcon(icon1)
            # Set spin box options
            self.fromRangeSpinBox.valueChanged.connect(self.fromSpinBoxChanged)
            self.toRangeSpinBox.valueChanged.connect(self.toSpinBoxChanged)
            self.fromRangeSpinBox.setValue(int(self.item.frameRange.split("-")[0]))
            self.toRangeSpinBox.setValue(int(self.item.frameRange.split("-")[-1]))
            self.fromRangeSpinBox.setMinimum(int(self.item.frameRange.split("-")[0]))
            self.toRangeSpinBox.setMaximum(int(self.item.frameRange.split("-")[-1]))
            # Display animated thumbnail
            self.thumbnailLabel.installEventFilter(self)
            self.movie = QtGui.QMovie(self.thumbpath, QtCore.QByteArray(), self)
            self.movie.setScaledSize(QtCore.QSize(200, 200))
            self.movie.setCacheMode(QtGui.QMovie.CacheNone)
            self.movie.setSpeed(100)
            self.thumbnailLabel.setMovie(self.movie)
            self.movie.start()
            self.movie.stop()

    def fromSpinBoxChanged(self):
        """Keep consistancy between spinboxes"""
        if self.fromRangeSpinBox.value() > self.toRangeSpinBox.value():
            self.toRangeSpinBox.setValue(self.fromRangeSpinBox.value())
        if self.fromRangeSpinBox.value() < self.fromRangeSpinBox.minimum():
            self.fromRangeSpinBox.setValue(self.fromRangeSpinBox.minimum())
        elif self.fromRangeSpinBox.value() > self.toRangeSpinBox.maximum():
            self.fromRangeSpinBox.setValue(self.toRangeSpinBox.maximum())

    def toSpinBoxChanged(self):
        """Keep consistancy between spinboxes"""
        if self.fromRangeSpinBox.value() > self.toRangeSpinBox.value():
            self.fromRangeSpinBox.setValue(self.toRangeSpinBox.value())
        if self.toRangeSpinBox.value() > self.toRangeSpinBox.maximum():
            self.toRangeSpinBox.setValue(self.toRangeSpinBox.maximum())

    def eventFilter(self, obj, event):
        """Event filter to play movie when hovered"""
        if obj == self.thumbnailLabel and event.type() == QtCore.QEvent.Enter:
            if self.movie:
                self.movie.start()
        if obj == self.thumbnailLabel and event.type() == QtCore.QEvent.Leave:
            if self.movie:
                self.movie.stop()
        return super(GaoLibInfoWidget, self).eventFilter(obj, event)
