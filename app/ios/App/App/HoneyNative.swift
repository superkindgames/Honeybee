// Small bridge between the web app (JavaScript) and native iPhone features.
import Foundation
import Capacitor
#if canImport(ActivityKit)
import ActivityKit
#endif

@objc(HoneyNativePlugin)
public class HoneyNativePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "HoneyNativePlugin"
    public let jsName = "HoneyNative"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "liveSupported", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "liveSync", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "takeAction", returnType: CAPPluginReturnPromise)
    ]

    /// Set when a lock-screen button (honeybee://wake etc.) opened the app before the web page was ready.
    static var pendingAction: String?

    override public func load() {
        NotificationCenter.default.addObserver(self, selector: #selector(onAction(_:)), name: Notification.Name("HoneyAction"), object: nil)
    }

    @objc func onAction(_ note: Notification) {
        guard let action = note.object as? String else { return }
        HoneyNativePlugin.pendingAction = nil
        notifyListeners("action", data: ["action": action])
    }

    @objc func takeAction(_ call: CAPPluginCall) {
        let a = HoneyNativePlugin.pendingAction ?? ""
        HoneyNativePlugin.pendingAction = nil
        call.resolve(["action": a])
    }

    @objc func liveSupported(_ call: CAPPluginCall) {
        #if canImport(ActivityKit)
        if #available(iOS 16.2, *) {
            call.resolve(["ok": ActivityAuthorizationInfo().areActivitiesEnabled])
            return
        }
        #endif
        call.resolve(["ok": false])
    }

    /// items: [{kind:"sleep"|"feed", title, startedAt (ms), side?, baby}] — starts, updates or ends timers to match.
    @objc func liveSync(_ call: CAPPluginCall) {
        #if canImport(ActivityKit)
        if #available(iOS 16.2, *) {
            let items = call.getArray("items", JSObject.self) ?? []
            var wanted: [String: JSObject] = [:]
            for item in items { if let k = item["kind"] as? String { wanted[k] = item } }
            Task {
                for activity in Activity<HoneyActivityAttributes>.activities {
                    if let w = wanted[activity.attributes.kind] {
                        await activity.update(ActivityContent(state: HoneyNativePlugin.state(w), staleDate: nil))
                        wanted.removeValue(forKey: activity.attributes.kind)
                    } else {
                        await activity.end(nil, dismissalPolicy: .immediate)
                    }
                }
                for (kind, w) in wanted {
                    let attrs = HoneyActivityAttributes(kind: kind, babyName: (w["baby"] as? String) ?? "")
                    _ = try? Activity.request(attributes: attrs, content: ActivityContent(state: HoneyNativePlugin.state(w), staleDate: nil), pushType: nil)
                }
                call.resolve()
            }
            return
        }
        #endif
        call.resolve()
    }

    #if canImport(ActivityKit)
    @available(iOS 16.2, *)
    static func state(_ w: JSObject) -> HoneyActivityAttributes.ContentState {
        let ms = (w["startedAt"] as? NSNumber)?.doubleValue ?? Date().timeIntervalSince1970 * 1000
        return HoneyActivityAttributes.ContentState(title: (w["title"] as? String) ?? "",
                                                   startedAt: Date(timeIntervalSince1970: ms / 1000),
                                                   side: w["side"] as? String)
    }
    #endif
}
