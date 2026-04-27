import SwiftUI
import PhotosUI
import UniformTypeIdentifiers

private extension ActivityCategory {
    var systemIconName: String {
        switch self {
        case .transport: return "figure.walk"
        case .plastic: return "bag"
        case .water: return "drop"
        case .waste: return "arrow.3.trianglepath"
        case .energy: return "bolt"
        case .custom: return "sparkles"
        }
    }

    var tintColor: Color {
        switch self {
        case .transport: return Color(hex: 0xFF9D1F)
        case .plastic: return Color(hex: 0x20D8C3)
        case .water: return Color(hex: 0x2DA9F5)
        case .waste: return Color(hex: 0x69D85A)
        case .energy: return Color(hex: 0xF2BF18)
        case .custom: return EcoTheme.primary
        }
    }

    var shortDescription: String {
        switch self {
        case .transport: return "Поездки и маршруты"
        case .plastic: return "Без одноразового"
        case .water: return "Экономия воды"
        case .waste: return "Сортировка и переработка"
        case .energy: return "Свет и электроприборы"
        case .custom: return "Своя эко-инициатива"
        }
    }

    var highlightGradient: [Color] {
        switch self {
        case .transport: return [Color(hex: 0xFFC86A), Color(hex: 0xFF9D1F)]
        case .plastic: return [Color(hex: 0x74F2E0), Color(hex: 0x20D8C3)]
        case .water: return [Color(hex: 0x7DD4FF), Color(hex: 0x2DA9F5)]
        case .waste: return [Color(hex: 0x8BEA74), Color(hex: 0x69D85A)]
        case .energy: return [Color(hex: 0xFFE06E), Color(hex: 0xF2BF18)]
        case .custom: return [Color(hex: 0xC9F18D), EcoTheme.primary]
        }
    }

    var pageGradient: [Color] {
        switch self {
        case .transport: return [Color(hex: 0xFFC86A), Color(hex: 0xFFB33E), Color(hex: 0xFF9D1F)]
        case .plastic: return [Color(hex: 0x74F2E0), Color(hex: 0x42E2CE), Color(hex: 0x20D8C3)]
        case .water: return [Color(hex: 0x7DD4FF), Color(hex: 0x50BDF9), Color(hex: 0x2DA9F5)]
        case .waste: return [Color(hex: 0x95ED7C), Color(hex: 0x78E163), Color(hex: 0x69D85A)]
        case .energy: return [Color(hex: 0xFFE06E), Color(hex: 0xF8CD33), Color(hex: 0xF2BF18)]
        case .custom: return [Color(hex: 0x9FBEFF), Color(hex: 0x7DA6FF), EcoTheme.primary]
        }
    }
}

struct AuthView: View {
    @EnvironmentObject private var appState: AppState
    @State private var stage: AuthStage = .welcome
    @State private var fullName = ""
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""

    private var canLogin: Bool {
        !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !password.isEmpty
    }

    private var canRegister: Bool {
        !fullName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !email.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
        !password.isEmpty &&
        password == confirmPassword
    }

    private var passwordHint: String? {
        guard !confirmPassword.isEmpty else { return nil }
        return password == confirmPassword ? nil : "Пароли не совпадают"
    }

    var body: some View {
        NavigationStack {
            GeometryReader { proxy in
                let compact = proxy.size.width < 390

                ZStack {
                    EcoBackground()

                    ScrollView(showsIndicators: false) {
                    VStack(spacing: compact ? 14 : 18) {
                        HStack {
                            if stage != .welcome {
                                Button {
                                    withAnimation(.spring(response: 0.3, dampingFraction: 0.85)) {
                                        switch stage {
                                        case .login, .register:
                                            stage = .welcome
                                        case .welcome:
                                            break
                                        }
                                    }
                                } label: {
                                    Image(systemName: "chevron.left")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundStyle(EcoTheme.ink)
                                        .frame(width: 36, height: 36)
                                        .background(EcoTheme.elevatedCard, in: Circle())
                                        .overlay(Circle().stroke(EcoTheme.surfaceStroke, lineWidth: 1))
                                }
                                .buttonStyle(.plain)
                            }
                            Spacer()
                        }
                        .padding(.top, compact ? 8 : 12)

                        VStack(spacing: 10) {
                            Image("AuthGlobe")
                                .resizable()
                                .scaledToFit()
                                .frame(width: compact ? 112 : 132, height: compact ? 112 : 132)
                                .shadow(color: Color.black.opacity(0.1), radius: 12, y: 5)

                            Image("AuthWordmark")
                                .resizable()
                                .scaledToFit()
                                .frame(width: compact ? 170 : 194)
                        }
                        .padding(.top, compact ? 4 : 8)

                        switch stage {
                        case .welcome:
                            VStack(spacing: 14) {
                                VStack(spacing: 10) {
                                    Text("Маленькие шаги каждый день")
                                        .font(EcoTypography.title2)
                                        .foregroundStyle(EcoTheme.ink)
                                        .multilineTextAlignment(.center)
                                        .lineSpacing(2)

                                    Text("Добавляй эко-активности, собирай серию и расти в уровне.")
                                        .font(EcoTypography.footnote)
                                        .foregroundStyle(EcoTheme.secondaryText.opacity(0.9))
                                        .multilineTextAlignment(.center)
                                        .lineSpacing(2)
                                }
                                .padding(.vertical, 12)

                                VStack(spacing: 10) {
                                    Button("Войти") {
                                        withAnimation(.spring(response: 0.3, dampingFraction: 0.85)) {
                                            stage = .login
                                        }
                                    }
                                    .buttonStyle(DuoPrimaryButtonStyle())

                                    Button("Создать аккаунт") {
                                        withAnimation(.spring(response: 0.3, dampingFraction: 0.85)) {
                                            stage = .register
                                        }
                                    }
                                    .buttonStyle(DuoSecondaryButtonStyle())
                                }
                            }
                            .padding(.top, 4)

                        case .login:
                            VStack(spacing: 12) {
                                Text("Рады видеть тебя снова")
                                    .font(EcoTypography.title2)
                                    .foregroundStyle(EcoTheme.ink)

                                DuoInputField(title: "Эл. почта", text: $email)
                                    .textInputAutocapitalization(.never)
                                    .keyboardType(.emailAddress)
                                DuoInputSecureField(title: "Пароль", text: $password)

                                if appState.isAuthenticating {
                                    ProgressView()
                                        .tint(EcoTheme.primary)
                                }

                                Button("Войти") {
                                    Task {
                                        _ = await appState.signIn(email: email, password: password)
                                    }
                                }
                                .buttonStyle(DuoPrimaryButtonStyle())
                                .disabled(!canLogin || appState.isAuthenticating)
                                .opacity((canLogin && !appState.isAuthenticating) ? 1 : 0.55)

                                Button("Нет аккаунта? Зарегистрироваться") {
                                    withAnimation(.spring(response: 0.3, dampingFraction: 0.85)) {
                                        stage = .register
                                    }
                                }
                                .font(EcoTypography.subheadline)
                                .foregroundStyle(EcoTheme.primary)
                                .buttonStyle(.plain)
                            }
                            .duoCard()

                        case .register:
                            VStack(spacing: 12) {
                                Text("Создай аккаунт")
                                    .font(EcoTypography.title2)
                                    .foregroundStyle(EcoTheme.ink)

                                DuoInputField(title: "ФИО", text: $fullName)
                                DuoInputField(title: "Эл. почта", text: $email)
                                    .textInputAutocapitalization(.never)
                                    .keyboardType(.emailAddress)
                                DuoInputSecureField(title: "Пароль", text: $password)
                                DuoInputSecureField(title: "Подтверди пароль", text: $confirmPassword)

                                if let passwordHint {
                                    Text(passwordHint)
                                        .font(EcoTypography.caption)
                                        .foregroundStyle(Color.red.opacity(0.8))
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }

                                if appState.isAuthenticating {
                                    ProgressView()
                                        .tint(EcoTheme.primary)
                                }

                                Button("Создать аккаунт") {
                                    Task {
                                        _ = await appState.register(name: fullName, email: email, password: password)
                                    }
                                }
                                .buttonStyle(DuoPrimaryButtonStyle())
                                .disabled(!canRegister || appState.isAuthenticating)
                                .opacity((canRegister && !appState.isAuthenticating) ? 1 : 0.55)
                            }
                            .duoCard()
                        }

                        Spacer(minLength: 0)
                    }
                    .padding(.horizontal, compact ? 14 : 18)
                    .frame(minHeight: proxy.size.height)
                    .padding(.bottom, compact ? 16 : 20)
                    }
                    .scrollDismissesKeyboard(.interactively)
                }
            }
            .navigationBarHidden(true)
        }
    }
}

private enum AuthStage {
    case welcome
    case login
    case register
}

private struct AuthBenefitRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: icon)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(EcoTheme.primary)
            Text(text)
                .font(EcoTypography.subheadline)
                .foregroundStyle(EcoTheme.ink.opacity(0.9))
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(.horizontal, 2)
    }
}

struct MainTabView: View {
    @State private var isChatPresented = false
    @State private var isAddPresented = false
    @State private var selectedTab = 0
    @State private var previousTab = 0

    var body: some View {
        GeometryReader { proxy in
            let width = proxy.size.width
            let safeBottom = max(proxy.safeAreaInsets.bottom, 8)
            let chatSize = min(max(width * 0.16, 56), 68)
            let addSize = min(max(width * 0.17, 58), 72)
            let addIconSize = addSize * 0.46
            let addLift = max(10, min(22, safeBottom * 0.55))

            ZStack(alignment: .bottom) {
                TabView(selection: $selectedTab) {
                    HomeView(selectedTab: $selectedTab)
                        .tabItem { Label("Главная", systemImage: "house.fill") }
                        .tag(0)

                    ChallengesView()
                        .tabItem { Label("Челленджи", systemImage: "flag.checkered.2.crossed") }
                        .tag(1)

                    Color.clear
                        .tabItem {
                            Text(" ")
                        }
                        .tag(2)

                    NewsView()
                        .tabItem { Label("Лента", systemImage: "newspaper.fill") }
                        .tag(3)

                    ProfileView()
                        .tabItem { Label("Профиль", systemImage: "person.crop.circle.fill") }
                        .tag(4)
                }
                .tint(EcoTheme.primary)
                .onChange(of: selectedTab) { _, newValue in
                    if newValue == 2 {
                        selectedTab = previousTab
                        return
                    }
                    previousTab = newValue
                }
                .overlay(alignment: .bottomTrailing) {
                    Button {
                        isChatPresented = true
                    } label: {
                        ZStack {
                            Circle()
                                .fill(LinearGradient(colors: [EcoTheme.sky, EcoTheme.primary], startPoint: .topLeading, endPoint: .bottomTrailing))
                                .frame(width: chatSize, height: chatSize)
                            Image(systemName: "sparkles")
                                .font(.system(size: chatSize * 0.36, weight: .black))
                                .foregroundStyle(.white)
                        }
                        .overlay(Circle().stroke(.white.opacity(0.7), lineWidth: 3))
                        .shadow(color: EcoTheme.sky.opacity(0.4), radius: 12, y: 6)
                    }
                    .padding(.trailing, 16)
                    .padding(.bottom, safeBottom + addSize * 0.78)
                }
                .overlay(alignment: .bottom) {
                    Button {
                        isAddPresented = true
                    } label: {
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [EcoTheme.primary, EcoTheme.secondary],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: addSize, height: addSize)
                            Image(systemName: "plus")
                                .font(.system(size: addIconSize, weight: .heavy))
                                .foregroundStyle(.white)
                        }
                        .overlay(Circle().stroke(.white, lineWidth: 4))
                        .shadow(color: EcoTheme.primary.opacity(0.35), radius: 14, y: 8)
                    }
                    .accessibilityLabel("Добавить активность")
                    .accessibilityHint("Открыть экран добавления активности")
                    .offset(y: -addLift)
                }
            }
        }
        .sheet(isPresented: $isChatPresented) {
            AIChatView()
        }
        .sheet(isPresented: $isAddPresented) {
            AddActivityView()
        }
    }
}

struct HomeView: View {
    private enum TrendRange: String {
        case week = "7 дней"
        case month = "30 дней"
    }

    @EnvironmentObject private var appState: AppState
    @Binding var selectedTab: Int
    @State private var heroProgress: CGFloat = 0
    @State private var contentVisible = false
    @State private var chartProgress: CGFloat = 0
    @State private var selectedTrendRange: TrendRange = .week
    @State private var selectedTrendIndex = 6
    private var trend: [TrendDataPoint] {
        let calendar = Calendar.current
        let today = calendar.startOfDay(for: Date())
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.dateFormat = selectedTrendRange == .week ? "EE" : "d MMM"

        switch selectedTrendRange {
        case .week:
            return (0..<7).map { offset in
                let dayDate = calendar.date(byAdding: .day, value: offset - 6, to: today) ?? today
                let points = appState.activities
                    .filter { calendar.isDate($0.createdAt, inSameDayAs: dayDate) }
                    .reduce(0) { $0 + $1.points }
                return TrendDataPoint(day: formatter.string(from: dayDate).capitalized, points: points)
            }
        case .month:
            return (0..<4).map { offset in
                let start = calendar.date(byAdding: .day, value: -27 + offset * 7, to: today) ?? today
                let end = calendar.date(byAdding: .day, value: 6, to: start) ?? start
                let points = appState.activities
                    .filter {
                        let day = calendar.startOfDay(for: $0.createdAt)
                        return day >= start && day <= end
                    }
                    .reduce(0) { $0 + $1.points }
                return TrendDataPoint(day: "\(offset + 1) нед", points: points)
            }
        }
    }
    private var levelInfo: (name: String, progress: CGFloat, remaining: Int) {
        let level = appState.user.level
        guard let upperBound = level.upperBoundExclusive else {
            return (level.rawValue, 1.0, 0)
        }
        let range = max(upperBound - level.lowerBound, 1)
        let current = min(max(appState.user.points - level.lowerBound, 0), range)
        return ("Прогресс уровня \(level.number)", CGFloat(Double(current) / Double(range)), max(upperBound - appState.user.points, 0))
    }

    private var selectedPoint: TrendDataPoint {
        trend[min(max(selectedTrendIndex, 0), max(trend.count - 1, 0))]
    }

    private var trendAxisValues: [Int] {
        let maxValue = max(trend.map(\.points).max() ?? 0, 1)
        let roundedTop = Int(ceil(Double(maxValue) / 10.0) * 10.0)
        let mid = max(roundedTop / 2, 1)
        return [roundedTop, mid, 0]
    }

    private var streakVisualProgress: CGFloat {
        CGFloat(min(max(appState.user.streakDays, 0), 30)) / 30
    }

    private var streakFlameSize: CGFloat {
        20 + streakVisualProgress * 10
    }

    private var streakFlameGlow: Double {
        0.18 + Double(streakVisualProgress) * 0.42
    }

    private var weeklyActivities: [EcoActivity] {
        let start = Calendar.current.date(byAdding: .day, value: -6, to: Date()) ?? Date()
        return appState.activities.filter { $0.createdAt >= start }
    }

    private var focusCategoryTitle: String {
        let grouped = Dictionary(grouping: weeklyActivities, by: \.category)
        return grouped.max { $0.value.count < $1.value.count }?.key.rawValue ?? "Начни с любой категории"
    }

    private var nextChallenge: Challenge? {
        appState.challenges
            .filter { !$0.isClaimed }
            .sorted {
                let left = Double(min($0.currentCount, $0.targetCount)) / Double(max($0.targetCount, 1))
                let right = Double(min($1.currentCount, $1.targetCount)) / Double(max($1.targetCount, 1))
                if left == right {
                    return $0.rewardPoints > $1.rewardPoints
                }
                return left > right
            }
            .first
    }

    private var weeklyActivityCount: Int {
        weeklyActivities.count
    }

    private var suggestedCategoryTitle: String {
        let grouped = Dictionary(grouping: weeklyActivities, by: \.category)
        let categories = ActivityCategory.allCases.filter { $0 != .custom }
        return categories.min {
            (grouped[$0]?.count ?? 0) < (grouped[$1]?.count ?? 0)
        }?.rawValue ?? ActivityCategory.transport.rawValue
    }

    private var challengeRemainingSteps: Int {
        guard let nextChallenge else { return 0 }
        return max(nextChallenge.targetCount - nextChallenge.currentCount, 0)
    }

    private var weeklyBestDay: TrendDataPoint {
        trend.max(by: { $0.points < $1.points }) ?? selectedPoint
    }

    private var streakHeadline: String {
        "\(appState.user.streakDays) дней в eco-ритме"
    }

    private var streakAccentText: String {
        appState.user.streakDays >= 14 ? "Зелёная привычка уже с тобой" : "Маленькие шаги уже работают"
    }

