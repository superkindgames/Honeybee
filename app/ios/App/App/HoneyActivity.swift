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
        var oneTap: Bool?        // true: Feed/Diaper/Pump log straight away (copy of the last one), no choices
        var lastFeed: String?    // the usual choice, highlighted: "formula:60"
        var lastDiaper: String?  // "dirty"
        var lastPump: Int?       // 120
        var cfg: String?         // what a button needs to save on its own (family, name, sleep id…), as JSON
        var bfSide: String?      // set while breastfeeding: "L" / "R" (the card then shows Left / Right / Done)
        var bfL: Int?            // time so far on each side (ms), not counting the running stretch
        var bfR: Int?
        var bfSeg: Date?         // when the current side started
        var bfAt: Date?          // when the feed started
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
        let part = kind.split(separator: ":").map(String.init)
        // "pick:feed" opens a card's choices, "pick:none" closes them (nothing is logged)
        if part.first == "pick" {
            let p = part.count > 1 ? part[1] : "none"
            if p == "none" { hub["pick"] = nil } else { hub["pick"] = p }
            hub["flash"] = nil
            c["hub"] = hub; save(c); await refresh(hub)
            return
        }
        // breastfeeding: "bf:L" / "bf:R" switch side, "bf:done" ends the feed
        if part.first == "bf" {
            let action = part.count > 1 ? part[1] : "done"
            guard var bf = c["bf"] as? [String: Any], let id = bf["id"] as? String else { return }
            let side = (bf["side"] as? String) ?? "L"
            if action == side { return }   // already on that side
            var l = (bf["l"] as? NSNumber)?.int64Value ?? 0, r = (bf["r"] as? NSNumber)?.int64Value ?? 0
            let seg = (bf["segAt"] as? NSNumber)?.int64Value ?? ms
            if side == "L" { l += max(0, ms - seg) } else { r += max(0, ms - seg) }
            let before = hub
            var ok = false
            if action == "done" {
                for k in ["bfSide", "bfL", "bfR", "bfSeg", "bfAt"] { hub[k] = nil }
                hub["feedAt"] = bf["at"] ?? NSNumber(value: ms)
                hub["flash"] = "✓ Logged \(clock(now)) · tap to edit"; hub["flashKind"] = "feed"; hub["pick"] = nil
                await refresh(hub)
                ok = await write(c, id: id, fields: ["l": NSNumber(value: l), "r": NSNumber(value: r), "end": NSNumber(value: ms), "segAt": NSNull()], mask: ["l", "r", "end", "segAt"])
                if ok { c["bf"] = nil }
            } else {
                hub["bfSide"] = action; hub["bfL"] = NSNumber(value: l); hub["bfR"] = NSNumber(value: r); hub["bfSeg"] = NSNumber(value: ms)
                hub["flash"] = nil; hub["pick"] = nil
                await refresh(hub)
                ok = await write(c, id: id, fields: ["l": NSNumber(value: l), "r": NSNumber(value: r), "side": action, "segAt": NSNumber(value: ms)], mask: ["l", "r", "side", "segAt"])
                if ok { bf["l"] = NSNumber(value: l); bf["r"] = NSNumber(value: r); bf["side"] = action; bf["segAt"] = NSNumber(value: ms); c["bf"] = bf }
            }
            if !ok { hub = before; hub["flash"] = "Couldn’t save (\(lastErr)) · open app"; hub["flashKind"] = "feed" }
            var keep = c; keep["hub"] = nil
            if let d = try? JSONSerialization.data(withJSONObject: keep), let t = String(data: d, encoding: .utf8) { hub["cfg"] = t }
            c["hub"] = hub
            save(c)
            await refresh(hub)
            return
        }
        var key = part.first ?? kind
        if !["sleep", "feed", "diaper", "pump"].contains(key) { key = "diaper" }
        let before = hub
        let napOpen = !((c["napId"] as? String) ?? "").isEmpty
        // 1) show it on the lock screen straight away (feels instant), then save in the background
        if key == "sleep" {
            if napOpen { hub["sleepAt"] = nil; hub["wakeAt"] = NSNumber(value: ms) } else { hub["sleepAt"] = NSNumber(value: ms) }
        } else {
            hub[key + "At"] = NSNumber(value: ms)
        }
        hub["flash"] = "✓ Logged \(clock(now)) · tap to edit"
        hub["flashKind"] = key
        hub["pick"] = nil
        await refresh(hub)
        // 2) save to the family log
        var ok = false
        if key == "sleep" {
            if napOpen, let nap = c["napId"] as? String {
                ok = await write(c, id: nap, fields: ["end": NSNumber(value: ms)], mask: ["end"])
                if ok { c["napId"] = "" }
            } else {
                let id = newId()
                ok = await write(c, id: id, fields: ["cat": "nap", "at": NSNumber(value: ms), "by": me, "end": NSNull(), "quick": true])
                if ok { c["napId"] = id }
            }
        } else {
            let cat = key == "feed" ? "feeding" : key
            var f = (c["tpl"] as? [String: Any])?[key] as? [String: Any] ?? [:]
            // chosen on the lock screen: feed:formula:60 · diaper:dirty · pump:120
            if key == "feed", part.count >= 3, let ml = Int(part[2]) { f = ["type": part[1], "ml": NSNumber(value: ml)] }
            if key == "diaper", part.count >= 2 { f = ["kind": part[1]] }
            if key == "pump", part.count >= 2, let ml = Int(part[1]) { f["ml"] = NSNumber(value: ml) }
            f["cat"] = cat; f["at"] = NSNumber(value: ms); f["by"] = me; f["quick"] = true
            ok = await write(c, id: newId(), fields: f)
        }
        // 3) if saving failed, put the card back the way it was and say why
        if !ok {
            hub = before
            hub["flash"] = "Couldn’t save (\(lastErr)) · open app"
            hub["flashKind"] = key
            hub["pick"] = nil
        }
        var keep = c; keep["hub"] = nil
        if let d = try? JSONSerialization.data(withJSONObject: keep), let t = String(data: d, encoding: .utf8) { hub["cfg"] = t }
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
                                           pumpSide: h["pumpSide"] as? String,
                                           oneTap: (h["oneTap"] as? NSNumber)?.boolValue,
                                           lastFeed: h["lastFeed"] as? String, lastDiaper: h["lastDiaper"] as? String,
                                           lastPump: (h["lastPump"] as? NSNumber)?.intValue,
                                           cfg: h["cfg"] as? String,
                                           bfSide: h["bfSide"] as? String,
                                           bfL: (h["bfL"] as? NSNumber)?.intValue, bfR: (h["bfR"] as? NSNumber)?.intValue,
                                           bfSeg: d("bfSeg"), bfAt: d("bfAt"))
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
