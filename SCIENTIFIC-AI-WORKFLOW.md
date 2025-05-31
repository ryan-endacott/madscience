# Scientific AI Workflow Framework

*A methodology for leveraging AI in scientific research with maximum efficiency and rigor.*

## Philosophy

Science has entered a new era where AI can dramatically accelerate hypothesis generation, data synthesis, and virtual validation. However, to unlock this potential, we need structured workflows that distinguish between what can be done **now** with existing data versus what requires **new experiments**.

This framework optimizes for two critical outcomes:
1. **Speed**: Exhaust the knowable before expensive data collection
2. **Rigor**: Maintain scientific standards while moving fast

## The Two-Mode Framework

### 🚀 Sprint Mode: Maximum Velocity Research

**Goal**: Move as fast as possible using available data, literature, and computational tools.

**When to use**: 
- Early hypothesis exploration
- Testing ideas against existing datasets
- Literature synthesis and gap analysis
- Computational modeling and simulation
- Cross-referencing public databases

**Key principle**: AI excels at synthesizing existing information. Don't jump to experiment design until you've exhausted what's already knowable.

**Characteristics**:
- Rapid iteration cycles (hours to days)
- Heavy AI assistance for data processing
- Focus on falsification with existing data
- Computational experiments and simulations
- Literature mining and synthesis

**Common pitfall**: AI will often suggest new experiments when existing data could answer the question. Push back and ask: "What can we determine with data that already exists?"

### 🔬 Experimental Mode: Rigorous Data Collection

**Goal**: Design and execute precise experiments when Sprint Mode has been exhausted.

**When to use**:
- Sprint Mode has identified specific, testable gaps
- Existing data cannot falsify/confirm hypothesis
- Need ground-truth validation
- Preparing for publication

**Characteristics**:
- Careful experimental design
- Statistical power analysis
- Control for confounding variables
- Reproducible methodologies
- Peer review considerations

**Transition criteria**: Only enter when you can articulate exactly what new data would change your conclusions.

## Documentation Structure

### The Unified Research Journal

**Core principle**: A single, append-only journal for each research session (e.g., "Mad Science Tuesday") preserves the evolution of ideas, captures all relevant information in chronological order, and simplifies the workflow for both humans and AI. Filenames should be date-stamped (e.g., `JOURNAL-YYYY-MM-DD.md`).

**Example Directory Structure:**
```
project/
├── WORKFLOW.md                    # This document
├── README.md                      # Project overview
├── journal/                       # Chronological research entries
│   ├── JOURNAL-YYYY-MM-DD.md      # Journal for session 1
│   └── JOURNAL-YYYY-MM-DD.md      # Journal for session 2
├── data/                          # Raw and processed data (may be referenced in journals)
│   ├── processed/
│   └── raw/
├── code/                          # Analysis scripts and tools (referenced in journals)
│   └── utils/
├── prompts/                       # AI interaction templates (if reusable)
└── outputs/                       # Generated visualizations, reports (referenced in journals)
    ├── figures/
    └── reports/
```

### Unified Journal Entry Formats

Within each `JOURNAL-YYYY-MM-DD.md`, entries are made using markdown with clear headings and timestamps. The following are recommended entry types, but can be adapted:

**1. Session Goal(s):**
   - Placed at the top of the journal.
   - Outlines what is intended for the current research session.

```markdown
# Research Journal - YYYY-MM-DD

## Session Goal(s):
- Test hypothesis X with new dataset Y.
- Refine data processing script for Z.
```

**2. Progress Update:**
   - Summarizes actions, decisions, and high-level outcomes.
   - Can link to specific code commits.

```markdown
## Progress Update - YYYY-MM-DD HH:MM
- Successfully pulled data using the new API (see Data Discovery entry below).
- Ran initial analysis script `code/analyze_correlation.py`.
- Code commit: `git commit a1b2c3d4` - "Initial correlation analysis script"
```

**3. Hypothesis Entry:**
   - Used for proposing, refining, testing, or revisiting hypotheses.
   - Each significant interaction with a hypothesis gets a new timestamped entry or a clearly marked update.

```markdown
## Hypothesis: [Descriptive Name, e.g., Inclino-Bathymetric Focusing V2] - YYYY-MM-DD HH:MM
- **Status**: [New | Refining | Testing | Validated | Falsified | Abandoned | Superseded by H-XYZ]
- **Parent/Previous Hypothesis (if any)**: [Link or ID to previous version]
- **Background**: [Why this hypothesis now? What changed from previous version?]
- **Core Idea**: [The hypothesis stated clearly and concisely.]
- **Predictions**: 
    - Prediction 1: [Specific, falsifiable prediction]
    - Prediction 2: [Another specific, falsifiable prediction]
- **Test Plan**: 
    - Use `code/simulate_whale_nav.py` with parameters A, B, C.
    - Compare output trajectories against historical stranding data in `data/processed/stranding_sites_geocoded.csv`.
- **Results/Observations**: 
    - Simulation run completed. Output in `outputs/simulations/IBF-V2-run1/`.
    - Initial plots `outputs/figures/IBF-V2-trajectories.png` show some alignment with site X.
- **Next Steps for this Hypothesis**: 
    - Investigate sensitivity to parameter B.
    - Compare with control simulation.
```

