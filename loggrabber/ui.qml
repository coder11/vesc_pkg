import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3

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
                            onClicked: {
                                // File selected
                                console.log("File selected: " + model.fullPath)
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
    
    Component.onCompleted: {
        fileModel.clear()
        scanDirectoryRecursive("/")
    }
}