    private var impactSummaryText: String {
        if let challenge = nextChallenge {
            return challengeRemainingSteps > 0
                ? "Ещё \(challengeRemainingSteps) шаг\(challengeRemainingSteps == 1 ? "" : (challengeRemainingSteps < 5 ? "а" : "ов")) до «\(challenge.title)»"
                : "Награда «\(challenge.title)» уже готова"
        }
        return "Короткий фокус на сегодня"
    }

    private var impactItems: [ImpactCardModel] {
        return [
            ImpactCardModel(
                value: suggestedCategoryTitle,
                title: "Фокус дня",
                subtitle: "Самый логичный следующий шаг",
                icon: "sparkles",
                tint: Color(hex: 0x11A7D8),
                background: Color(hex: 0xE6F7FF)
            ),
            ImpactCardModel(
                value: weeklyBestDay.points > 0 ? "\(weeklyBestDay.points) очк." : "0",
                title: "Пик недели",
                subtitle: weeklyBestDay.points > 0 ? "\(weeklyBestDay.day) дал лучший результат" : "Активный день ещё впереди",
                icon: "chart.line.uptrend.xyaxis",
                tint: Color(hex: 0xE7A700),
                background: Color(hex: 0xFFF9E6)
            )
        ]
    }

    @ViewBuilder
    private func profileHeader(compactLayout: Bool, avatarSize: CGFloat) -> some View {
        if compactLayout {
            VStack(alignment: .leading, spacing: 10) {
                profileButton(avatarSize: avatarSize, alignTop: false)
            }
        } else {
            profileButton(avatarSize: avatarSize, alignTop: true)
        }
    }

    private func profileButton(avatarSize: CGFloat, alignTop: Bool) -> some View {
        Button {
            selectedTab = 4
        } label: {
            HStack(alignment: alignTop ? .top : .center) {
                HStack(spacing: 12) {
                    Circle()
                        .fill(EcoTheme.avatarFill)
                        .frame(width: avatarSize, height: avatarSize)
                        .overlay(
                            Text(initials(from: appState.user.fullName))
                                .font(EcoTypography.title2)
                                .foregroundStyle(.white)
                        )
                        .shadow(color: .black.opacity(0.12), radius: 8, y: 4)

                    VStack(alignment: .leading, spacing: 8) {
                        Text(appState.user.fullName)
                            .font(EcoTypography.title1)
                            .lineLimit(1)
                            .minimumScaleFactor(0.7)
                        PillBadge(
                            icon: "trophy.fill",
                            text: appState.user.level.rawValue,
                            foreground: EcoTheme.ink,
                            background: EcoTheme.elevatedCard.opacity(0.82)
                        )
                    }
                }
                Spacer(minLength: 0)
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
    }

    private func heroPointsCard(heroValueFont: CGFloat) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Всего эко-очков")
                .font(EcoTypography.title2)
                .foregroundStyle(.white.opacity(0.92))
            HStack(alignment: .firstTextBaseline, spacing: 6) {
                Text("\(appState.user.points)")
                    .font(Font.system(size: heroValueFont, weight: .heavy, design: .rounded))
                    .foregroundStyle(.white)
                    .lineLimit(1)
                    .minimumScaleFactor(0.7)
                Text("очк.")
                    .font(EcoTypography.title1)
                    .foregroundStyle(.white.opacity(0.8))
            }

            VStack(spacing: 8) {
                HStack {
                    Text(levelInfo.name)
                        .font(EcoTypography.headline)
                        .foregroundStyle(.white.opacity(0.9))
                    Spacer()
                    Text("\(Int(levelInfo.progress * 100))%")
                        .font(EcoTypography.headline)
                        .foregroundStyle(.white.opacity(0.9))
                }

                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule()
                            .fill(Color.black.opacity(0.18))
                            .frame(height: 14)
                        Capsule()
                            .fill(Color(hex: 0xFFD500))
                            .frame(width: heroProgress * geo.size.width, height: 14)
                    }
                }
                .frame(height: 14)

                Text(levelInfo.remaining > 0
                     ? "\(levelInfo.remaining) очк. до следующего уровня"
                     : "Максимальный уровень достигнут")
                .font(EcoTypography.subheadline)
                .foregroundStyle(.white.opacity(0.75))
                .frame(maxWidth: .infinity, alignment: .center)
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            LinearGradient(
                colors: [Color(hex: 0x43CF68), Color(hex: 0x4DC172)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
        .shadow(color: EcoTheme.primary.opacity(0.22), radius: 14, y: 8)
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(.white.opacity(0.15), lineWidth: 1)
        )
        .opacity(contentVisible ? 1 : 0)
        .offset(y: contentVisible ? 0 : 16)
        .animation(.spring(response: 0.55, dampingFraction: 0.82), value: contentVisible)
    }

    private var streakOverviewCard: some View {
        HStack(alignment: .center, spacing: 12) {
            Circle()
                .fill(Color(hex: 0xFFF0E3))
                .frame(width: 54, height: 54)
                .overlay(
                    Image(systemName: "flame.fill")
                        .font(.system(size: streakFlameSize, weight: .bold))
                        .foregroundStyle(Color(hex: 0xF97316))
                        .shadow(color: Color(hex: 0xF97316).opacity(streakFlameGlow), radius: 10, y: 0)
                        .scaleEffect(1 + streakVisualProgress * 0.12)
                        .animation(.spring(response: 0.32, dampingFraction: 0.75), value: appState.user.streakDays)
                )
                .shadow(color: Color(hex: 0xF97316).opacity(streakFlameGlow * 0.55), radius: 12, y: 0)
            VStack(alignment: .leading, spacing: 6) {
                Text(streakHeadline)
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
                    .lineLimit(1)
                    .minimumScaleFactor(0.9)
                Text(streakAccentText)
                    .font(EcoTypography.footnote)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                    .minimumScaleFactor(0.9)
            }
            Spacer()
        }
        .padding(16)
        .background(Color.white.opacity(0.86), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .shadow(color: .black.opacity(0.08), radius: 10, y: 5)
        .opacity(contentVisible ? 1 : 0)
        .offset(y: contentVisible ? 0 : 14)
        .animation(.easeOut(duration: 0.36).delay(0.05), value: contentVisible)
    }

    private var nextStepsSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Text("Что дальше")
                    .font(EcoTypography.title1)
                    .foregroundStyle(EcoTheme.ink)
                Spacer()
            }

            HStack(spacing: 10) {
                Image(systemName: "person.crop.circle.fill")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundStyle(EcoTheme.primary)
                Text(impactSummaryText)
                    .font(EcoTypography.footnote)
                    .foregroundStyle(EcoTheme.ink.opacity(0.84))
                    .lineLimit(2)
                    .minimumScaleFactor(0.88)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
            )
        }
        .padding(.top, 2)
    }

    private var impactCardsGrid: some View {
        LazyVGrid(columns: [GridItem(.flexible(), spacing: 10), GridItem(.flexible(), spacing: 10)], spacing: 10) {
            ForEach(Array(impactItems.enumerated()), id: \.offset) { index, item in
                ImpactCard(item: item)
                    .opacity(contentVisible ? 1 : 0)
                    .offset(y: contentVisible ? 0 : 20)
                    .animation(
                        .spring(response: 0.58, dampingFraction: 0.84).delay(0.08 * Double(index)),
                        value: contentVisible
                    )
            }
        }
        .padding(.bottom, 4)
    }

    private var trendRangePicker: some View {
        HStack(spacing: 6) {
            ForEach([TrendRange.week, .month], id: \.rawValue) { range in
                Button {
                    withAnimation(.easeInOut(duration: 0.2)) {
                        selectedTrendRange = range
                        selectedTrendIndex = range == .week ? 6 : 3
                    }
                } label: {
                    Text(range.rawValue)
                        .font(EcoTypography.footnote)
                        .foregroundStyle(selectedTrendRange == range ? .white : .secondary)
                        .lineLimit(1)
                        .minimumScaleFactor(0.9)
                        .frame(maxWidth: .infinity)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 8)
                        .background(
                            Capsule()
                                .fill(selectedTrendRange == range ? EcoTheme.primary : Color.white.opacity(0.8))
                        )
                }
                .buttonStyle(.plain)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(4)
        .background(Color.white.opacity(0.7), in: Capsule())
    }

    private var activityTrendSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Динамика активностей")
                    .font(EcoTypography.title2)
                Spacer()
            }

            trendRangePicker

            HStack(alignment: .top, spacing: 6) {
                VStack(alignment: .trailing, spacing: 0) {
                    Text("баллы")
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)
                        .padding(.bottom, 6)
                    ForEach(Array(trendAxisValues.enumerated()), id: \.offset) { index, value in
                        Text("\(value)")
                            .font(EcoTypography.caption)
                            .foregroundStyle(.secondary)
                            .frame(height: index == trendAxisValues.count - 1 ? 26 : 62, alignment: .topTrailing)
                    }
                }
                .frame(width: 38, alignment: .trailing)
                .padding(.top, 8)

                TrendChart(
                    points: trend.map(\.points),
                    axisValues: trendAxisValues,
                    selectedIndex: $selectedTrendIndex,
                    progress: chartProgress
                )
                .frame(height: 190)
            }

            HStack(spacing: 6) {
                Color.clear
                    .frame(width: 38)

                HStack {
                    ForEach(Array(trend.enumerated()), id: \.offset) { index, point in
                        Button {
                            withAnimation(.spring(response: 0.35, dampingFraction: 0.8)) {
                                selectedTrendIndex = index
                            }
                        } label: {
                            Text(point.day)
                                .font(selectedTrendIndex == index ? EcoTypography.headline : EcoTypography.subheadline)
                                .foregroundStyle(selectedTrendIndex == index ? EcoTheme.primary : .secondary)
                                .frame(maxWidth: .infinity)
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 12)
            }

            HStack {
                Text(selectedPoint.day)
                    .font(EcoTypography.title2)
                Spacer()
                Text("\(selectedPoint.points) баллов")
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.primary)
            }
            .padding()
            .background(Color.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        }
        .padding(14)
        .background(Color.white.opacity(0.78), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(Color.white.opacity(0.6), lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.05), radius: 10, y: 5)
        .opacity(contentVisible ? 1 : 0)
        .offset(y: contentVisible ? 0 : 20)
        .animation(.easeOut(duration: 0.45).delay(0.12), value: contentVisible)
    }

    var body: some View {
        NavigationStack {
            GeometryReader { proxy in
                let width = proxy.size.width
                let compactLayout = width < 390
                let avatarSize: CGFloat = compactLayout ? 54 : 62
                let heroValueFont = min(max(width * 0.14, 46), 62)

                ZStack {
                    EcoBackground()

                    VStack(alignment: .leading, spacing: 16) {
                        profileHeader(compactLayout: compactLayout, avatarSize: avatarSize)
                            .opacity(contentVisible ? 1 : 0)
                            .offset(y: contentVisible ? 0 : 10)
                            .animation(.easeOut(duration: 0.36), value: contentVisible)

                        ScrollView {
                            VStack(alignment: .leading, spacing: 16) {
                                heroPointsCard(heroValueFont: heroValueFont)

                                streakOverviewCard

                                nextStepsSection

                                impactCardsGrid

                                activityTrendSection
                            }
                            .padding(.horizontal, compactLayout ? 14 : 16)
                            .padding(.bottom, 80)
                        }
                    }
                    .padding(.horizontal, compactLayout ? 14 : 16)
                    .padding(.top, compactLayout ? 10 : 12)
                }
            }
            .navigationBarHidden(true)
        }
        .onAppear {
            heroProgress = 0
            contentVisible = false
            chartProgress = 0
            selectedTrendIndex = max(trend.count - 1, 0)
            withAnimation(.spring(response: 0.7, dampingFraction: 0.85).delay(0.06)) {
                contentVisible = true
            }
            withAnimation(.easeOut(duration: 1.0).delay(0.18)) {
                heroProgress = max(0.05, min(levelInfo.progress, 1.0))
            }
            withAnimation(.easeOut(duration: 0.9).delay(0.28)) {
                chartProgress = 1
            }
        }
        .onChange(of: selectedTrendRange) { _, newValue in
            selectedTrendIndex = newValue == .week ? 6 : 3
        }
    }

    private func initials(from name: String) -> String {
        let words = name.split(separator: " ")
        let chars = words.prefix(2).compactMap { $0.first }
        return String(chars).uppercased()
    }

}

struct ChallengesView: View {
    @EnvironmentObject private var appState: AppState
    @State private var celebratingChallenge: Challenge?
    @State private var isCelebrationVisible = false
    @State private var selectedChallengeHint: Challenge?
    @State private var autoRefreshTask: Task<Void, Never>?

    private var visibleChallenges: [Challenge] {
        appState.challenges.filter { !$0.isClaimed }
    }

    private var completionCount: Int {
        appState.challenges.filter(\.isCompleted).count
    }

    private var overallProgress: Double {
        let totalTarget = appState.challenges.reduce(0) { $0 + max($1.targetCount, 1) }
        guard totalTarget > 0 else { return 0 }
        let totalCurrent = appState.challenges.reduce(0) { $0 + min($1.currentCount, $1.targetCount) }
        return min(max(Double(totalCurrent) / Double(totalTarget), 0), 1)
    }

    var body: some View {
        NavigationStack {
            GeometryReader { proxy in
                let compactLayout = proxy.size.width < 390

                ZStack {
                    EcoBackground()

                    VStack(alignment: .leading, spacing: 14) {
                        VStack(alignment: .leading, spacing: 14) {
                            Text("Мои достижения")
                                .font(EcoTypography.title1)
                                .foregroundStyle(EcoTheme.ink)
                            Text("Выполняй задания, закрывай прогресс и получай очки.")
                                .font(EcoTypography.subheadline)
                                .foregroundStyle(.secondary)
                                .padding(.bottom, 2)
                        }
                        .padding(.horizontal, compactLayout ? 14 : 16)
                        .padding(.top, compactLayout ? 10 : 12)

                        ScrollView {
                            VStack(alignment: .leading, spacing: 14) {
                                VStack(alignment: .leading, spacing: 12) {
                                    HStack {
                                        Text("Сезонный прогресс")
                                            .font(EcoTypography.headline)
                                        Spacer()
                                        Text("\(completionCount)/\(appState.challenges.count)")
                                            .font(EcoTypography.headline)
                                            .foregroundStyle(EcoTheme.primary)
                                    }
                                    GeometryReader { geo in
                                        ZStack(alignment: .leading) {
                                            Capsule()
                                                .fill(Color.black.opacity(0.08))
                                                .frame(height: 12)
                                            Capsule()
                                                .fill(Color(hex: 0xF7C300))
                                                .frame(width: geo.size.width * overallProgress, height: 12)
                                        }
                                    }
                                    .frame(height: 12)

                                    HStack(spacing: 10) {
                                        ChallengesStatChip(
                                            title: "Очки за миссии",
                                            value: "\(appState.challenges.reduce(0) { $0 + $1.rewardPoints })",
                                            icon: "star.fill",
                                            tint: Color(hex: 0xE7A700)
                                        )
                                        ChallengesStatChip(
                                            title: "В процессе",
                                            value: "\(visibleChallenges.filter { !$0.isCompleted }.count)",
                                            icon: "bolt.fill",
                                            tint: EcoTheme.primary
                                        )
                                    }
                                }
                                .surfaceCard()

                                if visibleChallenges.isEmpty {
                                    VStack(alignment: .leading, spacing: 8) {
                                        Text("Все текущие челленджи забраны")
                                            .font(EcoTypography.title2)
                                            .foregroundStyle(EcoTheme.ink)
                                        Text("Новые ачивки уже в профиле. Выполняй следующие активности, и мы добавим больше миссий.")
                                            .font(EcoTypography.subheadline)
                                            .foregroundStyle(.secondary)
                                    }
                                    .frame(maxWidth: .infinity, alignment: .leading)
                                    .surfaceCard()
                                } else {
                                    LazyVStack(spacing: 12) {
                                        ForEach(visibleChallenges) { item in
                                            ChallengeAchievementCard(
                                                challenge: item,
                                                compact: compactLayout,
                                                isClaiming: appState.isClaimingChallenge,
                                                onOpenHint: {
                                                    selectedChallengeHint = item
                                                },
                                                onClaim: {
                                                    Task {
                                                        guard let claimed = await appState.claimChallenge(item.id) else { return }
                                                        await MainActor.run {
                                                            celebratingChallenge = claimed
                                                            withAnimation(.spring(response: 0.38, dampingFraction: 0.82)) {
                                                                isCelebrationVisible = true
                                                            }
                                                        }
                                                    }
                                                }
                                            )
                                        }
                                    }
                                }
                            }
                            .padding(.horizontal, compactLayout ? 14 : 16)
                            .padding(.bottom, 80)
                        }
                        .allowsHitTesting(!isCelebrationVisible)
                    }

                    if let activeCelebrationChallenge = celebratingChallenge, isCelebrationVisible {
                        ChallengeClaimCelebrationOverlay(challenge: activeCelebrationChallenge) {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.88)) {
                                isCelebrationVisible = false
                            }
                            celebratingChallenge = nil
                        }
                        .zIndex(20)
                        .transition(.asymmetric(insertion: .scale(scale: 0.9).combined(with: .opacity), removal: .scale(scale: 0.96).combined(with: .opacity)))
                    }
                }
            }
            .navigationBarHidden(true)
            .task {
                await appState.refreshChallengesIfAuthenticated(silently: true)
                startAutoRefresh()
            }
            .onDisappear {
                stopAutoRefresh()
            }
            .sheet(item: $selectedChallengeHint) { challenge in
                ChallengeHintSheet(challenge: challenge)
            }
        }
    }

    private func startAutoRefresh() {
        autoRefreshTask?.cancel()
        autoRefreshTask = Task {
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(8))
                guard !Task.isCancelled else { break }
                await appState.refreshChallengesIfAuthenticated(silently: true)
            }
        }
    }

    private func stopAutoRefresh() {
        autoRefreshTask?.cancel()
        autoRefreshTask = nil
    }
}

