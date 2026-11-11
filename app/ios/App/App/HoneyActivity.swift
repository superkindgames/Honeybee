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
        var pick: String?        // a card showing its choices: "feed", "diaper" or "pump"
        var feedMl: [Int]?       // amount buttons (ml) and their labels (ml or oz)
        var feedLbls: [String]?
        var pumpMl: [Int]?
        var pumpLbls: [String]?
        var pumpSide: String?    // "Both", "Left"…
        var cfg: String?         // what a button needs to save on its own (family, name, sleep id…), as JSON
    }
    var kind: String             // "hub" (Feed+Diaper), "hub2" (Pump+Sleep), "sleep" or "feed"
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

    static var lastErr = ""
    static func write(_ c: [String: Any], id: String, fields: [String: Any], mask: [String]? = nil) async -> Bool {
        guard let p = c["project"] as? String, let fam = c["family"] as? String, !fam.isEmpty else { lastErr = "no family"; return false }
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
        guard let (_, resp) = try? await URLSession.shared.data(for: req) else { lastErr = "offline"; return false }
        let code = (resp as? HTTPURLResponse)?.statusCode ?? 500
        if code >= 300 { lastErr = "error \(code)" }
        return code < 300
    }

    static func clock(_ d: Date) -> String {
        let f = DateFormatter(); f.timeStyle = .short; f.dateStyle = .none
        return f.string(from: d)
    }

    static func run(_ kind: String, cfg: String = "") async {
        var c = config()
        // the button carries its own copy of the settings, so saving works even if this phone's copy is missing
        if let d = cfg.data(using: .utf8), let o = try? JSONSerialization.jsonObject(with: d) as? [String: Any] {
            let mine = !((c["family"] as? String) ?? "").isEmpty
            for (k, v) in o where !mine || c[k] == nil { c[k] = v }
        }
        let now = Date(), ms = Int64(now.timeIntervalSince1970 * 1000)
        var hub = c["hub"] as? [String: Any] ?? [:]
        let me = (c["me"] as? String) ?? ""
        var ok = false, msg = ""
        let part = kind.split(separator: ":").map(String.init)
        // "pick:feed" opens a card's choices, "pick:none" closes them (nothing is logged)
        if part.first == "pick" {
            let p = part.count > 1 ? part[1] : "none"
            if p == "none" { hub["pick"] = nil } else { hub["pick"] = p }
            hub["flash"] = nil
            c["hub"] = hub; save(c); await refresh(hub)
            return
        }
        var key = part.first ?? kind
        switch key {
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
            if !["feed", "diaper", "pump"].contains(key) { key = "diaper" }
            let cat = key == "feed" ? "feeding" : key
            var f = (c["tpl"] as? [String: Any])?[key] as? [String: Any] ?? [:]
            // chosen on the lock screen: feed:formula:60 · diaper:dirty · pump:120
            if key == "feed", part.count >= 3, let ml = Int(part[2]) { f = ["type": part[1], "ml": NSNumber(value: ml)] }
            if key == "diaper", part.count >= 2 { f = ["kind": part[1]] }
            if key == "pump", part.count >= 2, let ml = Int(part[1]) { f["ml"] = NSNumber(value: ml) }
            f["cat"] = cat; f["at"] = NSNumber(value: ms); f["by"] = me; f["quick"] = true
            ok = await write(c, id: newId(), fields: f)
            if ok {
                hub[key + "At"] = NSNumber(value: ms)
                msg = (key == "feed" ? "Feed" : key == "pump" ? "Pumping" : "Diaper") + " logged"
            }
        }
        _ = msg
        hub["flash"] = ok ? "✓ Logged \(clock(now)) · tap to edit" : "Couldn’t save (\(lastErr)) · open app"
        var keep = c; keep["hub"] = nil
        if let d = try? JSONSerialization.data(withJSONObject: keep), let t = String(data: d, encoding: .utf8) { hub["cfg"] = t }
        hub["flashKind"] = key
        hub["pick"] = nil
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
                                           flash: h["flash"] as? String, flashKind: h["flashKind"] as? String,
                                           pick: h["pick"] as? String,
                                           feedMl: (h["feedMl"] as? [Any])?.compactMap { ($0 as? NSNumber)?.intValue }, feedLbls: (h["feedLbls"] as? [Any])?.compactMap { $0 as? String },
                                           pumpMl: (h["pumpMl"] as? [Any])?.compactMap { ($0 as? NSNumber)?.intValue }, pumpLbls: (h["pumpLbls"] as? [Any])?.compactMap { $0 as? String },
                                           pumpSide: h["pumpSide"] as? String, cfg: h["cfg"] as? String)
    }

    static func refresh(_ h: [String: Any]) async {
        for a in Activity<HoneyActivityAttributes>.activities where a.attributes.kind.hasPrefix("hub") {
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
    @Parameter(title: "Settings") var cfg: String
    init() { kind = "diaper"; cfg = "" }
    init(kind: String, cfg: String) { self.kind = kind; self.cfg = cfg }
    func perform() async throws -> some IntentResult {
        await HoneyQuick.run(kind, cfg: cfg)
        return .result()
    }
}
#endif