**4. Data Discovery / Update:**
   - Documents new data sources, APIs, or significant changes to existing data.

```markdown
## Data Discovery: NOAA Magnetic Field API - YYYY-MM-DD HH:MM
- **Source Details**: Found underlying API for NOAA Magnetic Field Calculator. Endpoint: `https://www.ngdc.noaa.gov/geomag-web/calculators/calculateIgrf` (example)
- **Access Method**: Python script `code/utils/fetch_noaa_api_data.py` developed.
- **Key Variables Available**: Inclination, Declination, Total Field, etc. per lat/lon/date.
- **Initial Assessment**: Confirmed data matches web calculator. Significantly faster (N points in seconds vs minutes).
- **Implications**: Enables high-resolution mapping along coastlines.
- **Action Item**: Update all relevant scripts to use this API.
```

**5. Code Development / Update:**
   - Notes significant changes or new scripts. Details are in commit messages and code comments.

```markdown
## Code Development: `code/utils/fetch_noaa_api_data.py` - YYYY-MM-DD HH:MM
- **Purpose**: Fetch magnetic field data from NOAA API.
- **Key Features**: Handles batch requests, error checking, saves to CSV.
- **Link to Commit**: `git commit e5f6g7h8` - "Add NOAA API data puller utility"
- **Notes**: Consider adding caching for repeated calls to same location/date.
```

**6. Key Insight / Working Note:**
   - Captures reflections, "aha!" moments, questions, or raw ideas. This is the "scientist's notebook" component.

```markdown
## Key Insight - YYYY-MM-DD HH:MM
- The pattern of inclination isolines seems to correlate more strongly with older stranding data than recent events. Could there be a temporal shift in whale navigation or the environment? Worth investigating if this API allows historical field calculations.

