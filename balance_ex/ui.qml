/*
    Copyright 2022 Benjamin Vedder	benjamin@vedder.se

    This file is part of VESC Tool.

    VESC Tool is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    VESC Tool is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    */

import QtQuick 2.12
import QtQuick.Controls 2.12
import QtQuick.Layouts 1.3
import Vedder.vesc.utility 1.0

import Vedder.vesc.commands 1.0
import Vedder.vesc.configparams 1.0

// This example shows how to read and write settings using the custom
// config. It is also possible to send and receive custom data using
// send_app_data and set_app_data_handler on the euc-side and Commands
// onCustomAppDataReceived and mCommands.sendCustomAppData in qml.

Item {
    id: mainItem
    anchors.fill: parent
    anchors.margins: 5

    property Commands mCommands: VescIf.commands()
    property ConfigParams mMcConf: VescIf.mcConfig()
    property ConfigParams mCustomConf: VescIf.customConfig(0)
    
    readonly property int balanceCommandGetRealtimeData: 0x01
    readonly property int balanceCommandTriggerKillspin: 0x02
    
    // Gauge values
    property real dutyCycle: 0.0
    property real motorCurrent: 0.0
    property real batteryVoltage: 84.0
    property real speedKmh: 0.0
    property real maxMotorCurrent: mMcConf ? mMcConf.getParamDouble("l_current_max") : 100.0
    property real tempFet: 0.0
    property real tempMotor: 0.0

    // Gauge color utility: below safety margin = green,
    // above margin transitions green -> yellow -> red linearly
    // Uses darker tones to ensure white text remains readable
    function gaugeColor(percentage, safetyMargin) {
        if (percentage <= safetyMargin) {
            return Qt.rgba(0.0, 0.45, 0.0, 1.0) // Dark green
        }

        var t = (percentage - safetyMargin) / (100.0 - safetyMargin)
        if (t < 0) {
            t = 0
        } else if (t > 1) {
            t = 1
        }

        if (t <= 0.5) {
            // Green -> Yellow (darker tones)
            var k1 = t / 0.5
            // Transition from dark green (0, 0.45, 0) to dark yellow (0.5, 0.45, 0)
            return Qt.rgba(k1 * 0.5, 0.45, 0.0, 1.0)
        } else {
            // Yellow -> Red (darker tones)
            var k2 = (t - 0.5) / 0.5
            // Transition from dark yellow (0.5, 0.45, 0) to dark red (0.5, 0, 0)
            return Qt.rgba(0.5, 0.45 * (1.0 - k2), 0.0, 1.0)
        }
    }

    Component.onCompleted: {
        // Request VESC values periodically
        requestVescValues()
    }
    
    function requestVescValues() {
        if (mCommands) {
            mCommands.getValues()
        }
    }
    
    Timer {
        running: true
        repeat: true
        interval: 100
        
        onTriggered: {
            var buffer = new ArrayBuffer(1)
            var dv = new DataView(buffer)
            dv.setUint8(0, balanceCommandGetRealtimeData)
            mCommands.sendCustomAppData(buffer)
        }
    }
    
    // Request VESC values periodically for gauges
    Timer {
        running: true
        repeat: true
        interval: 200
        
        onTriggered: {
            requestVescValues()
        }
    }
    
    Connections {
        target: mCommands
        
        // Get VESC realtime values (duty cycle, temperature)
        onValuesReceived: {
            if (values) {
                dutyCycle = Math.abs(values.duty_now) * 100.0
                // Note: batteryVoltage and speedKmh are now updated from ui_data
                // in onCustomAppDataReceived
                if (typeof values.temp_mos !== "undefined") {
                    tempFet = values.temp_mos
                }
                if (typeof values.temp_motor !== "undefined") {
                    tempMotor = values.temp_motor
                }
            }
        }
        
        // This function will be called when VESC_IF->send_app_data is used. To
        // send data back mCommands.sendCustomAppData can be used. That data
        // will be received in the function registered with VESC_IF->set_app_data_handler
        onCustomAppDataReceived: {
            // Ints and floats can be extracted like this from the data
            var dv = new DataView(data, 0)
            var ind = 0
            var pid_value = dv.getFloat32(ind); ind += 4;
            var pitch = dv.getFloat32(ind); ind += 4;
            var roll = dv.getFloat32(ind); ind += 4;
            var time_diff = dv.getFloat32(ind); ind += 4;
            var motor_current = dv.getFloat32(ind); ind += 4;
            var state = dv.getInt16(ind); ind += 2;
            var setpoint = dv.getFloat32(ind); ind += 4;
            var motor_load = dv.getFloat32(ind); ind += 4;
            var motor_accel_load = dv.getFloat32(ind); ind += 4;
            var killSwitchTriggered = dv.getInt16(ind); ind += 2;
            var tiltback_type = dv.getInt16(ind); ind += 2;
            // UI data values
            var rpm = dv.getFloat32(ind); ind += 4;
            var speed_kmh = dv.getFloat32(ind); ind += 4;
            var voltage = dv.getFloat32(ind); ind += 4;
            var voltage_min = dv.getFloat32(ind); ind += 4;
            var voltage_max = dv.getFloat32(ind); ind += 4;
            var accel = dv.getFloat32(ind); ind += 4;
            var accel2 = dv.getFloat32(ind); ind += 4;
            
            // Update motor current for gauge
            motorCurrent = Math.abs(motor_current)
            
            // Update speed from ui_data
            speedKmh = speed_kmh
            
            // Update voltage gauge with ui_data values
            if (voltage_min > 0 && voltage_max > 0) {
                voltageGauge.minVoltage = voltage_min
                voltageGauge.maxVoltage = voltage_max
            }
            batteryVoltage = voltage
            
            var stateString
            if (state == 0) {
                stateString = "STARTUP"
            } else if (state == 1) {
                stateString = "CENTERING"
            } else if (state == 2) {
                stateString = "RUNNING"
            } else if (state == 3) {
                stateString = "FAULT_ANGLE_PITCH"
            } else if (state == 4) {
                stateString = "FAULT_ANGLE_ROLL"
            } else if (state == 5) {
                stateString = "FAULT_DUTY"
            } else if (state == 6) {
                stateString = "READY"
            } else if (state == 7) {
                stateString = "KILLSPIN"
            } else {
                stateString = "UNKNOWN"
            }
            
            var killSwitchTriggeredString
            if(killSwitchTriggered == 0){
                killSwitchTriggeredString = "No"
            }else{
                killSwitchTriggeredString = "Yes"
            }
            
            var tiltbackString
            if (tiltback_type == 0) {
                tiltbackString = "None"
            } else if (tiltback_type == 1) {
                tiltbackString = "Duty"
            } else if (tiltback_type == 2) {
                tiltbackString = "High Voltage"
            } else if (tiltback_type == 3) {
                tiltbackString = "Low Voltage"
            } else if (tiltback_type == 4) {
                tiltbackString = "Backing Off"
            } else {
                tiltbackString = "Unknown"
            }
            
            valText1.text =
                "rpm: " + rpm.toFixed(1) + "\n" +
                "speed: " + speed_kmh.toFixed(1) + "kmh\n" +
                
                "setpt: " + setpoint.toFixed(2) + "°\n" +
                "pitch  : " + pitch.toFixed(2) + "°\n" +
                "setp-pitch :" + (setpoint-pitch).toFixed(2) + "\n" +
                "roll   : " + roll.toFixed(2) + "°\n" +
                "Motor Load : " + motor_load.toFixed(5) + "\n" +
                "Motor Accel Load : " + motor_accel_load.toFixed(5) + "\n" +
                "accel: " + accel.toFixed(5) + "\n" +
                "accel2: " + accel2.toFixed(5) + "\n" +
                "state  : " + stateString + "\n" +
                "tiltback: " + tiltbackString + "\n" +
                "kill spin triggered: " + killSwitchTriggeredString;
        }
    }

    ColumnLayout {
        id: mainColumn
        anchors.fill: parent
        
        StackLayout {
            id: stackLayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            // Tab 1 - EUC RT data with gauges
            ColumnLayout {
                id: rtDataColumn
                anchors.fill: parent
                spacing: 10
                
                // Speed and temperature header above gauges
                RowLayout {
                    id: headerRow
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    Layout.topMargin: 20
                    Layout.bottomMargin: 10
                    spacing: 10

                    // FET temperature
                    ColumnLayout {
                        Layout.fillWidth: true

                        Text {
                            id: fetValueText
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 28
                            font.weight: Font.Black
                            text: tempFet.toFixed(1)
                        }

                        Text {
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 16
                            font.weight: Font.Black
                            text: "fet °C"
                        }
                    }

                    // Speed
                    ColumnLayout {
                        Layout.fillWidth: true

                        Text {
                            id: speedValueText
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 35
                            font.weight: Font.Black
                            text: speedKmh.toFixed(1)
                        }

                        Text {
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 16
                            font.weight: Font.Black
                            text: "kmh"
                        }
                    }

                    // Motor temperature
                    ColumnLayout {
                        Layout.fillWidth: true

                        Text {
                            id: motValueText
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 28
                            font.weight: Font.Black
                            text: tempMotor.toFixed(1)
                        }

                        Text {
                            Layout.fillWidth: true
                            horizontalAlignment: Text.AlignHCenter
                            color: Utility.getAppHexColor("lightText")
                            font.pixelSize: 16
                            font.weight: Font.Black
                            text: "mot °C"
                        }
                    }
                }
                
                // Gauges row
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    spacing: 20
                    
                    // Duty Cycle Gauge
                    Rectangle {
                        id: dutyGauge
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Utility.getAppHexColor("darkBackground")

                        // Safety margin in percent (0-100)
                        property real safetyMargin: 50.0
                        property real value: Math.max(0, Math.min(100, dutyCycle))
                        property real minValue: 0.0
                        property real maxValue: 100.0
                        property real borderWidth: 2
                        property real labelPadding: 4
                        
                        // Left border
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Right border
                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.right: maxValueLabelBg.left
                            height: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - right segment
                        Rectangle {
                            anchors.left: maxValueLabelBg.right
                            anchors.top: parent.top
                            anchors.right: parent.right
                            height: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.right: minValueLabelBg.left
                            height: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - right segment
                        Rectangle {
                            anchors.left: minValueLabelBg.right
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            height: dutyGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Fill rectangle
                        Rectangle {
                            z: 0
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: parent.height * (dutyGauge.value / 100.0)
                            color: gaugeColor(dutyGauge.value, dutyGauge.safetyMargin)
                            
                            Behavior on height {
                                NumberAnimation {
                                    duration: 100
                                    easing.type: Easing.OutQuad
                                }
                            }
                        }
                        
                        // Max value label background (breaks top border)
                        Rectangle {
                            id: maxValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: -dutyGauge.borderWidth
                            width: maxValueLabelText.width + 4
                            height: maxValueLabelText.height + dutyGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Max value label at top border
                        Text {
                            id: maxValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.top
                            anchors.verticalCenterOffset: dutyGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: dutyGauge.maxValue.toFixed(0) + "%"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }
                        
                        // Min value label background (breaks bottom border)
                        Rectangle {
                            id: minValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: -dutyGauge.borderWidth
                            width: minValueLabelText.width + 4
                            height: minValueLabelText.height + dutyGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Min value label at bottom border
                        Text {
                            id: minValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.bottom
                            anchors.verticalCenterOffset: -dutyGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: dutyGauge.minValue.toFixed(0) + "%"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }

                        // Safety margin line (horizontal)
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: parent.height * (dutyGauge.safetyMargin / 100.0)
                            height: 2
                            color: Utility.getAppHexColor("lightText")
                            opacity: 0.7
                        }
                        
                        // Value text
                        Text {
                            id: dutyValueText
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            color: Utility.getAppHexColor("lightText")
                            text: dutyGauge.value.toFixed(1)
                            font.pixelSize: 30
                            font.weight: Font.Black
                        }

                        // Label just below the value, inside the gauge
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: dutyValueText.bottom
                            anchors.topMargin: 2
                            verticalAlignment: Text.AlignTop
                            color: Utility.getAppHexColor("lightText")
                            text: "Duty%"
                            font.pixelSize: 14
                            font.weight: Font.Black
                        }
                    }
                    
                    // Current Gauge
                    Rectangle {
                        id: currentGauge
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Utility.getAppHexColor("darkBackground")
                        
                        property real value: Math.max(0, Math.min(maxMotorCurrent, motorCurrent))
                        property real percentage: maxMotorCurrent > 0 ? (value / maxMotorCurrent) * 100.0 : 0
                        // Safety margin in percent (0-100)
                        property real safetyMargin: 50.0
                        property real minValue: 0.0
                        property real maxValue: maxMotorCurrent
                        property real borderWidth: 2
                        property real labelPadding: 4
                        
                        // Left border
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Right border
                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.right: currentMaxValueLabelBg.left
                            height: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - right segment
                        Rectangle {
                            anchors.left: currentMaxValueLabelBg.right
                            anchors.top: parent.top
                            anchors.right: parent.right
                            height: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.right: currentMinValueLabelBg.left
                            height: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - right segment
                        Rectangle {
                            anchors.left: currentMinValueLabelBg.right
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            height: currentGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Fill rectangle
                        Rectangle {
                            z: 0
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: parent.height * (currentGauge.percentage / 100.0)
                            color: gaugeColor(currentGauge.percentage, currentGauge.safetyMargin)
                            
                            Behavior on height {
                                NumberAnimation {
                                    duration: 100
                                    easing.type: Easing.OutQuad
                                }
                            }
                        }
                        
                        // Max value label background (breaks top border)
                        Rectangle {
                            id: currentMaxValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: -currentGauge.borderWidth
                            width: currentMaxValueLabelText.width + 4
                            height: currentMaxValueLabelText.height + currentGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Max value label at top border
                        Text {
                            id: currentMaxValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.top
                            anchors.verticalCenterOffset: currentGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: currentGauge.maxValue.toFixed(1) + "A"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }
                        
                        // Min value label background (breaks bottom border)
                        Rectangle {
                            id: currentMinValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: -currentGauge.borderWidth
                            width: currentMinValueLabelText.width + 4
                            height: currentMinValueLabelText.height + currentGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Min value label at bottom border
                        Text {
                            id: currentMinValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.bottom
                            anchors.verticalCenterOffset: -currentGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: currentGauge.minValue.toFixed(1) + "A"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }

                        // Safety margin line (horizontal)
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: parent.height * (currentGauge.safetyMargin / 100.0)
                            height: 2
                            color: Utility.getAppHexColor("lightText")
                            opacity: 0.7
                        }
                        
                        // Value text
                        Text {
                            id: currentValueText
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            color: Utility.getAppHexColor("lightText")
                            text: currentGauge.value.toFixed(1) + "A"
                            font.pixelSize: 30
                            font.weight: Font.Black
                        }

                        // Label just below the value, inside the gauge
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: currentValueText.bottom
                            anchors.topMargin: 2
                            verticalAlignment: Text.AlignTop
                            color: Utility.getAppHexColor("lightText")
                            text: "Phase\nCurrent"
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                            font.weight: Font.Black
                        }
                    }
                    
                    // Voltage Gauge
                    Rectangle {
                        id: voltageGauge
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Utility.getAppHexColor("darkBackground")
                        
                        property real minVoltage: 60.0
                        property real maxVoltage: 84.0
                        property real value: Math.max(minVoltage, Math.min(maxVoltage, batteryVoltage))
                        // Inverted: lower voltage = higher percentage (more headroom used)
                        property real percentage: ((maxVoltage - value) / (maxVoltage - minVoltage)) * 100.0
                        // Safety margin in percent (0-100)
                        property real safetyMargin: 50.0
                        property real minValue: minVoltage
                        property real maxValue: maxVoltage
                        property real borderWidth: 2
                        property real labelPadding: 4
                        
                        // Left border
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Right border
                        Rectangle {
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.bottom: parent.bottom
                            width: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.top: parent.top
                            anchors.right: voltageMaxValueLabelBg.left
                            height: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Top border - right segment
                        Rectangle {
                            anchors.left: voltageMaxValueLabelBg.right
                            anchors.top: parent.top
                            anchors.right: parent.right
                            height: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - left segment
                        Rectangle {
                            anchors.left: parent.left
                            anchors.bottom: parent.bottom
                            anchors.right: voltageMinValueLabelBg.left
                            height: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Bottom border - right segment
                        Rectangle {
                            anchors.left: voltageMinValueLabelBg.right
                            anchors.bottom: parent.bottom
                            anchors.right: parent.right
                            height: voltageGauge.borderWidth
                            color: Utility.getAppHexColor("lightText")
                        }
                        
                        // Fill rectangle
                        Rectangle {
                            z: 0
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right
                            height: parent.height * (voltageGauge.percentage / 100.0)
                            color: gaugeColor(voltageGauge.percentage, voltageGauge.safetyMargin)
                            
                            Behavior on height {
                                NumberAnimation {
                                    duration: 100
                                    easing.type: Easing.OutQuad
                                }
                            }
                        }
                        
                        // Max value label background (breaks top border)
                        Rectangle {
                            id: voltageMaxValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: -voltageGauge.borderWidth
                            width: voltageMaxValueLabelText.width + 4
                            height: voltageMaxValueLabelText.height + voltageGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Min value label at top border (low voltage = high position on gauge)
                        Text {
                            id: voltageMaxValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.top
                            anchors.verticalCenterOffset: voltageGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: voltageGauge.minValue.toFixed(1) + "V"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }
                        
                        // Max value label background (breaks bottom border)
                        Rectangle {
                            id: voltageMinValueLabelBg
                            z: 1
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: -voltageGauge.borderWidth
                            width: voltageMinValueLabelText.width + 4
                            height: voltageMinValueLabelText.height + voltageGauge.labelPadding * 2
                            color: "transparent"
                        }
                        
                        // Max value label at bottom border (high voltage = low position on gauge)
                        Text {
                            id: voltageMinValueLabelText
                            z: 2
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.verticalCenter: parent.bottom
                            anchors.verticalCenterOffset: -voltageGauge.borderWidth / 2
                            color: Utility.getAppHexColor("lightText")
                            text: voltageGauge.maxValue.toFixed(1) + "V"
                            font.pixelSize: 16
                            font.weight: Font.Normal
                        }

                        // Safety margin line (horizontal)
                        Rectangle {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: parent.height * (voltageGauge.safetyMargin / 100.0)
                            height: 2
                            color: Utility.getAppHexColor("lightText")
                            opacity: 0.7
                        }
                        
                        // Value text
                        Text {
                            id: voltageValueText
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            color: Utility.getAppHexColor("lightText")
                            text: voltageGauge.value.toFixed(1) + "V"
                            font.pixelSize: 30
                            font.weight: Font.Black
                        }

                        // Label just below the value, inside the gauge
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: voltageValueText.bottom
                            anchors.topMargin: 2
                            verticalAlignment: Text.AlignTop
                            color: Utility.getAppHexColor("lightText")
                            text: "Battery\nVoltage"
                            font.pixelSize: 14
                            horizontalAlignment: Text.AlignHCenter
                            font.weight: Font.Black
                        }
                    }
                }
                
                // Spacer for future features
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
            }
            
            // Tab 2 - Original content
            ColumnLayout {
                id: gaugeColumn
                anchors.fill: parent
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    ColumnLayout {
                        Text {
                            id: header
                            color: Utility.getAppHexColor("lightText")
                            font.family: "DejaVu Sans Mono"
                            Layout.margins: 0
                            Layout.leftMargin: 0
                            Layout.fillWidth: true
                            text: "Balance App v{{VERSION}}-{{GIT_HASH}}\nRT Data"
                            font.underline: true
                            font.weight: Font.Black
                        }

                        Text {
                            id: valText1
                            color: Utility.getAppHexColor("lightText")
                            font.family: "DejaVu Sans Mono"
                            Layout.margins: 0
                            Layout.leftMargin: 5
                            Layout.preferredWidth: parent.width/3
                            text: "App not connected"
                        }

                        Text {
                            Layout.fillWidth: true
                            color: Utility.getAppHexColor("lightText")
                            horizontalAlignment: Text.AlignHCenter
                            font.pointSize: 20
                            text: "Controls"
                        }                

                        Button {
                            Layout.fillWidth: true
                            text: "Kill Switch"
                            
                            onClicked: {
                                var buffer = new ArrayBuffer(1)
                                var dv = new DataView(buffer)
                                dv.setUint8(0, balanceCommandTriggerKillspin)
                                mCommands.sendCustomAppData(buffer)
                            }
                        }
                    
                        Text {
                            Layout.fillWidth: true
                            color: Utility.getAppHexColor("lightText")
                            horizontalAlignment: Text.AlignHCenter
                            font.pointSize: 20
                            text: "Data Logging"
                        }
                        
                        CheckBox {
                            id: appendGnss
                            Layout.fillWidth: true
                            text: "Append GNSS"
                            checked: true
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            
                            Text {
                                color: Utility.getAppHexColor("lightText")
                                text: "Log Rate:"
                                Layout.preferredWidth: 100
                            }
                            
                            ComboBox {
                                id: logRate
                                Layout.fillWidth: true
                                model: [20, 50, 100, 200, 500, 1000]
                                currentIndex: 5 // Default to 1000
                            }
                        }
                                    
                        Button {
                            Layout.fillWidth: true
                            text: "Start Log"
                            
                            onClicked: {
                                var cmd = "(start-log " + appendGnss.checked + " " + logRate.model[logRate.currentIndex] + ")"
                                sendCode(cmd)
                            }
                        }
                        
                        Button {
                            Layout.fillWidth: true
                            text: "Stop Log"
                            
                            onClicked: {
                                var cmd = "(stop-log)"
                                sendCode(cmd)
                            }
                        }
                    }
                }
            }
            
            // Tab 3 - Setpoint
            ColumnLayout {
                id: setpointColumn
                anchors.fill: parent
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    ColumnLayout {
                        Text {
                            Layout.fillWidth: true
                            color: Utility.getAppHexColor("lightText")
                            horizontalAlignment: Text.AlignHCenter
                            font.pointSize: 20
                            text: "Setpoint things"
                        }
                        
                        // Placeholder for setpoint controls
                        Item {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                        }
                    }
                }
            }
        }
        
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "EUC RT data"
            }
            
            TabButton {
                text: "Debug stuff"
            }
            
            TabButton {
                text: "setpoint"
            }
        }
    }

    function sendCode(str) {
        mCommands.lispSendReplCmd(str)
    }
}
