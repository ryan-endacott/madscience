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

### Journal-Style Organization

**Core principle**: Append-only documentation preserves the evolution of ideas and prevents post-hoc rationalization.

```
project/
├── WORKFLOW.md                    # This document
├── README.md                      # Project overview
├── HYPOTHESIS-LOG.md              # Timestamped hypothesis entries
├── DATA-LOG.md                    # Data collection and findings
├── WORKING-NOTES.md               # Human observations and thoughts
├── EXPERIMENT-DESIGN.md           # When ready for new data
├── data/                          # Raw and processed data
├── code/                          # Analysis scripts and tools
├── prompts/                       # AI interaction templates
└── outputs/                       # Generated visualizations and reports
```

### Hypothesis Log Format

Each hypothesis gets a timestamped, immutable entry:

```markdown
## HYPOTHESIS-2025-05-29-001: Inclino-Bathymetric Focusing

### Background
[Context that led to this hypothesis]

### Core Idea
[The hypothesis in clear, testable terms]

### Predictions
[Specific, falsifiable predictions]

### Virtual Tests Possible
[What can be tested with existing data]

### Status
[Active/Validated/Falsified/Superseded]

### Next Steps
[Immediate actions in current mode]
```

### Data Log Format

```markdown
## DATA-2025-05-29-001: IGRF Magnetic Field Analysis

### Source
[Where the data came from]

### Processing
[What was done to it]

### Key Findings
[Bullet points of discoveries]

### Implications
[How this affects active hypotheses]

### Quality Assessment
[Limitations and confidence levels]
```

## Workflow Phases

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

### Documentation Guidelines
1. **Never edit history**: Append new entries rather than modifying old ones
2. **Timestamp everything**: Track the evolution of ideas
3. **Link references**: Connect data to hypotheses to conclusions
4. **Include failures**: Document what didn't work and why
5. **Human insights**: Add your own observations and intuitions

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