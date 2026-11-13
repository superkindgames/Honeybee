// Lock screen + Dynamic Island timer for a running sleep or breastfeed.
import WidgetKit
import SwiftUI
import ActivityKit
import AppIntents

private let honey = Color(red: 0xF5/255, green: 0xA5/255, blue: 0x24/255)   // Goldfox gold
private let ink = Color(red: 0.10, green: 0.13, blue: 0.20)
private let sleepBlue = Color(red: 0x94/255, green: 0x78/255, blue: 0xFF/255)
private let feedRose = Color(red: 0xFF/255, green: 0x6B/255, blue: 0x91/255)

private func accent(_ kind: String) -> Color { kind == "sleep" ? sleepBlue : feedRose }
private func icon(_ kind: String) -> String { kind == "sleep" ? "moon.zzz.fill" : "heart.fill" }

private struct Elapsed: View {
    let since: Date
    var body: some View {
        Text(timerInterval: since...Date.distantFuture, countsDown: false)
            .monospacedDigit()
    }
}

private struct ActionPill: View {
    let label: String
    let url: String
    let filled: Bool
    let tint: Color
    var body: some View {
        Link(destination: URL(string: url)!) {
            Text(label)
                .font(.system(size: 20, weight: .heavy, design: .rounded))
                .padding(.horizontal, 14).padding(.vertical, 15)
                .frame(maxWidth: .infinity)
                .background(filled ? tint : Color.white.opacity(0.14), in: Capsule())
                .foregroundColor(filled ? ink : .white)
        }
    }
}

@available(iOS 16.1, *)
private struct Buttons: View {
    let ctx: ActivityViewContext<HoneyActivityAttributes>
    var body: some View {
        if ctx.attributes.kind == "sleep" {
            ActionPill(label: "Woke up", url: "honeybee://wake", filled: true, tint: accent("sleep"))
        } else {
            HStack(spacing: 8) {
                ActionPill(label: ctx.state.side == "L" ? "Switch to right" : "Switch to left", url: "honeybee://switch", filled: false, tint: accent("feed"))
                ActionPill(label: "Done", url: "honeybee://done", filled: true, tint: accent("feed"))
            }
        }
    }
}

// ---------- quick-add grid: Feed · Diaper · Pumping · Sleep ----------
private let diaperGold = Color(red: 0xFF/255, green: 0xB7/255, blue: 0x40/255)   // Diaper amber
private let pumpPink = Color(red: 0x22/255, green: 0xCC/255, blue: 0xE8/255)   // Pumping aqua

private struct Since: View {
    let at: Date?
    var body: some View {
        // hours and minutes only ("1 hr, 14 min"), no ticking seconds
        if let at = at { Text(at, style: .relative) } else { Text("–") }
    }
}

/// Goldfox paw-print wallpaper, very faint, on every lock-screen tile (matches the app)
private struct Paws: View {
    var body: some View { Image("Paws").resizable(resizingMode: .tile).opacity(0.07).allowsHitTesting(false) }
}

private struct CfgKey: EnvironmentKey { static let defaultValue = "" }
extension EnvironmentValues { var hbCfg: String { get { self[CfgKey.self] } set { self[CfgKey.self] = newValue } } }

@available(iOS 16.2, *)
private struct QuickButton<Label: View>: View {
    @Environment(\.hbCfg) var cfg
    let kind: String
    @ViewBuilder let label: () -> Label
    var body: some View {
        if #available(iOS 17.0, *) {
            Button(intent: QuickAddIntent(kind: kind, cfg: cfg)) { label() }.buttonStyle(.plain)
        } else {
            Link(destination: URL(string: "honeybee://add/\(kind)")!) { label() }
        }
    }
}

// tile backgrounds = the app's dark category colours (same as the big tiles on Home)
private let feedSoft = Color(red: 0x64/255, green: 0x36/255, blue: 0x4A/255)
private let diaperSoft = Color(red: 0x64/255, green: 0x50/255, blue: 0x2F/255)
private let pumpSoft = Color(red: 0x18/255, green: 0x54/255, blue: 0x64/255)
private let sleepDeep = Color(red: 0x5B/255, green: 0x3F/255, blue: 0xD9/255)
private let napSoft = Color(red: 0x45/255, green: 0x3E/255, blue: 0x78/255)

