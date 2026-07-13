import QtQuick 2.12

QtObject {
    function getAppHexColor(name) {
        if (name === "darkBackground") {
            return "#ffffff"
        }
        if (name === "lightText") {
            return "#111111"
        }
        return "#666666"
    }
}