struct AddActivityView: View {
    @EnvironmentObject private var appState: AppState
    @Environment(\.dismiss) private var dismiss
    @State private var selectedCategory: ActivityCategory?
    @State private var selectedTransportTemplate: ActivityTemplate?
    @State private var transportDistance: Double = 7
    @State private var draftActivity: PendingActivity?
    @State private var pendingSubmission: PendingActivitySubmission?
    @State private var activityPickerItems: [PhotosPickerItem] = []
    @State private var activityMedia: [PostMediaAttachment] = []
    @State private var activityNote = ""
    @State private var customTitle = ""
    @State private var customDescription = ""
    @State private var showActivitySavedOverlay = false
    @State private var savedOverlayText = "Активность сохранена"

    private var quickCategories: [ActivityCategory] {
        [.transport, .water, .plastic, .waste, .energy, .custom]
    }

    private var hasRequiredActivityMedia: Bool {
        activityMedia.contains(where: { $0.kind == .photo })
    }

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                VStack(alignment: .leading, spacing: 14) {
                    VStack(alignment: .leading, spacing: 14) {
                        HStack {
                            Text("Добавить активность")
                                .font(EcoTypography.title1)
                                .foregroundStyle(EcoTheme.ink)
                            Spacer()
                            Button {
                                dismiss()
                            } label: {
                                Image(systemName: "xmark")
                                    .font(.system(size: 14, weight: .bold))
                                    .foregroundStyle(.secondary)
                                    .frame(width: 34, height: 34)
                                    .background(Color.white.opacity(0.9), in: Circle())
                                    .overlay(Circle().stroke(Color.black.opacity(0.06), lineWidth: 1))
                            }
                        }
                    }
                    .padding(.horizontal)

                    ScrollView {
                        VStack(alignment: .leading, spacing: 14) {
                            if let selectedCategory {
                                VStack(alignment: .leading, spacing: 10) {
                                    Button {
                                        withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                            pendingSubmission = nil
                                            draftActivity = nil
                                            selectedTransportTemplate = nil
                                            self.selectedCategory = nil
                                        }
                                    } label: {
                                        Label("Назад к категориям", systemImage: "chevron.left")
                                            .font(EcoTypography.subheadline)
                                            .foregroundStyle(.secondary)
                                    }
                                    .buttonStyle(.plain)
                                }
                                .padding(.horizontal, 2)

                                ZStack {
                                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                                        .fill(
                                            LinearGradient(
                                                colors: selectedCategory.pageGradient,
                                                startPoint: .topLeading,
                                                endPoint: .bottomTrailing
                                            )
                                        )
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 28, style: .continuous)
                                                .stroke(Color.white.opacity(0.22), lineWidth: 1)
                                        )
                                        .shadow(color: selectedCategory.tintColor.opacity(0.28), radius: 14, y: 8)

                                    if let pendingSubmission {
                                        VStack(alignment: .leading, spacing: 16) {
                                            Text(pendingSubmission.title)
                                                .font(EcoTypography.title2)
                                                .foregroundStyle(.white)
                                                .multilineTextAlignment(.leading)
                                            Text("Категория: \(pendingSubmission.category.rawValue)")
                                                .font(EcoTypography.subheadline)
                                                .foregroundStyle(.white.opacity(0.9))

                                            Spacer(minLength: 10)

                                            VStack(spacing: 8) {
                                                Text(pendingSubmission.isEstimated ? "Предварительная оценка CO₂" : "Сокращено CO₂")
                                                    .font(EcoTypography.title2)
                                                    .foregroundStyle(.white)
                                                Circle()
                                                    .fill(Color.white.opacity(0.22))
                                                    .frame(width: 92, height: 92)
                                                    .overlay(
                                                        Circle()
                                                            .stroke(Color.white.opacity(0.26), lineWidth: 1)
                                                    )
                                                    .overlay(
                                                        Image("AuthGlobe")
                                                            .resizable()
                                                            .scaledToFill()
                                                            .frame(width: 84, height: 84)
                                                            .clipShape(Circle())
                                                    )
                                                Text("\(pendingSubmission.isEstimated ? "≈" : "")\(String(format: "%.1f", pendingSubmission.co2)) кг")
                                                    .font(EcoTypography.title2)
                                                    .foregroundStyle(.white)
                                            }
                                            .frame(maxWidth: .infinity)

                                            if pendingSubmission.isEstimated {
                                                Text("Финальная оценка сохранится после отправки и рассчитывается автоматически на сервере.")
                                                    .font(EcoTypography.caption)
                                                    .foregroundStyle(.white.opacity(0.88))
                                                    .multilineTextAlignment(.center)
                                                    .frame(maxWidth: .infinity)
                                            }

                                            Spacer(minLength: 8)

                                            HStack(spacing: 10) {
                                                Button("Поделиться") {
                                                    Task {
                                                        await commitSubmission(shareToNews: true)
                                                    }
                                                }
                                                .buttonStyle(DuoSecondaryButtonStyle())
                                                .disabled(appState.isSubmittingActivity)
                                                .opacity(appState.isSubmittingActivity ? 0.55 : 1)

                                                Button("Готово") {
                                                    Task {
                                                        await commitSubmission(shareToNews: false)
                                                    }
                                                }
                                                .buttonStyle(DuoPrimaryButtonStyle())
                                                .disabled(appState.isSubmittingActivity)
                                                .opacity(appState.isSubmittingActivity ? 0.55 : 1)
                                            }

                                            if appState.isSubmittingActivity {
                                                ProgressView()
                                                    .tint(.white)
                                                    .frame(maxWidth: .infinity)
                                            }
                                        }
                                        .padding(16)
                                    } else if let draftActivity {
                                        VStack(alignment: .leading, spacing: 14) {
                                            Button {
                                                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                                    self.draftActivity = nil
                                                }
                                            } label: {
                                                Label("Назад", systemImage: "chevron.left")
                                                    .font(EcoTypography.subheadline)
                                                    .foregroundStyle(.white.opacity(0.9))
                                            }
                                            .buttonStyle(.plain)

                                            Text(draftActivity.title)
                                                .font(EcoTypography.title2)
                                                .foregroundStyle(.white)

                                            PhotosPicker(
                                                selection: $activityPickerItems,
                                                maxSelectionCount: 3,
                                                matching: .images
                                            ) {
                                                Label("Добавить фото", systemImage: "camera.fill")
                                                    .font(EcoTypography.callout)
                                                    .foregroundStyle(.white)
                                                    .padding(.vertical, 10)
                                                    .frame(maxWidth: .infinity)
                                                    .background(
                                                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                            .fill(Color.white.opacity(0.18))
                                                    )
                                            }

                                            if !activityMedia.isEmpty {
                                                ThreadMediaStrip(media: activityMedia)
                                            }

                                            Text(hasRequiredActivityMedia ? "Фото приложено. Это будет использовано как подтверждение активности." : "Добавь хотя бы одно фото. Оно обязательно как подтверждение активности.")
                                                .font(EcoTypography.caption)
                                                .foregroundStyle(hasRequiredActivityMedia ? .white.opacity(0.82) : Color.white)

                                            ZStack(alignment: .topLeading) {
                                                TextEditor(text: $activityNote)
                                                    .scrollContentBackground(.hidden)
                                                    .font(EcoTypography.body)
                                                    .foregroundStyle(EcoTheme.ink)
                                                    .padding(10)
                                                    .frame(minHeight: 120)
                                                    .background(
                                                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                            .fill(Color.white.opacity(0.95))
                                                    )
                                                    .overlay(
                                                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                            .stroke(Color.black.opacity(0.06), lineWidth: 1)
                                                    )

                                                if activityNote.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                                    Text("Напишите описание...")
                                                        .font(EcoTypography.body)
                                                        .foregroundStyle(.secondary)
                                                        .padding(.top, 20)
                                                        .padding(.leading, 16)
                                                        .allowsHitTesting(false)
                                                }
                                            }

                                            HStack(spacing: 10) {
                                                Button("Назад") {
                                                    withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                                        self.draftActivity = nil
                                                    }
                                                }
                                                .buttonStyle(DuoSecondaryButtonStyle())

                                                Button("Продолжить") {
                                                    completeDraft()
                                                }
                                                .buttonStyle(DuoPrimaryButtonStyle())
                                                .disabled(!hasRequiredActivityMedia)
                                                .opacity(hasRequiredActivityMedia ? 1 : 0.55)
                                            }
                                        }
                                        .padding(16)
                                    } else if selectedCategory == .custom {
                                        VStack(alignment: .leading, spacing: 14) {
                                            DuoInputField(title: "Название активности", text: $customTitle)
                                            ZStack(alignment: .topLeading) {
                                                TextEditor(text: $customDescription)
                                                    .scrollContentBackground(.hidden)
                                                    .font(EcoTypography.body)
                                                    .foregroundStyle(EcoTheme.ink)
                                                    .padding(10)
                                                    .frame(minHeight: 120)
                                                    .background(
                                                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                            .fill(Color.white.opacity(0.95))
                                                    )
                                                    .overlay(
                                                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                                                            .stroke(Color.black.opacity(0.06), lineWidth: 1)
                                                    )

                                                if customDescription.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                                                    Text("Что сделал, где и какой был эффект? Например: взял многоразовую кружку и отказался от одноразового стакана.")
                                                        .font(EcoTypography.body)
                                                        .foregroundStyle(.secondary)
                                                        .padding(.top, 20)
                                                        .padding(.leading, 16)
                                                        .allowsHitTesting(false)
                                                }
                                            }

                                            Text("Оценку CO₂ и очков мы рассчитаем автоматически.")
                                                .font(EcoTypography.caption)
                                                .foregroundStyle(.white.opacity(0.84))

                                            Button("Продолжить") {
                                                let estimate = estimateCustomImpact(title: customTitle, description: customDescription)
                                                startDraft(
                                                    category: .custom,
                                                    title: customTitle.isEmpty ? "Своя активность" : customTitle,
                                                    co2: estimate.co2,
                                                    points: estimate.points,
                                                    isEstimated: true,
                                                    initialNote: customDescription
                                                )
                                            }
                                            .buttonStyle(DuoPrimaryButtonStyle())
                                            .disabled(
                                                customTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                                                || customDescription.trimmingCharacters(in: .whitespacesAndNewlines).count < 12
                                            )
                                            .opacity(
                                                customTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                                                || customDescription.trimmingCharacters(in: .whitespacesAndNewlines).count < 12 ? 0.55 : 1
                                            )
                                        }
                                        .padding(16)
                                    } else if selectedCategory == .transport, let transport = selectedTransportTemplate {
                                        VStack(alignment: .leading, spacing: 16) {
                                            Button {
                                                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                                    selectedTransportTemplate = nil
                                                }
                                            } label: {
                                                Label("Назад к транспорту", systemImage: "chevron.left")
                                                    .font(EcoTypography.subheadline)
                                                    .foregroundStyle(.white.opacity(0.9))
                                            }
                                            .buttonStyle(.plain)

                                            Text(transport.title)
                                                .font(EcoTypography.title2)
                                                .foregroundStyle(.white)

                                            HStack {
                                                Text("Дистанция:")
                                                    .font(EcoTypography.title2)
                                                    .foregroundStyle(.white)
                                                Spacer()
                                                Text("\(Int(transportDistance)) км")
                                                    .font(EcoTypography.title2)
                                                    .foregroundStyle(.white)
                                            }

                                            Slider(value: $transportDistance, in: 1...10, step: 1)
                                                .tint(.white)

                                            HStack {
                                                Text("1 км")
                                                    .font(EcoTypography.caption)
                                                    .foregroundStyle(.white.opacity(0.9))
                                                Spacer()
                                                Text("10 км")
                                                    .font(EcoTypography.caption)
                                                    .foregroundStyle(.white.opacity(0.9))
                                            }

                                            Spacer(minLength: 12)

                                            Button("Продолжить") {
                                                let factor = transportDistance / 5.0
                                                let co2 = max(0.1, transport.estimatedCO2 * factor)
                                                let points = max(1, Int((Double(transport.points) * factor).rounded()))
                                                startDraft(
                                                    category: .transport,
                                                    title: "\(transport.title) • \(Int(transportDistance)) км",
                                                    co2: co2,
                                                    points: points
                                                )
                                            }
                                            .buttonStyle(DuoPrimaryButtonStyle())
                                        }
                                        .padding(16)
                                    } else {
                                        let templates = appState.templatesByCategory[selectedCategory] ?? []
                                        LazyVGrid(
                                            columns: [GridItem(.flexible(), spacing: 16), GridItem(.flexible(), spacing: 16)],
                                            spacing: 16
                                        ) {
                                            ForEach(templates) { item in
                                                AddSubactivityTile(
                                                    title: item.title,
                                                    icon: subIcon(for: selectedCategory, title: item.title),
                                                    tint: selectedCategory.tintColor
                                                ) {
                                                    if selectedCategory == .transport {
                                                        withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                                            selectedTransportTemplate = item
                                                            transportDistance = 7
                                                        }
                                                    } else {
                                                        startDraft(
                                                            category: selectedCategory,
                                                            title: item.title,
                                                            co2: item.estimatedCO2,
                                                            points: item.points
                                                        )
                                                    }
                                                }
                                            }
                                        }
                                        .padding(16)
                                    }
                                }
                                .frame(minHeight: 420)
                            } else {
                                VStack(alignment: .leading, spacing: 12) {
                                    Text("Категории")
                                        .font(EcoTypography.title2)
                                    Text("Сначала выбери категорию, потом подкатегорию")
                                        .font(EcoTypography.subheadline)
                                        .foregroundStyle(.secondary)

                                    LazyVGrid(
                                        columns: [GridItem(.flexible(), spacing: 14), GridItem(.flexible(), spacing: 14)],
                                        spacing: 14
                                    ) {
                                        ForEach(quickCategories) { category in
                                            AddCategoryTile(
                                                title: category.rawValue,
                                                subtitle: category.shortDescription,
                                                icon: category.systemIconName,
                                                tint: category.tintColor,
                                                gradient: category.highlightGradient,
                                                isSelected: false
                                            ) {
                                                withAnimation(.spring(response: 0.28, dampingFraction: 0.8)) {
                                                    selectedTransportTemplate = nil
                                                    selectedCategory = category
                                                }
                                            }
                                        }
                                    }
                                }
                                .surfaceCard()
                            }
                        }
                        .padding()
                        .padding(.bottom, 80)
                    }
                }

                if showActivitySavedOverlay {
                    ActivitySavedOverlay(text: savedOverlayText)
                        .transition(.asymmetric(insertion: .scale(scale: 0.88).combined(with: .opacity), removal: .opacity))
                        .zIndex(10)
                }
            }
            .navigationBarHidden(true)
        }
        .onChange(of: activityPickerItems) { _, newItems in
            Task {
                await loadActivityMedia(from: newItems)
            }
        }
    }

    private func startDraft(
        category: ActivityCategory,
        title: String,
        co2: Double,
        points: Int,
        isEstimated: Bool = false,
        initialNote: String = ""
    ) {
        draftActivity = PendingActivity(category: category, title: title, co2: co2, points: points, isEstimated: isEstimated)
        pendingSubmission = nil
        activityPickerItems = []
        activityMedia = []
        activityNote = initialNote
    }

    private func completeDraft() {
        guard let draftActivity else { return }
        let finalNote = activityNote
        pendingSubmission = PendingActivitySubmission(
            category: draftActivity.category,
            title: draftActivity.title,
            co2: draftActivity.co2,
            points: draftActivity.points,
            isEstimated: draftActivity.isEstimated,
            note: finalNote,
            media: activityMedia
        )
        self.draftActivity = nil
    }

    private func commitSubmission(shareToNews: Bool) async {
        guard let pendingSubmission else { return }
        let success = await appState.addActivity(
            category: pendingSubmission.category,
            title: pendingSubmission.title,
            co2: pendingSubmission.co2,
            points: pendingSubmission.points,
            note: pendingSubmission.note,
            media: pendingSubmission.media,
            shareToNews: shareToNews
        )
        if success {
            await MainActor.run {
                savedOverlayText = shareToNews ? "Активность и пост готовы" : "Активность сохранена"
                withAnimation(.spring(response: 0.36, dampingFraction: 0.82)) {
                    showActivitySavedOverlay = true
                }
                EcoFeedback.playActivitySaved()
            }

            try? await Task.sleep(for: .milliseconds(1050))

            await MainActor.run {
                dismiss()
            }
        }
    }

    private func loadActivityMedia(from items: [PhotosPickerItem]) async {
        var loaded: [PostMediaAttachment] = []
        for item in items {
            guard let data = try? await item.loadTransferable(type: Data.self), !data.isEmpty else { continue }
            let isVideo = item.supportedContentTypes.contains {
                $0.conforms(to: .movie) || $0.conforms(to: .video)
            }
            loaded.append(
                PostMediaAttachment(
                    kind: isVideo ? .video : .photo,
                    data: data
                )
            )
        }
        await MainActor.run {
            activityMedia = loaded
        }
    }

    private func estimateCustomImpact(title: String, description: String) -> (co2: Double, points: Int) {
        let combined = "\(title) \(description)".lowercased()
        let trimmedDescription = description.trimmingCharacters(in: .whitespacesAndNewlines)
        var score = 4
        var co2 = 0.12

        if combined.contains("велосип") || combined.contains("пеш") || combined.contains("метро") || combined.contains("автобус") || combined.contains("поезд") || combined.contains("самокат") {
            score += 4
            co2 += 0.42
        }
        if combined.contains("сортир") || combined.contains("переработ") || combined.contains("вторсыр") || combined.contains("мусор") || combined.contains("компост") {
            score += 3
            co2 += 0.28
        }
        if combined.contains("бутыл") || combined.contains("сумк") || combined.contains("упаков") || combined.contains("пластик") || combined.contains("многораз") {
            score += 2
            co2 += 0.16
        }
        if combined.contains("душ") || combined.contains("кран") || combined.contains("вода") || combined.contains("утеч") {
            score += 2
            co2 += 0.14
        }
        if combined.contains("свет") || combined.contains("ламп") || combined.contains("электр") || combined.contains("заряд") {
            score += 2
            co2 += 0.16
        }
        if combined.contains("вместо") || combined.contains("отказ") || combined.contains("замен") || combined.contains("сэконом") {
            score += 2
            co2 += 0.1
        }
        if trimmedDescription.count > 90 {
            score += 1
            co2 += 0.06
        }
        if trimmedDescription.count < 28 {
            score = min(score, 6)
            co2 = min(co2, 0.22)
        }

        return (round(min(co2, 1.1) * 100) / 100, min(score, 14))
    }

    private func title(for category: ActivityCategory) -> String {
        switch category {
        case .transport: return "Выбери транспорт"
        case .water: return "Выбери водную активность"
        case .plastic: return "Выбери шаг без пластика"
        case .waste: return "Выбери активность по отходам"
        case .energy: return "Выбери энергосбережение"
        case .custom: return "Добавь свою активность"
        }
    }

    private func subIcon(for category: ActivityCategory, title: String) -> String {
        let normalized = title.lowercased()
        switch category {
        case .transport:
            if normalized.contains("пеш") { return "figure.walk" }
            if normalized.contains("метро") { return "tram.fill" }
            if normalized.contains("поезд") { return "train.side.front.car" }
            if normalized.contains("велосипед") { return "bicycle" }
            if normalized.contains("самокат") { return "scooter" }
            if normalized.contains("мотоцикл") { return "motorcycle" }
            if normalized.contains("машина") { return "car.fill" }
            if normalized.contains("автобус") || normalized.contains("общ.") { return "bus.fill" }
            if normalized.contains("совмест") { return "person.2.fill" }
            return "bicycle"
        case .water:
            if normalized.contains("душ") { return "shower.fill" }
            if normalized.contains("кран") { return "drop.fill" }
            if normalized.contains("стирк") { return "washer.fill" }
            if normalized.contains("утеч") { return "wrench.adjustable.fill" }
            if normalized.contains("аэратор") { return "circle.grid.3x3.fill" }
            return "drop.fill"
        case .plastic:
            if normalized.contains("пакета") { return "takeoutbag.and.cup.and.straw.fill" }
            if normalized.contains("сумка") { return "bag.fill" }
            if normalized.contains("бутылка") { return "waterbottle.fill" }
            if normalized.contains("сдал") { return "arrow.triangle.2.circlepath" }
            return "takeoutbag.and.cup.and.straw.fill"
        case .waste:
            if normalized.contains("сортиров") { return "arrow.triangle.2.circlepath" }
            if normalized.contains("вторсыр") || normalized.contains("переработ") { return "arrow.triangle.2.circlepath.circle" }
            if normalized.contains("компост") { return "leaf.fill" }
            return "arrow.triangle.2.circlepath"
        case .energy:
            if normalized.contains("выключил") { return "lightbulb.slash.fill" }
            if normalized.contains("отключил") { return "powerplug.fill" }
            if normalized.contains("led") { return "lightbulb.led.fill" }
            if normalized.contains("дневной") { return "sun.max.fill" }
            return "bolt.badge.a.fill"
        case .custom:
            return "sparkles"
        }
    }
}

