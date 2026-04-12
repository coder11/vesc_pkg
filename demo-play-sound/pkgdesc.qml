import QtQuick 2.15

Item {
    property string pkgName: "Demo Play Sound"
    property string pkgDescriptionMd: "README.md"
    property string pkgLisp: ""
    property string pkgQml: "ui.qml"
    property bool pkgQmlIsFullscreen: false
    property string pkgOutput: "demo_play_sound.vescpkg"

    function isCompatible(fwRxParams) {
        return true
    }
}
