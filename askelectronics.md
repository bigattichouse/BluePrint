[**Back to Wiki Index**](https://www.reddit.com/r/AskElectronics/wiki/index/)

# Using AI in Electronics Design

>**Read this before trusting an AI-generated circuit**  
>  
>AI chatbots and design assistants can produce answers, schematics and part lists that look convincing but are electrically wrong. Typical errors include incorrect pinouts, power and ground on the wrong pins, missing components, invented part numbers and miscalculated values.  
>  
>A wrong circuit can destroy components, overheat, start a fire or cause electric shock. **Never use an AI-generated design for anything connected to mains electricity, high-energy batteries, chargers or safety-related equipment unless a competent person has checked it against the datasheets and tested it.**  
>  
>An AI tool cannot take responsibility for a design. You can.  
>  
>**If you cannot check the AI's answer yourself, treat it as a starting point for research, not as a finished design.**

---

**Quick verdict (as of late 2026)**

- **Good for:** explaining concepts, summarising datasheets, suggesting where to start, generating calculation scripts, drafting documentation, reviewing your own design for things to double-check, and (in dedicated tools) automating parts of placement and routing.
- **Unreliable for:** complete schematics from a text description, exact pinouts, component values without working, part availability, and anything where a single wrong connection matters.
- **Worst at:** drawing circuit diagrams as images. AI image generators produce pictures that resemble schematics but rarely make electrical sense.
- **Golden rule:** every AI output must be checked against a primary source (the datasheet, a simulation, or a measurement) before it reaches a soldering iron or a PCB order.

---

## 1. How accurate is it?

### What the research shows

Independent benchmarks published in 2026 give a sobering picture of general-purpose models designing circuits on their own.

- **HWE-Bench** (March 2026) asked six leading models to produce board-level schematics for 300 real open-source projects, given the requirements and the relevant datasheets. The designs were then checked by electrical rule checks and LTspice simulation. On average the models got roughly 72% of the basic pin connections right and passed about 59% of the simulation checks, but **the best model produced a fully correct design only 8.15% of the time**, and most models managed around 4–6%.
- The same study found that models were good at connecting pins with familiar names (SDA, TXD, RST, USB data lines) but frequently missed or invented connections on **multiplexed pins** and **devices with several ground or supply pins**. Accuracy also fell as the number of pins in the design increased.
- **MultModLM** (June 2026) found that when one AI model was asked to judge the quality of another's schematic, its scores had almost no agreement with human reviewers. In other words, **asking an AI to check an AI-generated schematic is not a meaningful check.**
- Other 2026 papers (CircuitLM, SchGen, EDASYTH) report much better results, but only when the model is forced to look up real pinouts from a parts database, generate a checkable netlist rather than a picture, and pass simulation or ERC before moving on. The improvement comes from the **verification around the model**, not from the model suddenly understanding electronics.

Models improve quickly, so specific percentages will date. The pattern has been consistent for several years, however: **AI is reasonably good at the overall structure of a circuit and poor at the exact details that make it work.**

### Common errors

When reviewing AI output, look specifically for:

- **Wrong or invented pinouts**, especially on ICs with several package options.
- **Supply and ground connected to the wrong pins**, or unused supply pins left floating.
- **Missing support components**: decoupling capacitors, pull-up resistors, bootstrap capacitors, reverse-polarity protection, flyback diodes.
- **Values that are stated but not calculated**, or calculations with arithmetic errors.
- **Ratings ignored**: voltage, current, power dissipation and thermal limits.
- **Obsolete, unavailable or non-existent part numbers.**
- **Pin conflicts on microcontrollers**: one pin assigned to two functions at once.
- **Confident tone.** A wrong answer is usually written just as fluently as a right one.

### Where it does better

AI answers are more reliable for:

- Well-known textbook circuits (voltage dividers, LED resistors, basic op-amp stages, standard regulator applications).
- Explaining *why* a circuit works, rather than designing a new one.
- Standard interfaces and buses that appear in a lot of open-source code (I²C, SPI, UART, CAN, RS-485).
- Tasks where you can immediately verify the result, such as writing a script to calculate filter values or parse a BOM.

---

## 2. Pros and cons

| | Pros | Cons |
|:--|:--|:--|
| **Learning** | Patient, available at any time, can explain a concept several ways and at different levels. | Can teach misconceptions with complete confidence. A beginner has no way to tell. |
| **Datasheets** | Quickly summarises long datasheets and finds relevant sections. | May misread tables or graphs, or mix up variants of the same part. Always confirm figures in the datasheet itself. |
| **Calculations** | Can show working and write scripts you can rerun. | Arithmetic and unit errors are common when the answer is given in prose. Ask for the working or a script. |
| **Schematic generation** | Fast first draft or block diagram. Good for exploring options. | Low end-to-end accuracy. Every connection needs checking. |
| **Design review** | Useful as an extra checklist ("what have I forgotten?"). | Misses real errors and flags non-problems. Not a substitute for ERC, DRC, simulation or a human review. |
| **Layout and routing** | Dedicated tools can produce multiple candidate layouts quickly and check them against constraints. | Output still needs DRC and an experienced eye on critical nets, grounding, thermal and EMC behaviour. |
| **Firmware and test code** | Generally strong at driver code, test scripts and automation. | Can call registers or library functions that do not exist for your specific part. |
| **Documentation** | Drafts test procedures, design notes and README files well. | Can describe features the design does not actually have. |
| **Confidentiality** | Local or enterprise-hosted models can keep data in-house. | Pasting a client's design into a public chatbot may breach an NDA or company policy. |

---

## 3. Quality of diagramming

This is the area where AI output is most misleading, because a drawing can *look* right while being completely wrong.

### A. AI image generators

AI image generators produce pictures that resemble schematics: symbols, lines and labels in a familiar style. In practice, wires often end nowhere, symbols are malformed, pin labels are gibberish, components are connected in electrically meaningless ways, and text values are invented. Recent community tests of 2026 image models show the drawings are now cleaner and more attractive, but connections still go missing (in one test, a ground connection vanished when the model edited a diagram).

**Do not build from an AI-generated image of a circuit, and do not post one here as "your schematic".** It cannot be checked, because there is no underlying netlist.

### B. Text and ASCII schematics from chatbots

Chatbots often draw circuits as ASCII art. These are acceptable for very simple circuits but frequently misalign, making it unclear which lines connect. Asking for a **netlist or a connection list** instead ("U1 pin 4 → GND, R1 between U1 pin 2 and VCC…") gives something you can check line by line against the datasheet.

### C. Code-based schematics

The most promising approach is for the AI to write code that produces a real schematic in a real tool: for example, SKiDL (Python), JITX, or scripts that generate KiCad files. The output is editable, can be checked with ERC, and can be exported to simulation. Layout and readability are often poor (cramped symbols, odd placement, overlapping labels), so expect to tidy it up by hand.

### D. AI inside EDA tools

AI assistants built into PCB software work on your real schematic, so they cannot invent a symbol that does not exist in the library and their changes appear as normal edits you can undo. Diagram quality is as good as the tool's own drawing engine. The risk moves from "the drawing is fake" to "the AI made a plausible but wrong edit", so review the change history.

### E. Layout tools

Autonomous placement and routing tools produce real board files. Their vendors describe checking candidates against signal-integrity, power-integrity and manufacturing constraints. That is helpful, but a layout can pass design-rule checks and still have serious electrical problems. Critical nets, grounding, thermal paths and EMC still need an experienced reviewer.

---

## 4. Using AI well: a practical workflow

1. **Write down the requirements yourself first.** Supply voltage, current, input and output ranges, environment, size, budget. An AI cannot design to requirements you have not stated.
2. **Use AI to explore and explain**, not to decide. Ask for several approaches and the trade-offs between them.
3. **Choose real parts and download their datasheets.** Give the AI the datasheet (or the relevant section) rather than relying on what it "remembers" about a part.
4. **Ask for a netlist or connection list, with working for every calculated value.** Avoid accepting pictures.
5. **Check every connection against the datasheet**, especially supply, ground, enable, reset and configuration pins.
6. **Simulate** (LTspice, ngspice, Falstad) wherever practical. Simulation catches many errors that look fine on paper.
7. **Draw the schematic in proper EDA software and run ERC.** Run DRC on the layout.
8. **Prototype and measure** on a current-limited bench supply before trusting the design.
9. **Keep a record** of what the AI suggested and what you changed. This helps when something goes wrong and when asking for help.

---

## 5. Notes for hobbyists

- AI is a genuinely useful tutor for understanding *why* circuits work. Ask it to explain, then check the explanation against a textbook, application note or reputable tutorial.
- If you cannot yet tell whether an AI's circuit is correct, build from a **manufacturer's reference design or application note** instead. These are tested and are usually the best starting point.
- Treat AI-chosen parts with suspicion. Check that the part exists, is in stock and comes in a package you can actually solder.
- Never trust AI with **mains, lithium battery charging or high-voltage circuits**. Use proven modules or designs from reputable sources.
- AI is very good at writing Arduino, ESP32 and Raspberry Pi code, and at explaining error messages. Hardware is where it most often goes wrong.

## 6. Notes for professionals

- **Accountability does not transfer.** The engineer who signs off a design is responsible for it, however it was produced.
- **Check your company policy and NDAs** before pasting schematics, BOMs or client data into a public AI service. Enterprise or locally hosted models may be required.
- **Vendor claims are marketing until proven on your designs.** Most published comparisons of AI PCB tools come from the vendors themselves. Pilot on a non-critical board and measure the result.
- **Verification is the value.** Industry commentary in 2026 consistently emphasises that useful AI workflows are the ones where the model's output is continuously checked by deterministic simulation and verification engines, not the ones where the model is trusted directly.
- **Regulated work** (medical, automotive, aerospace, safety-critical) needs a clear record of how a design was produced and verified. Consider how AI-assisted steps fit into your quality system before adopting them.
- Many experienced designers see AI shifting the job from drawing and routing towards defining constraints, reviewing and validating. Those skills still depend on understanding the physics.

---

## 7. Asking for help with an AI-generated design on this subreddit

You are welcome to ask about a circuit an AI suggested, but please:

- **Say that it came from an AI**, and which tool.
- **Post a proper schematic** drawn in EDA software or neatly by hand, not an AI-generated image.
- **Include datasheet links** for the main parts.
- **Explain what you have already checked** and what you are unsure about.
- **Ask a specific question.** "Is this AI circuit right?" is hard to answer; "Is the feedback divider on this buck converter correct for 3.3 V output?" gets a useful reply.

Be aware that some related subreddits have stricter rules. For example, r/PrintedCircuitBoard does not accept AI designs or AI topics in its review requests.

---

### Further reading

**Research on accuracy**

- [HWE-Bench: Can Language Models Perform Board-level Schematic Designs? — arXiv, March 2026](https://arxiv.org/abs/2603.18102). Benchmark of six leading models on 300 real board-level designs, checked with ERC and LTspice. The source of the 8.15% best-case figure above; the failure-mode analysis is worth reading.
- [MultModLM: A multi-modal benchmark for LLM-based hardware schematic generation — arXiv, June 2026](https://arxiv.org/abs/2606.27666). Finds that AI models judging schematics barely agree with human reviewers. A useful warning against "AI checking AI".
- [CircuitLM: A Multi-Agent LLM-Aided Design Framework for Generating Circuit Schematics — arXiv, 2026](https://arxiv.org/abs/2601.04505). Shows how grounding a model in a real pinout database reduces hallucinated connections.
- [SchGen — Microsoft Research (GitHub)](https://github.com/microsoft/SchGen). Research model that writes code to generate editable KiCad schematics. The repository itself warns that generated designs may contain wrong connections and should be inspected in KiCad.
- [AMSbench: Evaluating Multimodal LLMs on Analog/Mixed-Signal Circuits — arXiv](https://arxiv.org/abs/2505.24138). Benchmark covering schematic reading, analysis and design; highlights particular weakness on complex analogue design.

**Industry commentary**

- [AI in PCB design: hype or the future of engineering? — Siemens EDA blog, August 2026](https://blogs.sw.siemens.com/electronic-systems-design/2026/08/24/ai-in-pcb-design-hype-or-the-future-of-engineering/). Interview-based discussion of how AI changes the PCB designer's role and job market. Vendor perspective, but balanced on the need for human oversight.
- [PCB Design in 2026 and Beyond — I-Connect007, February 2026](https://iconnect007.com/article/148786/pcb-design-in-2026-and-beyond/148783/design). Short opinion piece from a principal PCB design engineer on designers' concerns about AI and why PCB design should be recognised as engineering.
- [PCB Design in the Age of AI (Elektor Engineering Insights #64) — Elektor, October 2026](https://www.elektormagazine.com/news/pcb-design-in-the-age-of-ai/). Conversation with Robert Feranec (FEDEVEL) on what AI layout tools can and cannot handle, and why simulation, measurement and testing still matter.
- [Synopsys, Cadence, and Siemens Take Agentic Chip Design Autonomous at DAC — Futurum Group, July 2026](https://futurumgroup.com/insights/synopsys-cadence-and-siemens-take-agentic-chip-design-autonomous-at-dac/). Analyst summary of the major EDA vendors' agentic AI announcements, including Cadence's agent for PCB and advanced packaging.
- [Flux Copilot: Under the Hood — Flux](https://unified.flux.ai/p/blog/flux-copilot-under-the-hood). A tool vendor's own explanation of how its AI assistant works and why it sometimes gets pin mappings and default values wrong. Refreshingly candid.
- [AI Tools for PCB Design: Which Tool Fits Your Workflow Stage? — JLCPCB](https://jlcpcb.com/blog/ai-tools-for-pcb-design). Overview of current AI PCB tools by design stage, including a section on limitations. Written by a manufacturer, so treat recommendations accordingly.
- [The 2026 Guide to Autonomous PCB Design: Quilter vs. DeepPCB vs. Flux.ai — Quilter](https://www.quilter.ai/blog/the-2026-guide-to-autonomous-pcb-design-quilter-vs-deeppcb-vs-flux-ai). Useful explanation of the difference between co-pilot tools and autonomous layout tools. Written by one of the vendors compared.

**Community tests and discussion**

- [Will the new GPT-Image 2 generate an electronic circuit diagram? — Elektroda, 2026](https://www.elektroda.com/news/news4172034.html). Hands-on test of current image models drawing circuits. Good illustration of why AI images are not schematics.
- [KiCad MCP Pro (GitHub)](https://github.com/oaslananka/kicad-mcp-pro). An example of the community tools that connect AI assistants to KiCad for ERC/DRC and design review. Its own documentation describes it as a first-pass review assistant, not a sign-off authority, which is the right way to think about all of these tools.

The research papers above describe the state of the art at the time of publication. AI tools change quickly, so check the date of any source and expect today's figures to improve. The need to verify AI output against datasheets, simulation and measurement is unlikely to change.
