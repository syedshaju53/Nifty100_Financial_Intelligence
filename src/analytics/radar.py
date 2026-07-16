
import numpy as np
import matplotlib.pyplot as plt


METRICS = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "debt_to_equity",
    "free_cash_flow",
    "revenue_cagr_5yr",
    "pat_cagr_5yr",
    "composite_quality_score"
]


def normalize(values):

    values = np.array(values, dtype=float)

    mn = np.nanmin(values)
    mx = np.nanmax(values)

    if mx == mn:
        return np.ones_like(values) * 50

    return (values - mn) / (mx - mn) * 100


def create_radar(company_name, company_values, peer_values, output_path):

    company = normalize(company_values)
    peer = normalize(peer_values)

    labels = [
        "ROE",
        "NPM",
        "OPM",
        "D/E",
        "FCF",
        "Revenue CAGR",
        "PAT CAGR",
        "Quality"
    ]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    ).tolist()

    company = np.concatenate((company, [company[0]]))
    peer = np.concatenate((peer, [peer[0]]))
    angles += angles[:1]

    fig = plt.figure(figsize=(8, 8))

    ax = plt.subplot(111, polar=True)

    ax.plot(
        angles,
        company,
        linewidth=2,
        label=company_name
    )

    ax.fill(
        angles,
        company,
        alpha=0.25
    )

    ax.plot(
        angles,
        peer,
        linestyle="--",
        linewidth=2,
        label="Peer Average"
    )

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    plt.title(company_name)

    plt.legend(loc="upper right")

    plt.tight_layout()

    plt.savefig(output_path)

    plt.close()