@available(iOS 16.2, *)
private struct Tile: View {
    let kind: String, name: String, symbol: String, tint: Color, bg: Color, since: Date?, note: String?, live: Bool
    var compact = false
    var body: some View {
        if compact { small } else { wide }
    }
    /// narrow version (three in a row, while baby sleeps)
    var small: some View {
        QuickButton(kind: kind) {
            VStack(spacing: 2) {
                HStack(spacing: 5) {
                    ZStack {
                        Circle().fill(tint).frame(width: 26, height: 26)
                        Image(systemName: symbol).font(.system(size: 13, weight: .bold)).foregroundColor(ink)
                    }
                    Text(name).font(.system(size: 15, weight: .heavy, design: .rounded)).foregroundColor(.white.opacity(0.92)).lineLimit(1).minimumScaleFactor(0.7)
                }
                Since(at: since).font(.system(size: 16, weight: .black, design: .rounded)).monospacedDigit()
                    .foregroundColor(.white).lineLimit(1).minimumScaleFactor(0.55)
                if let note = note {
                    Text(note).font(.system(size: 9, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.8)).lineLimit(1).minimumScaleFactor(0.7)
                }
            }
            .padding(.horizontal, 5)
            .frame(maxWidth: .infinity, minHeight: 68, maxHeight: 68)
            .background(RoundedRectangle(cornerRadius: 16, style: .continuous).fill(bg))
            .overlay(Paws().clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous)))
        }
    }
    var wide: some View {
        QuickButton(kind: kind) {
            HStack(spacing: 10) {
                ZStack {
                    Circle().fill(tint).frame(width: 50, height: 50)
                    Image(systemName: symbol).font(.system(size: 23, weight: .bold)).foregroundColor(ink)
                }
                VStack(alignment: .leading, spacing: 0) {
                    Text(name).font(.system(size: 17, weight: .heavy, design: .rounded)).foregroundColor(.white.opacity(0.92)).lineLimit(1)
                    Since(at: since).font(.system(size: 20, weight: .black, design: .rounded)).monospacedDigit()
                        .foregroundColor(.white).lineLimit(1).minimumScaleFactor(0.6)
                    if let note = note {
                        Text(note).font(.system(size: 11, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.8)).lineLimit(1).minimumScaleFactor(0.8)
                    }
                }
                Spacer(minLength: 0)
            }
            .padding(.horizontal, 10)
            .frame(maxWidth: .infinity, minHeight: 77, maxHeight: 77, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(LinearGradient(colors: [bg.opacity(1), bg.opacity(0.82)], startPoint: .topLeading, endPoint: .bottomTrailing))
            )
            .overlay(Paws().clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous)))
            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(live ? tint : .clear, lineWidth: 2.5))
        }
    }
}

