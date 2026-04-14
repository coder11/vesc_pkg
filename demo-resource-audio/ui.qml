import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 5.15

Item {
    id: root
    anchors.fill: parent
    anchors.margins: 10

    readonly property string rccRoot: "qrc:/vesc_pkg/audio-res/"
    property int currentTrack: -1

    ListModel {
        id: trackModel
        ListElement { name: "Beep";    file: "beep.wav";    fmt: "WAV";  desc: "440 Hz · 0.3 s" }
        ListElement { name: "Alert";   file: "alert.ogg";   fmt: "OGG";  desc: "880→660 Hz · 0.3 s" }
        ListElement { name: "Chime";   file: "chime.flac";  fmt: "FLAC"; desc: "C5-E5-G5 arpeggio · 0.6 s" }
        ListElement { name: "Warning"; file: "warning.wav"; fmt: "WAV";  desc: "220 Hz × 2 pulses · 0.5 s" }
        ListElement { name: "Click";   file: "click.ogg";   fmt: "OGG";  desc: "1 kHz burst · 50 ms" }
    }

    MediaPlayer {
        id: player
        volume: volumeSlider.value

        onStatusChanged: {
            var names = ["NoMedia","Loading","Loaded","Buffering",
                         "Stalled","Buffered","EndOfMedia","InvalidMedia"]
            log("status → " + (names[status] || status))
        }
        onPlaybackStateChanged: {
            var names = ["Stopped","Playing","Paused"]
            log("state  → " + (names[playbackState] || playbackState))
        }
        onError: log("ERROR " + error + ": " + errorString)
        onPositionChanged: {
            if (!posSlider.pressed)
                posSlider.value = duration > 0 ? position / duration : 0
        }
    }

    function playTrack(index) {
        currentTrack = index
        var entry = trackModel.get(index)
        player.source = rccRoot + entry.file
        log("play: " + entry.name + " (" + entry.file + ")")
        player.play()
    }

    function log(msg) {
        console.log("[demo-resource-audio] " + msg)
        var ts = Qt.formatDateTime(new Date(), "hh:mm:ss.zzz")
        logModel.append({ "line": ts + " " + msg })
        while (logModel.count > 200)
            logModel.remove(0)
        Qt.callLater(function () {
            if (logList.count > 0)
                logList.positionViewAtEnd()
        })
    }

    ListModel { id: logModel }

    Component.onCompleted: {
        try {
            Qt.createQmlObject(
                'import QtQuick 2.15; import QtMultimedia 5.15; Item {}',
                root, "probe")
            log("QtMultimedia 5.15 available")
        } catch (e) {
            log("QtMultimedia NOT available: " + e)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Text {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            text: "Resource Audio Demo"
            font.bold: true
            font.pointSize: 18
            color: "white"
        }

        Text {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
            text: "Audio files embedded in the .rcc resource bundle"
            font.pointSize: 11
            color: "#aaa"
        }

        SectionHeader { title: "Tracks" }

        ListView {
            id: trackList
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(contentHeight, 220)
            clip: true
            model: trackModel
            spacing: 4
            ScrollBar.vertical: ScrollBar {}

            delegate: Rectangle {
                width: trackList.width
                height: trackRow.implicitHeight + 16
                radius: 6
                color: root.currentTrack === index ? "#2a2a5e" : (index % 2 === 0 ? "#1e1e3a" : "#22223e")
                border.color: root.currentTrack === index ? "#e94560" : "transparent"
                border.width: root.currentTrack === index ? 1 : 0

                RowLayout {
                    id: trackRow
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 10

                    Text {
                        text: (index + 1)
                        font.pointSize: 12
                        font.bold: true
                        color: "#e94560"
                        Layout.preferredWidth: 20
                        horizontalAlignment: Text.AlignRight
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        RowLayout {
                            spacing: 6
                            Text {
                                text: model.name
                                font.pointSize: 13
                                font.bold: true
                                color: "#e0e0e0"
                            }
                            Rectangle {
                                implicitWidth: fmtLabel.implicitWidth + 8
                                implicitHeight: fmtLabel.implicitHeight + 4
                                radius: 3
                                color: model.fmt === "WAV" ? "#2e7d32"
                                     : model.fmt === "OGG" ? "#1565c0"
                                     : "#6a1b9a"
                                Text {
                                    id: fmtLabel
                                    anchors.centerIn: parent
                                    text: model.fmt
                                    font.pointSize: 8
                                    font.bold: true
                                    color: "white"
                                }
                            }
                        }
                        Text {
                            text: model.desc
                            font.pointSize: 10
                            color: "#888"
                        }
                    }

                    Button {
                        text: (root.currentTrack === index
                               && player.playbackState === MediaPlayer.PlayingState)
                              ? "⏹" : "▶"
                        font.pointSize: 14
                        implicitWidth: 44
                        implicitHeight: 36
                        onClicked: {
                            if (root.currentTrack === index
                                && player.playbackState === MediaPlayer.PlayingState) {
                                player.stop()
                            } else {
                                root.playTrack(index)
                            }
                        }
                    }
                }
            }
        }

        SectionHeader { title: "Transport" }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Button {
                text: "⏮"
                font.pointSize: 14
                implicitWidth: 44
                onClicked: {
                    if (root.currentTrack > 0)
                        root.playTrack(root.currentTrack - 1)
                }
            }

            Button {
                text: player.playbackState === MediaPlayer.PlayingState ? "⏸" : "▶"
                font.pointSize: 14
                implicitWidth: 44
                onClicked: {
                    if (player.playbackState === MediaPlayer.PlayingState) {
                        player.pause()
                    } else if (root.currentTrack >= 0) {
                        player.play()
                    } else {
                        root.playTrack(0)
                    }
                }
            }

            Button {
                text: "⏹"
                font.pointSize: 14
                implicitWidth: 44
                onClicked: player.stop()
            }

            Button {
                text: "⏭"
                font.pointSize: 14
                implicitWidth: 44
                onClicked: {
                    if (root.currentTrack < trackModel.count - 1)
                        root.playTrack(root.currentTrack + 1)
                }
            }

            Text {
                id: posLabel
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignRight
                font.pointSize: 11
                font.family: "monospace"
                color: "#ccc"
                text: {
                    if (player.duration <= 0) return "— / —"
                    var p = (player.position / 1000).toFixed(1)
                    var d = (player.duration / 1000).toFixed(1)
                    return p + " / " + d + " s"
                }
            }
        }

        Slider {
            id: posSlider
            Layout.fillWidth: true
            from: 0; to: 1; value: 0
            onPressedChanged: {
                if (!pressed && player.duration > 0)
                    player.seek(value * player.duration)
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Volume"
                font.pointSize: 11
                color: "#aaa"
            }

            Slider {
                id: volumeSlider
                Layout.fillWidth: true
                from: 0; to: 1; value: 1
            }

            Text {
                text: (volumeSlider.value * 100).toFixed(0) + "%"
                font.pointSize: 11
                font.family: "monospace"
                color: "#ccc"
                Layout.preferredWidth: 40
            }
        }

        SectionHeader { title: "Log" }

        RowLayout {
            Layout.fillWidth: true

            Item { Layout.fillWidth: true }
            Button {
                text: "Clear"
                onClicked: logModel.clear()
            }
        }

        ListView {
            id: logList
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 80
            clip: true
            model: logModel
            spacing: 2
            ScrollBar.vertical: ScrollBar {}

            delegate: Text {
                width: logList.width
                wrapMode: Text.Wrap
                text: line
                font.pointSize: 10
                font.family: "monospace"
                color: "#bbb"
            }
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
