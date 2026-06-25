<div align="center">

# TotemEngine

**AI-powered research assistant** — decompose, search, crawl, summarize, synthesize.

[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/langgraph-%F0%9F%94%97-1f2937)](https://langchain-ai.github.io/langgraph/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.137%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Playwright](https://img.shields.io/badge/playwright-%E2%80%93-2e8533?logo=playwright&logoColor=white)](https://playwright.dev)
[![Docker](https://img.shields.io/badge/docker-%E2%80%93-2496ED?logo=docker&logoColor=white)](https://docker.com)

**Docker-only** · **CLI** · **REST API** · **LangGraph pipeline** · **Playwright web scraping**

</div>

---

## What It Does

TotemEngine is a self-contained research pipeline that:

1. **Decomposes** your query into 3-5 focused sub-questions (LLM)
2. **Searches** the web for each sub-question (DuckDuckGo)
3. **Crawls** full page content from JS-heavy sites (headless Chromium via Playwright)
4. **Summarizes** each source (LLM)
5. **Synthesises** everything into a coherent research report (LLM)

Everything runs inside a Docker container — no Python, browsers, or dependencies needed on the host.

---

## Quick Start

### Prerequisites

- **Docker** (Engine 24.0+ or Docker Desktop with Compose plugin)
- API key from [Mistral AI](https://console.mistral.ai/) or [Groq](https://console.groq.com/)

> No Python runtime, virtual environment, or browser installation required on your machine.

### 1. Clone

```bash
git clone https://github.com/nayaksomkar/TotemEngine.git
cd TotemEngine
```

### 2. Configure API keys

```bash
cp .env.example .env
```

Edit `.env` with at least one key:

```bash
MISTRAL_API_KEY=your-key-here      # or
GROQ_API_KEY=your-key-here
```

### 3. Build

```bash
docker compose build
```

### 4. Run

**One-shot research query:**

```bash
docker compose run --rm cli research "How does quantum computing work?" --model mistral
```

**Start the API server:**

```bash
docker compose up server
```

---

## Sample Output

### Query 1: "What are the main health benefits of green tea?" (Groq)

```
============================================================
  TotemEngine — AI Research Assistant
============================================================
  Query: What are the main health benefits of green tea?
  Model: Groq (Llama 3.3 70B)

Generated 5 sub-queries
Found 6 search results
  Fetched (1/3): https://www.healthline.com/nutrition/top-10-evidence-based-health-benefits-of-green-tea
  Fetched (2/3): https://pmc.ncbi.nlm.nih.gov/articles/PMC3679539/
  Fetched (3/3): https://pmc.ncbi.nlm.nih.gov/articles/PMC6412948/
Collected 3 pages — proceeding to summarize
Generated 3 summaries

============================================================
  TOPICS TO RESEARCH
============================================================
  1. What are the antioxidant properties of green tea and how do they contribute to overall health?
  2. How does green tea consumption affect the risk of developing certain types of cancer?
  3. What is the relationship between green tea consumption and cardiovascular health?
  4. Can green tea aid in weight loss or improve metabolic function?
  5. Are there any potential benefits of green tea for brain health?

============================================================
  SOURCES ANALYZED
============================================================
  1. https://www.healthline.com/nutrition/top-10-evidence-based-health-benefits-of-green-tea
  2. https://pmc.ncbi.nlm.nih.gov/articles/PMC3679539/
  3. https://pmc.ncbi.nlm.nih.gov/articles/PMC6412948/

============================================================
  SYNTHESIS
============================================================

**The Health Benefits of Green Tea: A Comprehensive Review**

### Introduction
Green tea has been extensively studied for its potential health benefits, and the evidence suggests that it may be a valuable addition to a healthy lifestyle. This report summarizes the main health benefits of green tea, including its antioxidant properties, cognitive function, and potential to reduce the risk of certain diseases.

### Antioxidant Properties and Overall Health
Green tea contains a range of antioxidants, including epigallocatechin-3-gallate (EGCG) and polyphenols, which have been shown to nullify excess reactive oxygen species (ROS) and reactive nitrogen species (RNS) in the body. These antioxidant properties can help reduce the impact of photoaging and promote overall health. The phytochemicals present in green tea have also been found to increase collagen and elastin fiber content in the skin, suppressing collagen-degrading enzyme production and conferring an anti-wrinkle effect.

### Cognitive Function and Neuroprotection
Green tea may help protect the brain from aging and support cognitive function. The antioxidants present in green tea, such as EGCG, may help prevent cell damage and provide other health benefits. Additionally, green tea has been reported to have neuroprotective properties, making it a potential agent for mediating neurodegenerative diseases such as Alzheimer's disease.

### Disease Prevention and Management
Regular consumption of green tea has been linked to a lower risk of cognitive impairment and certain diseases, such as heart disease and type 2 diabetes. Green tea may also help manage blood sugar levels and support oral health. Furthermore, the antioxidants present in green tea may help reduce the risk of certain cancers.

### Conclusion
In conclusion, the evidence suggests that green tea may have numerous health benefits, including improving cognitive function, aiding in fat burning, and reducing the risk of certain diseases. The antioxidant properties of green tea, particularly its polyphenols and EGCG, make it a potent agent for promoting overall health and well-being.
```

---

### Query 2: "How does a lithium-ion battery work?" (Mistral)

```
============================================================
  TotemEngine — AI Research Assistant
============================================================
  Query: How does a lithium-ion battery work?
  Model: Mistral AI

Generated 5 sub-queries
Found 6 search results
  Fetched (1/3): https://en.wikipedia.org/wiki/Lithium-ion_battery
  Fetched (2/3): https://www.flashbattery.tech/en/blog/types-of-lithium-batteries-which-chemistry-use/
  Fetched (3/3): https://en.wikipedia.org/wiki/Lithium-ion_battery
Collected 3 pages — proceeding to summarize
Generated 3 summaries

============================================================
  TOPICS TO RESEARCH
============================================================
  1. What is the basic chemical composition and structure of a lithium-ion battery?
  2. How do the charging and discharging processes occur in a lithium-ion battery at the electrochemical level?
  3. What roles do the anode, cathode, and electrolyte play in the operation of a lithium-ion battery?
  4. What are the key chemical reactions that take place during the operation of a lithium-ion battery?
  5. How do lithium ions move between the anode and cathode during charging and discharging cycles?

============================================================
  SOURCES ANALYZED
============================================================
  1. https://en.wikipedia.org/wiki/Lithium-ion_battery
  2. https://www.flashbattery.tech/en/blog/types-of-lithium-batteries-which-chemistry-use/
  3. https://en.wikipedia.org/wiki/Lithium-ion_battery

============================================================
  SYNTHESIS
============================================================

# **Lithium-Ion Batteries: Mechanisms, Chemistries, and Applications**

## **1. Introduction**
Lithium-ion (Li-ion) batteries are rechargeable energy storage systems that have transformed modern technology due to their high energy density, efficiency, and long cycle life. They power a wide range of applications, from portable electronics to electric vehicles (EVs) and grid storage. This report synthesizes key findings on how Li-ion batteries function, their chemical variations, and their advantages and limitations.

## **2. Operating Principles of Lithium-Ion Batteries**

### **2.1 Basic Mechanism**
Li-ion batteries store and release energy through the reversible movement of lithium ions (Li⁺) between two electrodes:
- **Anode (Negative Electrode):** Typically made of graphite or other carbon-based materials, which can intercalate (absorb) lithium ions during charging.
- **Cathode (Positive Electrode):** Usually composed of lithium metal oxides (e.g., lithium cobalt oxide, LiCoO₂) or other lithium-based compounds that can reversibly host lithium ions.
- **Electrolyte:** A lithium salt dissolved in an organic solvent, facilitating ion transport between the electrodes while preventing electron flow.

During **discharge**, lithium ions move from the anode to the cathode through the electrolyte, while electrons flow through an external circuit, generating electrical energy. During **charging**, an external voltage reverses this process, driving lithium ions back into the anode.

### **2.2 Key Performance Metrics**
- **Specific Energy:** 160–450 Wh/kg
- **Energy Density:** 250–1,100 Wh/L
- **Efficiency:** 80–90%
- **Nominal Cell Voltage:** 3.6–3.85 V
- **Cycle Life:** 400–1,200 full charge-discharge cycles

## **3. Chemical Variations in Lithium-Ion Batteries**

| Chemistry | Cathode Material | Key Characteristics | Primary Applications |
|-----------|-----------------|---------------------|----------------------|
| **LCO** | LiCoO₂ | High energy density, safety risks | Smartphones, laptops |
| **LMO** | LiMn₂O₄ | High power output, good thermal stability | Power tools, e-bikes |
| **LFP** | LiFePO₄ | Excellent safety, long cycle life | EVs, grid storage |
| **NMC** | LiNiMnCoO₂ | Balanced performance | EVs, energy storage |
| **NCA** | LiNiCoAlO₂ | High energy density | EVs (e.g., Tesla) |
| **LTO** | Li₄Ti₅O₁₂ | Ultra-fast charging, long lifespan | High-power applications |

## **4. Historical Development**
- **M. Stanley Whittingham (1970s):** Developed first functional lithium battery
- **John Goodenough (1980):** Introduced LiCoO₂ cathode
- **Akira Yoshino (1985):** Carbon-based anode, first commercial Li-ion battery (Sony, 1991)
These advancements earned the **2019 Nobel Prize in Chemistry**.

## **5. Advantages and Limitations**

### Advantages
- High energy density vs. older technologies
- Long cycle life (hundreds to thousands of cycles)
- Low self-discharge (~1.5–2%/month)
- No memory effect
- Versatile chemistries for different applications

### Limitations
- Safety risks (flammable electrolytes, thermal runaway)
- Degradation over time (capacity fade)
- Cost (cobalt, nickel dependency)
- Environmental impact of lithium/cobalt mining

## **6. Applications**
- **Consumer Electronics:** Smartphones, laptops (LCO, NMC)
- **Electric Vehicles:** Passenger cars, buses (NMC, NCA, LFP)
- **Energy Storage:** Grid storage, solar/wind (LFP, NMC, LTO)
- **Industrial Equipment:** Forklifts, robotics (LFP, LMO)
- **Medical Devices:** Pacemakers, diagnostics (LMO, LCO)
- **Aerospace:** Satellites, drones (NCA, NMC)

## **7. Future Directions**
- Solid-state batteries (safer, higher energy density)
- Silicon anodes (higher capacity)
- Sustainable materials (reduce cobalt reliance)
- Fast charging improvements
- Recycling advancements

## **8. Conclusion**
Li-ion batteries are a cornerstone of modern energy storage. Their operation relies on reversible lithium-ion intercalation between carbon-based anodes and lithium metal oxide cathodes. While challenges persist, ongoing innovations promise enhanced capabilities and sustainability.
```

---

## Usage

### CLI (Docker)

```bash
# Research a query
docker compose run --rm cli research "Your question" --model mistral

# Use Groq instead
docker compose run --rm cli research "Your question" --model groq

# List available models
docker compose run --rm cli models
```

### REST API (Docker)

Start server:

```bash
docker compose up server
```

Health check:

```bash
curl http://localhost:8000/health
```

Sync research (blocks until done):

```bash
curl -X POST http://localhost:8000/research/sync \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question", "model": "mistral"}'
```

Async research (returns task ID, poll for result):

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question"}'
```

---

## What's in the Image

The Docker image (`python:3.12-slim` base) packages:

- Python runtime + all dependencies (`langchain`, `langgraph`, `playwright`, `fastapi`, etc.)
- Chromium browser binary (`playwright install chromium` at build time)
- System libraries required by Chromium

You only need Docker on the host. Nothing else.

---

## Environment Variables

Set in `.env` at the project root:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MISTRAL_API_KEY` | For `mistral` model | — | Mistral AI API key |
| `GROQ_API_KEY` | For `groq` model | — | Groq API key |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## Documentation

| File | Description |
|------|-------------|
| [DOCKER.md](docs/DOCKER.md) | Full Docker deployment guide, troubleshooting |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Environment variables, model config, pipeline settings |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Pipeline structure, data flow, runtime details |
| [API.md](docs/API.md) | REST API endpoint reference |
| [CONTRIBUTING.md](docs/CONTRIBUTING.md) | Local development setup (non-Docker) |

---

## Supported Models

| Name | Provider | Default Model | Key Required |
|------|----------|---------------|--------------|
| `mistral` | [Mistral AI](https://mistral.ai) | `mistral-large-latest` | `MISTRAL_API_KEY` |
| `groq` | [Groq](https://groq.com) | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |

---

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for local development setup.

1. Fork → `git checkout -b feature/my-feature`
2. `git commit -am 'Add feature'`
3. `git push origin feature/my-feature`
4. Open a Pull Request

---

<div align="center">
  <sub>
    Built with LangChain, LangGraph, FastAPI, and Playwright.
    ·
    <a href="https://github.com/nayaksomkar/TotemEngine">GitHub</a>
  </sub>
</div>
