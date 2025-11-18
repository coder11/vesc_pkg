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
            downloadProgressDialog.filePath = filePath;
            downloadProgressDialog.saveUrl = fUrl;
            downloadProgressDialog.fileData = null;
            downloadProgressDialog.downloadComplete = false;
            downloadProgressDialog.cancelled = false;
            downloadProgressDialog.progressText = "Preparing download...";
            downloadProgressDialog.open();
            
            // Start the download in a Timer to allow the dialog to render and progress signals to be processed
            downloadStartTimer.filePath = filePath;
            downloadStartTimer.start();
        }
    }
    
    Timer {
        id: downloadStartTimer
        interval: 100
        repeat: false
        property string filePath: ""
        
        onTriggered: {
            // Reset cancellation flag
            downloadProgressDialog.cancelled = false;
            downloadProgressDialog.progressText = "Grabbing bytes...";
            
            // Start the download
            try {
                // Check if cancelled before starting
                if (downloadProgressDialog.cancelled) {
                    return;
                }
                
                console.log("Attempting to read file:", filePath);
                var data = mCommands.fileBlockRead(filePath);
                
                // Check if cancelled after read
                if (downloadProgressDialog.cancelled) {
                    return;
                }
                
                console.log("File read result - data type:", typeof data, "is ArrayBuffer:", data instanceof ArrayBuffer);
                
                // Handle different data types
                var dataLength = 0;
                if (data instanceof ArrayBuffer) {
                    dataLength = data.byteLength;
                    console.log("ArrayBuffer length:", dataLength);
                } else if (data && typeof data.length !== 'undefined') {
                    dataLength = data.length;
                    console.log("Data length:", dataLength);
                } else if (data) {
                    // Try to get byteLength if it's a QByteArray-like object
                    try {
                        dataLength = data.byteLength || 0;
                        console.log("ByteLength:", dataLength);
                    } catch (e) {
                        console.log("Could not determine data length");
                    }
                }
                
                if (downloadProgressDialog.cancelled) {
                    return;
                }
                
                if (data && dataLength > 0) {
                    downloadProgressDialog.fileData = data;
                    downloadProgressDialog.downloadComplete = true;
                    downloadProgressDialog.progressText = "Download complete, saving...";
                    // Use a small delay before saving to ensure progress is shown
                    Qt.callLater(function() {
                        if (!downloadProgressDialog.cancelled) {
                            downloadProgressDialog.saveFile();
                        }
                    });
                } else {
                    if (!downloadProgressDialog.cancelled) {
                        downloadProgressDialog.close();
                        var errorMsg = "Failed to read file from device";
                        if (!data) {
                            errorMsg += " (null data)";
                        } else if (dataLength === 0) {
                            errorMsg += " (empty data, length: 0)";
                        } else {
                            errorMsg += " (unknown data format)";
                        }
                        VescIf.emitStatusMessage(errorMsg, false);
                    }
                }
            } catch (e) {
                if (!downloadProgressDialog.cancelled) {
                    console.log("File read exception:", e.toString());
                    downloadProgressDialog.close();
                    VescIf.emitStatusMessage("Download error: %1".arg(e.toString()), false);
                }
            }
        }
    }
    
    Dialog {
        id: downloadProgressDialog
        title: "Downloading File..."
        closePolicy: Popup.NoAutoClose
        modal: true
        focus: true
        width: parent.width - 20
        x: 10
        y: parent.height / 2 - height / 2
        parent: container
        standardButtons: Dialog.Cancel
        
        property string filePath: ""
        property string saveUrl: ""
        property var fileData: null
        property bool downloadComplete: false
        property bool cancelled: false
        property string progressText: "Downloading..."
        
        onRejected: {
            // User clicked Cancel
            cancelled = true;
            close();
            VescIf.emitStatusMessage("Download cancelled", false);
        }
        
        function saveFile() {
            if (cancelled) {
                return;
            }
            
            if (!fileData || fileData.length === 0) {
                close();
                VescIf.emitStatusMessage("No data to save", false);
                return;
            }
            
            try {
                // Convert ArrayBuffer to string if needed, or use as-is
                var dataToSend = fileData;
                if (fileData instanceof ArrayBuffer) {
                    // Convert ArrayBuffer to binary string for XMLHttpRequest
                    var uint8Array = new Uint8Array(fileData);
                    var binaryString = "";
                    var chunkSize = 8192; // Process in chunks to avoid blocking
                    for (var i = 0; i < uint8Array.length; i += chunkSize) {
                        var chunk = uint8Array.subarray(i, Math.min(i + chunkSize, uint8Array.length));
                        for (var j = 0; j < chunk.length; j++) {
                            binaryString += String.fromCharCode(chunk[j]);
                        }
                    }
                    dataToSend = binaryString;
                } else if (fileData && typeof fileData.byteLength !== 'undefined') {
                    // Handle QByteArray-like objects
                    try {
                        var uint8Array = new Uint8Array(fileData.byteLength);
                        for (var i = 0; i < fileData.byteLength; i++) {
                            uint8Array[i] = fileData[i] || 0;
                        }
                        var binaryString = "";
                        for (var i = 0; i < uint8Array.length; i++) {
                            binaryString += String.fromCharCode(uint8Array[i]);
                        }
                        dataToSend = binaryString;
                    } catch (e) {
                        console.log("Error converting data:", e.toString());
                        // Try sending as-is
                    }
                }
                
                var request = new XMLHttpRequest();
                request.open("PUT", saveUrl, false);
                request.send(dataToSend);
                
                close();
                
                if (request.status === 0 || request.status === 200) {
                    VescIf.emitStatusMessage("File downloaded successfully", true);
                } else {
                    VescIf.emitStatusMessage("Download failed: Status %1".arg(request.status), false);
                }
            } catch (e) {
                close();
                VescIf.emitStatusMessage("Download failed: %1".arg(e.toString()), false);
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 15
            
            Text {
                id: progressTextDisplay
                Layout.fillWidth: true
                color: Utility.getAppHexColor("lightText")
                horizontalAlignment: Text.AlignHCenter
                text: downloadProgressDialog.progressText
            }
            
            ProgressBar {
                id: progressBar
                Layout.fillWidth: true
                indeterminate: true
            }
        }
        
        Component.onCompleted: {
            standardButton(Dialog.Cancel).text = "Cancel"
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
        
        // Extract filename from path and set it as default
        var pathParts = path.split("/");
        var fileName = pathParts[pathParts.length - 1];
        saveFileDialog.file = "file:///" + fileName;
        
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
