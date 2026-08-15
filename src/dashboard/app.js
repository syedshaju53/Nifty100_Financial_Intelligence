/* =========================================================
   NIFTY100 FINANCIAL INTELLIGENCE
   Dashboard Application
========================================================= */


const API_BASE =
    "http://127.0.0.1:8000/api/v1";


/* =========================================================
   CHART INSTANCES
========================================================= */

const chartInstances = {};


/* =========================================================
   FORMAT NUMBER
========================================================= */

function formatNumber(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "-";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
        return "-";
    }

    return number.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );
}


/* =========================================================
   FORMAT PERCENT
========================================================= */

function formatPercent(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "-";
    }

    const number = Number(value);

    if (Number.isNaN(number)) {
        return "-";
    }

    return `${number.toFixed(2)}%`;
}


/* =========================================================
   CHECK API
========================================================= */

async function checkAPI() {

    const status =
        document.getElementById("apiStatus");

    try {

        const response =
            await fetch(
                `${API_BASE}/health`
            );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data =
            await response.json();

        if (data.status === "ok") {

            status.textContent =
                "● API Connected";

            status.style.color =
                "#4ade80";

        } else {

            status.textContent =
                "● API Error";

            status.style.color =
                "#f87171";
        }

    } catch (error) {

        status.textContent =
            "● API Offline";

        status.style.color =
            "#f87171";

        console.error(
            "API health check failed:",
            error
        );
    }
}


/* =========================================================
   LOAD COMPANY
========================================================= */

