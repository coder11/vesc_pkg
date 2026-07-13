import QtQuick 2.12
import "." as Components

Rectangle {
    id: gauge

    component CustomTextRef: Components.CustomText {}

    required property real inputValue
    required property var mUtility

    property real minValue: 0.0
    property real maxValue: 100.0
    property real safetyMargin: 50.0
    property real borderWidth: 2.0
    property real labelPadding: 4.0
    property bool inverted: false
    property string valueUnit: ""
    property string rangeUnit: valueUnit
    property string label: ""
    property int valueDecimals: 1
    property int rangeDecimals: 1

    readonly property real value:
        Math.max(minValue, Math.min(maxValue, inputValue))
    readonly property real normalizedPercentage:
        maxValue > minValue
            ? ((value - minValue) / (maxValue - minValue)) * 100.0
            : 0.0
    readonly property real percentage:
        inverted ? 100.0 - normalizedPercentage : normalizedPercentage
    readonly property real topValue: inverted ? minValue : maxValue
    readonly property real bottomValue: inverted ? maxValue : minValue

    color: mUtility.getAppHexColor("darkBackground")

    function gaugeColor(percentageValue, margin) {
        if (percentageValue <= margin) {
            return Qt.rgba(0.0, 0.45, 0.0, 1.0)
        }

        var denominator = 100.0 - margin
        var transition = denominator > 0.0
                ? (percentageValue - margin) / denominator
                : 1.0
        transition = Math.max(0.0, Math.min(1.0, transition))

        if (transition <= 0.5) {
            var greenToYellow = transition / 0.5
            return Qt.rgba(greenToYellow * 0.5, 0.45, 0.0, 1.0)
        }

        var yellowToRed = (transition - 0.5) / 0.5
        return Qt.rgba(0.5, 0.45 * (1.0 - yellowToRed), 0.0, 1.0)
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.right: topValueLabelBackground.left
        height: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        anchors.left: topValueLabelBackground.right
        anchors.top: parent.top
        anchors.right: parent.right
        height: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.right: bottomValueLabelBackground.left
        height: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        anchors.left: bottomValueLabelBackground.right
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        height: gauge.borderWidth
        color: mUtility.getAppHexColor("lightText")
    }

    Rectangle {
        z: 0
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: parent.height * gauge.percentage / 100.0
        color: gauge.gaugeColor(gauge.percentage, gauge.safetyMargin)

        Behavior on height {
            NumberAnimation {
                duration: 100
                easing.type: Easing.OutQuad
            }
        }
    }

    Rectangle {
        id: topValueLabelBackground
        z: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: -gauge.borderWidth
        width: topValueLabel.width + 4
        height: topValueLabel.height + gauge.labelPadding * 2
        color: "transparent"
    }

    CustomTextRef {
        id: topValueLabel
        mUtility: gauge.mUtility
        z: 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.top
        anchors.verticalCenterOffset: gauge.borderWidth / 2
        text: gauge.topValue.toFixed(gauge.rangeDecimals) + gauge.rangeUnit
        font.pixelSize: 16
        font.weight: Font.Normal
    }

    Rectangle {
        id: bottomValueLabelBackground
        z: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: -gauge.borderWidth
        width: bottomValueLabel.width + 4
        height: bottomValueLabel.height + gauge.labelPadding * 2
        color: "transparent"
    }

    CustomTextRef {
        id: bottomValueLabel
        mUtility: gauge.mUtility
        z: 2
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.bottom
        anchors.verticalCenterOffset: -gauge.borderWidth / 2
        text: gauge.bottomValue.toFixed(gauge.rangeDecimals) + gauge.rangeUnit
        font.pixelSize: 16
        font.weight: Font.Normal
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.bottomMargin: parent.height * gauge.safetyMargin / 100.0
        height: 2
        color: mUtility.getAppHexColor("lightText")
        opacity: 0.7
    }

    CustomTextRef {
        id: valueLabel
        mUtility: gauge.mUtility
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
        text: gauge.value.toFixed(gauge.valueDecimals) + gauge.valueUnit
        font.pixelSize: 30
        font.weight: Font.Black
    }

    CustomTextRef {
        mUtility: gauge.mUtility
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: valueLabel.bottom
        anchors.topMargin: 2
        text: gauge.label
        verticalAlignment: Text.AlignTop
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 14
        font.weight: Font.Black
    }
}
