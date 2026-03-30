import Foundation

enum EcoLevel: String, CaseIterable, Codable {
    case level1 = "Эко-новичок"
    case level2 = "Эко-исследователь"
    case level3 = "Эко-помощник"
    case level4 = "Хранитель природы"
    case level5 = "Зеленый герой"
    case level6 = "Эко-наставник"
    case level7 = "Защитник планеты"
    case level8 = "Мастер устойчивости"
    case level9 = "Амбассадор Eco Iz"
    case level10 = "Хранитель Земли"

    static func from(points: Int) -> EcoLevel {
        switch points {
        case 0..<200:
            return .level1
        case 200..<400:
            return .level2
        case 400..<700:
            return .level3
        case 700..<1100:
            return .level4
        case 1100..<1600:
            return .level5
        case 1600..<2200:
            return .level6
        case 2200..<3000:
            return .level7
        case 3000..<4000:
            return .level8
        case 4000..<5500:
            return .level9
        default:
            return .level10
        }
    }

    var number: Int {
        switch self {
        case .level1: return 1
        case .level2: return 2
        case .level3: return 3
        case .level4: return 4
        case .level5: return 5
        case .level6: return 6
        case .level7: return 7
        case .level8: return 8
        case .level9: return 9
        case .level10: return 10
        }
    }

    var lowerBound: Int {
        switch self {
        case .level1: return 0
        case .level2: return 200
        case .level3: return 400
        case .level4: return 700
        case .level5: return 1100
        case .level6: return 1600
        case .level7: return 2200
        case .level8: return 3000
        case .level9: return 4000
        case .level10: return 5500
        }
    }

    var upperBoundExclusive: Int? {
        switch self {
        case .level1: return 200
        case .level2: return 400
        case .level3: return 700
        case .level4: return 1100
        case .level5: return 1600
        case .level6: return 2200
        case .level7: return 3000
        case .level8: return 4000
        case .level9: return 5500
        case .level10: return nil
        }
    }
}

enum ActivityCategory: String, CaseIterable, Identifiable, Codable {
    case transport = "Транспорт"
    case plastic = "Пластик"
    case water = "Вода"
    case waste = "Отходы"
    case energy = "Энергия"
    case custom = "Своя активность"

    var id: String { rawValue }
}

struct ActivityTemplate: Identifiable {
    let id = UUID()
    let title: String
    let estimatedCO2: Double
    let points: Int
}

struct EcoActivity: Identifiable, Decodable {
    let id: String
    let category: ActivityCategory
    let title: String
    let co2Saved: Double
    let points: Int
    let createdAt: Date

    init(
        id: String = UUID().uuidString,
        category: ActivityCategory,
        title: String,
        co2Saved: Double,
        points: Int,
        createdAt: Date
    ) {
        self.id = id
        self.category = category
        self.title = title
        self.co2Saved = co2Saved
        self.points = points
        self.createdAt = createdAt
    }

    private enum CodingKeys: String, CodingKey {
        case id
        case category
        case title
        case co2Saved
        case co2_saved
        case points
        case createdAt
        case created_at
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        let rawCategory = try container.decodeIfPresent(String.self, forKey: .category) ?? ActivityCategory.custom.rawValue
        category = ActivityCategory(rawValue: rawCategory) ?? .custom
        title = try container.decodeIfPresent(String.self, forKey: .title) ?? "Активность"
        co2Saved =
            try container.decodeIfPresent(Double.self, forKey: .co2Saved)
            ?? container.decodeIfPresent(Double.self, forKey: .co2_saved)
            ?? 0
        points = try container.decodeIfPresent(Int.self, forKey: .points) ?? 0
        createdAt =
            try container.decodeIfPresent(Date.self, forKey: .createdAt)
            ?? container.decodeIfPresent(Date.self, forKey: .created_at)
            ?? .now
    }
}

struct UserProfile: Decodable {
    let id: String
    var fullName: String
    var email: String
    var points: Int
    var streakDays: Int
    var co2SavedTotal: Double

    var level: EcoLevel {
        EcoLevel.from(points: points)
    }

    init(
        id: String = "local-user",
        fullName: String,
        email: String,
        points: Int,
        streakDays: Int,
        co2SavedTotal: Double
    ) {
        self.id = id
        self.fullName = fullName
        self.email = email
        self.points = points
        self.streakDays = streakDays
        self.co2SavedTotal = co2SavedTotal
    }