async function loadCompany() {

    const input =
        document.getElementById(
            "companyInput"
        );

    if (!input) {
        return;
    }

    const company =
        input.value
            .trim()
            .toUpperCase();

    if (!company) {

        alert(
            "Enter a company ID"
        );

        return;
    }


    try {

        const response =
            await fetch(
                `${API_BASE}/financials/${company}/latest`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const result =
            await response.json();


        if (
            result.status !==
            "success"
        ) {

            alert(
                "Company not found"
            );

            return;
        }


        const d =
            result.data;


        /* ===============================
           COMPANY INFORMATION
        =============================== */

        document.getElementById(
            "companyName"
        ).textContent =
            company;


        document.getElementById(
            "companyYear"
        ).textContent =
            `Financial Year: ${result.year}`;


        /* ===============================
           KPI
        =============================== */

        document.getElementById(
            "npm"
        ).textContent =
            formatPercent(
                d.net_profit_margin_pct
            );


        document.getElementById(
            "opm"
        ).textContent =
            formatPercent(
                d.operating_profit_margin_pct
            );


        document.getElementById(
            "roe"
        ).textContent =
            formatPercent(
                d.return_on_equity_pct
            );


        document.getElementById(
            "de"
        ).textContent =
            formatNumber(
                d.debt_to_equity
            );


        document.getElementById(
            "interestCoverage"
        ).textContent =
            formatNumber(
                d.interest_coverage
            );


        document.getElementById(
            "assetTurnover"
        ).textContent =
            formatNumber(
                d.asset_turnover
            );


        /* ===============================
           FINANCIAL PERFORMANCE
        =============================== */

        document.getElementById(
            "sales"
        ).textContent =
            formatNumber(
                d.sales
            );


        document.getElementById(
            "operatingProfit"
        ).textContent =
            formatNumber(
                d.operating_profit
            );


        document.getElementById(
            "pbt"
        ).textContent =
            formatNumber(
                d.profit_before_tax
            );


        document.getElementById(
            "netProfit"
        ).textContent =
            formatNumber(
                d.net_profit
            );


        document.getElementById(
            "eps"
        ).textContent =
            formatNumber(
                d.eps
            );


        document.getElementById(
            "fcf"
        ).textContent =
            formatNumber(
                d.free_cash_flow
            );


        /* ===============================
           VALUATION
        =============================== */

        document.getElementById(
            "marketCap"
        ).textContent =
            formatNumber(
                d.market_cap_crore
            );


        document.getElementById(
            "enterpriseValue"
        ).textContent =
            formatNumber(
                d.enterprise_value_crore
            );


        document.getElementById(
            "pe"
        ).textContent =
            formatNumber(
                d.pe_ratio
            );


        document.getElementById(
            "pb"
        ).textContent =
            formatNumber(
                d.pb_ratio
            );


        document.getElementById(
            "evEbitda"
        ).textContent =
            formatNumber(
                d.ev_ebitda
            );


        document.getElementById(
            "dividendYield"
        ).textContent =
            formatPercent(
                d.dividend_yield_pct
            );


        /* ===============================
           CAGR
        =============================== */

        document.getElementById(
            "revenueCagr"
        ).textContent =
            formatPercent(
                d.revenue_cagr_5yr
            );


        document.getElementById(
            "patCagr"
        ).textContent =
            formatPercent(
                d.pat_cagr_5yr
            );


        document.getElementById(
            "epsCagr"
        ).textContent =
            formatPercent(
                d.eps_cagr_5yr
            );


        document.getElementById(
            "fcfCagr"
        ).textContent =
            formatPercent(
                d.fcf_cagr_5yr
            );


        /* ===============================
           SHOW COMPANY SECTION
        =============================== */

        document
            .getElementById(
                "companySection"
            )
            .classList
            .remove("hidden");


        /* ===============================
           LOAD HISTORY
        =============================== */

        await loadFinancialHistory(
            company
        );


    } catch (error) {

        console.error(
            "Company loading error:",
            error
        );

        alert(
            "Unable to connect to API"
        );
    }
}


/* =========================================================
   LOAD FINANCIAL HISTORY
========================================================= */

async function loadFinancialHistory(
    company
) {

    try {

        const response =
            await fetch(
                `${API_BASE}/financials/${company}`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const result =
            await response.json();


        if (
            result.status !==
            "success"
        ) {

            console.error(
                "Financial history unavailable"
            );

            return;
        }


        const data =
            result.data;


        if (
            !Array.isArray(data) ||
            data.length === 0
        ) {

            console.error(
                "No historical data found"
            );

            return;
        }


        /* ===============================
           SORT BY YEAR
        =============================== */

        data.sort(
            (a, b) =>
                Number(a.year) -
                Number(b.year)
        );


        /* ===============================
           PREPARE DATA
        =============================== */

        const years =
            data.map(
                row =>
                    row.year
            );


        const revenue =
            data.map(
                row =>
                    row.sales
            );


        const profit =
            data.map(
                row =>
                    row.net_profit
            );


        const roe =
            data.map(
                row =>
                    row.return_on_equity_pct
            );


        const npm =
            data.map(
                row =>
                    row.net_profit_margin_pct
            );


        /* ===============================
           SHOW HISTORY SECTION
        =============================== */

        document
            .getElementById(
                "historySection"
            )
            .classList
            .remove("hidden");


        /* ===============================
           CREATE CHARTS
        =============================== */

        createLineChart(
            "revenueChart",
            "Revenue",
            years,
            revenue,
            "₹ Cr"
        );


        createLineChart(
            "profitChart",
            "Net Profit",
            years,
            profit,
            "₹ Cr"
        );


        createLineChart(
            "roeChart",
            "ROE",
            years,
            roe,
            "%"
        );


        createLineChart(
            "marginChart",
            "Net Profit Margin",
            years,
            npm,
            "%"
        );


    } catch (error) {

        console.error(
            "Financial history error:",
            error
        );
    }
}


/* =========================================================
   CREATE LINE CHART
========================================================= */

function createLineChart(
    canvasId,
    label,
    labels,
    values,
    unit
) {

    const canvas =
        document.getElementById(
            canvasId
        );


    if (!canvas) {
        return;
    }


    /* ===============================
       DESTROY OLD CHART
    =============================== */

    if (
        chartInstances[canvasId]
    ) {

        chartInstances[
            canvasId
        ].destroy();

        chartInstances[
            canvasId
        ] = null;
    }


    /* ===============================
       REMOVE INVALID VALUES
    =============================== */

    const cleanValues =
        values.map(
            value => {

                if (
                    value === null ||
                    value === undefined ||
                    value === ""
                ) {

                    return null;
                }

                const number =
                    Number(value);

                return Number.isNaN(
                    number
                )
                    ? null
                    : number;
            }
        );


    /* ===============================
       CREATE CHART
    =============================== */

    chartInstances[
        canvasId
    ] = new Chart(
        canvas,
        {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {

                        label: label,

                        data:
                            cleanValues,

                        borderWidth: 2,

                        tension: 0.3,

                        fill: false,

                        pointRadius: 3,

                        pointHoverRadius: 5

                    }

                ]

            },


            options: {

                responsive: true,

                maintainAspectRatio:
                    false,


                interaction: {

                    intersect: false,

                    mode: "index"

                },


                plugins: {

                    legend: {

                        display: true,

                        position:
                            "top"

                    },


                    tooltip: {

                        callbacks: {

                            label:
                                function (
                                    context
                                ) {

                                    const value =
                                        context.raw;

                                    if (
                                        value ===
                                        null
                                    ) {

                                        return `${label}: -`;
                                    }


                                    return `${label}: ${Number(value).toLocaleString("en-IN", {
                                        maximumFractionDigits: 2
                                    })} ${unit}`;

                                }

                        }

                    }

                },


                scales: {

                    x: {

                        title: {

                            display: true,

                            text:
                                "Financial Year"

                        }

                    },


                    y: {

                        beginAtZero: false,

                        title: {

                            display: true,

                            text: unit

                        },

                        ticks: {

                            callback:
                                function (
                                    value
                                ) {

                                    return Number(
                                        value
                                    ).toLocaleString(
                                        "en-IN",
                                        {
                                            maximumFractionDigits:
                                                0
                                        }
                                    );

                                }

                        }

                    }

                }

            }

        }
    );
}