@available(iOS 16.2, *)
private struct HubGrid: View {
    let h: HoneyActivityAttributes.Hub
    func act(_ k: String) -> String { h.oneTap == true ? k : "pick:" + k }
    func note(_ k: String) -> String? { h.flashKind == k ? h.flash : nil }
    var body: some View {
        if let since = h.sleepAt {
            // baby is asleep: make it impossible to miss, with a big Woke up button
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Tile(kind: act("feed"), name: "Feed", symbol: "drop.fill", tint: feedRose, bg: feedSoft, since: h.feedAt, note: note("feed"), live: false, compact: true)
                    Tile(kind: act("diaper"), name: "Diaper", symbol: "sparkles", tint: diaperGold, bg: diaperSoft, since: h.diaperAt, note: note("diaper"), live: false, compact: true)
                    Tile(kind: act("pump"), name: "Pump", symbol: "bolt.heart.fill", tint: pumpPink, bg: pumpSoft, since: h.pumpAt, note: note("pump"), live: false, compact: true)
                }
                HStack(spacing: 10) {
                    Image("GoldieSleepy").resizable().scaledToFill()
                        .frame(width: 58, height: 58).clipShape(Circle())
                        .overlay(Circle().stroke(Color.white.opacity(0.8), lineWidth: 2.5))
                    VStack(alignment: .leading, spacing: 0) {
                        Text("SLEEPING NOW").font(.system(size: 13, weight: .black, design: .rounded)).foregroundColor(.white.opacity(0.9))
                        Since(at: since).font(.system(size: 24, weight: .black, design: .rounded)).monospacedDigit()
                            .foregroundColor(.white).lineLimit(1).minimumScaleFactor(0.6)
                        if let n = note("sleep") {
                            Text(n).font(.system(size: 10, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.85)).lineLimit(1).minimumScaleFactor(0.7)
                        }
                    }
                    Spacer(minLength: 4)
                    QuickButton(kind: "sleep") {
                        Text("Woke up")
                            .font(.system(size: 20, weight: .black, design: .rounded))
                            .foregroundColor(sleepDeep)
                            .frame(width: 124, height: 60)
                            .background(Color.white, in: Capsule())
                    }
                }
                .padding(.leading, 10).padding(.trailing, 8)
                .frame(maxWidth: .infinity, minHeight: 86, maxHeight: 86)
                .background(
                    RoundedRectangle(cornerRadius: 20, style: .continuous)
                        .fill(LinearGradient(colors: [sleepBlue, sleepDeep], startPoint: .topLeading, endPoint: .bottomTrailing))
                )
                .overlay(Paws().clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous)))
            }
        } else {
            VStack(spacing: 4) {
                HStack(spacing: 4) {
                    Tile(kind: act("feed"), name: "Feed", symbol: "drop.fill", tint: feedRose, bg: feedSoft, since: h.feedAt, note: note("feed"), live: false)
                    Tile(kind: act("diaper"), name: "Diaper", symbol: "sparkles", tint: diaperGold, bg: diaperSoft, since: h.diaperAt, note: note("diaper"), live: false)
                }
                HStack(spacing: 4) {
                    Tile(kind: act("pump"), name: "Pump", symbol: "bolt.heart.fill", tint: pumpPink, bg: pumpSoft, since: h.pumpAt, note: note("pump"), live: false)
                    Tile(kind: "sleep", name: "Awake", symbol: "sun.max.fill", tint: sleepBlue, bg: napSoft,
                         since: h.wakeAt, note: note("sleep") ?? "Tap: start sleep", live: false)
                }
            }
        }
    }
}

/// One tall button filling half a card: big icon, name, big time.
@available(iOS 16.2, *)
private struct BigTile: View {
    let kind: String, name: String, symbol: String, tint: Color, bg: Color, since: Date?, note: String?, live: Bool
    var body: some View {
        QuickButton(kind: kind) {
            VStack(spacing: 5) {
                ZStack {
                    Circle().fill(tint).frame(width: 62, height: 62)
                    Image(systemName: symbol).font(.system(size: 28, weight: .bold)).foregroundColor(ink)
                }
                Text(name).font(.system(size: 21, weight: .heavy, design: .rounded)).foregroundColor(.white.opacity(0.92)).lineLimit(1)
                Since(at: since).font(.system(size: 22, weight: .black, design: .rounded)).monospacedDigit()
                    .foregroundColor(.white).lineLimit(1).minimumScaleFactor(0.6).multilineTextAlignment(.center)
                if let note = note {
                    Text(note).font(.system(size: 11, weight: .bold, design: .rounded)).foregroundColor(.white.opacity(0.8)).lineLimit(1).minimumScaleFactor(0.7)
                }
            }
            .padding(.horizontal, 8)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(
                RoundedRectangle(cornerRadius: 20, style: .continuous)
                    .fill(LinearGradient(colors: [bg, bg.opacity(0.82)], startPoint: .topLeading, endPoint: .bottomTrailing))
            )
            .overlay(Paws().clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous)))
            .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(live ? tint : .clear, lineWidth: 3))
        }
    }
}

