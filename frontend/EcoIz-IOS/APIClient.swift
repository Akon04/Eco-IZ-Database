import Foundation

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse(String? = nil)
    case server(String)
    case unauthorized

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Некорректный адрес backend."
        case .invalidResponse(let message):
            return message ?? "Backend вернул некорректный ответ."
        case .server(let message):
            return message
        case .unauthorized:
            return "Сессия истекла. Войди снова."
        }
    }
}

private struct APIErrorResponse: Decodable {
    let error: String?
    let detail: String?
    let message: String?

    var resolvedMessage: String? {
        let candidates = [error, detail, message]
        return candidates
            .compactMap { $0?.trimmingCharacters(in: .whitespacesAndNewlines) }
            .first(where: { !$0.isEmpty })
    }
}

struct AuthSessionResponse: Decodable {
    let token: String
    let user: UserProfile

    private enum CodingKeys: String, CodingKey {
        case token
        case accessToken
        case access_token
        case user
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        token =
            try container.decodeIfPresent(String.self, forKey: .token)
            ?? container.decodeIfPresent(String.self, forKey: .accessToken)
            ?? container.decodeIfPresent(String.self, forKey: .access_token)
            ?? ""
        user = try container.decode(UserProfile.self, forKey: .user)
    }
}

struct BootstrapResponse: Decodable {
    let user: UserProfile
    let activities: [EcoActivity]
    let challenges: [Challenge]
    let posts: [EcoPost]
    let chatMessages: [ChatMessage]
    let communityImpact: CommunityImpact

    private enum CodingKeys: String, CodingKey {
        case user
        case activities
        case challenges
        case posts
        case chatMessages
        case communityImpact
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        user = try container.decode(UserProfile.self, forKey: .user)
        activities = try container.decodeIfPresent([EcoActivity].self, forKey: .activities) ?? []
        challenges = try container.decodeIfPresent([Challenge].self, forKey: .challenges) ?? []
        posts = try container.decodeIfPresent([EcoPost].self, forKey: .posts) ?? []
        chatMessages = try container.decodeIfPresent([ChatMessage].self, forKey: .chatMessages) ?? []
        communityImpact = try container.decodeIfPresent(CommunityImpact.self, forKey: .communityImpact)
            ?? CommunityImpact(
                totalUsers: 0,
                activeUsers: 0,
                totalActivities: activities.count,
                totalPosts: posts.count,
                totalChallengesCompleted: challenges.filter(\.isCompleted).count,
                totalCo2Saved: activities.reduce(0) { $0 + $1.co2Saved },
                totalPoints: max(user.points, activities.reduce(0) { $0 + $1.points })
            )
    }
}

struct ActivityMutationResponse: Decodable {
    let activity: EcoActivity
    let user: UserProfile
    let challenges: [Challenge]
}

struct ChallengeClaimResponse: Decodable {
    let user: UserProfile
    let challenge: Challenge
    let challenges: [Challenge]
}

private struct PostEnvelope: Decodable {
    let post: EcoPost
}

private struct PostsEnvelope: Decodable {
    let posts: [EcoPost]

    init(from decoder: Decoder) throws {
        if let container = try? decoder.singleValueContainer(),
           let items = try? container.decode([EcoPost].self) {
            posts = items
            return
        }

        let keyed = try decoder.container(keyedBy: CodingKeys.self)
        posts = try keyed.decodeIfPresent([EcoPost].self, forKey: .posts) ?? []
    }

    private enum CodingKeys: String, CodingKey {
        case posts
        case data
    }
}

private struct ChatEnvelope: Decodable {
    let messages: [ChatMessage]

    init(from decoder: Decoder) throws {
        if let container = try? decoder.singleValueContainer(),
           let items = try? container.decode([ChatMessage].self) {
            messages = items
            return
        }

        let keyed = try decoder.container(keyedBy: CodingKeys.self)
        messages =
            try keyed.decodeIfPresent([ChatMessage].self, forKey: .messages)
            ?? keyed.decodeIfPresent([ChatMessage].self, forKey: .data)
            ?? []
    }

    private enum CodingKeys: String, CodingKey {
        case messages
        case data
    }
}

private struct LoginRequest: Encodable {
    let email: String
    let password: String
}

private struct RegisterRequest: Encodable {
    let fullName: String
    let email: String
    let password: String
}

private struct ActivityRequest: Encodable {
    let category: String
    let title: String
    let co2Saved: Double
    let points: Int
    let note: String
    let media: [PostMediaAttachment]
    let shareToNews: Bool
}