/* =========================================================
   LOAD SCREENER
========================================================= */

async function loadScreener() {

    const tbody =
        document.getElementById(
            "screenerBody"
        );


    if (!tbody) {
        return;
    }


    tbody.innerHTML = `
        <tr>
            <td
                colspan="7"
                class="loading-cell"
            >
                Loading...
            </td>
        </tr>
    `;


    try {

        const response =
            await fetch(
                `${API_BASE}/screener`
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const result =
            await response.json();


        if (
            result.status !==
            "success"
        ) {

            throw new Error(
                "Screener API returned an error"
            );
        }


        tbody.innerHTML = "";


        if (
            !Array.isArray(
                result.data
            ) ||
            result.data.length === 0
        ) {

            tbody.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="loading-cell"
                    >
                        No companies found
                    </td>
                </tr>
            `;

            return;
        }


        result.data.forEach(
            company => {

                const row =
                    document.createElement(
                        "tr"
                    );


                const companyCell =
                    document.createElement(
                        "td"
                    );

                const companyStrong =
                    document.createElement(
                        "strong"
                    );

                companyStrong.textContent =
                    company.id || "-";


                companyCell.appendChild(
                    companyStrong
                );


                companyCell.appendChild(
                    document.createElement(
                        "br"
                    )
                );


                const companyName =
                    document.createTextNode(
                        company.company_name ||
                        "-"
                    );


                companyCell.appendChild(
                    companyName
                );


                row.appendChild(
                    companyCell
                );


                /* SECTOR */

                const sectorCell =
                    document.createElement(
                        "td"
                    );

                sectorCell.textContent =
                    company.broad_sector ||
                    "-";

                row.appendChild(
                    sectorCell
                );


                /* ROE */

                const roeCell =
                    document.createElement(
                        "td"
                    );

                roeCell.textContent =
                    formatPercent(
                        company.roe_pct
                    );

                row.appendChild(
                    roeCell
                );


                /* ROCE */

                const roceCell =
                    document.createElement(
                        "td"
                    );

                roceCell.textContent =
                    formatPercent(
                        company.roce_pct
                    );

                row.appendChild(
                    roceCell
                );


                /* DEBT EQUITY */

                const debtCell =
                    document.createElement(
                        "td"
                    );

                debtCell.textContent =
                    formatNumber(
                        company.debt_to_equity
                    );

                row.appendChild(
                    debtCell
                );


                /* NPM */

                const npmCell =
                    document.createElement(
                        "td"
                    );

                npmCell.textContent =
                    formatPercent(
                        company.net_profit_margin_pct
                    );

                row.appendChild(
                    npmCell
                );


                /* OPM */

                const opmCell =
                    document.createElement(
                        "td"
                    );

                opmCell.textContent =
                    formatPercent(
                        company.operating_profit_margin_pct
                    );

                row.appendChild(
                    opmCell
                );


                tbody.appendChild(
                    row
                );

            }
        );


    } catch (error) {

        console.error(
            "Screener error:",
            error
        );


        tbody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="loading-cell"
                >
                    Unable to load screener
                </td>
            </tr>
        `;
    }
}


/* =========================================================
   ANALYZE BUTTON
========================================================= */

function setupEventListeners() {

    const analyzeBtn =
        document.getElementById(
            "analyzeBtn"
        );


    const refreshBtn =
        document.getElementById(
            "refreshScreener"
        );


    const companyInput =
        document.getElementById(
            "companyInput"
        );


    if (analyzeBtn) {

        analyzeBtn.addEventListener(
            "click",
            loadCompany
        );
    }


    if (refreshBtn) {

        refreshBtn.addEventListener(
            "click",
            loadScreener
        );
    }


    if (companyInput) {

        companyInput.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key ===
                    "Enter"
                ) {

                    loadCompany();
                }

            }
        );
    }
}


/* =========================================================
   PAGE INITIALIZATION
========================================================= */

window.addEventListener(
    "load",
    async function () {

        console.log(
            "Nifty100 Financial Intelligence loaded"
        );


        /* API */

        await checkAPI();


        /* EVENT LISTENERS */

        setupEventListeners();


        /* COMPANY */

        const input =
            document.getElementById(
                "companyInput"
            );


        if (
            input &&
            input.value.trim()
        ) {

            await loadCompany();

        }


        /* SCREENER */

        await loadScreener();

    }
);