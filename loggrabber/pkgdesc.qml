import QtQuick 2.15

Item {
    property string pkgName: "LogGrabber"
    property string pkgDescriptionMd: "README.md"
    property string pkgQml: "ui.qml"
    property bool pkgQmlIsFullscreen: false
    property string pkgOutput: "loggrabber.vescpkg"

    // This function should return true when this package is compatible
    // with the connected vesc-based device
    function isCompatible (fwRxParams) {
        var hwName = fwRxParams.hw.toLowerCase();
        var fwName = fwRxParams.fwName.toLowerCase();

        // vesc, vesc bms or custom module
        // Note that VBMS32 is a custom module
        var hwType = fwRxParams.hwTypeStr().toLowerCase();		

        //console.log("HW Name: " + hwName)
        //console.log("FW Name: " + fwName)
        //console.log("HW Type: " + hwType)

        // The classic VESC BMS does not support packages at all
        if (hwType == "vesc bms") {
            return false
        }
        
        // Prevent installing on VBMS
        if (hwName == "vbms16" || hwName == "vbms32") {
            return false
        }
		
		// This package works on VESC Express only
        if (!hwName.includes("express")) {
            return false
        }
        
        return true
    }
}