private struct ActivitySavedOverlay: View {
    let text: String
    @State private var badgeScale: CGFloat = 0.72
    @State private var glowOpacity = 0.0
    @State private var capsuleWidth: CGFloat = 0.86

    var body: some View {
        ZStack {
            Color.black.opacity(0.12)
                .ignoresSafeArea()

            VStack(spacing: 14) {
                ZStack {
                    Circle()
                        .fill(
                            RadialGradient(
                                colors: [Color(hex: 0xDDF7C8), Color.white.opacity(0.08)],
                                center: .center,
                                startRadius: 8,
                                endRadius: 78
                            )
                        )
                        .frame(width: 132, height: 132)
                        .opacity(glowOpacity)

                    ForEach(0..<8, id: \.self) { index in
                        Capsule()
                            .fill(Color.white.opacity(0.9))
                            .frame(width: 5, height: 22)
                            .offset(y: -78)
                            .rotationEffect(.degrees(Double(index) * 45))
                            .opacity(glowOpacity)
                    }

                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color(hex: 0x66D94D), Color(hex: 0x22B96B)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 84, height: 84)
                        .overlay(
                            Image(systemName: "checkmark")
                                .font(.system(size: 34, weight: .black))
                                .foregroundStyle(.white)
                        )
                        .scaleEffect(badgeScale)
                        .shadow(color: EcoTheme.primary.opacity(0.28), radius: 16, y: 8)
                }

                Text("Готово")
                    .font(EcoTypography.title1)
                    .foregroundStyle(EcoTheme.ink)

                Text(text)
                    .font(EcoTypography.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
            }
            .padding(.horizontal, 26)
            .padding(.vertical, 24)
            .frame(maxWidth: 270)
            .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 30, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 30, style: .continuous)
                    .stroke(EcoTheme.softStroke, lineWidth: 1)
                    .scaleEffect(capsuleWidth)
                    .opacity(glowOpacity * 0.7)
            )
            .onAppear {
                withAnimation(.spring(response: 0.34, dampingFraction: 0.74)) {
                    badgeScale = 1
                    glowOpacity = 1
                    capsuleWidth = 1
                }
            }
        }
    }
}

struct NewsView: View {
    @EnvironmentObject private var appState: AppState
    @State private var postText = ""
    @State private var pickerItems: [PhotosPickerItem] = []
    @State private var selectedMedia: [PostMediaAttachment] = []
    @State private var autoRefreshTask: Task<Void, Never>?
    @State private var selectedEvent: EcoEvent?
    @State private var joinedEventIDs: Set<String> = []

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                VStack(alignment: .leading, spacing: 12) {
                    HStack {
                        Text("Твой EcoIz")
                            .font(EcoTypography.title1)
                            .foregroundStyle(EcoTheme.ink)
                        Spacer()
                        Image(systemName: "line.3.horizontal.decrease.circle")
                            .font(.system(size: 20, weight: .semibold))
                            .foregroundStyle(.secondary)
                    }
                    .padding(.horizontal)
                    .padding(.top, 8)

                    ThreadComposerBar(
                        text: $postText,
                        pickerItems: $pickerItems,
                        selectedMedia: $selectedMedia,
                        username: appState.user.fullName,
                        isPosting: appState.isPosting,
                        onPost: {
                            Task {
                                let success = await appState.addPost(text: postText, media: selectedMedia)
                                guard success else { return }
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    postText = ""
                                    selectedMedia = []
                                    pickerItems = []
                                }
                            }
                        }
                    )
                    .padding(.horizontal)

                    ScrollView {
                        LazyVStack(spacing: 0) {
                            if appState.events.isEmpty {
                                EcoEventsPlaceholder(isLoading: appState.isRefreshingEvents)
                                    .padding(.bottom, 14)
                            } else {
                                EcoEventsCarousel(
                                    events: appState.events,
                                    joinedEventIDs: joinedEventIDs,
                                    onSelect: { selectedEvent = $0 }
                                )
                                .padding(.bottom, 14)
                            }

                            ForEach(appState.posts) { post in
                                ThreadPostCell(post: post)
                            }
                        }
                        .padding(.horizontal)
                        .padding(.bottom, 80)
                    }
                    .refreshable {
                        await appState.refreshPostsIfAuthenticated()
                    }
                }
            }
            .navigationBarHidden(true)
            .task {
                await appState.refreshPostsIfAuthenticated()
                await appState.refreshEventsIfAuthenticated()
                startAutoRefresh()
            }
            .onDisappear {
                stopAutoRefresh()
            }
        }
        .onChange(of: pickerItems) { _, newItems in
            Task {
                await loadMedia(from: newItems)
            }
        }
        .sheet(item: $selectedEvent) { event in
            EcoEventFullDetailSheet(event: event, isJoined: joinedEventIDs.contains(event.id)) {
                joinedEventIDs.insert(event.id)
            }
        }
    }

    private func loadMedia(from items: [PhotosPickerItem]) async {
        var loaded: [PostMediaAttachment] = []

        for item in items {
            guard let data = try? await item.loadTransferable(type: Data.self), !data.isEmpty else { continue }
            let isVideo = item.supportedContentTypes.contains {
                $0.conforms(to: .movie) || $0.conforms(to: .video)
            }
            loaded.append(
                PostMediaAttachment(
                    kind: isVideo ? .video : .photo,
                    data: data
                )
            )
        }

        await MainActor.run {
            selectedMedia = loaded
        }
    }

    private func startAutoRefresh() {
        stopAutoRefresh()
        autoRefreshTask = Task {
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(8))
                guard !Task.isCancelled else { break }
                await appState.refreshPostsIfAuthenticated()
            }
        }
    }

    private func stopAutoRefresh() {
        autoRefreshTask?.cancel()
        autoRefreshTask = nil
    }
}

private struct EcoEventsPlaceholder: View {
    let isLoading: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text("Ближайшие эко-ивенты")
                        .font(EcoTypography.headline)
                        .foregroundStyle(EcoTheme.ink)
                    Text(isLoading ? "Загружаем события рядом с тобой" : "Скоро здесь появятся новые события")
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Text("Все")
                    .font(EcoTypography.caption.weight(.semibold))
                    .foregroundStyle(EcoTheme.primary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 7)
                    .background(EcoTheme.primary.opacity(0.1), in: Capsule())
            }
            .padding(.horizontal)

            HStack(spacing: 12) {
                ForEach(0..<2, id: \.self) { index in
                    RoundedRectangle(cornerRadius: 26, style: .continuous)
                        .fill(EcoTheme.elevatedCard)
                        .frame(width: 246, height: 156)
                        .overlay(alignment: .topLeading) {
                            RoundedRectangle(cornerRadius: 22, style: .continuous)
                                .fill(
                                    LinearGradient(
                                        colors: [
                                            (index == 0 ? EcoTheme.primary : EcoTheme.sky).opacity(0.18),
                                            (index == 0 ? EcoTheme.primary : EcoTheme.sky).opacity(0.08),
                                        ],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(height: 92)
                                .padding(12)
                        }
                        .overlay(
                            RoundedRectangle(cornerRadius: 26, style: .continuous)
                                .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
                        )
                        .redacted(reason: isLoading ? .placeholder : [])
                }
            }
            .padding(.horizontal)
        }
        .padding(.top, 4)
    }
}

private struct EcoEventsCarousel: View {
    let events: [EcoEvent]
    let joinedEventIDs: Set<String>
    let onSelect: (EcoEvent) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                VStack(alignment: .leading, spacing: 3) {
                    Text("Ближайшие эко-ивенты")
                        .font(EcoTypography.headline)
                        .foregroundStyle(EcoTheme.ink)
                    Text("Участвуй, получай очки и делай вклад офлайн")
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Text("Все")
                    .font(EcoTypography.caption.weight(.semibold))
                    .foregroundStyle(EcoTheme.primary)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 7)
                    .background(EcoTheme.primary.opacity(0.1), in: Capsule())
            }
            .padding(.horizontal)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(events) { event in
                        EcoEventCard(event: event, isJoined: joinedEventIDs.contains(event.id))
                            .onTapGesture {
                                onSelect(event)
                            }
                    }
                }
                .padding(.horizontal)
            }
        }
        .padding(.top, 4)
    }
}

private struct EcoEventCard: View {
    let event: EcoEvent
    let isJoined: Bool

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            ZStack(alignment: .topLeading) {
                if let coverAssetName = ecoEventCoverAssetName(event) {
                    Image(coverAssetName)
                        .resizable()
                        .scaledToFill()
                        .frame(height: 118)
                        .frame(maxWidth: .infinity)
                        .clipped()
                        .overlay {
                            LinearGradient(
                                colors: [
                                    .black.opacity(0.04),
                                    .black.opacity(0.12),
                                    .black.opacity(0.42),
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        }
                        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
                } else {
                    RoundedRectangle(cornerRadius: 22, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color(hex: UInt32(event.imageTintHex)).opacity(0.95),
                                    Color(hex: UInt32(event.imageTintHex)).opacity(0.58),
                                    EcoTheme.ink.opacity(0.12),
                                ],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(height: 118)
                        .overlay(alignment: .bottomTrailing) {
                            Image(systemName: ecoEventIcon(event))
                                .font(.system(size: 54, weight: .black))
                                .foregroundStyle(.white.opacity(0.28))
                                .padding(14)
                        }
                }

                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 6) {
                        EventBadge(text: isJoined ? "Участвую" : event.badge, tint: isJoined ? EcoTheme.primary : .white)
                        if event.rewardPoints > 0 {
                            EventBadge(text: "+\(event.rewardPoints) очков", tint: Color(hex: 0xF7C300))
                        }
                    }
                    Spacer()
                    Text(event.partnerName ?? "EcoIz Events")
                        .font(EcoTypography.caption.weight(.semibold))
                        .foregroundStyle(.white.opacity(0.92))
                }
                .padding(12)
            }

            VStack(alignment: .leading, spacing: 5) {
                Text(event.title)
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
                Text(eventTime)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
                Text(event.location)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
        }
        .frame(width: 246, alignment: .leading)
        .padding(12)
        .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 26, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
        )
        .shadow(color: EcoTheme.shadow.opacity(0.4), radius: 10, y: 5)
    }

    private var eventTime: String {
        event.startsAt.formatted(.dateTime.day().month(.wide).hour().minute())
    }
}

private struct EventBadge: View {
    let text: String
    let tint: Color

    var body: some View {
        Text(text)
            .font(EcoTypography.caption.weight(.bold))
            .foregroundStyle(EcoTheme.ink)
            .padding(.horizontal, 9)
            .padding(.vertical, 5)
            .background(tint.opacity(0.86), in: Capsule())
    }
}

private func ecoEventIsTreePlanting(_ event: EcoEvent) -> Bool {
    let text = "\(event.title) \(event.description)".lowercased()
    return text.contains("дерев") || text.contains("посад")
}

private func ecoEventIsMarathon(_ event: EcoEvent) -> Bool {
    let text = "\(event.title) \(event.description) \(event.partnerName ?? "")".lowercased()
    return text.contains("марафон") || text.contains("bi group")
}

private func ecoEventCoverAssetName(_ event: EcoEvent) -> String? {
    if ecoEventIsTreePlanting(event) {
        return "EventTreePlantingCover"
    }
    if ecoEventIsMarathon(event) {
        return "EventMarathonCover"
    }
    return nil
}

private func ecoEventIcon(_ event: EcoEvent) -> String {
    let text = "\(event.title) \(event.description)".lowercased()
    if ecoEventIsTreePlanting(event) || text.contains("сад") {
        return "tree.fill"
    }
    if ecoEventIsMarathon(event) || text.contains("бег") {
        return "figure.run"
    }
    if text.contains("пласт") || text.contains("сбор") || text.contains("переработ") {
        return "arrow.3.trianglepath"
    }
    if text.contains("вело") || text.contains("авто") {
        return "bicycle"
    }
    if text.contains("лекц") || text.contains("студ") {
        return "graduationcap.fill"
    }
    return "sparkles"
}

