import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import Qt.labs.platform 1.1 as Platform

import Vedder.vesc.commands 1.0
import Vedder.vesc.configparams 1.0
import Vedder.vesc.utility 1.0

Item {
    id: container
    anchors.fill: parent
    anchors.margins: 10
    
    property Commands mCommands: VescIf.commands()
    property var fileModel: ListModel {}
    
    ColumnLayout {
        anchors.fill: parent
        
        RowLayout {
            Layout.fillWidth: true
            
            Text {
                Layout.fillWidth: true
                color: Utility.getAppHexColor("lightText")
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 20
                text: "LogGrabber"
            }
            
            Button {
                text: "Rescan"
                onClicked: {
                    fileModel.clear()
                    scanDirectoryRecursive("/")
                }
            }
        }
        
        // Flat file list
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ListView {
                id: fileListView
                model: fileModel
                
                delegate: Item {
                    width: fileListView.width
                    height: model.isDir ? 0 : fileItem.height
                    visible: !model.isDir
                    
                    Rectangle {
                        id: fileItem
                        width: parent.width
                        height: 30
                        color: mouseArea.containsMouse ? 
                               Utility.getAppHexColor("lightBackground") : 
                               "transparent"
                        
                        Row {
                            anchors.left: parent.left
                            anchors.leftMargin: 10
                            anchors.right: parent.right
                            anchors.rightMargin: 10
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 10
                            
                            Text {
                                text: model.fullPath
                                color: Utility.getAppHexColor("lightText")
                                anchors.verticalCenter: parent.verticalCenter
                                elide: Text.ElideLeft
                            }
                            
                            Text {
                                text: "(" + formatSize(model.size) + ")"
                                color: Utility.getAppHexColor("lightText")
                                anchors.verticalCenter: parent.verticalCenter
                                opacity: 0.7
                            }
                        }
                        
                        MouseArea {
                            id: mouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            acceptedButtons: Qt.LeftButton | Qt.RightButton
                            onClicked: {
                                if (mouse.button === Qt.RightButton || mouse.button === Qt.LeftButton) {
                                    contextMenu.popup(mouseArea, mouse.x, mouse.y)
                                }
                            }
                        }
                        
                        Menu {
                            id: contextMenu
                            
                            MenuItem {
                                text: "Download"
                                onTriggered: {
                                    downloadFile(model.fullPath)
                                }
                            }
                            
                            MenuItem {
                                text: "Delete"
                                onTriggered: {
                                    deleteFile(model.fullPath)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    function scanDirectoryRecursive(path) {
        var items = mCommands.fileBlockList(path)
        var hasFiles = false
        
        if (items && items.length > 0) {
            for (var i = 0; i < items.length; i++) {
                var item = items[i]
                var fullPath = path === "/" ? "/" + item.name : path + "/" + item.name
                
                if (item.isDir) {
                    // Recursively scan directory first to check if it contains files
                    var dirHasFiles = scanDirectoryRecursive(fullPath)
                    if (dirHasFiles) {
                        // Don't add directories to the list, just track that they have files
                        hasFiles = true
                    }
                } else {
                    // Always add files
                    fileModel.append({
                        isDir: false,
                        fullPath: fullPath,
                        size: item.size || 0
                    })
                    hasFiles = true
                }
            }
        }
        
        return hasFiles
    }
    
    function formatSize(bytes) {
        if (bytes === 0) return "0 B"
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB"
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + " GB"
    }
    
    Platform.FileDialog {
        id: saveFileDialog
        title: "Save File"
        fileMode: Platform.FileDialog.SaveFile
        
        property string filePath: ""
        
        onAccepted: {
            if (!Utility.requestFilePermission()) {
                VescIf.emitMessageDialog(
                    "File Permissions",
                    "Unable to request file system permission.",
                    false, false);
                return;
            }
            
            var fUrl = file.toString();

            // Debug popup to display filepath
            VescIf.emitMessageDialog(
                "Debug: File Path",
                "File path: " + fUrl + "\nSource path: " + filePath,
                false, false);
            
            var data = mCommands.fileBlockRead(filePath);

            
            if (data && data.length > 0) {
                var request = new XMLHttpRequest();
                request.open("PUT", fUrl, false);
                request.send(data);
                
                if (request.status === 0) {
                    VescIf.emitStatusMessage("File downloaded successfully", true);
                } else {
                    VescIf.emitStatusMessage("Download failed: %1".arg(request.status), false);
                }
            } else {
                VescIf.emitStatusMessage("Failed to read file from device", false);
            }
        }
    }
    
    Dialog {
        id: deleteConfirmDialog
        title: "Delete File"
        standardButtons: Dialog.Ok | Dialog.Cancel
        modal: true
        focus: true
        width: parent.width - 20
        closePolicy: Popup.CloseOnEscape
        x: 10
        y: 10 + parent.height / 2 - height / 2
        parent: container
        
        property string filePath: ""
        
        Component.onCompleted: {
            standardButton(Dialog.Ok).text = "Delete"
        }
        
        onAccepted: {
            var ok = mCommands.fileBlockRemove(filePath);
            if (ok) {
                VescIf.emitStatusMessage("File deleted", true);
                // Rescan to update the list
                fileModel.clear()
                scanDirectoryRecursive("/")
            } else {
                VescIf.emitStatusMessage("Failed to delete file", false);
            }
        }
        
        Overlay.modal: Rectangle {
            color: "#AA000000"
        }
        
        ColumnLayout {
            anchors.fill: parent
            Text {
                color: Utility.getAppHexColor("lightText")
                verticalAlignment: Text.AlignVCenter
                Layout.fillWidth: true
                wrapMode: Text.WordWrap
                text: "This will delete the file permanently. Are you sure?"
            }
        }
    }
    
    function downloadFile(path) {
        if (!Utility.requestFilePermission()) {
            VescIf.emitMessageDialog(
                "File Permissions",
                "Unable to request file system permission.",
                false, false);
            return;
        }
        
        saveFileDialog.filePath = path;
        saveFileDialog.nameFilters = ["CSV files (*.csv)", "All files (*)"];
        saveFileDialog.open();
    }
    
    function deleteFile(path) {
        deleteConfirmDialog.filePath = path;
        deleteConfirmDialog.open();
    }
    
    Component.onCompleted: {
        fileModel.clear()
        scanDirectoryRecursive("/")
    }
}
