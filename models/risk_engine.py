def calculate_risk(hb, bp, sugar, month):

    score = 0

    try:
        systolic = int(bp.split("/")[0])
    except:
        systolic = 0

    if hb < 10:
        score += 2

    if systolic > 140:
        score += 3

    if sugar > 140:
        score += 2

    if month >= 8:
        score += 1

    if score >= 6:
        level = "High"
    elif score >= 3:
        level = "Medium"
    else:
        level = "Low"

    return score, level