private struct EcoEventFullDetailSheet: View {
    let event: EcoEvent
    let isJoined: Bool
    let onJoin: () -> Void
    @Environment(\.dismiss) private var dismiss
    @Environment(\.openURL) private var openURL
    @State private var didJoin = false

    private var joined: Bool { isJoined || didJoin }
    private var registrationURL: URL? {
        guard let registrationUrl = event.registrationUrl else { return nil }
        return URL(string: registrationUrl)
    }

    var body: some View {
        NavigationStack {
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 18) {
                    EcoEventHeroCover(event: event, joined: joined)

                    VStack(alignment: .leading, spacing: 12) {
                        EventInfoRow(icon: "calendar", title: "Дата и время", value: event.startsAt.formatted(.dateTime.day().month(.wide).hour().minute()))
                        EventInfoRow(icon: "mappin.and.ellipse", title: "Место", value: event.location)
                        if let partner = event.partnerName {
                            EventInfoRow(icon: "person.2.fill", title: "Организатор", value: partner)
                        }
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(16)
                    .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
                    )

                    EventRewardCard(points: event.rewardPoints)

                    VStack(alignment: .leading, spacing: 10) {
                        Text("Что будет")
                            .font(EcoTypography.headline)
                            .foregroundStyle(EcoTheme.ink)

                        Text(event.description)
                            .font(EcoTypography.body)
                            .foregroundStyle(EcoTheme.ink.opacity(0.86))
                            .lineSpacing(4)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(18)
                    .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
                    .overlay(
                        RoundedRectangle(cornerRadius: 24, style: .continuous)
                            .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
                    )

                }
                .padding(20)
                .padding(.bottom, 86)
            }
            .background {
                EcoBackground()
                    .ignoresSafeArea()
            }
            .safeAreaInset(edge: .bottom) {
                VStack(spacing: 0) {
                    Button(primaryButtonTitle) {
                        handlePrimaryAction()
                    }
                    .buttonStyle(DuoPrimaryButtonStyle())
                    .disabled(joined && registrationURL == nil)
                    .opacity(joined && registrationURL == nil ? 0.7 : 1)
                    .padding(.horizontal, 20)
                    .padding(.top, 12)
                    .padding(.bottom, 10)
                }
                .background(.ultraThinMaterial)
            }
            .navigationTitle("Эко-ивент")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") {
                        dismiss()
                    }
                    .font(EcoTypography.subheadline.weight(.semibold))
                    .foregroundStyle(EcoTheme.primary)
                }
            }
        }
        .presentationDetents([.large])
        .presentationDragIndicator(.visible)
    }

    private var primaryButtonTitle: String {
        if registrationURL != nil {
            return joined ? "Открыть регистрацию" : "Зарегистрироваться"
        }
        return joined ? "Вы участвуете" : "Участвовать"
    }

    private func handlePrimaryAction() {
        if let registrationURL {
            if !joined {
                joinEvent()
            }
            openURL(registrationURL)
            return
        }
        joinEvent()
    }

    private func joinEvent() {
        guard !joined else { return }
        didJoin = true
        onJoin()
        EcoFeedback.playActivitySaved()
    }

}

private struct EcoEventHeroCover: View {
    let event: EcoEvent
    let joined: Bool

    var body: some View {
        ZStack(alignment: .bottomLeading) {
            if let coverAssetName = ecoEventCoverAssetName(event) {
                Image(coverAssetName)
                    .resizable()
                    .scaledToFill()
                    .frame(height: 222)
                    .frame(maxWidth: .infinity)
                    .clipped()
                    .overlay {
                        LinearGradient(
                            colors: [
                                .black.opacity(0.02),
                                .black.opacity(0.18),
                                .black.opacity(0.56),
                            ],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    }
            } else {
                RoundedRectangle(cornerRadius: 32, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [
                                Color(hex: UInt32(event.imageTintHex)).opacity(0.95),
                                Color(hex: UInt32(event.imageTintHex)).opacity(0.54),
                                EcoTheme.primary.opacity(0.16),
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(height: 222)
                    .overlay(alignment: .bottomTrailing) {
                        Image(systemName: ecoEventIcon(event))
                            .font(.system(size: 108, weight: .black))
                            .foregroundStyle(.white.opacity(0.3))
                            .padding(24)
                    }
            }

            VStack(alignment: .leading, spacing: 12) {
                HStack(spacing: 8) {
                    EventBadge(text: joined ? "Участвую" : event.badge, tint: EcoTheme.primary)
                    if event.rewardPoints > 0 {
                        EventBadge(text: "+\(event.rewardPoints) очков", tint: Color(hex: 0xF7C300))
                    }
                }

                VStack(alignment: .leading, spacing: 5) {
                    Text(event.title)
                        .font(EcoTypography.title2)
                        .foregroundStyle(.white)
                        .shadow(color: .black.opacity(0.22), radius: 8, y: 3)
                        .fixedSize(horizontal: false, vertical: true)

                    Text(ecoEventHeroSubtitle(event))
                        .font(EcoTypography.subheadline.weight(.semibold))
                        .foregroundStyle(.white.opacity(0.88))
                        .shadow(color: .black.opacity(0.18), radius: 6, y: 2)
                }
            }
            .padding(18)
        }
        .clipShape(RoundedRectangle(cornerRadius: 32, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 32, style: .continuous)
                .stroke(.white.opacity(0.5), lineWidth: 1)
        )
        .shadow(color: EcoTheme.shadow.opacity(0.45), radius: 18, y: 10)
    }
}

private func ecoEventHeroSubtitle(_ event: EcoEvent) -> String {
    if ecoEventIsMarathon(event) {
        return "Бег, энергия и помощь детям"
    }
    return "Делаем город зеленее вместе с EcoIz"
}

private struct EventRewardCard: View {
    let points: Int

    var body: some View {
        HStack(alignment: .center, spacing: 14) {
            Image(systemName: "doc.badge.seal.fill")
                .font(.system(size: 24, weight: .bold))
                .foregroundStyle(EcoTheme.primary)
                .frame(width: 48, height: 48)
                .background(EcoTheme.primary.opacity(0.12), in: RoundedRectangle(cornerRadius: 16, style: .continuous))

            VStack(alignment: .leading, spacing: 4) {
                Text("Бонус участникам")
                    .font(EcoTypography.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text("Благодарственное письмо")
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
                Text(points > 0 ? "После участия ты получишь письмо и +\(points) эко-очков." : "После участия ты получишь письмо от организаторов.")
                    .font(EcoTypography.caption)
                    .foregroundStyle(EcoTheme.secondaryText)
                    .fixedSize(horizontal: false, vertical: true)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
        )
    }
}

private struct EventInfoRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .top, spacing: 11) {
            Image(systemName: icon)
                .font(.system(size: 14, weight: .bold))
                .foregroundStyle(EcoTheme.primary)
                .frame(width: 22, height: 22)
                .background(EcoTheme.primary.opacity(0.12), in: Circle())

            VStack(alignment: .leading, spacing: 3) {
                Text(title)
                    .font(EcoTypography.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text(value)
                    .font(EcoTypography.subheadline.weight(.semibold))
                    .foregroundStyle(EcoTheme.ink)
                    .fixedSize(horizontal: false, vertical: true)
            }
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}

private struct ThreadComposerBar: View {
    @Binding var text: String
    @Binding var pickerItems: [PhotosPickerItem]
    @Binding var selectedMedia: [PostMediaAttachment]
    let username: String
    let isPosting: Bool
    let onPost: () -> Void

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            avatar(initials: initials(from: username))

            VStack(alignment: .leading, spacing: 8) {
                TextField("Что нового?", text: $text, axis: .vertical)
                    .font(EcoTypography.body)
                    .lineLimit(1...4)

                if !selectedMedia.isEmpty {
                    ThreadMediaStrip(media: selectedMedia)
                }

                HStack {
                    PhotosPicker(
                        selection: $pickerItems,
                        maxSelectionCount: 4,
                        matching: .any(of: [.images, .videos])
                    ) {
                        Label("Медиа", systemImage: "paperclip")
                            .font(EcoTypography.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    Button("Опубликовать", action: onPost)
                        .font(EcoTypography.buttonSecondary)
                        .foregroundStyle(EcoTheme.primary)
                        .opacity((text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && selectedMedia.isEmpty) || isPosting ? 0.5 : 1)
                        .disabled((text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && selectedMedia.isEmpty) || isPosting)
                }

                if isPosting {
                    ProgressView()
                        .tint(EcoTheme.primary)
                }
            }
        }
        .padding(14)
        .background(EcoTheme.elevatedCard, in: RoundedRectangle(cornerRadius: 18, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(EcoTheme.surfaceStroke, lineWidth: 1)
        )
        .shadow(color: EcoTheme.shadow.opacity(0.45), radius: 8, y: 4)
    }

    private func initials(from name: String) -> String {
        let words = name.split(separator: " ")
        let chars = words.prefix(2).compactMap { $0.first }
        return String(chars).uppercased()
    }

    private func avatar(initials: String) -> some View {
        Circle()
            .fill(EcoTheme.avatarFill)
            .frame(width: 40, height: 40)
            .overlay(
                Text(initials)
                    .font(EcoTypography.footnote)
                    .foregroundStyle(.white)
            )
    }
}

private struct ThreadPostCell: View {
    @EnvironmentObject private var appState: AppState
    let post: EcoPost
    @State private var liked = false
    @State private var showingDeleteConfirmation = false

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(alignment: .top, spacing: 10) {
                avatar(initials: initials(from: post.author))
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(post.author)
                            .font(EcoTypography.headline)
                        Spacer()
                        HStack(spacing: 8) {
                            moderationBadge
                            if post.isOwnPost {
                                Menu {
                                    Button("Удалить пост", role: .destructive) {
                                        showingDeleteConfirmation = true
                                    }
                                } label: {
                                    Image(systemName: "ellipsis")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundStyle(.secondary)
                                }
                            } else if post.state == .published {
                                Menu {
                                    ForEach(EcoPost.ReportReason.allCases) { reason in
                                        Button(reason.rawValue) {
                                            Task {
                                                _ = await appState.reportPost(post.id, reason: reason)
                                            }
                                        }
                                    }
                                } label: {
                                    Image(systemName: "exclamationmark.bubble")
                                        .font(.system(size: 16, weight: .semibold))
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                    }
                    Text(handle(from: post.username))
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)

                    Text(post.text)
                        .font(EcoTypography.body)
                        .foregroundStyle(EcoTheme.ink)
                        .padding(.top, 2)

                    if !post.media.isEmpty {
                        ThreadMediaGrid(media: post.media)
                            .padding(.top, 2)
                    }

                    Label("Социальные реакции появятся в следующих версиях", systemImage: liked ? "heart.fill" : "heart")
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)
                        .padding(.top, 6)
                        .onTapGesture {
                            withAnimation(.spring(response: 0.25, dampingFraction: 0.7)) {
                                liked.toggle()
                            }
                        }
                }
            }
            Divider()
                .padding(.leading, 50)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.vertical, 12)
        .alert("Удалить этот пост?", isPresented: $showingDeleteConfirmation) {
            Button("Отмена", role: .cancel) {}
            Button("Удалить", role: .destructive) {
                Task {
                    _ = await appState.deletePost(post.id)
                }
            }
        } message: {
            Text("Пост исчезнет из вашей ленты.")
        }
    }

    @ViewBuilder
    private var moderationBadge: some View {
        if post.isPendingReview {
            HStack(spacing: 6) {
                ProgressView()
                    .controlSize(.small)
                    .tint(EcoTheme.primary)
                Text("В обработке")
                    .font(EcoTypography.caption)
                    .foregroundStyle(EcoTheme.primary)
            }
        } else if post.isHiddenForAuthor {
            Text(hiddenPostMessage)
                .font(EcoTypography.caption)
                .foregroundStyle(Color.red.opacity(0.8))
        } else {
            Text(relativeTime(post.createdAt))
                .font(EcoTypography.caption)
                .foregroundStyle(.secondary)
        }
    }

    private var hiddenPostMessage: String {
        let rawNote = post.moderatorNote?.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let note = rawNote, !note.isEmpty else {
            return "Нарушает правила сообщества"
        }
        if note == "Действие модерации позже будет попадать в аудит-лог backend." {
            return "Нарушает правила сообщества"
        }
        return note
    }

    private func handle(from username: String) -> String {
        let clean = username.trimmingCharacters(in: .whitespacesAndNewlines)
        if clean.hasPrefix("@") {
            return clean
        }
        return "@\(clean.lowercased())"
    }

    private func relativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }

    private func initials(from name: String) -> String {
        let words = name.split(separator: " ")
        let chars = words.prefix(2).compactMap { $0.first }
        return String(chars).uppercased()
    }

    private func avatar(initials: String) -> some View {
        Circle()
            .fill(EcoTheme.avatarFill)
            .frame(width: 36, height: 36)
            .overlay(
                Text(initials)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.white)
            )
    }
}

private struct ThreadMediaStrip: View {
    let media: [PostMediaAttachment]

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                ForEach(media) { item in
                    ThreadMediaThumbnail(item: item, height: 80)
                }
            }
        }
    }
}

private struct ThreadMediaGrid: View {
    let media: [PostMediaAttachment]

    var body: some View {
        GeometryReader { proxy in
            let width = proxy.size.width
            let halfWidth = max((width - 8) / 2, 0)

            Group {
                switch media.count {
                case 0:
                    EmptyView()
                case 1:
                    ThreadMediaThumbnail(item: media[0], height: 220)
                case 2:
                    mediaRow(media[0], media[1], width: halfWidth, height: 160)
                case 3:
                    VStack(spacing: 8) {
                        ThreadMediaThumbnail(item: media[0], height: 190)
                        mediaRow(media[1], media[2], width: halfWidth, height: 128)
                    }
                default:
                    LazyVGrid(columns: [GridItem(.fixed(halfWidth), spacing: 8), GridItem(.fixed(halfWidth), spacing: 8)], spacing: 8) {
                        ForEach(Array(media.prefix(4))) { item in
                            ThreadMediaThumbnail(item: item, height: 130)
                                .frame(width: halfWidth)
                        }
                    }
                }
            }
            .frame(width: width, alignment: .leading)
        }
        .frame(height: gridHeight)
    }

    private var gridHeight: CGFloat {
        switch media.count {
        case 0:
            return 0
        case 1:
            return 220
        case 2:
            return 160
        case 3:
            return 326
        default:
            return 268
        }
    }

    private func mediaRow(_ leading: PostMediaAttachment, _ trailing: PostMediaAttachment, width: CGFloat, height: CGFloat) -> some View {
        HStack(spacing: 8) {
            ThreadMediaThumbnail(item: leading, height: height)
                .frame(width: width)
            ThreadMediaThumbnail(item: trailing, height: height)
                .frame(width: width)
        }
    }
}

private struct ThreadMediaThumbnail: View {
    let item: PostMediaAttachment
    let height: CGFloat

