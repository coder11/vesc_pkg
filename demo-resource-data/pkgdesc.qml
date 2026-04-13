import QtQuick 2.15

Item {
    property string pkgName: "Demo Resource Data"
    property string pkgDescriptionMd: "README.md"
    property string pkgLisp: ""
    property string pkgQml: "ui.qml"
    property string pkgRcc: "resources.rcc"
    property bool pkgQmlIsFullscreen: false
    property string pkgOutput: "demo_resource_data.vescpkg"

    function isCompatible(fwRxParams) {
        return true
    }
}
