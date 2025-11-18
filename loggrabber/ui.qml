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
        
        Text {
            Layout.fillWidth: true
            color: Utility.getAppHexColor("lightText")
            horizontalAlignment: Text.AlignHCenter
            font.pointSize: 20
            text: "LogGrabber"
        }
        
        // File tree view
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ListView {
                id: fileTreeView
                model: fileModel
                
                delegate: Item {
                    width: fileTreeView.width
                    height: fileItem.height
                    
                    Rectangle {
                        id: fileItem
                        width: parent.width
                        height: 30
                        color: mouseArea.containsMouse ? 
                               Utility.getAppHexColor("lightBackground") : 
                               "transparent"
                        
                        Row {
                            anchors.left: parent.left
                            anchors.leftMargin: (model.level || 0) * 20
                            anchors.verticalCenter: parent.verticalCenter
                            spacing: 5
                            
                            Text {
                                text: model.isDir ? (model.expanded ? "▼" : "▶") : "  "
                                color: Utility.getAppHexColor("lightText")
                                width: 15
                                visible: model.isDir
                            }
                            
                            Text {
                                text: model.isDir ? "[D]" : "[F]"
                                color: Utility.getAppHexColor("lightText")
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: model.name
                                color: Utility.getAppHexColor("lightText")
                                anchors.verticalCenter: parent.verticalCenter
                            }
                            
                            Text {
                                text: model.isDir ? "" : "(" + formatSize(model.size) + ")"
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
                                if (model.isDir) {
                                    var newPath = model.fullPath
                                    if (model.expanded) {
                                        // Collapse - remove children
                                        collapseDirectory(model.index)
                                    } else {
                                        // Expand - load children
                                        expandDirectory(model.index, newPath)
                                    }
                                } else {
                                    // File selected
                                    console.log("File selected: " + model.fullPath)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    function loadDirectory(path) {
        fileModel.clear()
        var items = mCommands.fileBlockList(path)
        
        if (items && items.length > 0) {
            for (var i = 0; i < items.length; i++) {
                var item = items[i]
                var fullPath = path === "/" ? "/" + item.name : path + "/" + item.name
                fileModel.append({
                    name: item.name,
                    isDir: item.isDir || false,
                    fullPath: fullPath,
                    level: 0,
                    expanded: false,
                    parentIndex: -1,
                    size: item.size || 0
                })
            }
        }
    }
    
    function expandDirectory(index, path) {
        // Mark as expanded
        fileModel.setProperty(index, "expanded", true)
        
        // Load children
        var items = mCommands.fileBlockList(path)
        
        if (items && items.length > 0) {
            var parentLevel = fileModel.get(index).level
            var insertIndex = index + 1
            
            for (var i = 0; i < items.length; i++) {
                var item = items[i]
                var fullPath = path === "/" ? "/" + item.name : path + "/" + item.name
                fileModel.insert(insertIndex + i, {
                    name: item.name,
                    isDir: item.isDir || false,
                    fullPath: fullPath,
                    level: parentLevel + 1,
                    expanded: false,
                    parentIndex: index,
                    size: item.size || 0
                })
            }
        }
    }
    
    function collapseDirectory(index) {
        // Mark as collapsed
        fileModel.setProperty(index, "expanded", false)
        
        // Collect all indices to remove (all descendants)
        var level = fileModel.get(index).level
        var indicesToRemove = []
        
        for (var i = index + 1; i < fileModel.count; i++) {
            var item = fileModel.get(i)
            if (item.level > level) {
                // This is a descendant (child or deeper)
                indicesToRemove.push(i)
            } else {
                // We've reached a sibling or parent (same or lower level), stop
                break
            }
        }
        
        // Remove in reverse order to avoid index shifting issues
        for (var j = indicesToRemove.length - 1; j >= 0; j--) {
            fileModel.remove(indicesToRemove[j])
        }
    }
    
    function formatSize(bytes) {
        if (bytes === 0) return "0 B"
        if (bytes < 1024) return bytes + " B"
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB"
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB"
        return (bytes / (1024 * 1024 * 1024)).toFixed(1) + " GB"
    }
    
    Component.onCompleted: {
        loadDirectory("/")
    }
}