    var body: some View {
        Group {
            if item.kind == .photo, let image = UIImage(data: item.data) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                ZStack {
                    LinearGradient(
                        colors: [Color(hex: 0xEAF0F5), Color(hex: 0xDCE6EE)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                    VStack(spacing: 6) {
                        Image(systemName: "play.circle.fill")
                            .font(.system(size: 26, weight: .semibold))
                            .foregroundStyle(EcoTheme.ink.opacity(0.82))
                        Text("Видео")
                            .font(EcoTypography.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }
        }
        .frame(maxWidth: .infinity)
        .frame(height: height)
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

struct ProfileView: View {
    @EnvironmentObject private var appState: AppState
    @State private var showAllChallengeAchievements = false
    @State private var showAllActivities = false
    @State private var selectedAchievement: Challenge?
    @State private var selectedActivity: EcoActivity?

    var completedChallengeAchievements: [Challenge] {
        appState.challenges.filter(\.isClaimed)
    }

    var profileAchievementPreview: [Challenge] {
        Array(completedChallengeAchievements.prefix(3))
    }

    var nextLevelProgress: CGFloat {
        let level = appState.user.level
        guard let upperBound = level.upperBoundExclusive else {
            return 1
        }
        let range = max(upperBound - level.lowerBound, 1)
        return CGFloat(min(Double(max(appState.user.points - level.lowerBound, 0)) / Double(range), 1))
    }

    var pointsToNext: Int {
        guard let upperBound = appState.user.level.upperBoundExclusive else {
            return 0
        }
        return max(upperBound - appState.user.points, 0)
    }

    var weeklyActivities: [EcoActivity] {
        let start = Calendar.current.date(byAdding: .day, value: -6, to: Date()) ?? Date()
        return appState.activities.filter { $0.createdAt >= start }
    }

    var bestCategoryTitle: String {
        let grouped = Dictionary(grouping: weeklyActivities, by: \.category)
        let top = grouped.max { $0.value.count < $1.value.count }?.key
        return top?.rawValue ?? "Нет данных"
    }

    var body: some View {
        NavigationStack {
            GeometryReader { proxy in
                ZStack {
                    EcoBackground()

                    VStack(spacing: 14) {
                        HStack {
                            Text("Профиль")
                                .font(EcoTypography.title1)
                            Spacer()
                        }
                        .padding(.horizontal)

                        ScrollView(.vertical, showsIndicators: false) {
                        VStack(spacing: 14) {
                        VStack(alignment: .leading, spacing: 12) {
                            ViewThatFits(in: .horizontal) {
                                HStack(spacing: 12) {
                                    ZStack {
                                        Circle()
                                            .fill(Color(hex: 0xE5F8EF))
                                            .frame(width: 84, height: 84)
                                        Circle()
                                            .stroke(EcoTheme.primary, lineWidth: 3)
                                            .frame(width: 84, height: 84)
                                        Text(initials(from: appState.user.fullName))
                                            .font(EcoTypography.title1)
                                            .foregroundStyle(EcoTheme.primary)
                                    }
                                    VStack(alignment: .leading, spacing: 6) {
                                        Text(appState.user.fullName)
                                            .font(EcoTypography.largeTitle)
                                            .lineLimit(1)
                                            .minimumScaleFactor(0.72)
                                        Text(appState.user.email)
                                            .font(EcoTypography.subheadline)
                                            .foregroundStyle(.secondary)
                                            .lineLimit(1)
                                            .minimumScaleFactor(0.8)
                                        PillBadge(
                                            icon: "trophy.fill",
                                            text: appState.user.level.rawValue,
                                            foreground: EcoTheme.primary,
                                            background: Color(hex: 0xDDF8EE)
                                        )
                                    }
                                    Spacer()
                                }

                                VStack(alignment: .leading, spacing: 10) {
                                    HStack(spacing: 12) {
                                        ZStack {
                                            Circle()
                                                .fill(Color(hex: 0xE5F8EF))
                                                .frame(width: 84, height: 84)
                                            Circle()
                                                .stroke(EcoTheme.primary, lineWidth: 3)
                                                .frame(width: 84, height: 84)
                                            Text(initials(from: appState.user.fullName))
                                                .font(EcoTypography.title1)
                                                .foregroundStyle(EcoTheme.primary)
                                        }
                                        VStack(alignment: .leading, spacing: 6) {
                                            Text(appState.user.fullName)
                                                .font(EcoTypography.largeTitle)
                                                .lineLimit(2)
                                                .minimumScaleFactor(0.72)
                                            Text(appState.user.email)
                                                .font(EcoTypography.subheadline)
                                                .foregroundStyle(.secondary)
                                                .lineLimit(2)
                                                .minimumScaleFactor(0.82)
                                        }
                                        Spacer(minLength: 0)
                                    }
                                    PillBadge(
                                        icon: "trophy.fill",
                                        text: appState.user.level.rawValue,
                                        foreground: EcoTheme.primary,
                                        background: Color(hex: 0xDDF8EE)
                                    )
                                }
                            }

                            VStack(alignment: .leading, spacing: 8) {
                                HStack {
                                    Text("Прогресс уровня")
                                        .font(EcoTypography.headline)
                                    Spacer()
                                    Text("\(Int(nextLevelProgress * 100))%")
                                        .font(EcoTypography.headline)
                                }
                                GeometryReader { geo in
                                    ZStack(alignment: .leading) {
                                        Capsule().fill(Color.black.opacity(0.08))
                                        Capsule()
                                            .fill(EcoTheme.primary)
                                            .frame(width: geo.size.width * max(0.05, nextLevelProgress))
                                    }
                                }
                                .frame(height: 12)

                                Text(pointsToNext > 0 ? "\(pointsToNext) очк. до следующего уровня" : "Максимальный уровень достигнут")
                                    .font(EcoTypography.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .surfaceCard()

                        HStack(spacing: 10) {
                            ProfileMetricPill(title: "CO₂", value: String(format: "%.1f кг", appState.user.co2SavedTotal), icon: "wind")
                            ProfileMetricPill(title: "Серия", value: "\(appState.user.streakDays) дн", icon: "flame.fill")
                            ProfileMetricPill(title: "Очки", value: "\(appState.user.points)", icon: "star.fill")
                        }

                        HStack(spacing: 10) {
                            ProfileMetricPill(title: "Топ-категория", value: bestCategoryTitle, icon: "chart.bar.fill")
                        }

                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Ачивки")
                                    .font(EcoTypography.title2)
                                Spacer()
                                if completedChallengeAchievements.count > 3 {
                                    Button("Смотреть все") {
                                        showAllChallengeAchievements = true
                                    }
                                    .font(EcoTypography.caption)
                                    .foregroundStyle(EcoTheme.primary)
                                    .buttonStyle(.plain)
                                }
                            }

                            if profileAchievementPreview.isEmpty {
                                Text("Заверши хотя бы один челлендж, и ачивка появится здесь.")
                                    .font(EcoTypography.subheadline)
                                    .foregroundStyle(.secondary)
                                    .padding(.top, 4)
                            } else {
                                HStack(spacing: 10) {
                                    ChallengesStatChip(
                                        title: "Получено",
                                        value: "\(completedChallengeAchievements.count)",
                                        icon: "checkmark.seal.fill",
                                        tint: Color(hex: 0x0A8E79)
                                    )
                                    ChallengesStatChip(
                                        title: "Очки",
                                        value: "+\(completedChallengeAchievements.reduce(0) { $0 + $1.rewardPoints })",
                                        icon: "star.fill",
                                        tint: Color(hex: 0xD89A00)
                                    )
                                }

                                if profileAchievementPreview.count == 1, let challenge = profileAchievementPreview.first {
                                    ProfileAchievementHeroCard(challenge: challenge) {
                                        selectedAchievement = challenge
                                    }
                                } else {
                                    HStack(spacing: 10) {
                                        ForEach(profileAchievementPreview) { challenge in
                                            ProfileAchievementMiniCard(challenge: challenge) {
                                                selectedAchievement = challenge
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .surfaceCard()

                        VStack(alignment: .leading, spacing: 8) {
                            HStack {
                                Text("Добавленные активити: \(appState.activities.count)")
                                    .font(EcoTypography.title2)
                                Spacer()
                                Button("Смотреть все") {
                                    showAllActivities = true
                                }
                                .font(EcoTypography.caption)
                                .foregroundStyle(EcoTheme.primary)
                                .buttonStyle(.plain)
                            }
                            ForEach(appState.activities.prefix(5)) { activity in
                                Button {
                                    selectedActivity = activity
                                } label: {
                                    HStack(spacing: 8) {
                                        Circle()
                                            .fill(Color(hex: 0xEAF5FF))
                                            .frame(width: 28, height: 28)
                                            .overlay(
                                                Image(systemName: activity.category.systemIconName)
                                                    .font(.system(size: 12, weight: .bold))
                                                    .foregroundStyle(activity.category.tintColor)
                                            )
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(activity.title)
                                                .font(EcoTypography.subheadline)
                                                .foregroundStyle(EcoTheme.ink)
                                                .multilineTextAlignment(.leading)
                                            Text("\(activity.category.rawValue) • \(relativeTime(activity.createdAt))")
                                                .font(EcoTypography.caption)
                                                .foregroundStyle(.secondary)
                                        }
                                        Spacer()
                                        Text("+\(activity.points)")
                                            .font(EcoTypography.caption)
                                            .foregroundStyle(EcoTheme.primary)
                                    }
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .surfaceCard()

                        Button("Выйти") {
                            appState.signOut()
                        }
                        .buttonStyle(DuoDestructiveButtonStyle())
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .padding(.bottom, 80)
                    .frame(width: proxy.size.width)
                }
                    }
                }
            }
            .navigationBarHidden(true)
            .sheet(isPresented: $showAllChallengeAchievements) {
                AllChallengeAchievementsView(challenges: completedChallengeAchievements)
            }
            .sheet(isPresented: $showAllActivities) {
                AllActivitiesView(activities: appState.activities)
            }
            .sheet(item: $selectedAchievement) { challenge in
                AchievementDetailSheet(challenge: challenge)
            }
            .sheet(item: $selectedActivity) { activity in
                ActivityDetailSheet(activity: activity)
            }
        }
    }

    private func initials(from name: String) -> String {
        let words = name.split(separator: " ")
        let chars = words.prefix(2).compactMap { $0.first }
        return String(chars).uppercased()
    }

    private func relativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

private struct ProfileMetricPill: View {
    let title: String
    let value: String
    let icon: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Label(title, systemImage: icon)
                .font(EcoTypography.caption)
                .foregroundStyle(.secondary)
            Text(value)
                .font(EcoTypography.title2)
                .foregroundStyle(EcoTheme.ink)
                        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(12)
        .background(Color.white.opacity(0.88), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(Color.black.opacity(0.05), lineWidth: 1)
        )
    }
}

private struct AllActivitiesView: View {
    let activities: [EcoActivity]
    @Environment(\.dismiss) private var dismiss
    @State private var selectedActivity: EcoActivity?

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()
                ScrollView {
                    VStack(alignment: .leading, spacing: 10) {
                        if activities.isEmpty {
                            Text("Пока нет добавленных активити.")
                                .font(EcoTypography.subheadline)
                                .foregroundStyle(.secondary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .padding(.top, 24)
                        } else {
                            ForEach(activities) { activity in
                                Button {
                                    selectedActivity = activity
                                } label: {
                                    HStack(spacing: 10) {
                                        Circle()
                                            .fill(Color(hex: 0xEAF5FF))
                                            .frame(width: 32, height: 32)
                                            .overlay(
                                                Image(systemName: activity.category.systemIconName)
                                                    .font(.system(size: 13, weight: .bold))
                                                    .foregroundStyle(activity.category.tintColor)
                                            )
                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(activity.title)
                                                .font(EcoTypography.subheadline)
                                                .foregroundStyle(EcoTheme.ink)
                                                .multilineTextAlignment(.leading)
                                            Text("\(activity.category.rawValue) • \(relativeTime(activity.createdAt))")
                                                .font(EcoTypography.caption)
                                                .foregroundStyle(.secondary)
                                        }
                                        Spacer()
                                        Text("+\(activity.points)")
                                            .font(EcoTypography.caption)
                                            .foregroundStyle(EcoTheme.primary)
                                    }
                                    .surfaceCard()
                                }
                                .buttonStyle(.plain)
                            }
                        }
                    }
                    .padding()
                    .padding(.bottom, 20)
                }
            }
            .navigationTitle("Все активити")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") { dismiss() }
                }
            }
            .sheet(item: $selectedActivity) { activity in
                ActivityDetailSheet(activity: activity)
            }
        }
    }

    private func relativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

private struct ActivityDetailSheet: View {
    let activity: EcoActivity
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                ScrollView {
                    VStack(spacing: 18) {
                        VStack(spacing: 12) {
                            Circle()
                                .fill(Color.white.opacity(0.92))
                                .frame(width: 86, height: 86)
                                .overlay(
                                    Image(systemName: activity.category.systemIconName)
                                        .font(.system(size: 32, weight: .semibold))
                                        .foregroundStyle(activity.category.tintColor)
                                )
                                .shadow(color: activity.category.tintColor.opacity(0.12), radius: 14, y: 8)

                            Text(activity.title)
                                .font(EcoTypography.largeTitle)
                                .foregroundStyle(EcoTheme.ink)
                                .multilineTextAlignment(.center)
                                .lineLimit(3)
                                .minimumScaleFactor(0.82)

                            Text("\(activity.category.rawValue) • \(relativeTime(activity.createdAt))")
                                .font(EcoTypography.subheadline)
                                .foregroundStyle(.secondary)
                                .multilineTextAlignment(.center)
                        }

                        VStack(alignment: .leading, spacing: 14) {
                            ActivityDetailRow(
                                icon: "star.fill",
                                iconTint: Color(hex: 0xE5AF3C),
                                title: "Награда",
                                value: "+\(activity.points) очк."
                            )
                            ActivityDetailRow(
                                icon: "leaf.fill",
                                iconTint: EcoTheme.primary,
                                title: "Эко-вклад",
                                value: "\(String(format: "%.1f", activity.co2Saved)) кг CO₂"
                            )
                            ActivityDetailRow(
                                icon: "text.alignleft",
                                iconTint: Color(hex: 0x78A7FF),
                                title: "Описание",
                                value: detailDescription
                            )
                        }
                        .surfaceCard()

                        if !activity.media.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Фото")
                                    .font(EcoTypography.title2)
                                    .foregroundStyle(EcoTheme.ink)

                                ThreadMediaGrid(media: activity.media)
                            }
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .surfaceCard()
                        }
                    }
                    .padding()
                    .padding(.bottom, 24)
                }
            }
            .navigationTitle("Активити")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") { dismiss() }
                }
            }
        }
    }

    private var detailDescription: String {
        let trimmed = activity.note?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
        return trimmed.isEmpty ? "Пользователь добавил активность без текстового описания." : trimmed
    }

    private func relativeTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.unitsStyle = .full
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

private struct ActivityDetailRow: View {
    let icon: String
    let iconTint: Color
    let title: String
    let value: String

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Circle()
                .fill(iconTint.opacity(0.14))
                .frame(width: 34, height: 34)
                .overlay(
                    Image(systemName: icon)
                        .font(.system(size: 14, weight: .semibold))
                        .foregroundStyle(iconTint)
                )

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
                Text(value)
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
                    .multilineTextAlignment(.leading)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer()
        }
    }
}

private struct ProfileAchievementMiniCard: View {
    let challenge: Challenge
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(alignment: .leading, spacing: 10) {
                AchievementBadgeView(challenge: challenge, size: 60)
                    .frame(maxWidth: .infinity, alignment: .leading)

                Text(challenge.title)
                    .font(EcoTypography.subheadline)
                    .fontWeight(.semibold)
                    .foregroundStyle(EcoTheme.ink)
                    .multilineTextAlignment(.leading)
                    .lineLimit(2)
                    .minimumScaleFactor(0.82)

                Text("+\(challenge.rewardPoints) очк.")
                    .font(EcoTypography.caption)
                    .foregroundStyle(Color(hex: challenge.badgeTintHex))
            }
            .frame(maxWidth: .infinity, minHeight: 140, maxHeight: 140, alignment: .topLeading)
            .padding(12)
            .background(Color.white.opacity(0.82), in: RoundedRectangle(cornerRadius: 16, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color(hex: challenge.badgeTintHex).opacity(0.18), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

private struct ProfileAchievementHeroCard: View {
    let challenge: Challenge
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 14) {
                AchievementBadgeView(challenge: challenge, size: 78)

                VStack(alignment: .leading, spacing: 6) {
                    Text("Последняя ачивка")
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)

                    Text(challenge.title)
                        .font(EcoTypography.headline)
                        .foregroundStyle(EcoTheme.ink)
                        .multilineTextAlignment(.leading)
                        .lineLimit(2)

                    HStack(spacing: 8) {
                        PillBadge(
                            icon: "star.fill",
                            text: "+\(challenge.rewardPoints) очк.",
                            foreground: Color(hex: challenge.badgeTintHex),
                            background: Color(hex: challenge.badgeBackgroundHex)
                        )
                    }
                }

                Spacer(minLength: 0)
            }
            .padding(14)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(Color.white.opacity(0.84), in: RoundedRectangle(cornerRadius: 18, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .stroke(Color(hex: challenge.badgeTintHex).opacity(0.18), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

private struct AchievementDetailSheet: View {
    let challenge: Challenge
    @Environment(\.dismiss) private var dismiss

    private var progressText: String {
        challenge.isClaimed ? "Ачивка уже получена и хранится в профиле." : "Прогресс: \(min(challenge.currentCount, challenge.targetCount))/\(challenge.targetCount)"
    }

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                VStack(spacing: 18) {
                    AchievementBadgeView(challenge: challenge, size: 116)

                    VStack(spacing: 8) {
                        Text(challenge.title)
                            .font(EcoTypography.largeTitle)
                            .foregroundStyle(EcoTheme.ink)
                            .multilineTextAlignment(.center)

                        Text(challenge.description)
                            .font(EcoTypography.body)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                            .lineSpacing(2)
                    }

                    VStack(spacing: 10) {
                        AchievementInfoRow(label: "Награда", value: "+\(challenge.rewardPoints) очк.", icon: "star.fill", tint: Color(hex: 0xD89A00))
                        AchievementInfoRow(label: "Цель", value: "\(challenge.targetCount) действий", icon: "flag.fill", tint: EcoTheme.primary)
                        AchievementInfoRow(label: "Статус", value: challenge.isClaimed ? "Получена" : (challenge.isCompleted ? "Готова к получению" : "В процессе"), icon: challenge.isClaimed ? "checkmark.seal.fill" : "bolt.fill", tint: challenge.isClaimed ? Color(hex: 0x0A8E79) : EcoTheme.sky)
                    }
                    .surfaceCard()

                    Text(progressText)
                        .font(EcoTypography.subheadline)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)

                    Spacer()
                }
                .padding()
                .padding(.bottom, 20)
            }
            .navigationTitle("Ачивка")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") { dismiss() }
                }
            }
        }
    }
}

private struct AchievementInfoRow: View {
    let label: String
    let value: String
    let icon: String
    let tint: Color

    var body: some View {
        HStack(spacing: 12) {
            Circle()
                .fill(tint.opacity(0.14))
                .frame(width: 36, height: 36)
                .overlay(
                    Image(systemName: icon)
                        .font(.system(size: 14, weight: .bold))
                        .foregroundStyle(tint)
                )
            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
                Text(value)
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
            }
            Spacer()
        }
    }
}

private struct AllChallengeAchievementsView: View {
    let challenges: [Challenge]
    @Environment(\.dismiss) private var dismiss
    @State private var selectedChallenge: Challenge?

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()
                ScrollView {
                    VStack(alignment: .leading, spacing: 12) {
                        if challenges.isEmpty {
                            Text("Пока нет завершенных челленджей.")
                                .font(EcoTypography.subheadline)
                                .foregroundStyle(.secondary)
                                .frame(maxWidth: .infinity, alignment: .center)
                                .padding(.top, 24)
                        } else {
                            ForEach(challenges) { challenge in
                                Button {
                                    selectedChallenge = challenge
                                } label: {
                                    HStack(spacing: 12) {
                                        AchievementBadgeView(challenge: challenge, size: 50)

                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(challenge.title)
                                                .font(EcoTypography.headline)
                                                .foregroundStyle(EcoTheme.ink)
                                                .multilineTextAlignment(.leading)
                                            Text("+\(challenge.rewardPoints) очк.")
                                                .font(EcoTypography.caption)
                                                .foregroundStyle(Color(hex: 0xD89A00))
                                        }
                                        Spacer()
                                        Image(systemName: "checkmark.seal.fill")
                                            .foregroundStyle(Color(hex: 0x0A8E79))
                                    }
                                }
                                .buttonStyle(.plain)
                                .surfaceCard()
                            }
                        }
                    }
                    .padding()
                    .padding(.bottom, 20)
                }
            }
            .navigationTitle("Все ачивки")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") { dismiss() }
                }
            }
        }
        .sheet(item: $selectedChallenge) { challenge in
            AchievementDetailSheet(challenge: challenge)
        }
    }
}