## Working Note - YYYY-MM-DD HH:MM
- Struggled with debugging the simulation script for an hour due to a subtle coordinate system mismatch. Need to standardize all geo data transformations.
```

This unified journal approach simplifies the number of files to manage while providing a rich, chronological, and interlinked record of the research process. It is designed to be easily parseable by AI tools for summarization, question answering, and even generating new entries based on actions taken (e.g., summarizing a code commit).

**Interacting with AI Assistants:**
When working with an AI assistant (like this one), you can direct it to create or append entries to your `JOURNAL-YYYY-MM-DD.md` file. The AI should be prompted to:
1.  Identify the appropriate entry type (e.g., Hypothesis, Data Discovery, Code Development) based on your request and the templates provided below.
2.  Format the information you provide according to the selected template.
3.  Include necessary timestamps.
4.  If creating a new journal for the day, use the `JOURNAL-YYYY-MM-DD.md` filename format.

**Using the `prompts/` Directory:**
It is recommended to store reusable, high-quality prompts in the `prompts/` directory. This helps ensure consistent and effective interaction with AI tools within this framework. Examples:
-   A prompt to summarize key findings related to a specific hypothesis from a journal file.
-   A prompt to draft a "Data Discovery" entry based on a template and provided information.

**Linking to `outputs/`:**
Journal entries should generally link to large output files (e.g., extensive data tables, complex visualizations, detailed simulation reports) stored in the `outputs/` directory, rather than embedding the raw output directly in the journal. This keeps the journal concise and readable.

## Workflow Phases

### Phase 0: Problem Discovery (Optional)
- **Input**: Curiosity about solvable mysteries
- **Process**: Query AI for phenomena that lack explanations but have available data
- **Output**: High-potential research questions
- **Mode**: Pre-Sprint exploration

This phase is revolutionary - you don't need domain expertise to identify important unsolved problems. AI can help surface mysteries where existing data might hold answers.

### Phase 1: Hypothesis Generation
- **Input**: Problem statement, existing literature
- **Process**: AI-assisted brainstorming, literature synthesis
- **Output**: Multiple testable hypotheses
- **Mode**: Sprint

### Phase 2: Virtual Validation
- **Input**: Hypotheses + available datasets
- **Process**: Computational testing, simulation, cross-referencing
- **Output**: Refined hypotheses, identified gaps
- **Mode**: Sprint

### Phase 3: Gap Analysis
- **Input**: Virtual validation results
- **Process**: Identify what specific new data would be decisive
- **Output**: Experiment requirements
- **Mode**: Transition point

### Phase 4: Experimental Design
- **Input**: Specific data requirements
- **Process**: Design rigorous experiments
- **Output**: Data collection protocol
- **Mode**: Experimental

### Phase 5: Validation & Iteration
- **Input**: New experimental data
- **Process**: Test hypotheses, refine understanding
- **Output**: Updated hypotheses or conclusions
- **Mode**: Both (analyze data in Sprint, design follow-ups in Experimental)

## AI Integration Points

### Data Synthesis
- Combine multiple datasets
- Cross-reference databases
- Identify patterns and anomalies
- Generate summary statistics

### Literature Mining
- Search for relevant papers
- Extract key findings
- Identify contradictions
- Find overlooked connections

### Hypothesis Refinement
- Test logical consistency
- Generate predictions
- Identify confounding factors
- Suggest alternative explanations

### Simulation & Modeling
- Agent-based models
- Statistical analysis
- Computational experiments
- Sensitivity analysis

### Visualization
- Generate explanatory figures
- Create interactive dashboards
- Produce publication-ready graphics
- Design conceptual diagrams

## Best Practices

### Sprint Mode Guidelines
1. **Exhaust before you expand**: Use all available data before seeking new data
2. **Falsify fast**: Look for ways to quickly rule out hypotheses
3. **Document everything**: Preserve the reasoning behind each step
4. **Question AI suggestions**: Push back when AI jumps to experiment design
5. **Iterate rapidly**: Prefer many small tests over one big analysis

### The Push Back Protocol
When AI suggests jumping to experiments, always ask:
- "What existing datasets could test this?"
- "Can we simulate this computationally first?"
- "What public databases haven't we checked?"
- "Could literature meta-analysis answer this?"
- "Is there a cheaper proxy measurement we could use?"

This protocol is critical - it's the difference between Sprint Mode and traditional research.

### Documentation Guidelines
1. **Maintain the Unified Journal**: For each research session, create or append to your `JOURNAL-YYYY-MM-DD.md`.
2. **Timestamp Entries**: Clearly timestamp each significant entry or update within the journal.
3. **Be Append-Only Where Possible**: For new thoughts, hypotheses, or data discoveries, add new sections. For updates to existing items, create new timestamped entries within or referring to the original. The goal is to see the evolution.
4. **Link Generously**: Reference code commits, data files (in `data/`), output files (in `outputs/`), and entries in previous `JOURNAL-YYYY-MM-DD.md` files (e.g., "This builds on HYPOTHESIS-ABC from JOURNAL-YYYY-MM-DD-PREVIOUS.md"). This creates a connected web of knowledge.
5. **Capture "Why" and "What Next"**: Don't just record *what* you did, but *why* you did it and what you plan to do next. This is crucial for continuity.
6. **Embrace "Working Notes"**: Your informal thoughts, struggles, and hunches are valuable parts of the discovery process.

### Version Control Integration
- Use Git for all code and data versioning
- Commit frequently with descriptive messages  
- Branch for exploratory analyses
- Tag major hypothesis validations
- Push to GitHub/GitLab for collaboration and reproducibility
- `.gitignore` large data files but document their sources

### Mode Transition Guidelines
1. **Clear transition criteria**: Know exactly when to switch modes
2. **Explicit gap identification**: State precisely what new data is needed
3. **Cost-benefit analysis**: Ensure new experiments are worth the investment
4. **Stakeholder alignment**: Get buy-in before major data collection efforts

## Example: Whale Stranding Research

### Sprint Mode Success
- Used existing IGRF magnetic field data
- Cross-referenced with bathymetric databases
- Tested multiple hypotheses computationally
- Identified novel "inclino-bathymetric focusing" mechanism
- Months of progress in days

### Transition Point
- Existing data showed promising patterns
- Need higher-resolution magnetic measurements
- Specific locations identified for field work
- Clear experimental protocol defined

### Key Insight
- Previous approaches jumped to expensive sonar studies
- Sprint Mode revealed simpler explanation using available data
- Saved months of premature experimentation

## Publishing the Framework

This methodology could benefit the broader scientific community:

### Potential Impact
- Accelerate early-stage research
- Reduce premature experimentation
- Improve hypothesis quality
- Enable solo scientists to do team-scale work

### Next Steps
- Test on diverse scientific problems
- Develop AI tooling for each phase
- Create templates and examples
- Gather community feedback

---

*This framework was developed during whale stranding research where Sprint Mode analysis using existing magnetic and bathymetric data revealed a novel hypothesis that had eluded decades of experimental approaches.* 