    private enum CodingKeys: String, CodingKey {
        case id
        case fullName
        case full_name
        case username
        case email
        case points
        case ecoPoints
        case streakDays
        case streak_days
        case co2SavedTotal
        case co2_saved_total
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? "local-user"
        fullName =
            try container.decodeIfPresent(String.self, forKey: .fullName)
            ?? container.decodeIfPresent(String.self, forKey: .full_name)
            ?? container.decodeIfPresent(String.self, forKey: .username)
            ?? "Пользователь"
        email = try container.decodeIfPresent(String.self, forKey: .email) ?? "user@ecoiz.app"
        points =
            try container.decodeIfPresent(Int.self, forKey: .points)
            ?? container.decodeIfPresent(Int.self, forKey: .ecoPoints)
            ?? 0
        streakDays =
            try container.decodeIfPresent(Int.self, forKey: .streakDays)
            ?? container.decodeIfPresent(Int.self, forKey: .streak_days)
            ?? 0
        co2SavedTotal =
            try container.decodeIfPresent(Double.self, forKey: .co2SavedTotal)
            ?? container.decodeIfPresent(Double.self, forKey: .co2_saved_total)
            ?? 0
    }
}

struct CommunityImpact: Decodable {
    let totalUsers: Int
    let activeUsers: Int
    let totalActivities: Int
    let totalPosts: Int
    let totalChallengesCompleted: Int
    let totalCo2Saved: Double
    let totalPoints: Int

    private enum CodingKeys: String, CodingKey {
        case totalUsers
        case total_users
        case activeUsers
        case active_users
        case totalActivities
        case total_activities
        case totalPosts
        case total_posts
        case totalChallengesCompleted
        case total_challenges_completed
        case totalCo2Saved
        case total_co2_saved
        case totalPoints
        case total_points
    }

    init(
        totalUsers: Int,
        activeUsers: Int,
        totalActivities: Int,
        totalPosts: Int,
        totalChallengesCompleted: Int,
        totalCo2Saved: Double,
        totalPoints: Int
    ) {
        self.totalUsers = totalUsers
        self.activeUsers = activeUsers
        self.totalActivities = totalActivities
        self.totalPosts = totalPosts
        self.totalChallengesCompleted = totalChallengesCompleted
        self.totalCo2Saved = totalCo2Saved
        self.totalPoints = totalPoints
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        totalUsers =
            try container.decodeIfPresent(Int.self, forKey: .totalUsers)
            ?? container.decodeIfPresent(Int.self, forKey: .total_users)
            ?? 0
        activeUsers =
            try container.decodeIfPresent(Int.self, forKey: .activeUsers)
            ?? container.decodeIfPresent(Int.self, forKey: .active_users)
            ?? 0
        totalActivities =
            try container.decodeIfPresent(Int.self, forKey: .totalActivities)
            ?? container.decodeIfPresent(Int.self, forKey: .total_activities)
            ?? 0
        totalPosts =
            try container.decodeIfPresent(Int.self, forKey: .totalPosts)
            ?? container.decodeIfPresent(Int.self, forKey: .total_posts)
            ?? 0
        totalChallengesCompleted =
            try container.decodeIfPresent(Int.self, forKey: .totalChallengesCompleted)
            ?? container.decodeIfPresent(Int.self, forKey: .total_challenges_completed)
            ?? 0
        totalCo2Saved =
            try container.decodeIfPresent(Double.self, forKey: .totalCo2Saved)
            ?? container.decodeIfPresent(Double.self, forKey: .total_co2_saved)
            ?? 0
        totalPoints =
            try container.decodeIfPresent(Int.self, forKey: .totalPoints)
            ?? container.decodeIfPresent(Int.self, forKey: .total_points)
            ?? 0
    }
}

struct Challenge: Identifiable, Decodable {
    let id: String
    let title: String
    let description: String
    let targetCount: Int
    var currentCount: Int
    let rewardPoints: Int
    let badgeSymbol: String
    let badgeTintHex: UInt32
    let badgeBackgroundHex: UInt32
    var isClaimed: Bool

    var isCompleted: Bool {
        currentCount >= targetCount
    }

    init(
        id: String = UUID().uuidString,
        title: String,
        description: String,
        targetCount: Int,
        currentCount: Int,
        rewardPoints: Int,
        badgeSymbol: String,
        badgeTintHex: UInt32,
        badgeBackgroundHex: UInt32,
        isClaimed: Bool = false
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.targetCount = targetCount
        self.currentCount = currentCount
        self.rewardPoints = rewardPoints
        self.badgeSymbol = badgeSymbol
        self.badgeTintHex = badgeTintHex
        self.badgeBackgroundHex = badgeBackgroundHex
        self.isClaimed = isClaimed
    }

