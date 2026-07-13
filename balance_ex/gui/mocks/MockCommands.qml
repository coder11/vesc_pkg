import QtQuick 2.12

QtObject {
    signal valuesReceived(var values)
    signal customAppDataReceived(var data)

    property real phase: 0.0

    function getValues() {
        phase += 0.08
        valuesReceived({
            duty_now: 0.35 + Math.sin(phase) * 0.1,
            temp_mos: 42.0 + Math.sin(phase) * 2.0,
            temp_motor: 38.0 + Math.sin(phase * 0.7) * 2.0
        })
    }

    function sendCustomAppData(request) {
        if (!request || request.byteLength < 1 || new DataView(request).getUint8(0) !== 0x01) {
            return
        }

        var response = new ArrayBuffer(58)
        var data = new DataView(response)
        var offset = 0

        function putFloat(value) {
            data.setFloat32(offset, value)
            offset += 4
        }

        function putInt16(value) {
            data.setInt16(offset, value)
            offset += 2
        }

        putFloat(Math.sin(phase) * 0.2)       // PID value
        putFloat(Math.sin(phase) * 4.0)       // Pitch
        putFloat(Math.cos(phase * 0.6) * 2.0) // Roll
        putFloat(0.1)                         // Time difference
        putFloat(24.0 + Math.sin(phase) * 8.0)// Motor current
        putInt16(2)                           // Running
        putFloat(0.0)                         // Setpoint
        putFloat(0.35)                        // Motor load
        putFloat(0.04)                        // Motor acceleration load
        putInt16(0)                           // Kill switch
        putInt16(0)                           // Tiltback type
        putFloat(2200.0 + Math.sin(phase) * 500.0)
        putFloat(24.0 + Math.sin(phase) * 5.0)
        putFloat(78.0 + Math.sin(phase * 0.2))
        putFloat(60.0)
        putFloat(84.0)

        customAppDataReceived(response)
    }

    function lispSendReplCmd(command) {
        console.log("Mock Lisp command:", command)
    }
}
