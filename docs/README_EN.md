# Industrial predictive maintenance — portfolio overview

Personal data science and data engineering project by [Joseph / JsphLynx](https://github.com/JsphLynx). It explores whether simulated equipment failures can be anticipated with useful lead time and a controlled false-alert burden.

**All data are synthetic.** The case is inspired by public information about Sestao's CSP process. There is no implied company affiliation, access to real plant telemetry, validated digital twin, or demonstrated industrial savings.

| Version | Contribution |
|---|---|
| v1 | Initial CSP simulation, compressed CSV, traceability and a baseline model experiment |
| v2 | Broader scenario, Parquet, PostgreSQL schema and event-based baseline evaluation |
| v3 | Focused motor/bearing subsystem, quality and latency handling, 24-hour target |
| v3.1 | Audit corrections, 16 simulated worlds, observable IF reference, executable evaluation protocol and local PostgreSQL evidence |

Baseline experiments exist in v1/v2. **XGBoost and Isolation Forest training for v3.1 remains pending.** Version metrics are not directly comparable because scenarios, horizons and alert policies change.

Explore the [Spanish portfolio guide](PORTFOLIO.md), [version history](EVOLUCION.md), [v3.1 source](../versions/v3.1/src/), [audit closure](reports/cierre_auditoria_v3_1.pdf), [videos](../media/README.md), and [roadmap](ROADMAP.md).

The repository includes source code, configuration, dictionaries, SQL, reports and historical evidence. Bulk generated data are kept outside the source history; see [distribution status](DESCARGAS.md). Historical validation is distinguished from checks rerun for this publication.