/// A choice button inside an opened card (e.g. "60 ml"): one tap logs it.
@available(iOS 16.2, *)
private struct Choice: View {
    let action: String, big: String, small: String?, tint: Color, bg: Color
    var on = false               // the usual choice: filled, so it's quick to spot
    var body: some View {
        QuickButton(kind: action) {
            VStack(spacing: 1) {
                Text(big).font(.system(size: 22, weight: .black, design: .rounded)).foregroundColor(on ? ink : .white).lineLimit(1).minimumScaleFactor(0.6)
                if let small = small {
                    Text(small).font(.system(size: 12, weight: .bold, design: .rounded)).foregroundColor(on ? ink.opacity(0.75) : .white.opacity(0.75)).lineLimit(1).minimumScaleFactor(0.7)
                }
            }
            .padding(.horizontal, 4)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(on ? tint : bg, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(Paws().clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous)))
            .overlay(RoundedRectangle(cornerRadius: 16, style: .continuous).stroke(tint.opacity(on ? 1 : 0.55), lineWidth: on ? 2.5 : 1.5))
        }
    }
}

/// ✕: close the choices without logging.
@available(iOS 16.2, *)
private struct CloseChoices: View {
    var body: some View {
        QuickButton(kind: "pick:none") {
            Image(systemName: "xmark").font(.system(size: 18, weight: .heavy)).foregroundColor(.white.opacity(0.85))
                .frame(width: 44).frame(maxHeight: .infinity)
                .background(Color.white.opacity(0.12), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
    }
}

/// Left-hand label of a row of choices ("Formula").
private struct RowLabel: View {
    let text: String, symbol: String, tint: Color
    var body: some View {
        VStack(spacing: 3) {
            Image(systemName: symbol).font(.system(size: 17, weight: .bold)).foregroundColor(tint)
            Text(text).font(.system(size: 12, weight: .heavy, design: .rounded)).foregroundColor(.white).lineLimit(1).minimumScaleFactor(0.7)
        }
        .frame(width: 70).frame(maxHeight: .infinity)
    }
}

@available(iOS 16.2, *)
private struct HubView: View {
    let ctx: ActivityViewContext<HoneyActivityAttributes>
    var body: some View {
        let h = ctx.state.hub ?? HoneyActivityAttributes.Hub(feedLbl: "Feed", diaperLbl: "Diaper", pumpLbl: "Pump")
        let note: (String) -> String? = { k in h.flashKind == k ? h.flash : nil }
        let sleeping = h.sleepAt != nil
        let fm = Array((h.feedMl ?? [30, 60, 90]).prefix(3)), fl = h.feedLbls ?? fm.map { "\($0) ml" }
        let pm = Array((h.pumpMl ?? [60, 120, 180]).prefix(4)), pl = h.pumpLbls ?? pm.map { "\($0) ml" }
        Group {
            if h.pick == "feed" {
                // Feed opened: Formula / Breastmilk rows of amounts
                HStack(spacing: 4) {
                    VStack(spacing: 4) {
                        ForEach(["formula", "breastmilk"], id: \.self) { t in
                            HStack(spacing: 4) {
                                RowLabel(text: t == "formula" ? "Formula" : "Breastmilk", symbol: t == "formula" ? "takeoutbag.and.cup.and.straw.fill" : "drop.fill", tint: feedRose)
                                ForEach(Array(fm.enumerated()), id: \.offset) { i, ml in
                                    Choice(action: "feed:\(t):\(ml)", big: i < fl.count ? fl[i] : "\(ml) ml", small: nil, tint: feedRose, bg: feedSoft, on: h.lastFeed == "\(t):\(ml)")
                                }
                            }
                        }
                    }
                    CloseChoices()
                }
            } else if h.pick == "diaper" {
                HStack(spacing: 4) {
                    Choice(action: "diaper:wet", big: "Pee", small: nil, tint: diaperGold, bg: diaperSoft, on: h.lastDiaper == "wet")
                    Choice(action: "diaper:dirty", big: "Poop", small: nil, tint: diaperGold, bg: diaperSoft, on: h.lastDiaper == "dirty")
                    Choice(action: "diaper:both", big: "Both", small: "Pee + Poop", tint: diaperGold, bg: diaperSoft, on: h.lastDiaper == "both")
                    CloseChoices()
                }
            } else if h.pick == "pump" {
                HStack(spacing: 4) {
                    ForEach(Array(pm.enumerated()), id: \.offset) { i, ml in
                        Choice(action: "pump:\(ml)", big: i < pl.count ? pl[i] : "\(ml) ml", small: h.pumpSide, tint: pumpPink, bg: pumpSoft, on: h.lastPump == ml)
                    }
                    CloseChoices()
                }
            } else {
                HubGrid(h: h)
            }
        }
        .transition(.identity)          // switch menus instantly, no slow cross-fade
        .animation(nil, value: h.pick)
        .frame(height: 158)
        .padding(1)
        .environment(\.hbCfg, h.cfg ?? "")
    }
}

@available(iOS 16.1, *)
private struct LockView: View {
    let ctx: ActivityViewContext<HoneyActivityAttributes>
    var body: some View {
        let kind = ctx.attributes.kind
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .center, spacing: 12) {
                Image(kind == "sleep" ? "GoldieSleepy" : "GoldieAwake").resizable().scaledToFill()
                    .frame(width: 46, height: 46).clipShape(Circle())
                    .overlay(Circle().stroke(accent(kind), lineWidth: 2.5))
                VStack(alignment: .leading, spacing: 2) {
                    Text(ctx.state.title).font(.system(size: 16, weight: .bold, design: .rounded)).foregroundColor(.white)
                    Text(ctx.attributes.babyName.isEmpty ? "Goldfox" : ctx.attributes.babyName)
                        .font(.system(size: 13, weight: .semibold, design: .rounded)).foregroundColor(.white.opacity(0.65))
                }
                Spacer()
                Elapsed(since: ctx.state.startedAt)
                    .font(.system(size: 30, weight: .heavy, design: .rounded))
                    .foregroundColor(accent(kind))
                    .multilineTextAlignment(.trailing)
                    .frame(maxWidth: 130, alignment: .trailing)
            }
            Buttons(ctx: ctx)
        }
        .padding(16)
    }
}

