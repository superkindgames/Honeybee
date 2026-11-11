// Shared by the app and the widget extension: what the lock screen shows, and the one-tap quick add.
import Foundation
#if canImport(ActivityKit)
import ActivityKit

@available(iOS 16.1, *)
struct HoneyActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var title: String        // "Sleeping" or "Breastfeeding · Left"
        var startedAt: Date      // the timer counts up from here
        var side: String?        // "L" / "R" while breastfeeding
        var hub: Hub?            // quick-add grid (kind "hub")
    }
    /// The 2×2 quick-add grid: when each thing last happened, and what one tap will log.
    public struct Hub: Codable, Hashable {
        var feedAt: Date?
        var diaperAt: Date?
        var pumpAt: Date?
        var sleepAt: Date?       // set while sleeping (timer counts up from here)
        var wakeAt: Date?        // last time baby woke up (awake timer)
        var feedLbl: String
        var diaperLbl: String
        var pumpLbl: String
        var flash: String?       // "✓ Logged 01:10"
        var flashKind: String?   // which tile it belongs to: feed / diaper / pump / sleep
    }
    var kind: String             // "hub", "sleep" or "feed"
    var babyName: String
}

/// One-tap logging from the lock screen. Runs inside the app (in the background), writes the
/// event straight to the family database, then refreshes the lock-screen grid.
@available(iOS 16.2, *)
enum HoneyQuick {
    static let key = "hb.quick"

    static func config() -> [String: Any] {
        guard let d = UserDefaults.standard.data(forKey: key),
              let o = try? JSONSerialization.jsonObject(with: d) as? [String: Any] else { return [:] }
        return o
    }
    static func save(_ c: [String: Any]) {
        if let d = try? JSONSerialization.data(withJSONObject: c) { UserDefaults.standard.set(d, forKey: key) }
    }

    static func value(_ v: Any?) -> [String: Any] {
        switch v {
        case let s as String: return ["stringValue": s]
        case let n as NSNumber:
            if CFGetTypeID(n) == CFBooleanGetTypeID() { return ["booleanValue": n.boolValue] }
            if CFNumberIsFloatType(n as CFNumber), n.doubleValue != n.doubleValue.rounded() { return ["doubleValue": n.doubleValue] }
            return ["integerValue": String(n.int64Value)]
        default: return ["nullValue": NSNull()]
        }
    }

    static func newId() -> String {
        let chars = Array("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789")
        return String((0..<20).map { _ in chars.randomElement()! })
    }

    static func write(_ c: [String: Any], id: String, fields: [String: Any], mask: [String]? = nil) async -> Bool {
        guard let p = c["project"] as? String, let fam = c["family"] as? String, !fam.isEmpty else { return false }
        var comp = URLComponents(string: "https://firestore.googleapis.com/v1/projects/\(p)/databases/(default)/documents/families/\(fam)/events/\(id)")!
        var q: [URLQueryItem] = []
        if let k = c["apiKey"] as? String { q.append(URLQueryItem(name: "key", value: k)) }
        for m in mask ?? [] { q.append(URLQueryItem(name: "updateMask.fieldPaths", value: m)) }
        if mask != nil { q.append(URLQueryItem(name: "currentDocument.exists", value: "true")) }
        comp.queryItems = q
        var req = URLRequest(url: comp.url!)
        req.httpMethod = "PATCH"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.httpBody = try? JSONSerialization.data(withJSONObject: ["fields": fields.mapValues { value($0) }])
        guard let (_, resp) = try? await URLSession.shared.data(for: req) else { return false }
        return ((resp as? HTTPURLResponse)?.statusCode ?? 500) < 300
    }

    static func clock(_ d: Date) -> String {
        let f = DateFormatter(); f.timeStyle = .short; f.dateStyle = .none
        return f.string(from: d)
    }

    static func run(_ kind: String) async {
        var c = config()
        let now = Date(), ms = Int64(now.timeIntervalSince1970 * 1000)
        var hub = c["hub"] as? [String: Any] ?? [:]
        let me = (c["me"] as? String) ?? ""
        var ok = false, msg = ""
        switch kind {
        case "sleep":
            if let nap = c["napId"] as? String, !nap.isEmpty {
                ok = await write(c, id: nap, fields: ["end": NSNumber(value: ms)], mask: ["end"])
                if ok { c["napId"] = ""; hub["sleepAt"] = nil; hub["wakeAt"] = NSNumber(value: ms); msg = "Woke up" }
            } else {
                let id = newId()
                ok = await write(c, id: id, fields: ["cat": "nap", "at": NSNumber(value: ms), "by": me, "end": NSNull(), "quick": true])
                if ok { c["napId"] = id; hub["sleepAt"] = NSNumber(value: ms); msg = "Sleep started" }
            }
        default:
            let cat = kind == "feed" ? "feeding" : kind
            var f = (c["tpl"] as? [String: Any])?[kind] as? [String: Any] ?? [:]
            f["cat"] = cat; f["at"] = NSNumber(value: ms); f["by"] = me; f["quick"] = true
            ok = await write(c, id: newId(), fields: f)
            if ok {
                hub[kind + "At"] = NSNumber(value: ms)
                msg = (kind == "feed" ? "Feed" : kind == "pump" ? "Pumping" : "Diaper") + " logged"
            }
        }
        _ = msg
        hub["flash"] = ok ? "✓ Logged \(clock(now)) · tap to edit" : "Couldn’t save · open app"
        hub["flashKind"] = kind
        c["hub"] = hub
        save(c)
        await refresh(hub)
    }

    static func hubState(_ h: [String: Any]) -> HoneyActivityAttributes.Hub {
        func d(_ k: String) -> Date? { (h[k] as? NSNumber).map { Date(timeIntervalSince1970: $0.doubleValue / 1000) } }
        return HoneyActivityAttributes.Hub(feedAt: d("feedAt"), diaperAt: d("diaperAt"), pumpAt: d("pumpAt"),
                                           sleepAt: d("sleepAt"), wakeAt: d("wakeAt"),
                                           feedLbl: (h["feedLbl"] as? String) ?? "Feed",
                                           diaperLbl: (h["diaperLbl"] as? String) ?? "Diaper",
                                           pumpLbl: (h["pumpLbl"] as? String) ?? "Pump",
                                           flash: h["flash"] as? String, flashKind: h["flashKind"] as? String)
    }

    static func refresh(_ h: [String: Any]) async {
        for a in Activity<HoneyActivityAttributes>.activities where a.attributes.kind == "hub" {
            let st = HoneyActivityAttributes.ContentState(title: "", startedAt: Date(), side: nil, hub: hubState(h))
            await a.update(ActivityContent(state: st, staleDate: nil))
        }
    }
}
#endif

#if canImport(AppIntents) && canImport(ActivityKit)
import AppIntents

/// The lock-screen grid buttons (iOS 17+): log without unlocking or opening the app.
@available(iOS 17.0, *)
struct QuickAddIntent: LiveActivityIntent {
    static var title: LocalizedStringResource = "Quick add"
    static var description = IntentDescription("Log a feed, diaper, pumping or sleep for your baby.")
    @Parameter(title: "Kind") var kind: String
    init() { kind = "diaper" }
    init(kind: String) { self.kind = kind }
    func perform() async throws -> some IntentResult {
        await HoneyQuick.run(kind)
        return .result()
    }
}
#endif
