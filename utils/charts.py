import matplotlib.pyplot as plt


# -------------------------------------
# Bar Chart
# -------------------------------------
def create_bar_chart(parameters):
    """Create a bar chart from a dict-like `parameters` and return the Figure."""
    fig, ax = plt.subplots(figsize=(6, 4))

    ax.bar(list(parameters.keys()), list(parameters.values()))

    ax.set_title("Medical Parameters")
    ax.set_ylabel("Values")

    plt.setp(ax.get_xticklabels(), rotation=20)

    plt.tight_layout()

    return fig


# -------------------------------------
# Pie Chart
# -------------------------------------
def create_pie_chart(range_results):

    normal = 0
    abnormal = 0

    for result in range_results.values():

        if result["Status"] == "🟢 Normal":
            normal += 1
        else:
            abnormal += 1

    labels = ["🟢 Normal", "🔴 Abnormal"]
    sizes = [normal, abnormal]

    fig, ax = plt.subplots(figsize=(5, 5))

    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )

    ax.set_title("Health Status Distribution")

    return fig