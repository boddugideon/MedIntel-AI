def calculate_dashboard(range_results, risk_factors):

    total = len(range_results)

    normal = 0
    abnormal = 0

    for result in range_results.values():

        if result["Status"] == "🟢 Normal":
            normal += 1
        else:
            abnormal += 1

    dashboard = {
        "Total Parameters": total,
        "Normal": normal,
        "Abnormal": abnormal,
        "Risk Factors": len(risk_factors)
    }

    return dashboard