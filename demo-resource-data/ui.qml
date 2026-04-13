import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    anchors.fill: parent
    anchors.margins: 10

    readonly property string rccRoot: "qrc:/vesc_pkg/demo-res/"
    property var configData: null

    function loadTextFile(url) {
        var xhr = new XMLHttpRequest()
        xhr.open("GET", url, false)
        xhr.send()
        return xhr.responseText
    }

    Component.onCompleted: {
        stringsLabel.text = loadTextFile(rccRoot + "strings.txt")
        try {
            root.configData = JSON.parse(loadTextFile(rccRoot + "config.json"))
            jsonRepeater.model = root.configData.features
            paramRepeater.model = Object.keys(root.configData.parameters)
        } catch (e) {
            jsonErrorLabel.text = "JSON parse error: " + e
        }
    }

    Flickable {
        anchors.fill: parent
        contentWidth: width
        contentHeight: mainColumn.height
        clip: true
        ScrollBar.vertical: ScrollBar {}

        ColumnLayout {
            id: mainColumn
            width: parent.width
            spacing: 16

            // ── Header ──
            Image {
                Layout.alignment: Qt.AlignHCenter
                source: rccRoot + "logo_vesc.svg"
                sourceSize.width: 180
                sourceSize.height: 60
                fillMode: Image.PreserveAspectFit
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: "Resource Data Demo"
                font.bold: true
                font.pointSize: 18
                color: "white"
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.Wrap
                text: "All assets below are loaded from a compiled .rcc embedded in this package."
                font.pointSize: 11
                color: "#aaa"
            }

            // ── Section: SVG Icons ──
            SectionHeader { title: "SVG Icons" }

            RowLayout {
                Layout.fillWidth: true
                spacing: 16
                Layout.alignment: Qt.AlignHCenter

                Repeater {
                    model: [
                        { src: "icon_battery.svg",  label: "Battery" },
                        { src: "icon_motor.svg",    label: "Motor" },
                        { src: "icon_settings.svg", label: "Settings" },
                        { src: "icon_warning.svg",  label: "Warning" }
                    ]

                    delegate: ColumnLayout {
                        spacing: 4
                        Image {
                            Layout.alignment: Qt.AlignHCenter
                            source: rccRoot + modelData.src
                            sourceSize.width: 48
                            sourceSize.height: 48
                        }
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: modelData.label
                            font.pointSize: 10
                            color: "#ccc"
                        }
                    }
                }
            }

            // ── Section: Raster Image ──
            SectionHeader { title: "PNG Image" }

            Image {
                Layout.alignment: Qt.AlignHCenter
                source: rccRoot + "sample_image.png"
                sourceSize.width: 128
                sourceSize.height: 128
                fillMode: Image.PreserveAspectFit

                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -2
                    color: "transparent"
                    border.color: "#555"
                    border.width: 1
                    radius: 4
                    z: -1
                }
            }

            Text {
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignHCenter
                text: "64 × 64 gradient (embedded PNG)"
                font.pointSize: 10
                color: "#aaa"
            }

            // ── Section: Text File ──
            SectionHeader { title: "Text File (strings.txt)" }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: stringsLabel.implicitHeight + 20
                color: "#1a1a2e"
                radius: 6

                Text {
                    id: stringsLabel
                    anchors.fill: parent
                    anchors.margins: 10
                    wrapMode: Text.Wrap
                    text: "Loading…"
                    font.pointSize: 12
                    font.family: "monospace"
                    color: "#e0e0e0"
                }
            }

            // ── Section: JSON Data ──
            SectionHeader { title: "JSON Data (config.json)" }

            Text {
                visible: jsonErrorLabel.text.length > 0
                id: jsonErrorLabel
                text: ""
                color: "#F44336"
                font.pointSize: 11
            }

            Text {
                Layout.fillWidth: true
                text: "Features:"
                font.bold: true
                font.pointSize: 12
                color: "#ccc"
            }

            Repeater {
                id: jsonRepeater
                model: []

                delegate: Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: featureCol.implicitHeight + 12
                    color: index % 2 === 0 ? "#1e1e3a" : "#22223e"
                    radius: 4

                    ColumnLayout {
                        id: featureCol
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.margins: 8
                        spacing: 2

                        Text {
                            text: modelData.name
                            font.bold: true
                            font.pointSize: 11
                            color: "#e94560"
                        }
                        Text {
                            Layout.fillWidth: true
                            text: modelData.description
                            font.pointSize: 10
                            color: "#bbb"
                            wrapMode: Text.Wrap
                        }
                    }
                }
            }

            Text {
                Layout.fillWidth: true
                Layout.topMargin: 8
                text: "Parameters:"
                font.bold: true
                font.pointSize: 12
                color: "#ccc"
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                columnSpacing: 12
                rowSpacing: 4

                Repeater {
                    id: paramRepeater
                    model: []

                    delegate: RowLayout {
                        Layout.columnSpan: 1
                        spacing: 6

                        Text {
                            text: modelData + ":"
                            font.pointSize: 11
                            color: "#888"
                        }
                        Text {
                            text: root.configData ? JSON.stringify(root.configData.parameters[modelData]) : ""
                            font.pointSize: 11
                            font.bold: true
                            color: "#4fc3f7"
                        }
                    }
                }
            }

            // ── Section: Resource paths ──
            SectionHeader { title: "Resource Paths" }

            Text {
                Layout.fillWidth: true
                wrapMode: Text.Wrap
                text: "Mount point: <b>qrc:/vesc_pkg/</b><br/>" +
                      "Icon example: <b>" + rccRoot + "icon_battery.svg</b><br/>" +
                      "Text example: <b>" + rccRoot + "strings.txt</b><br/>" +
                      "JSON example: <b>" + rccRoot + "config.json</b>"
                font.pointSize: 10
                color: "#999"
                textFormat: Text.RichText
            }

            Item { Layout.preferredHeight: 20 }
        }
    }

    component SectionHeader: ColumnLayout {
        property string title
        Layout.fillWidth: true
        Layout.topMargin: 4
        spacing: 2

        Text {
            text: title
            font.bold: true
            font.pointSize: 14
            color: "#e94560"
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: "#444"
        }
    }
}
