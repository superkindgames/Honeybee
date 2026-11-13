// Small bridge between the web app (JavaScript) and native iPhone features.
import Foundation
import UIKit
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
        CAPPluginMethod(name: "takeAction", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "openSettings", returnType: CAPPluginReturnPromise)
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

    /// Opens Goldfox's page in iPhone Settings (where Live Activities and Notifications are switched on).
    @objc func openSettings(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
            call.resolve()
        }
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
            // quick-add settings (family, name, what one tap logs) for the lock-screen grid buttons
            if let hub = wanted["hub"], let q = hub["quick"] as? JSObject {
                var c = q as [String: Any]
                if let h = hub["hub"] as? JSObject { c["hub"] = h as [String: Any] }
                HoneyQuick.save(c)
            }
            Task {
                for activity in Activity<HoneyActivityAttributes>.activities {
                    // swiped away or timed out (iPhone ends them after ~8 h): clear it so a fresh one starts
                    if activity.activityState == .ended || activity.activityState == .dismissed {
                        await activity.end(nil, dismissalPolicy: .immediate)
                        continue
                    }
                    if let w = wanted[activity.attributes.kind] {
                        await activity.update(ActivityContent(state: HoneyNativePlugin.state(w), staleDate: nil))
                        wanted.removeValue(forKey: activity.attributes.kind)
                    } else {
                        await activity.end(nil, dismissalPolicy: .immediate)
                    }
                }
                // the two quick-add cards must start together so they stack in order (Feed+Diaper on top)
                if (wanted["hub"] == nil) != (wanted["hub2"] == nil), let a = items.first(where: { ($0["kind"] as? String) == "hub" }),
                   let b = items.first(where: { ($0["kind"] as? String) == "hub2" }) {
                    for act in Activity<HoneyActivityAttributes>.activities where act.attributes.kind.hasPrefix("hub") {
                        await act.end(nil, dismissalPolicy: .immediate)
                    }
                    wanted["hub"] = a; wanted["hub2"] = b
                }
                var errors: [String] = []
                var started = 0
                // newest shows on top: start the lower cards first
                let order = ["hub2", "hub", "sleep", "feed"]
                let kinds = wanted.keys.sorted { (order.firstIndex(of: $0) ?? 9) < (order.firstIndex(of: $1) ?? 9) }
                for kind in kinds {
                    guard let w = wanted[kind] else { continue }
                    let attrs = HoneyActivityAttributes(kind: kind, babyName: (w["baby"] as? String) ?? "")
                    do {
                        _ = try Activity.request(attributes: attrs, content: ActivityContent(state: HoneyNativePlugin.state(w), staleDate: nil), pushType: nil)
                        started += 1
                    } catch {
                        errors.append(String(describing: error))
                    }
                }
                call.resolve(["started": started, "running": Activity<HoneyActivityAttributes>.activities.count,
                              "enabled": ActivityAuthorizationInfo().areActivitiesEnabled, "error": errors.joined(separator: "; ")])
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
                                                   side: w["side"] as? String,
                                                   hub: (w["hub"] as? JSObject).map { HoneyQuick.hubState($0 as [String: Any]) })
    }
    #endif
}