private struct ChallengesStatChip: View {
    let title: String
    let value: String
    let icon: String
    let tint: Color

    var body: some View {
        HStack(spacing: 8) {
            Image(systemName: icon)
                .font(.system(size: 13, weight: .bold))
                .foregroundStyle(tint)
            VStack(alignment: .leading, spacing: 2) {
                Text(value)
                    .font(EcoTypography.headline)
                    .foregroundStyle(EcoTheme.ink)
                Text(title)
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(Color.black.opacity(0.05), lineWidth: 1)
        )
    }
}

private struct ChallengeAchievementCard: View {
    let challenge: Challenge
    let compact: Bool
    let isClaiming: Bool
    let onOpenHint: () -> Void
    let onClaim: () -> Void

    private var progress: Double {
        guard challenge.targetCount > 0 else { return 0 }
        return min(max(Double(challenge.currentCount) / Double(challenge.targetCount), 0), 1)
    }

    var body: some View {
        let tint = Color(hex: challenge.badgeTintHex)

        VStack(alignment: .leading, spacing: 10) {
            Button(action: onOpenHint) {
                HStack(alignment: .top, spacing: 12) {
                    AchievementBadgeView(challenge: challenge, size: compact ? 68 : 74)

                    VStack(alignment: .leading, spacing: 6) {
                        HStack(alignment: .firstTextBaseline) {
                            Text(challenge.title)
                                .font(EcoTypography.title2)
                                .foregroundStyle(EcoTheme.ink)
                                .lineLimit(2)
                                .minimumScaleFactor(0.8)
                            Spacer()
                            Text("\(min(challenge.currentCount, challenge.targetCount))/\(challenge.targetCount)")
                                .font(EcoTypography.headline)
                                .foregroundStyle(.secondary)
                        }

                        GeometryReader { geo in
                            ZStack(alignment: .leading) {
                                Capsule()
                                    .fill(Color.black.opacity(0.08))
                                    .frame(height: 12)
                                Capsule()
                                    .fill(Color(hex: 0xF7C300))
                                    .frame(width: geo.size.width * progress, height: 12)
                            }
                        }
                        .frame(height: 12)

                        Text("- \(challenge.description)")
                            .font(EcoTypography.subheadline)
                            .foregroundStyle(.secondary)
                            .lineLimit(2)

                        Label("Нажми, чтобы посмотреть подсказку", systemImage: "lightbulb.fill")
                            .font(EcoTypography.caption)
                            .foregroundStyle(tint)
                    }
                }
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            HStack {
                Label("+\(challenge.rewardPoints) очк.", systemImage: "star.fill")
                    .font(EcoTypography.caption)
                    .foregroundStyle(Color(hex: 0xD89A00))
                Spacer()
                if challenge.isCompleted {
                    Button(action: onClaim) {
                        HStack(spacing: 6) {
                            Image(systemName: "gift.fill")
                            Text("Забрать ачивку")
                        }
                        .font(EcoTypography.caption)
                        .foregroundStyle(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(
                            LinearGradient(
                                colors: [Color(hex: 0xFFB703), Color(hex: 0xFB8500)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            ),
                            in: Capsule()
                        )
                    }
                    .buttonStyle(.plain)
                    .disabled(isClaiming)
                    .opacity(isClaiming ? 0.55 : 1)
                } else {
                    Text("В процессе")
                        .font(EcoTypography.caption)
                        .foregroundStyle(EcoTheme.ink.opacity(0.7))
                }
            }
        }
        .padding(12)
        .background(Color.white.opacity(0.9), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(tint.opacity(0.22), lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.06), radius: 8, y: 4)
    }
}

private struct ChallengeHintSheet: View {
    let challenge: Challenge
    @Environment(\.dismiss) private var dismiss

    private var hintText: String {
        let title = challenge.title.lowercased()

        if title.contains("7 эко-действий") {
            return "Добавь любые 7 активностей за последние 7 дней. Подойдут все категории: вода, энергия, транспорт, пластик и отходы."
        }
        if title.contains("3 дня без пластика") {
            return "Тебе нужно 3 раза отметить действия из категории «Пластик», например многоразовую бутылку, сумку или отказ от пакета."
        }
        if title.contains("эко-транспорт") {
            return "Засчитываются экологичные поездки: пешком, велосипед, самокат, метро или общественный транспорт. Нужно выполнить 5 таких действий."
        }
        if title.contains("водный баланс") {
            return "Выбирай действия из категории «Вода»: короткий душ, закрытый кран, полная загрузка стирки и другие привычки на экономию воды. Нужно 4 действия."
        }
        if title.contains("энергия под контролем") {
            return "Выполняй действия из категории «Энергия»: выключай свет, отключай приборы из сети, используй LED-лампы. Нужно 6 действий."
        }
        if title.contains("неделя сортировки") {
            return "Засчитываются действия по отходам: сортировка, сдача вторсырья и компост. Нужно сделать это 5 раз."
        }
        if title.contains("эко-утро") {
            return "Этот челлендж считается по утренним экопривычкам. Подойдут утренние действия вроде короткого душа, выключенного света, отказа от пластика или пешей прогулки. Нужно выполнить 3 таких действия."
        }
        if title.contains("чистый воздух") {
            return "Здесь считаются именно пешие прогулки вместо машины. Выбирай активность «Пешая прогулка» и выполни её 4 раза."
        }
        if title.contains("многоразовый герой") {
            return "Используй многоразовые вещи: сумку, бутылку, контейнер или похожую привычку. Нужно 5 таких действий."
        }
        if title.contains("осознанный шопинг") {
            return "Покупай без лишней упаковки или отказывайся от одноразового пакета. Нужно выполнить 3 таких действия."
        }
        if title.contains("эко-комьюнити") {
            return "Для этой ачивки нужно опубликовать 2 поста о своих экопривычках или результатах в ленте."
        }
        if title.contains("зеленая неделя") {
            return "Добавь 10 любых экологичных активностей за 7 дней. Считаются все категории."
        }
        if title.contains("ноль отходов") {
            return "Нужно 4 раза выполнить действия без одноразового пластика и лишнего мусора, например эко-сумка, бутылка или сортировка."
        }
        if title.contains("дом без потерь") {
            return "Здесь считаются домашние привычки на экономию воды, энергии и ресурсов. Нужно 5 таких действий."
        }
        if title.contains("эко-мастер") {
            return "Просто продолжай выполнять активности и копить очки. Когда наберёшь 250 очков экопрогресса, ачивка закроется."
        }

        return challenge.description
    }

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                VStack(spacing: 18) {
                    AchievementBadgeView(challenge: challenge, size: 96)

                    VStack(spacing: 8) {
                        Text(challenge.title)
                            .font(EcoTypography.title1)
                            .foregroundStyle(EcoTheme.ink)
                            .multilineTextAlignment(.center)

                        Text(hintText)
                            .font(EcoTypography.body)
                            .foregroundStyle(.secondary)
                            .multilineTextAlignment(.center)
                            .lineSpacing(3)
                    }

                    HStack(spacing: 10) {
                        CelebrationPill(text: "\(min(challenge.currentCount, challenge.targetCount))/\(challenge.targetCount)", icon: "flag.fill", tint: EcoTheme.primary)
                        CelebrationPill(text: "+\(challenge.rewardPoints) очк.", icon: "star.fill", tint: Color(hex: 0xD89A00))
                    }

                    Button("Понятно") {
                        dismiss()
                    }
                    .buttonStyle(DuoPrimaryButtonStyle())
                }
                .padding(24)
                .background(Color.white.opacity(0.94), in: RoundedRectangle(cornerRadius: 28, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .stroke(Color.white.opacity(0.75), lineWidth: 1)
                )
                .padding(.horizontal, 20)
            }
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Закрыть") { dismiss() }
                }
            }
        }
    }
}


private struct ChallengeClaimCelebrationOverlay: View {
    let challenge: Challenge
    let onDismiss: () -> Void
    @State private var badgeScale: CGFloat = 0.5
    @State private var glowOpacity = 0.0
    @State private var ringScale: CGFloat = 0.7
    @State private var contentOffset: CGFloat = 18
    @State private var sparkleRotation: Double = -16
    @State private var particleOffset: CGFloat = 18
    @State private var particleOpacity = 0.0
    @State private var cardScale: CGFloat = 0.94

    var body: some View {
        ZStack {
            Rectangle()
                .fill(.ultraThinMaterial)
                .overlay(
                    LinearGradient(
                        colors: [Color.white.opacity(0.1), Color.black.opacity(0.18)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
                .ignoresSafeArea()

            VStack {
                Spacer()

                VStack(spacing: 16) {
                    ZStack {
                        Circle()
                            .stroke(Color.white.opacity(0.38), lineWidth: 2)
                            .frame(width: 188, height: 188)
                            .scaleEffect(ringScale)
                            .opacity(1.1 - glowOpacity * 0.35)

                        Circle()
                            .fill(
                                RadialGradient(
                                    colors: [Color(hex: challenge.badgeBackgroundHex), Color.white.opacity(0.12)],
                                    center: .center,
                                    startRadius: 10,
                                    endRadius: 120
                                )
                            )
                            .frame(width: 170, height: 170)
                            .scaleEffect(1 + glowOpacity * 0.08)

                        ForEach(0..<8, id: \.self) { index in
                            Capsule()
                                .fill(Color.white.opacity(0.85))
                                .frame(width: 6, height: 22)
                                .offset(y: -112)
                                .rotationEffect(.degrees(Double(index) * 45 + sparkleRotation))
                                .opacity(glowOpacity)
                        }

                        ForEach(0..<10, id: \.self) { index in
                            Image(systemName: index.isMultiple(of: 2) ? "sparkles" : "leaf.fill")
                                .font(.system(size: index.isMultiple(of: 2) ? 16 : 13, weight: .bold))
                                .foregroundStyle(index.isMultiple(of: 2) ? Color.white : Color(hex: 0xD7F4BD))
                                .offset(y: -110 - particleOffset)
                                .rotationEffect(.degrees(Double(index) * 36))
                                .opacity(particleOpacity)
                        }

                        AchievementBadgeView(challenge: challenge, size: 108)
                            .scaleEffect(badgeScale)
                            .shadow(color: Color(hex: challenge.badgeTintHex).opacity(0.35), radius: 22, y: 10)
                    }

                    VStack(spacing: 8) {
                        Text("Ты молодец!")
                            .font(EcoTypography.largeTitle)
                            .foregroundStyle(EcoTheme.ink)
                        Text("Ачивка «\(challenge.title)» получена")
                            .font(EcoTypography.headline)
                            .lineSpacing(2)
                            .foregroundStyle(EcoTheme.ink)
                            .multilineTextAlignment(.center)
                            .lineLimit(2)
                            .minimumScaleFactor(0.82)
                            .fixedSize(horizontal: false, vertical: true)
                        Text("Теперь она хранится в профиле.")
                            .font(EcoTypography.subheadline)
                            .foregroundStyle(.secondary)
                    }
                    .offset(y: contentOffset)
                    .opacity(glowOpacity)

                    HStack(spacing: 10) {
                        CelebrationPill(text: "+\(challenge.rewardPoints) очк.", icon: "star.fill", tint: Color(hex: 0xD89A00))
                        CelebrationPill(text: "Профиль обновлен", icon: "person.crop.circle.fill", tint: EcoTheme.primary)
                    }
                    .offset(y: contentOffset)
                    .opacity(glowOpacity)

                    Button("Продолжить") {
                        onDismiss()
                    }
                    .buttonStyle(DuoPrimaryButtonStyle())
                    .padding(.top, 6)
                }
                .padding(28)
                .frame(maxWidth: 360)
                .background(Color.white.opacity(0.96), in: RoundedRectangle(cornerRadius: 30, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 30, style: .continuous)
                        .stroke(Color.white.opacity(0.72), lineWidth: 1)
                )
                .shadow(color: Color.black.opacity(0.14), radius: 28, y: 12)
                .padding(.horizontal, 28)
                .scaleEffect(cardScale)
                .onAppear {
                    EcoFeedback.playAchievementUnlocked()
                    withAnimation(.spring(response: 0.42, dampingFraction: 0.64)) {
                        badgeScale = 1.0
                        glowOpacity = 1.0
                        ringScale = 1.14
                        contentOffset = 0
                        sparkleRotation = 12
                        particleOpacity = 1.0
                        particleOffset = 0
                        cardScale = 1.0
                    }
                    withAnimation(.easeOut(duration: 0.95).delay(0.08)) {
                        ringScale = 1.18
                    }
                }

                Spacer()
            }
        }
        .contentShape(Rectangle())
        .onTapGesture {
            onDismiss()
        }
    }
}

struct CelebrationPill: View {
    let text: String
    let icon: String
    let tint: Color

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
            Text(text)
        }
        .font(EcoTypography.caption)
        .foregroundStyle(tint)
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(tint.opacity(0.12), in: Capsule())
    }
}

private struct AchievementBadgeView: View {
    let challenge: Challenge
    let size: CGFloat

    var body: some View {
        let tint = Color(hex: challenge.badgeTintHex)
        let background = Color(hex: challenge.badgeBackgroundHex)
        let innerSize = size * 0.56

        ZStack {
            RoundedRectangle(cornerRadius: size * 0.24, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [background, tint.opacity(0.22)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )

            RoundedRectangle(cornerRadius: size * 0.24, style: .continuous)
                .stroke(tint.opacity(0.32), lineWidth: 1.2)

            Circle()
                .stroke(Color.white.opacity(0.8), style: StrokeStyle(lineWidth: 2, dash: [6, 5]))
                .padding(size * 0.15)

            Circle()
                .fill(
                    RadialGradient(
                        colors: [Color.white.opacity(0.95), tint.opacity(0.35)],
                        center: .topLeading,
                        startRadius: 2,
                        endRadius: innerSize * 0.8
                    )
                )
                .frame(width: innerSize, height: innerSize)
                .overlay(Circle().stroke(tint.opacity(0.3), lineWidth: 1))

            Image(systemName: challenge.badgeSymbol)
                .font(.system(size: size * 0.34, weight: .black))
                .foregroundStyle(tint)
                .shadow(color: tint.opacity(0.18), radius: 2, y: 1)

            Circle()
                .fill(Color.white.opacity(0.55))
                .frame(width: size * 0.13, height: size * 0.13)
                .offset(x: size * 0.24, y: -size * 0.24)
        }
        .frame(width: size, height: size)
        .shadow(color: tint.opacity(0.24), radius: 8, y: 4)
    }
}

struct AIChatView: View {
    @EnvironmentObject private var appState: AppState
    @Environment(\.dismiss) private var dismiss
    @State private var text = ""
    @FocusState private var inputFocused: Bool

