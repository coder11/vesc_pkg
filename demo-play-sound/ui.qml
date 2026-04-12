import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtMultimedia 5.15

Item {
    id: root
    anchors.fill: parent
    anchors.margins: 10

    readonly property int logMaxLines: 500

    ListModel {
        id: logModel
    }

    function log(msg) {
        console.log("[demo-play-sound] " + msg)
        var ts = Qt.formatDateTime(new Date(), "hh:mm:ss.zzz")
        logModel.append({ "line": ts + " " + msg })
        while (logModel.count > logMaxLines) {
            logModel.remove(0)
        }
        Qt.callLater(function () {
            if (logList.count > 0) {
                logList.positionViewAtEnd()
            }
        })
    }

    MediaPlayer {
        id: player
        source: urlField.text

        onStatusChanged: {
            var names = ["NoMedia","Loading","Loaded","Buffering","Stalled","Buffered","EndOfMedia","InvalidMedia"]
            root.log("status → " + (names[status] || status))
        }
        onPlaybackStateChanged: {
            var names = ["Stopped","Playing","Paused"]
            root.log("state  → " + (names[playbackState] || playbackState))
        }
        onError: root.log("ERROR " + error + ": " + errorString)
        onPositionChanged: {
            if (player.playbackState === MediaPlayer.PlayingState)
                posLabel.text = (position / 1000).toFixed(1) + " / " + (duration / 1000).toFixed(1) + " s"
        }
    }

    Component.onCompleted: {
        try {
            Qt.createQmlObject(`
                import QtQuick 2.15
                import QtMultimedia 5.15
                Item {}
            `, this, "probe")
            root.log("QtMultimedia 5.15 is importable")
        } catch (e) {
            root.log("QtMultimedia 5.15 is NOT importable: " + e)
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        Text {
            Layout.fillWidth: true
            horizontalAlignment: Text.AlignHCenter
            text: "Audio Playback Test"
            font.bold: true
            font.pointSize: 16
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Label { text: "URL:" }

            TextField {
                id: urlField
                Layout.fillWidth: true
                placeholderText: "file:///sdcard/Music/test.mp3  or  https://…"
                selectByMouse: true
                text: "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 6

            Button {
                text: "▶ Play"
                onClicked: {
                    root.log("play() source=" + player.source)
                    player.play()
                }
            }
            Button {
                text: "⏸ Pause"
                onClicked: { root.log("pause()"); player.pause() }
            }
            Button {
                text: "⏹ Stop"
                onClicked: { root.log("stop()"); player.stop() }
            }

            Label {
                id: posLabel
                text: "— / —"
                font.family: "monospace"
            }
        }

        Slider {
            id: volumeSlider
            Layout.fillWidth: true
            from: 0; to: 1; value: 1
            onValueChanged: {
                player.volume = value
                root.log("volume=" + value.toFixed(2))
            }

            Label {
                anchors.left: parent.left
                anchors.bottom: parent.top
                text: "Volume: " + (volumeSlider.value * 100).toFixed(0) + "%"
                font.pointSize: 10
            }
        }

        RowLayout {
            Layout.fillWidth: true

            Label { text: "Debug log" }
            Item { Layout.fillWidth: true }
            Button {
                text: "Clear log"
                onClicked: logModel.clear()
            }
        }

        ListView {
            id: logList
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.minimumHeight: 140
            clip: true
            model: logModel
            spacing: 2
            ScrollBar.vertical: ScrollBar {}

            delegate: Text {
                width: logList.width
                wrapMode: Text.Wrap
                text: line
                font.pointSize: 12
                font.family: "monospace"
                color: "white"
            }
        }
    }
}
