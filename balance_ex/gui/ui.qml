/*
    Production entry point loaded by VESC Tool.
*/

import QtQuick 2.12
import Vedder.vesc.utility 1.0
import Vedder.vesc.commands 1.0
import Vedder.vesc.configparams 1.0
import "components" as Components

Item {
    anchors.fill: parent

    component BalanceUiRef: Components.BalanceUi {}

    BalanceUiRef {
        anchors.fill: parent
        appVersion: "{{VERSION}}"
        mCommands: VescIf.commands()
        mMcConf: VescIf.mcConfig()
        mCustomConf: VescIf.customConfig(0)
        mUtility: Utility
    }
}