    private enum CodingKeys: String, CodingKey {
        case id
        case title
        case description
        case targetCount
        case target_count
        case currentCount
        case current_count
        case rewardPoints
        case reward_points
        case badgeSymbol
        case badge_symbol
        case badgeTintHex
        case badge_tint_hex
        case badgeBackgroundHex
        case badge_background_hex
        case isCompleted
        case is_completed
        case isClaimed
        case is_claimed
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        title = try container.decodeIfPresent(String.self, forKey: .title) ?? "Челлендж"
        description = try container.decodeIfPresent(String.self, forKey: .description) ?? ""
        targetCount =
            try container.decodeIfPresent(Int.self, forKey: .targetCount)
            ?? container.decodeIfPresent(Int.self, forKey: .target_count)
            ?? 1
        currentCount =
            try container.decodeIfPresent(Int.self, forKey: .currentCount)
            ?? container.decodeIfPresent(Int.self, forKey: .current_count)
            ?? 0
        rewardPoints =
            try container.decodeIfPresent(Int.self, forKey: .rewardPoints)
            ?? container.decodeIfPresent(Int.self, forKey: .reward_points)
            ?? 0
        badgeSymbol =
            try container.decodeIfPresent(String.self, forKey: .badgeSymbol)
            ?? container.decodeIfPresent(String.self, forKey: .badge_symbol)
            ?? "star.fill"
        badgeTintHex = try container.decodeIfPresent(UInt32.self, forKey: .badgeTintHex)
            ?? container.decodeIfPresent(UInt32.self, forKey: .badge_tint_hex)
            ?? 0x43B244
        badgeBackgroundHex = try container.decodeIfPresent(UInt32.self, forKey: .badgeBackgroundHex)
            ?? container.decodeIfPresent(UInt32.self, forKey: .badge_background_hex)
            ?? 0xEAF8DF
        isClaimed =
            try container.decodeIfPresent(Bool.self, forKey: .isClaimed)
            ?? container.decodeIfPresent(Bool.self, forKey: .is_claimed)
            ?? false
    }
}

enum PostMediaKind: String, Codable {
    case photo
    case video
}

struct PostMediaAttachment: Identifiable, Codable {
    let id: String
    let kind: PostMediaKind
    let data: Data

    private enum CodingKeys: String, CodingKey {
        case id
        case kind
        case base64Data
        case base64_data
        case data
    }

    init(id: String = UUID().uuidString, kind: PostMediaKind, data: Data) {
        self.id = id
        self.kind = kind
        self.data = data
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        kind = try container.decodeIfPresent(PostMediaKind.self, forKey: .kind) ?? .photo
        let base64 =
            try container.decodeIfPresent(String.self, forKey: .base64Data)
            ?? container.decodeIfPresent(String.self, forKey: .base64_data)
            ?? container.decodeIfPresent(String.self, forKey: .data)
            ?? ""
        guard let decoded = Data(base64Encoded: base64) else {
            throw DecodingError.dataCorruptedError(forKey: .base64Data, in: container, debugDescription: "Invalid base64 media data")
        }
        data = decoded
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(id, forKey: .id)
        try container.encode(kind, forKey: .kind)
        try container.encode(data.base64EncodedString(), forKey: .base64Data)
    }
}

struct EcoPost: Identifiable, Decodable {
    let id: String
    let author: String
    let text: String
    let createdAt: Date
    let media: [PostMediaAttachment]

    init(
        id: String = UUID().uuidString,
        author: String,
        text: String,
        createdAt: Date,
        media: [PostMediaAttachment]
    ) {
        self.id = id
        self.author = author
        self.text = text
        self.createdAt = createdAt
        self.media = media
    }

    private enum CodingKeys: String, CodingKey {
        case id
        case author
        case author_name
        case username
        case text
        case content
        case createdAt
        case created_at
        case media
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        author =
            try container.decodeIfPresent(String.self, forKey: .author)
            ?? container.decodeIfPresent(String.self, forKey: .author_name)
            ?? container.decodeIfPresent(String.self, forKey: .username)
            ?? "Пользователь"
        text =
            try container.decodeIfPresent(String.self, forKey: .text)
            ?? container.decodeIfPresent(String.self, forKey: .content)
            ?? ""
        createdAt =
            try container.decodeIfPresent(Date.self, forKey: .createdAt)
            ?? container.decodeIfPresent(Date.self, forKey: .created_at)
            ?? .now
        media = try container.decodeIfPresent([PostMediaAttachment].self, forKey: .media) ?? []
    }
}

struct ChatMessage: Identifiable, Decodable {
    let id: String
    let isUser: Bool
    let text: String
    let createdAt: Date

    init(id: String = UUID().uuidString, isUser: Bool, text: String, createdAt: Date) {
        self.id = id
        self.isUser = isUser
        self.text = text
        self.createdAt = createdAt
    }

    private enum CodingKeys: String, CodingKey {
        case id
        case isUser
        case is_user
        case role
        case text
        case createdAt
        case created_at
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        if let explicitIsUser = try container.decodeIfPresent(Bool.self, forKey: .isUser)
            ?? container.decodeIfPresent(Bool.self, forKey: .is_user) {
            isUser = explicitIsUser
        } else {
            let role = try container.decodeIfPresent(String.self, forKey: .role)?.lowercased()
            isUser = role == "user"
        }
        text = try container.decodeIfPresent(String.self, forKey: .text) ?? ""
        createdAt =
            try container.decodeIfPresent(Date.self, forKey: .createdAt)
            ?? container.decodeIfPresent(Date.self, forKey: .created_at)
            ?? .now
    }
}