private struct PostRequest: Encodable {
    let text: String
    let media: [PostMediaAttachment]
}

private struct ChatRequest: Encodable {
    let text: String
}

final class APIClient {
    private let session: URLSession
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder
    private let tokenKey = "ecoiz.backend.token"
    private let baseURL: URL

    init(session: URLSession = .shared) {
        self.session = session
        self.encoder = APIClient.makeEncoder()
        self.decoder = APIClient.makeDecoder()
        guard let url = URL(string: Self.resolveBaseURL()) else {
            fatalError("Invalid EcoIZ backend URL")
        }
        self.baseURL = url
    }

    var hasStoredToken: Bool {
        storedToken != nil
    }

    func clearToken() {
        UserDefaults.standard.removeObject(forKey: tokenKey)
    }

    func login(email: String, password: String) async throws -> AuthSessionResponse {
        let response: AuthSessionResponse = try await request(
            path: "/auth/login",
            method: "POST",
            body: LoginRequest(email: email, password: password),
            requiresAuth: false
        )
        storedToken = response.token
        return response
    }

    func register(name: String, email: String, password: String) async throws -> AuthSessionResponse {
        let response: AuthSessionResponse = try await request(
            path: "/auth/register",
            method: "POST",
            body: RegisterRequest(fullName: name, email: email, password: password),
            requiresAuth: false
        )
        storedToken = response.token
        return response
    }

    func bootstrap() async throws -> BootstrapResponse {
        try await request(path: "/bootstrap", method: "GET", requiresAuth: true)
    }

    func fetchPosts() async throws -> [EcoPost] {
        let response: PostsEnvelope = try await request(path: "/posts", method: "GET", requiresAuth: true)
        return response.posts
    }

    func addActivity(
        category: ActivityCategory,
        title: String,
        co2: Double,
        points: Int,
        note: String?,
        media: [PostMediaAttachment],
        shareToNews: Bool
    ) async throws -> ActivityMutationResponse {
        try await request(
            path: "/activities",
            method: "POST",
            body: ActivityRequest(
                category: category.rawValue,
                title: title,
                co2Saved: co2,
                points: points,
                note: note ?? "",
                media: media,
                shareToNews: shareToNews
            ),
            requiresAuth: true
        )
    }

    func addPost(text: String, media: [PostMediaAttachment]) async throws -> EcoPost {
        let response: PostEnvelope = try await request(
            path: "/posts",
            method: "POST",
            body: PostRequest(text: text, media: media),
            requiresAuth: true
        )
        return response.post
    }

    func sendMessage(_ text: String) async throws -> [ChatMessage] {
        let response: ChatEnvelope = try await request(
            path: "/chat/messages",
            method: "POST",
            body: ChatRequest(text: text),
            requiresAuth: true
        )
        return response.messages
    }

    func claimChallenge(id: String) async throws -> ChallengeClaimResponse {
        try await request(
            path: "/challenges/\(id)/claim",
            method: "POST",
            requiresAuth: true
        )
    }

    private func request<Response: Decodable>(
        path: String,
        method: String,
        requiresAuth: Bool
    ) async throws -> Response {
        try await request(path: path, method: method, body: Optional<String>.none, requiresAuth: requiresAuth)
    }

    private func request<Response: Decodable, Body: Encodable>(
        path: String,
        method: String,
        body: Body?,
        requiresAuth: Bool
    ) async throws -> Response {
        let endpoint = baseURL.appendingPathComponent(path.trimmingCharacters(in: CharacterSet(charactersIn: "/")))
        var request = URLRequest(url: endpoint)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if requiresAuth {
            guard let storedToken else {
                throw APIError.unauthorized
            }
            request.setValue("Bearer \(storedToken)", forHTTPHeaderField: "Authorization")
        }

        if let body {
            request.httpBody = try encoder.encode(body)
        }

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse()
        }

        if httpResponse.statusCode == 401 {
            clearToken()
            throw APIError.unauthorized
        }

        guard (200...299).contains(httpResponse.statusCode) else {
            if let errorResponse = try? decoder.decode(APIErrorResponse.self, from: data) {
                throw APIError.server(
                    errorResponse.resolvedMessage ?? HTTPURLResponse.localizedString(forStatusCode: httpResponse.statusCode)
                )
            }
            if let rawBody = String(data: data, encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines),
               !rawBody.isEmpty {
                throw APIError.server(rawBody)
            }
            throw APIError.invalidResponse()
        }

