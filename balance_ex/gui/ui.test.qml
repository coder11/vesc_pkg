import QtQuick 2.12
import QtQuick.Controls 2.12
import "components" as Components
import "mocks" as Mocks

ApplicationWindow {
    width: 850
    height: 1232
    visible: true
    title: "Balance UI (mock VESC)"
    color: "#f7f7f7"

    component BalanceUiRef: Components.BalanceUi {}
    component MockCommandsRef: Mocks.MockCommands {}
    component MockConfigRef: Mocks.MockConfig {}
    component MockUtilityRef: Mocks.MockUtility {}

    Item {
        id: vescViewport
        width: 850
        height: 1232
        anchors.centerIn: parent
        scale: Math.min(1.0,
                        parent.width / width,
                        parent.height / height)

        BalanceUiRef {
            anchors.fill: parent
            appVersion: "dev"
            gitHash: "mock"
            mCommands: MockCommandsRef {}
            mMcConf: MockConfigRef {}
            mCustomConf: MockConfigRef {}
            mUtility: MockUtilityRef {}
        }
    }
}