@available(iOS 16.1, *)
struct HoneyLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: HoneyActivityAttributes.self) { ctx in
            Group {
                if ctx.attributes.kind.hasPrefix("hub") { HubView(ctx: ctx) } else { LockView(ctx: ctx) }
            }
                .activityBackgroundTint(Color(red: 0.09, green: 0.10, blue: 0.15).opacity(0.92))
                .activitySystemActionForegroundColor(honey)
                .widgetURL(URL(string: ctx.attributes.kind.hasPrefix("hub") ? "honeybee://log" : "honeybee://open"))
        } dynamicIsland: { ctx in
            let hubSleep = ctx.state.hub?.sleepAt
            let kind = ctx.attributes.kind.hasPrefix("hub") ? (hubSleep != nil ? "sleep" : "feed") : ctx.attributes.kind
            let since = ctx.attributes.kind.hasPrefix("hub") ? (hubSleep ?? ctx.state.hub?.feedAt ?? Date()) : ctx.state.startedAt
            let title = ctx.attributes.kind.hasPrefix("hub") ? (hubSleep != nil ? "Sleeping" : "Since last feed") : ctx.state.title
            return DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label { Text(title).font(.system(size: 15, weight: .bold, design: .rounded)) }
                        icon: { Image(systemName: icon(kind)).foregroundColor(accent(kind)) }
                        .padding(.leading, 4)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Elapsed(since: since)
                        .font(.system(size: 22, weight: .heavy, design: .rounded))
                        .foregroundColor(accent(kind))
                        .frame(maxWidth: 110, alignment: .trailing)
                }
                DynamicIslandExpandedRegion(.bottom) {
                    if ctx.attributes.kind.hasPrefix("hub"), let h = ctx.state.hub { HubGrid(h: h).padding(.top, 4).environment(\.hbCfg, h.cfg ?? "") }
                    else { Buttons(ctx: ctx).padding(.top, 4) }
                }
            } compactLeading: {
                Image(systemName: icon(kind)).foregroundColor(accent(kind))
            } compactTrailing: {
                Elapsed(since: since).frame(maxWidth: 56).foregroundColor(accent(kind)).font(.system(size: 14, weight: .bold, design: .rounded))
            } minimal: {
                Image(systemName: icon(kind)).foregroundColor(accent(kind))
            }
            .widgetURL(URL(string: "honeybee://open"))
        }
    }
}