        do {
            return try decoder.decode(Response.self, from: data)
        } catch {
            let decodeMessage = describeDecodingError(error, path: path)
            #if DEBUG
            let rawBody = String(data: data, encoding: .utf8) ?? "<non-utf8>"
            print("EcoIZ decode error for \(path): \(error)")
            print("EcoIZ raw response: \(rawBody)")
            #endif
            throw APIError.invalidResponse(decodeMessage)
        }
    }

    private var storedToken: String? {
        get { UserDefaults.standard.string(forKey: tokenKey) }
        set {
            if let newValue {
                UserDefaults.standard.set(newValue, forKey: tokenKey)
            } else {
                UserDefaults.standard.removeObject(forKey: tokenKey)
            }
        }
    }

    private static func resolveBaseURL() -> String {
        if let override = validatedBaseURLOverride() {
            return override
        }

        #if targetEnvironment(simulator)
        return "http://127.0.0.1:8000"
        #else
        return "http://MacBook-Pro--Erke.local:8000"
        #endif
    }

    private static func validatedBaseURLOverride() -> String? {
        guard let rawOverride = UserDefaults.standard.string(forKey: "ecoiz.backend.baseURLOverride")?
            .trimmingCharacters(in: .whitespacesAndNewlines),
            !rawOverride.isEmpty,
            let url = URL(string: rawOverride),
            let scheme = url.scheme?.lowercased(),
            let host = url.host?.lowercased()
        else {
            return nil
        }

        guard scheme == "http" || scheme == "https" else {
            UserDefaults.standard.removeObject(forKey: "ecoiz.backend.baseURLOverride")
            return nil
        }

        let isAllowedHost =
            host == "127.0.0.1" ||
            host == "localhost" ||
            host.hasSuffix(".local") ||
            host.hasPrefix("192.168.") ||
            host.hasPrefix("10.") ||
            host.hasPrefix("172.16.") ||
            host.hasPrefix("172.17.") ||
            host.hasPrefix("172.18.") ||
            host.hasPrefix("172.19.") ||
            host.hasPrefix("172.2") ||
            host.hasPrefix("172.30.") ||
            host.hasPrefix("172.31.")

        guard isAllowedHost else {
            UserDefaults.standard.removeObject(forKey: "ecoiz.backend.baseURLOverride")
            return nil
        }

        return rawOverride
    }

    private static func makeDecoder() -> JSONDecoder {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .custom { value in
            let container = try value.singleValueContainer()
            let raw = try container.decode(String.self)
            if let date = DateParsing.iso8601WithFractional.date(from: raw)
                ?? DateParsing.iso8601.date(from: raw)
                ?? DateParsing.postgresFractional.date(from: raw)
                ?? DateParsing.postgres.date(from: raw) {
                return date
            }
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Unsupported date: \(raw)")
        }
        return decoder
    }

    private static func makeEncoder() -> JSONEncoder {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .custom { date, encoder in
            var container = encoder.singleValueContainer()
            try container.encode(DateParsing.iso8601WithFractional.string(from: date))
        }
        return encoder
    }

    private func describeDecodingError(_ error: Error, path: String) -> String {
        guard let decodingError = error as? DecodingError else {
            return "Backend вернул некорректный ответ для \(path)."
        }

        switch decodingError {
        case .typeMismatch(_, let context):
            return "Некорректный тип данных в \(codingPathDescription(context.codingPath)) для \(path)."
        case .valueNotFound(_, let context):
            return "В ответе нет значения \(codingPathDescription(context.codingPath)) для \(path)."
        case .keyNotFound(let key, let context):
            let pathWithKey = codingPathDescription(context.codingPath + [key])
            return "В ответе отсутствует поле \(pathWithKey) для \(path)."
        case .dataCorrupted(let context):
            return context.debugDescription.isEmpty
                ? "Поврежденные данные в ответе \(path)."
                : "\(context.debugDescription) (\(path))."
        @unknown default:
            return "Backend вернул неподдерживаемый формат ответа для \(path)."
        }
    }

    private func codingPathDescription(_ codingPath: [CodingKey]) -> String {
        let path = codingPath.map(\.stringValue).joined(separator: ".")
        return path.isEmpty ? "корневом объекте" : path
    }
}

enum DateParsing {
    static let iso8601WithFractional: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter
    }()

    static let iso8601: ISO8601DateFormatter = {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        return formatter
    }()

    static let postgresFractional: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
        return formatter
    }()

    static let postgres: DateFormatter = {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(secondsFromGMT: 0)
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        return formatter
    }()
}
