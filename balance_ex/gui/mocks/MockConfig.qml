import QtQuick 2.12

QtObject {
    function getParamDouble(name) {
        if (name === "l_current_max") {
            return 100.0
        }
        return 0.0
    }
}
