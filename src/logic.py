
from ClassHero import ClassHero


def CreateHeroes():
    return [
        ClassHero("Ares", "blue", "warrior", "melee"),
        ClassHero("Blaze", "red", "mage", "ranged"),
        ClassHero("Cora", "green", "marksman", "artillery"),
        ClassHero("Drax", "blue", "marksman", "ranged"),
        ClassHero("Ezra", "red", "warrior", "melee"),
        ClassHero("Faye", "green", "mage", "artillery"),
    ]


def FactionScore(a, b):
    if a.Faction == "blue" and b.Faction == "red":
        return 1
    if a.Faction == "red" and b.Faction == "green":
        return 1
    if a.Faction == "green" and b.Faction == "blue":
        return 1

    if b.Faction == "blue" and a.Faction == "red":
        return -1
    if b.Faction == "red" and a.Faction == "green":
        return -1
    if b.Faction == "green" and a.Faction == "blue":
        return -1

    return 0


def RoleScore(a, b):
    if a.Role == "warrior" and b.Role == "marksman":
        return 1
    if a.Role == "marksman" and b.Role == "mage":
        return 1
    if a.Role == "mage" and b.Role == "warrior":
        return 1

    if b.Role == "warrior" and a.Role == "marksman":
        return -1
    if b.Role == "marksman" and a.Role == "mage":
        return -1
    if b.Role == "mage" and a.Role == "warrior":
        return -1

    return 0


def AttackScore(a, b):
    if a.AttackType == "melee" and b.AttackType == "ranged":
        return 1
    if a.AttackType == "ranged" and b.AttackType == "artillery":
        return 1
    if a.AttackType == "artillery" and b.AttackType == "melee":
        return 1

    if b.AttackType == "melee" and a.AttackType == "ranged":
        return -1
    if b.AttackType == "ranged" and a.AttackType == "artillery":
        return -1
    if b.AttackType == "artillery" and a.AttackType == "melee":
        return -1

    return 0


def CompareHeroes(hero, other):
    score = 0
    score += FactionScore(hero, other)
    score += RoleScore(hero, other)
    score += AttackScore(hero, other)
    return score


def EvaluateHero(hero, allHeroes):
    totalScore = 0
    details = []

    for other in allHeroes:
        if other.Name == hero.Name:
            continue

        result = CompareHeroes(hero, other)
        totalScore += result

        if result > 0:
            status = "хорош"
        elif result < 0:
            status = "плох"
        else:
            status = "средний"

        details.append((other.Name, status))

    return totalScore, details


def MetaRanking(allHeroes):
    scores = []

    for hero in allHeroes:
        score, _ = EvaluateHero(hero, allHeroes)
        scores.append((hero, score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores
