// Shared by the app and the widget extension: what a lock-screen timer (Live Activity) shows.
import Foundation
#if canImport(ActivityKit)
import ActivityKit

@available(iOS 16.1, *)
struct HoneyActivityAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var title: String        // "Sleeping" or "Breastfeeding · Left"
        var startedAt: Date      // the timer counts up from here
        var side: String?        // "L" / "R" while breastfeeding
    }
    var kind: String             // "sleep" or "feed"
    var babyName: String
}
#endif
