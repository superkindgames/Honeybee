// Lock screen + Dynamic Island timer for a running sleep or breastfeed.
import WidgetKit
import SwiftUI
import ActivityKit

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
                .font(.system(size: 15, weight: .bold, design: .rounded))
                .padding(.horizontal, 14).padding(.vertical, 9)
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
            LockView(ctx: ctx)
                .activityBackgroundTint(Color(red: 0.09, green: 0.10, blue: 0.15).opacity(0.92))
                .activitySystemActionForegroundColor(honey)
                .widgetURL(URL(string: "honeybee://open"))
        } dynamicIsland: { ctx in
            let kind = ctx.attributes.kind
            return DynamicIsland {
                DynamicIslandExpandedRegion(.leading) {
                    Label { Text(ctx.state.title).font(.system(size: 15, weight: .bold, design: .rounded)) }
                        icon: { Image(systemName: icon(kind)).foregroundColor(accent(kind)) }
                        .padding(.leading, 4)
                }
                DynamicIslandExpandedRegion(.trailing) {
                    Elapsed(since: ctx.state.startedAt)
                        .font(.system(size: 22, weight: .heavy, design: .rounded))
                        .foregroundColor(accent(kind))
                        .frame(maxWidth: 110, alignment: .trailing)
                }
                DynamicIslandExpandedRegion(.bottom) { Buttons(ctx: ctx).padding(.top, 4) }
            } compactLeading: {
                Image(systemName: icon(kind)).foregroundColor(accent(kind))
            } compactTrailing: {
                Elapsed(since: ctx.state.startedAt).frame(maxWidth: 56).foregroundColor(accent(kind)).font(.system(size: 14, weight: .bold, design: .rounded))
            } minimal: {
                Image(systemName: icon(kind)).foregroundColor(accent(kind))
            }
            .widgetURL(URL(string: "honeybee://open"))
        }
    }
}
