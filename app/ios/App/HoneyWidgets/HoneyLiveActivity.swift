// Lock screen + Dynamic Island timer for a running sleep or breastfeed.
import WidgetKit
import SwiftUI
import ActivityKit
import AppIntents

private let honey = Color(red: 1.0, green: 0.76, blue: 0.12)
private let ink = Color(red: 0.10, green: 0.13, blue: 0.20)
private let sleepBlue = Color(red: 0.49, green: 0.61, blue: 1.0)
private let feedRose = Color(red: 1.0, green: 0.44, blue: 0.56)

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
private let diaperGold = Color(red: 0.96, green: 0.75, blue: 0.29)
private let pumpPink = Color(red: 1.0, green: 0.43, blue: 0.78)

private struct Since: View {
    let at: Date?
    var body: some View {
        // hours and minutes only ("1 hr, 14 min"), no ticking seconds
        if let at = at { Text(at, style: .relative) } else { Text("–") }
    }
}

@available(iOS 16.2, *)
private struct QuickButton<Label: View>: View {
    let kind: String
    @ViewBuilder let label: () -> Label
    var body: some View {
        if #available(iOS 17.0, *) {
            Button(intent: QuickAddIntent(kind: kind)) { label() }.buttonStyle(.plain)
        } else {
            Link(destination: URL(string: "honeybee://add/\(kind)")!) { label() }
        }
    }
}

// tile backgrounds = the app's dark category colours (same as the big tiles on Home)
private let feedSoft = Color(red: 0x8A/255, green: 0x2C/255, blue: 0x45/255)
private let diaperSoft = Color(red: 0x7D/255, green: 0x61/255, blue: 0x18/255)
private let pumpSoft = Color(red: 0x7C/255, green: 0x1F/255, blue: 0x5C/255)
private let napSoft = Color(red: 0x2D/255, green: 0x47/255, blue: 0x9C/255)

@available(iOS 16.2, *)
private struct Tile: View {
    let kind: String, name: String, symbol: String, tint: Color, bg: Color, since: Date?, note: String?, live: Bool
    var body: some View {
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
            .overlay(RoundedRectangle(cornerRadius: 18, style: .continuous).stroke(live ? tint : .clear, lineWidth: 2.5))
        }
    }
}

@available(iOS 16.2, *)
private struct HubGrid: View {
    let h: HoneyActivityAttributes.Hub
    func note(_ k: String) -> String? { h.flashKind == k ? h.flash : nil }
    var body: some View {
        let sleeping = h.sleepAt != nil
        VStack(spacing: 4) {
            HStack(spacing: 4) {
                Tile(kind: "feed", name: "Feed", symbol: "drop.fill", tint: feedRose, bg: feedSoft, since: h.feedAt, note: note("feed"), live: false)
                Tile(kind: "diaper", name: "Diaper", symbol: "sparkles", tint: diaperGold, bg: diaperSoft, since: h.diaperAt, note: note("diaper"), live: false)
            }
            HStack(spacing: 4) {
                Tile(kind: "pump", name: "Pump", symbol: "bolt.heart.fill", tint: pumpPink, bg: pumpSoft, since: h.pumpAt, note: note("pump"), live: false)
                Tile(kind: "sleep", name: sleeping ? "Sleeping" : "Awake", symbol: sleeping ? "moon.zzz.fill" : "sun.max.fill", tint: sleepBlue, bg: napSoft,
                     since: sleeping ? h.sleepAt : h.wakeAt, note: note("sleep"), live: sleeping)
            }
        }
    }
}

@available(iOS 16.2, *)
private struct HubView: View {
    let ctx: ActivityViewContext<HoneyActivityAttributes>
    var body: some View {
        HubGrid(h: ctx.state.hub ?? HoneyActivityAttributes.Hub(feedLbl: "Feed", diaperLbl: "Diaper", pumpLbl: "Pump"))
            .padding(1)
    }
}

@available(iOS 16.1, *)
private struct LockView: View {
    let ctx: ActivityViewContext<HoneyActivityAttributes>
    var body: some View {
        let kind = ctx.attributes.kind
        VStack(alignment: .leading, spacing: 12) {
            HStack(alignment: .center, spacing: 12) {
                ZStack {
                    Circle().fill(accent(kind)).frame(width: 40, height: 40)
                    Image(systemName: icon(kind)).font(.system(size: 18, weight: .bold)).foregroundColor(ink)
                }
                VStack(alignment: .leading, spacing: 2) {
                    Text(ctx.state.title).font(.system(size: 16, weight: .bold, design: .rounded)).foregroundColor(.white)
                    Text(ctx.attributes.babyName.isEmpty ? "Honey Bee" : ctx.attributes.babyName)
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
                if ctx.attributes.kind == "hub" { HubView(ctx: ctx) } else { LockView(ctx: ctx) }
            }
                .activityBackgroundTint(Color(red: 0.09, green: 0.10, blue: 0.15).opacity(0.92))
                .activitySystemActionForegroundColor(honey)
                .widgetURL(URL(string: ctx.attributes.kind == "hub" ? "honeybee://log" : "honeybee://open"))
        } dynamicIsland: { ctx in
            let hubSleep = ctx.state.hub?.sleepAt
            let kind = ctx.attributes.kind == "hub" ? (hubSleep != nil ? "sleep" : "feed") : ctx.attributes.kind
            let since = ctx.attributes.kind == "hub" ? (hubSleep ?? ctx.state.hub?.feedAt ?? Date()) : ctx.state.startedAt
            let title = ctx.attributes.kind == "hub" ? (hubSleep != nil ? "Sleeping" : "Since last feed") : ctx.state.title
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
                    if ctx.attributes.kind == "hub", let h = ctx.state.hub { HubGrid(h: h).padding(.top, 4) }
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
