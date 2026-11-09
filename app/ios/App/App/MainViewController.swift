import UIKit
import Capacitor

/// The app's main screen: the normal Capacitor web view, plus our own native bridge.
class MainViewController: CAPBridgeViewController {
    override open func capacitorDidLoad() {
        bridge?.registerPluginInstance(HoneyNativePlugin())
    }
}