    private var canSend: Bool {
        !text.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var body: some View {
        NavigationStack {
            ZStack {
                EcoBackground()

                VStack(spacing: 12) {
                    HStack(spacing: 10) {
                        Circle()
                            .fill(Color(hex: 0xD9F2E6))
                            .frame(width: 34, height: 34)
                            .overlay(
                                Image(systemName: "sparkles")
                                    .font(.system(size: 16, weight: .bold))
                                    .foregroundStyle(EcoTheme.primary)
                            )
                        VStack(alignment: .leading, spacing: 1) {
                            Text("Эко-помощник")
                                .font(EcoTypography.title2)
                            Text("Советы по твоим действиям и вкладу")
                                .font(EcoTypography.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                        Button("Закрыть") {
                            dismiss()
                        }
                        .font(EcoTypography.buttonSecondary)
                        .foregroundStyle(.secondary)
                    }
                    .padding(.horizontal, 2)

                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 10) {
                                ForEach(appState.chatMessages) { message in
                                    AIChatMessageRow(message: message)
                                        .id(message.id)
                                }
                            }
                            .padding(12)
                        }
                        .onAppear {
                            if let last = appState.chatMessages.last {
                                proxy.scrollTo(last.id, anchor: .bottom)
                            }
                        }
                        .onChange(of: appState.chatMessages.count) { _, _ in
                            if let last = appState.chatMessages.last {
                                withAnimation(.easeOut(duration: 0.2)) {
                                    proxy.scrollTo(last.id, anchor: .bottom)
                                }
                            }
                        }
                    }
                    .surfaceCard()
                    .frame(maxHeight: .infinity)

                    HStack(spacing: 8) {
                        TextField("Спросить ИИ про эко...", text: $text, axis: .vertical)
                            .focused($inputFocused)
                            .font(EcoTypography.body)
                            .lineLimit(1...4)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 10)
                            .background(
                                RoundedRectangle(cornerRadius: 14, style: .continuous)
                                    .fill(Color.white.opacity(0.95))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 14, style: .continuous)
                                    .stroke(Color.black.opacity(0.06), lineWidth: 1)
                            )

                        Button {
                            Task {
                                let currentText = text
                                let success = await appState.sendMessageToAI(currentText)
                                guard success else { return }
                                text = ""
                                inputFocused = true
                            }
                        } label: {
                            Image(systemName: "arrow.up")
                                .font(.system(size: 16, weight: .black))
                                .foregroundStyle(.white)
                                .frame(width: 42, height: 42)
                                .background(
                                    LinearGradient(
                                        colors: [EcoTheme.primary, EcoTheme.secondary],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    ),
                                    in: Circle()
                                )
                        }
                        .buttonStyle(.plain)
                        .disabled(!canSend || appState.isSendingMessage)
                        .opacity(canSend && !appState.isSendingMessage ? 1 : 0.5)
                    }
                    .surfaceCard()

                    if appState.isSendingMessage {
                        ProgressView()
                            .tint(EcoTheme.primary)
                    }
                }
                .padding(.horizontal)
                .padding(.top, 10)
                .padding(.bottom, 12)
            }
            .navigationBarHidden(true)
        }
    }
}

private struct AIChatMessageRow: View {
    let message: ChatMessage

    var body: some View {
        HStack(alignment: .bottom, spacing: 8) {
            if message.isUser { Spacer(minLength: 44) }

            if !message.isUser {
                Circle()
                    .fill(Color(hex: 0xD9F2E6))
                    .frame(width: 28, height: 28)
                    .overlay(
                        Image(systemName: "sparkles")
                            .font(.system(size: 12, weight: .bold))
                            .foregroundStyle(EcoTheme.primary)
                    )
            }

            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                Text(message.text)
                    .font(EcoTypography.subheadline)
                    .foregroundStyle(message.isUser ? Color.white : EcoTheme.ink)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 10)
                    .background(
                        message.isUser
                            ? LinearGradient(colors: [EcoTheme.primary, EcoTheme.secondary], startPoint: .topLeading, endPoint: .bottomTrailing)
                            : LinearGradient(colors: [Color.white, Color.white], startPoint: .top, endPoint: .bottom),
                        in: RoundedRectangle(cornerRadius: 14, style: .continuous)
                    )
                    .overlay(
                        RoundedRectangle(cornerRadius: 14, style: .continuous)
                            .stroke(message.isUser ? Color.clear : Color.black.opacity(0.05), lineWidth: 1)
                    )

                Text(timeString(from: message.createdAt))
                    .font(EcoTypography.caption)
                    .foregroundStyle(.secondary)
            }

            if message.isUser {
                Circle()
                    .fill(Color.black)
                    .frame(width: 28, height: 28)
                    .overlay(
                        Image(systemName: "person.fill")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundStyle(.white)
                    )
            }

            if !message.isUser { Spacer(minLength: 44) }
        }
    }

    private func timeString(from date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ru_RU")
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
}

private struct PillBadge: View {
    let icon: String
    let text: String
    var foreground: Color = EcoTheme.ink
    var background: Color = EcoTheme.sun.opacity(0.45)

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
            Text(text)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
            .font(EcoTypography.footnote)
            .foregroundStyle(foreground)
            .fixedSize(horizontal: true, vertical: false)
            .padding(.horizontal, 14)
            .padding(.vertical, 8)
            .background(background, in: Capsule())
            .overlay(
                Capsule().stroke(foreground.opacity(0.16), lineWidth: 1)
            )
    }
}

private struct InsightPill: View {
    let text: String
    let icon: String
    let tint: Color

    var body: some View {
        HStack(spacing: 6) {
            Image(systemName: icon)
            Text(text)
                .lineLimit(1)
                .minimumScaleFactor(0.8)
        }
        .font(EcoTypography.caption)
        .foregroundStyle(tint)
        .padding(.horizontal, 10)
        .padding(.vertical, 8)
        .background(Color.white.opacity(0.14), in: Capsule())
        .overlay(
            Capsule()
                .stroke(Color.white.opacity(0.22), lineWidth: 1)
        )
    }
}

private struct AddCategoryTile: View {
    let title: String
    let subtitle: String
    let icon: String
    let tint: Color
    let gradient: [Color]
    let isSelected: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 10) {
                ZStack {
                    RoundedRectangle(cornerRadius: 18, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: isSelected ? gradient : [gradient.first?.opacity(0.92) ?? Color.white, gradient.last?.opacity(0.92) ?? Color.white],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 62, height: 62)
                    Image(systemName: icon)
                        .font(.system(size: 28, weight: .bold))
                        .foregroundStyle(.white)
                }
                .shadow(color: tint.opacity(isSelected ? 0.28 : 0.14), radius: 10, y: 6)

                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(EcoTypography.callout)
                        .foregroundStyle(EcoTheme.ink)
                        .multilineTextAlignment(.leading)
                        .lineLimit(2)
                        .minimumScaleFactor(0.85)
                    Text(subtitle)
                        .font(EcoTypography.caption)
                        .foregroundStyle(.secondary)
                        .lineLimit(2)
                }
            }
            .frame(maxWidth: .infinity, minHeight: 144, maxHeight: 144, alignment: .topLeading)
            .padding(14)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.96))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(tint.opacity(isSelected ? 0.35 : 0.18), lineWidth: 1.2)
            )
            .scaleEffect(isSelected ? 1.02 : 1)
        }
        .buttonStyle(.plain)
    }
}

private struct AddSubactivityTile: View {
    let title: String
    let icon: String
    let tint: Color
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            VStack(spacing: 10) {
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(
                        LinearGradient(
                            colors: [Color.white.opacity(0.92), Color.white.opacity(0.82)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 64, height: 64)
                    .overlay(
                        Image(systemName: icon)
                            .font(.system(size: 24, weight: .bold))
                            .foregroundStyle(tint)
                    )
                Text(title)
                    .font(EcoTypography.callout)
                    .foregroundStyle(.white)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
                    .minimumScaleFactor(0.82)
            }
            .frame(maxWidth: .infinity, minHeight: 148, maxHeight: 148)
            .padding(.horizontal, 10)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .fill(Color.white.opacity(0.14))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(Color.white.opacity(0.18), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

private struct PendingActivity {
    let category: ActivityCategory
    let title: String
    let co2: Double
    let points: Int
    let isEstimated: Bool
}

private struct PendingActivitySubmission {
    let category: ActivityCategory
    let title: String
    let co2: Double
    let points: Int
    let isEstimated: Bool
    let note: String?
    let media: [PostMediaAttachment]
}

private struct TrendDataPoint {
    let day: String
    let points: Int
}

private struct ImpactCardModel {
    let value: String
    let title: String
    let subtitle: String
    let icon: String
    let tint: Color
    let background: Color
}

private struct ImpactCard: View {
    let item: ImpactCardModel
    @State private var tapPulse = false

    var body: some View {
        VStack(alignment: .leading, spacing: 7) {
            Image(systemName: item.icon)
                .font(.system(size: 16, weight: .semibold))
                .foregroundStyle(item.tint)
                .frame(width: 38, height: 38)
                .background(Color.white.opacity(0.82), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
                .scaleEffect(tapPulse ? 1.08 : 1)
                .animation(.spring(response: 0.22, dampingFraction: 0.6), value: tapPulse)

            Text(item.value)
                .font(Font.system(size: 20, weight: .heavy, design: .rounded))
                .foregroundStyle(EcoTheme.ink)
                .lineLimit(1)
                .minimumScaleFactor(0.6)
            Text(item.title)
                .font(EcoTypography.subheadline)
                .foregroundStyle(EcoTheme.ink)
                .lineLimit(2)
                .minimumScaleFactor(0.9)
            Text(item.subtitle)
                .font(EcoTypography.caption)
                .foregroundStyle(.secondary)
                .lineLimit(2)
                .minimumScaleFactor(0.88)
        }
        .frame(maxWidth: .infinity)
        .frame(minHeight: 136, alignment: .topLeading)
        .padding(.vertical, 12)
        .padding(.horizontal, 12)
        .background(item.background.opacity(0.72), in: RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 20, style: .continuous)
                .stroke(item.tint.opacity(0.14), lineWidth: 1)
        )
        .shadow(color: .black.opacity(0.04), radius: 8, y: 4)
        .scaleEffect(tapPulse ? 0.97 : 1)
        .onTapGesture {
            tapPulse = true
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.14) {
                tapPulse = false
            }
        }
    }
}

private struct TrendChart: View {
    let points: [Int]
    let axisValues: [Int]
    @Binding var selectedIndex: Int
    let progress: CGFloat

    var body: some View {
        GeometryReader { geo in
            let clampedIndex = min(max(selectedIndex, 0), max(points.count - 1, 0))
            let frame = CGRect(origin: .zero, size: geo.size)
            let horizontalInset: CGFloat = 12
            let chartWidth = max(frame.width - horizontalInset * 2, 1)
            ZStack(alignment: .bottomLeading) {
                ForEach(Array(axisValues.enumerated()), id: \.offset) { index, _ in
                    let y = 8 + CGFloat(index) * ((frame.height - 34) / CGFloat(max(axisValues.count - 1, 1)))
                    Path { path in
                        path.move(to: CGPoint(x: horizontalInset, y: y))
                        path.addLine(to: CGPoint(x: frame.width - horizontalInset, y: y))
                    }
                    .stroke(Color.white.opacity(index == axisValues.count - 1 ? 0.2 : 0.45), style: StrokeStyle(lineWidth: 1, dash: [5, 6]))
                }

                TrendAreaShape(values: points, horizontalInset: horizontalInset)
                    .trim(from: 0, to: progress)
                    .fill(
                        LinearGradient(
                            colors: [EcoTheme.primary.opacity(0.25), EcoTheme.primary.opacity(0.04)],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )

                TrendLineShape(values: points, horizontalInset: horizontalInset)
                    .trim(from: 0, to: progress)
                    .stroke(EcoTheme.primary, style: StrokeStyle(lineWidth: 7, lineCap: .round, lineJoin: .round))

                let xStep = chartWidth / CGFloat(max(points.count - 1, 1))
                let maxValue = max(points.max() ?? 1, 1)
                let minValue = min(points.min() ?? 0, maxValue)
                let availableHeight = frame.height - 30
                let x = horizontalInset + CGFloat(clampedIndex) * xStep

                ForEach(Array(points.enumerated()), id: \.offset) { index, value in
                    let normalizedPoint = CGFloat(value - minValue) / CGFloat(max(maxValue - minValue, 1))
                    let pointY = (1 - normalizedPoint) * availableHeight + 8
                    let pointX = horizontalInset + CGFloat(index) * xStep
                    let isSelected = index == clampedIndex
                    Circle()
                        .fill(isSelected ? EcoTheme.primary : Color.white.opacity(0.9))
                        .frame(width: isSelected ? 16 : 12, height: isSelected ? 16 : 12)
                        .overlay(
                            Circle().stroke(isSelected ? Color.white : EcoTheme.primary, lineWidth: 2)
                        )
                        .shadow(color: EcoTheme.primary.opacity(isSelected ? 0.3 : 0.12), radius: 4, y: 2)
                        .position(x: pointX, y: pointY)
                        .onTapGesture {
                            withAnimation(.spring(response: 0.3, dampingFraction: 0.75)) {
                                selectedIndex = index
                            }
                        }
                }

                Path { path in
                    path.move(to: CGPoint(x: x, y: 0))
                    path.addLine(to: CGPoint(x: x, y: frame.height))
                }
                .stroke(style: StrokeStyle(lineWidth: 2, dash: [8, 8]))
                .foregroundStyle(EcoTheme.primary.opacity(0.7))
            }
        }
    }
}

private struct TrendLineShape: Shape {
    let values: [Int]
    let horizontalInset: CGFloat

    func path(in rect: CGRect) -> Path {
        var path = Path()
        guard values.count > 1 else { return path }

        let maxValue = max(values.max() ?? 1, 1)
        let minValue = min(values.min() ?? 0, maxValue)
        let range = CGFloat(max(maxValue - minValue, 1))
        let chartWidth = max(rect.width - horizontalInset * 2, 1)
        let xStep = chartWidth / CGFloat(values.count - 1)

        let points = values.enumerated().map { index, value in
            let x = horizontalInset + CGFloat(index) * xStep
            let normalized = CGFloat(value - minValue) / range
            let y = (1 - normalized) * (rect.height - 30) + 8
            return CGPoint(x: x, y: y)
        }

        path.move(to: points[0])
        for idx in 1..<points.count {
            let prev = points[idx - 1]
            let point = points[idx]
            let mid = CGPoint(x: (prev.x + point.x) / 2, y: (prev.y + point.y) / 2)
            path.addQuadCurve(to: mid, control: CGPoint(x: prev.x + xStep * 0.35, y: prev.y))
            path.addQuadCurve(to: point, control: CGPoint(x: mid.x + xStep * 0.15, y: point.y))
        }
        return path
    }
}

private struct TrendAreaShape: Shape {
    let values: [Int]
    let horizontalInset: CGFloat

    func path(in rect: CGRect) -> Path {
        var path = TrendLineShape(values: values, horizontalInset: horizontalInset).path(in: rect)
        path.addLine(to: CGPoint(x: rect.maxX - horizontalInset, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX + horizontalInset, y: rect.maxY))
        path.closeSubpath()
        return path
    }
}

private struct DuoInputField: View {
    let title: String
    @Binding var text: String

    var body: some View {
        TextField(title, text: $text)
            .font(EcoTypography.body)
            .foregroundStyle(EcoTheme.ink)
            .padding(12)
            .background(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .fill(EcoTheme.fieldBackground)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12, style: .continuous)
                    .stroke(EcoTheme.surfaceStroke.opacity(0.7), lineWidth: 1)
            )
    }
}

private struct DuoInputSecureField: View {
    let title: String
    @Binding var text: String
    @State private var isRevealed = false

    var body: some View {
        HStack(spacing: 10) {
            Group {
                if isRevealed {
                    TextField(title, text: $text)
                } else {
                    SecureField(title, text: $text)
                }
            }
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .font(EcoTypography.body)
            .foregroundStyle(EcoTheme.ink)

            Button {
                isRevealed.toggle()
            } label: {
                Image(systemName: isRevealed ? "eye.slash" : "eye")
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundStyle(.secondary)
                    .frame(width: 24, height: 24)
            }
            .buttonStyle(.plain)
            .accessibilityLabel(isRevealed ? "Скрыть пароль" : "Показать пароль")
        }
        .padding(12)
        .background(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .fill(EcoTheme.fieldBackground)
        )
        .overlay(
            RoundedRectangle(cornerRadius: 12, style: .continuous)
                .stroke(EcoTheme.surfaceStroke.opacity(0.7), lineWidth: 1)
        )
    }
}

private struct SurfaceCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(EcoTheme.card, in: RoundedRectangle(cornerRadius: 22, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 22, style: .continuous)
                    .stroke(EcoTheme.softStroke, lineWidth: 1)
            )
            .shadow(color: EcoTheme.shadow.opacity(0.55), radius: 10, y: 5)
    }
}

private extension View {
    func surfaceCard() -> some View {
        modifier(SurfaceCardModifier())
    }
}
