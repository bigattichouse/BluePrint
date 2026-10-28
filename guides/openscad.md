# OpenSCAD to Fabrication: A Practical Training Guide

**From parametric code to real parts: mechanical drafting, fit testing, 3D printing, laser cutting, and CNC machining**  
**Revision:** 1.1 · **Prepared:** October 2026 · **Updated:** October 28, 2026  
**Audience:** makers, inventors, small-model developers, repairers, machinists-in-training, and humans using AI-assisted CAD tools

> **Core principle:** A model is not finished when it looks right on screen. It is finished when the fabricated part meets its functional requirements, fits the parts it must fit, and can be reproduced from a known design revision and process.

This guide uses OpenSCAD as the main design tool because it describes geometry as code. A small number of dimensions can control an entire family of parts, and the source file can be reviewed, versioned, tested, and regenerated. The same general engineering workflow applies to other CAD systems.

This is a practical training guide, not a substitute for a machine's operating manual, material safety data, an engineer's review, or the applicable engineering standards. Use the rules of the specific machine, material supplier, and fabrication shop whenever they differ from generic examples here.

---

## Contents

1. [The fabrication mindset](#1-the-fabrication-mindset)
2. [The complete digital-to-physical workflow](#2-the-complete-digital-to-physical-workflow)
3. [Mechanical drawing and CAD vocabulary](#3-mechanical-drawing-and-cad-vocabulary)
4. [Measurement before modeling](#4-measurement-before-modeling)
5. [OpenSCAD fundamentals](#5-openscad-fundamentals)
6. [Parametric design that survives change](#6-parametric-design-that-survives-change)
7. [Boolean geometry and reusable design patterns](#7-boolean-geometry-and-reusable-design-patterns)
8. [Physical test coupons: test the fit before committing](#8-physical-test-coupons-test-the-fit-before-committing)
9. [Designing for FDM and resin 3D printing](#9-designing-for-fdm-and-resin-3d-printing)
10. [Designing for laser cutting](#10-designing-for-laser-cutting)
11. [Designing for CNC milling and routing](#11-designing-for-cnc-milling-and-routing)
12. [Export formats: SCAD, STL, 3MF, DXF, SVG, and more](#12-export-formats-scad-stl-3mf-dxf-svg-and-more)
13. [From geometry to machine instructions](#13-from-geometry-to-machine-instructions)
14. [Inspection, debugging, and quality control](#14-inspection-debugging-and-quality-control)
15. [Worked OpenSCAD projects](#15-worked-openscad-projects)
16. [A repeatable project folder and revision system](#16-a-repeatable-project-folder-and-revision-system)
17. [Safety and engineering limits](#17-safety-and-engineering-limits)
18. [Learning path and practice exercises](#18-learning-path-and-practice-exercises)
19. [Quick-reference checklists](#19-quick-reference-checklists)
20. [Glossary](#20-glossary)
21. [References and further reading](#21-references-and-further-reading)

---

# 1. The fabrication mindset

## 1.1 Design the function, not merely the shape

Before opening OpenSCAD, describe what the part has to do. A useful requirement statement identifies:

- **Function:** what the part supports, aligns, retains, seals, transfers, protects, or moves.
- **Interfaces:** the surfaces, holes, shafts, fasteners, rails, panels, or other parts it touches.
- **Loads:** what forces, moments, vibration, impact, pressure, or weight it must tolerate.
- **Environment:** temperature, water, UV exposure, oil, chemicals, dust, food contact, or outdoor use.
- **Fabrication process:** FDM printing, resin printing, laser cutting, CNC milling/routing, or a hybrid of these.
- **Constraints:** available stock, build volume, material thickness, cutter size, cost, time, and tools.
- **Acceptance criteria:** what can be measured or observed to decide whether the part works.

A vague requirement such as “make a bracket” is hard to validate. “Support a 1 kg sensor 60 mm from a vertical panel, with two M4 fasteners, keeping the sensor face within 1 degree of vertical” is much more useful. It still may need engineering analysis, but it gives the design a target.

## 1.2 Distinguish appearance models from manufacturing models

A **visual model** communicates what something looks like. A **manufacturing model** communicates geometry that a process can produce. They overlap, but they are not identical.

A visual model may have paper-thin walls, touching-but-not-connected solids, decorative details below the printer's resolution, or sharp internal corners a CNC cutter cannot make. A manufacturing model must respect process limitations, tolerances, material behavior, tool access, workholding, and assembly.

## 1.3 The iterative loop

Use this cycle for every functional part:

1. **Specify:** write down function, interfaces, loads, environment, and acceptance criteria.
2. **Measure:** measure the mating item or record the drawing/manufacturer specification.
3. **Parameterize:** identify the dimensions that should be named variables rather than buried in geometry.
4. **Model:** create simple, readable geometry in OpenSCAD.
5. **Preview and render:** catch code errors, geometry errors, and unintended intersections.
6. **Export:** generate a file appropriate for the target fabrication process.
7. **Make a coupon or prototype:** test critical dimensions and interfaces cheaply.
8. **Measure and assemble:** record what actually happened—not just whether it “seemed close.”
9. **Revise:** change the model or process based on evidence.
10. **Make the finished part:** preserve the source, settings, and revision that produced it.

For an inexpensive part, one prototype may be enough. For a complicated or expensive assembly, several rounds of coupons may save hours of wasted material and machine time.

## 1.4 Separate design error from process error

If a hole is too small, several causes are possible:

- the modeled hole is too small;
- the export was scaled incorrectly;
- the slicer or CAM software interpreted units differently;
- the printer's holes print undersize;
- the laser kerf or CNC toolpath compensation is wrong;
- the stock thickness is different from its nominal value;
- the part warped, shrank, or was measured inconsistently.

Do not compensate for every problem by randomly changing the CAD model. Identify where the error entered the pipeline. A good test coupon helps isolate the cause.

---

# 2. The complete digital-to-physical workflow

A typical project crosses several representations. Each representation serves a different purpose.

| Stage | Artifact | Purpose | Main risk |
|---|---|---|---|
| Design intent | Requirements and hand measurements | Defines what the part must do | Missing interfaces or constraints |
| Parametric model | `.scad` | Editable, reproducible source geometry | Incorrect parameters or assumptions |
| 2D profile | `.dxf` or `.svg` | Planar geometry for laser cutting or 2D CAM | Wrong scale, duplicate paths, unsuitable contours |
| 3D surface mesh | `.stl` or `.3mf` | Geometry for a slicer or mesh-oriented workflow | Open mesh, wrong scale, poor tessellation |
| Drawing | PDF/DWG/DXF or a drawing from a CAD package | Communicates dimensions, tolerances, datums, notes, and revision | Ambiguity or incomplete specification |
| CAM project | Native CAM file | Converts geometry into machine paths and operations | Wrong tool, work zero, feeds, or stock assumptions |
| Machine instructions | G-code or machine-specific output | Drives the machine | Incorrect postprocessor or unsafe setup |
| Inspection record | Measurements, photos, test results | Shows whether the part met the requirements | No traceability to design/process revision |

**OpenSCAD is primarily a geometry authoring tool.** It creates solid geometry and exports selected file formats. It is not, by itself, a complete laser-cutter controller, slicer, CNC CAM package, or formal drawing-management system.

A robust project normally retains the `.scad` source even after an STL or DXF is made. Export files are outputs; the source is the design intent.

---

# 3. Mechanical drawing and CAD vocabulary

The following terms appear frequently in mechanical design, drafting, inspection, and fabrication. Learn to use them precisely: they help humans, machinists, suppliers, and AI tools talk about the same geometry.

## 3.1 Geometry terms

- **Part:** one manufactured item.
- **Assembly:** two or more parts joined or arranged to perform a function.
- **Component:** an individual item within an assembly; often used interchangeably with part.
- **Feature:** a meaningful geometric element, such as a hole, slot, boss, rib, pocket, flange, or fillet.
- **Primitive:** a basic geometric form, such as a cube, cylinder, sphere, polygon, or circle.
- **Profile:** a 2D outline or cross-section.
- **Section:** the shape revealed by cutting through an object with an imaginary plane; in a drawing it may be shown as a section view.
- **Pocket:** a recessed region that does not necessarily pass through the whole part.
- **Through-hole:** a hole extending through the full thickness of a part.
- **Blind hole:** a hole that terminates inside the part.
- **Bore:** a cylindrical internal surface or hole, commonly with an emphasis on accuracy or function.
- **Counterbore:** a larger, usually flat-bottomed cylindrical recess around a hole, often to seat a bolt head.
- **Countersink:** a conical recess, often to seat a countersunk screw head.
- **Spotface:** a shallow machined flat surface around a hole to provide a clean seating area.
- **Boss:** a raised feature, often used around a fastener or bearing.
- **Rib:** a thin strengthening feature.
- **Gusset:** a reinforcing web or plate between structural members.
- **Web:** a relatively thin wall connecting thicker regions.
- **Flange:** a projecting rim or plate used for fastening, locating, or stiffening.
- **Slot:** an elongated opening, often used for adjustment.
- **Keyway:** a slot that accepts a key to prevent relative rotation between a shaft and hub.
- **Fillet:** a rounded transition between surfaces, commonly an internal concave radius.
- **Round:** often used for a convex rounded edge; usage varies by industry and CAD package.
- **Chamfer:** a beveled edge, often specified by size and angle.
- **Draft angle:** a taper that assists removal from a mold or tool; also used to describe taper in other manufacturing contexts.
- **Taper:** a gradual change in diameter or width.
- **Relief:** a feature that creates clearance or avoids interference at an edge or corner.
- **Dogbone / T-bone relief:** a small relief at an internal corner to let a round CNC cutter produce a mating square-cornered feature.
- **Undercut:** geometry that is hidden from a direct tool approach or cannot be made by a simple straight-pull tool or ordinary 3-axis milling operation.
- **Envelope:** the overall bounding dimensions or space a part occupies.
- **Datum feature:** a real surface, edge, or feature used as the physical basis for measurement or geometric control.

## 3.2 Dimensions and measurement language

- **Dimension:** a numerical value that defines size, location, or orientation.
- **Nominal dimension:** the target or stated size, such as 10 mm. The actual permitted range depends on the tolerance.
- **Actual size:** the measured size of a manufactured feature.
- **Basic dimension:** an exact theoretical value used as a reference in a drawing or geometric-tolerancing scheme; it is not, by itself, a tolerance band.
- **Overall dimension:** the full length, width, or height of a part.
- **Center-to-center distance:** distance between the centers of two holes, shafts, or features.
- **Pitch:** repeated spacing, such as hole spacing in a line or the distance between adjacent thread crests measured parallel to the thread axis.
- **Bolt circle / pitch circle diameter (BCD/PCD):** diameter of a circle passing through the centers of a repeated pattern of holes.
- **Radius (R):** distance from a circle's center to its edge.
- **Diameter (Ø):** distance across a circle through its center; the diameter equals twice the radius.
- **Wall thickness:** thickness of a wall or shell.
- **Material thickness / stock thickness:** actual thickness of sheet, plate, or stock material before machining.
- **Depth:** distance into a pocket or down from a referenced surface.
- **Height:** vertical or feature-height measurement; be clear about the reference plane.
- **Datum / reference plane:** a chosen origin or geometric reference from which other dimensions are defined.
- **Baseline dimensioning:** multiple dimensions measured from a common reference.
- **Chain dimensioning:** dimensions measured sequentially from one feature to the next; errors can accumulate along the chain.
- **Ordinate dimensioning:** coordinates of features measured from a common datum, often useful for hole patterns.
- **Dimension stack-up:** cumulative effect of multiple dimensions and tolerances in an assembly.
- **Symmetry:** corresponding geometry arranged around a centerline or plane.
- **Concentricity (informal usage):** sharing a common center or axis. Formal GD&T has a narrower meaning and is not interchangeable with simple coaxiality in every standard.
- **Coaxial:** two cylindrical or rotational features sharing the same axis.
- **Perpendicular / square:** at 90 degrees to a reference, within an applicable tolerance.
- **Parallel:** running in the same direction while remaining at a specified separation.
- **Flatness:** control of how much a surface varies from a perfect plane.
- **Straightness:** control of how much a line element or axis varies from a perfect straight line.
- **Roundness / circularity:** control of how close a cross-section is to a perfect circle.
- **Runout:** variation of a rotating surface relative to a datum axis as it rotates.
- **Position:** in GD&T, a defined control on the location of a feature relative to datums; not merely a rough coordinate.

## 3.3 Fits, clearance, and tolerance

These concepts are central to making parts that assemble reliably.

- **Tolerance:** the permitted variation in a dimension or geometric characteristic.
- **Tolerance band:** the interval between the lower and upper allowed limits.
- **Allowance:** an intentional difference between mating parts at maximum material condition; the exact usage is standard-dependent.
- **Clearance fit:** mating parts are intended to have space between them, so they can assemble or move.
- **Sliding fit:** a clearance fit intended to allow linear movement.
- **Running fit:** a fit intended for relative motion during operation.
- **Locational fit:** a fit intended primarily to position parts.
- **Transition fit:** a fit that may result in slight clearance or slight interference depending on actual sizes.
- **Interference fit / press fit:** the mating features overlap in nominal size so assembly requires force, deformation, or another controlled process.
- **Loose fit:** generous clearance to ease assembly or allow variability.
- **Friction fit:** retention primarily by contact pressure and friction. In hobby use the term is broad; specify real dimensions when reliability matters.
- **Snap fit:** a flexible feature deflects during assembly and returns to hold the parts together.
- **Radial / per-side clearance:** the gap on one side between a centered shaft and hole. If a shaft is 6.00 mm and the desired radial clearance is 0.20 mm, the hole is 6.40 mm.
- **Diametral clearance:** the difference between hole diameter and shaft diameter. A 6.40 mm hole around a 6.00 mm shaft has 0.40 mm diametral clearance, or 0.20 mm per side when centered.
- **Interference value:** the amount by which the shaft is larger than the hole, stated with a clearly defined sign convention.
- **Shrinkage:** dimensional change as a material cools, cures, dries, or solidifies.
- **Kerf:** width of material removed by a cutting process, such as a laser beam or saw blade.
- **Kerf compensation:** adjustment to the cut path so the retained material has the intended dimensions.
- **Process capability:** the real-world ability of a machine/process to repeatedly produce a feature within the desired limits.
- **Repeatability:** how consistently the process produces the same result.
- **Accuracy:** closeness to a target value.
- **Precision:** closeness of repeated measurements or results to one another; high precision does not automatically imply accuracy.

**Important:** never write “0.2 mm tolerance” when you actually mean “0.2 mm extra clearance per side.” Tolerance, clearance, and measurement uncertainty are different concepts. State what is allowed to vary and how the gap is defined.

## 3.4 Fits are not universal numbers

Traditional engineering fit systems (for example, hole-basis fits) define standardized ranges for mating dimensions. Those systems are useful for precision shafts, bearings, pins, and machined assemblies. A printed polymer hole or a laser-cut slot behaves differently and needs process-specific validation.

For an ordinary maker project, choose a sensible starting clearance, then fabricate a coupon on the actual machine with the actual material. For a critical mechanism, use the applicable fit standard and verify the tolerance capability of the manufacturing process. Do not apply a single “magic” clearance to every printer, resin, polymer, laser, router, or material thickness.

## 3.5 Drawings and annotation

A mechanical drawing commonly contains:

- **Title block:** part name/number, drawing number, units, scale, revision, author/checker, and other control information.
- **Orthographic views:** front, top, side, and other aligned views.
- **Isometric view:** a 3D pictorial view for orientation; usually not used to extract precise dimensions by scaling the image.
- **Section view:** shows interior geometry by imagining the part cut through a plane.
- **Detail view:** enlarged view of a small or complex region.
- **Centerline / center mark:** indicates axes or centers of circular features.
- **Hidden line:** indicates edges not visible in a particular view.
- **Leader:** line connecting a note or dimension to a feature.
- **Callout:** a note identifying a feature or requirement, such as a hole diameter or thread.
- **General tolerance note:** a drawing-level note setting tolerances for dimensions not individually toleranced. Its meaning depends on the referenced standard and the drawing.
- **Material specification:** exact grade or class where relevant, not just “metal” or “plastic.”
- **Finish note:** surface treatment, roughness, paint, anodizing, deburring, or other process instructions.
- **Revision block:** history of design changes.
- **BOM (bill of materials):** list of the components in an assembly, often including quantities and part numbers.

OpenSCAD can generate geometry and simple 2D profiles, but a native `.scad` model is not a complete engineering drawing. If a supplier or machinist needs dimensions, tolerances, datums, surface finish, material, or inspection requirements, issue a drawing or specification that communicates those things explicitly.

## 3.6 GD&T: know what it is for

**Geometric Dimensioning and Tolerancing (GD&T)** is a standardized symbolic language for specifying how much form, orientation, location, and runout may vary. **Datums** define the references used to evaluate a feature. A **feature control frame** states a geometric control and its tolerance, often with datum references.

Common GD&T controls include flatness, straightness, circularity, cylindricity, perpendicularity, parallelism, angularity, position, profile, and runout. The exact symbols, rules, and interpretation depend on the applicable standard and edition. ASME Y14.5 is a major U.S. reference; see the resources at the end of this guide. Learn the concept here, but consult the applicable standard or a qualified drawing specialist before using formal GD&T on a production drawing.

---

# 4. Measurement before modeling

## 4.1 Tools and their practical uses

| Tool | Best uses | Limitations / cautions |
|---|---|---|
| Steel rule | Quick overall measurements and layout | Readability and parallax limit precision |
| Digital or dial calipers | Outside dimensions, inside dimensions, depth, step measurements | Jaw pressure, burrs, alignment, and caliper quality affect readings; not ideal for every tight tolerance |
| Micrometer | More controlled measurement of thickness and outside diameter | Limited range; requires correct technique and suitable measuring faces |
| Feeler gauges | Measuring small gaps or checking clearance | Not a substitute for measuring complex geometry |
| Drill bits / pin gauges | Approximate hole checking or accurate gauge checking when properly specified | Shank diameters and tolerances vary; use known gauge dimensions for critical fits |
| Square | Checking right angles and setup | Quality and reference surfaces matter |
| Straightedge | Checking straightness or flatness by comparison | Quantitative assessment may require more suitable metrology |
| Thread pitch gauge | Identifying thread pitch | Does not fully establish thread class or diameter |
| Radius gauge | Checking common radii | Limited to the supplied radii |
| Scale, ruler, or known reference feature | Catching import/export scale errors | Only useful if the reference is known and the measurement is reliable |

Calipers are often sufficient for maker-level fit work, but always match the tool to the tolerance and the feature. Measuring a flexible printed wall with excessive caliper force can give a false result.

## 4.2 Measure interfaces, not just the outside

For a replacement part, record the dimensions that determine function:

- mating shaft diameter and usable length;
- hole diameter, depth, and access for a fastener;
- center-to-center distances for multiple holes;
- panel or stock thickness at several points;
- clearances to nearby parts;
- mounting-face flatness and orientation when important;
- head diameter and height for screws or bolts;
- connector or bearing dimensions from a trusted data sheet where available.

Measure a feature at more than one orientation where ovality, taper, wear, or distortion might matter. For sheet stock, measure thickness in several places and record a range rather than assuming the catalog thickness is exact.

## 4.3 Build a small measurement record

A practical record looks like this:

| Feature | Measurement method | Readings | Chosen design value | Notes |
|---|---|---|---|---|
| Shaft | Calipers at 3 orientations | 5.98, 6.00, 6.01 mm | 6.00 mm nominal | Light burr removed |
| Panel | Calipers at 4 points | 2.92–3.02 mm | 2.97 mm observed average | Sheet stock, not truly 3.00 mm |
| Hole pattern | Center marks / calipers | 30.02 mm c-c | 30.0 mm target | Verify against the mating part |

Record enough digits to preserve what the tool actually resolves, but do not mistake display resolution for accuracy. If a caliper shows hundredths of a millimeter, that does not guarantee every measurement is accurate to 0.01 mm.

## 4.4 Establish a datum strategy

A **datum strategy** is the choice of surfaces or features used as references. On a simple bracket, the bottom face may be datum A, the rear face datum B, and the left edge datum C. Hole locations can then be dimensioned from those references.

In code, choose coordinate origins that make the part easy to reason about. For example:

- place the bottom of a printed part on `z = 0`;
- place a panel corner at `[0,0]` for a laser-cut sheet;
- place the shaft axis at `[0,0]` for a rotational part;
- use center-based geometry where symmetry is a dominant feature.

There is no universally correct origin. Choose one that reduces sign errors and makes important interfaces easy to parameterize.

---

## 4.5 Gauge numbers are labels, not reliable CAD dimensions

Fabrication catalogs often identify sheet metal, wire, and other stock by a **gauge** number. A gauge is a designation within a particular system; it is not a universal unit. The same number can refer to different physical sizes in different materials or gauge systems. For CAD, convert the designation to an explicit decimal thickness or diameter, then verify the actual stock.

### Sheet-metal gauge

The following are representative trade values for common sheet-gauge tables. They are useful for estimating a design, not a substitute for a supplier's drawing or measured stock. Values can differ with the gauge system, alloy, coating, specification, and supplier.

| Gauge | Standard steel / MSG (in) | Approx. mm | Stainless (in) | Approx. mm | Aluminum (in) | Approx. mm |
|---:|---:|---:|---:|---:|---:|---:|
| 16 | 0.0598 | 1.519 | 0.0625 | 1.588 | 0.0508 | 1.290 |
| 18 | 0.0478 | 1.214 | 0.0500 | 1.270 | 0.0403 | 1.024 |
| 20 | 0.0359 | 0.912 | 0.0375 | 0.953 | 0.0320 | 0.813 |
| 22 | 0.0299 | 0.759 | 0.0312 | 0.792 | 0.0253 | 0.643 |
| 24 | 0.0239 | 0.607 | 0.0250 | 0.635 | 0.0201 | 0.511 |
| 26 | 0.0179 | 0.455 | 0.0187 | 0.475 | 0.0159 | 0.404 |
| 28 | 0.0149 | 0.378 | 0.0156 | 0.396 | 0.0126 | 0.320 |
| 30 | 0.0126 | 0.320 | 0.0125 | 0.318 | 0.0100 | 0.254 |

**Important:** “16 gauge” alone is an incomplete stock specification. Prefer a callout such as `aluminum sheet, 1.29 mm nominal thickness, alloy/temper as specified` or `steel sheet, 1.52 mm nominal thickness`; use the supplier's exact material specification when strength, weldability, corrosion resistance, or interchangeability matters. A quoted thickness may be nominal, and coatings can affect measured thickness.

Gauge numbers usually run in the counterintuitive direction: a larger gauge number means thinner stock. Do not assume the difference between successive gauges is constant; the system is not a linear scale. The U.S. Code has a legal standard-gauge table for iron and steel, while industry charts may identify other systems such as Manufacturers' Standard Gauge (MSG). Make sure the chart matches the material and standard you intend to use.

### American Wire Gauge (AWG)

AWG is commonly used for electrical conductor sizes in North America. The table below gives approximate **bare round conductor diameter**, not the outside diameter of insulation, a jacket, or an entire cable.

| AWG | Bare conductor diameter (in) | Bare conductor diameter (mm) | Approx. area (mm²) |
|---:|---:|---:|---:|
| 10 | 0.1019 | 2.588 | 5.26 |
| 12 | 0.0808 | 2.053 | 3.31 |
| 14 | 0.0641 | 1.628 | 2.08 |
| 16 | 0.0508 | 1.291 | 1.31 |
| 18 | 0.0403 | 1.024 | 0.823 |
| 20 | 0.0320 | 0.812 | 0.518 |
| 22 | 0.0253 | 0.644 | 0.326 |
| 24 | 0.0201 | 0.511 | 0.205 |
| 26 | 0.0159 | 0.405 | 0.129 |
| 28 | 0.0126 | 0.321 | 0.0810 |
| 30 | 0.0100 | 0.255 | 0.0509 |

The AWG number describes nominal conductor size; stranded conductors can have a slightly different overall diameter from a solid conductor of equivalent copper area, and insulation can make the finished wire much larger. For a printed wire clip, grommet, strain relief, guide, or cable pass-through, measure the actual wire or cable that will go through it. If insulation must not be crushed, design around the insulated outside diameter and validate the clip force with a coupon.

AWG is not the same system as SWG (Standard Wire Gauge), steel wire gauge, sheet-metal gauge, or a drill-number chart. If a listing says only “gauge wire,” ask which standard it means and what the actual diameter is.

### How to use a gauge in a parametric model

Convert a stock label into an explicit dimensional parameter before calculating slots, bends, walls, or clearances. For example:

```scad
// Values measured or confirmed from the actual sheet stock.
stock_thickness = 1.52;       // mm; do not use "16" as if it were mm
slot_clearance  = 0.15;       // mm per side, example starting value only
slot_width      = stock_thickness + 2 * slot_clearance;

wire_bare_diameter = 1.02;    // mm, approximate example for 18 AWG bare conductor
wire_insulation_diameter = 2.05; // mm, example only: measure the real wire
wire_hole_diameter = wire_insulation_diameter + 0.25; // starting test value
```

The allowances above are examples, not universal manufacturing settings. For laser-cut joints, use a measured kerf and a sheet-thickness/slot coupon. For a printed cable clip, use a wire-fit coupon. In both cases, the intended behavior—sliding, snug location, press fit, or retention—determines the allowance.

### Stock-thickness checklist

1. Identify the material and applicable gauge system.
2. Find the supplier's stated thickness in inches or millimeters.
3. Measure several locations on the actual sheet or wire when practical.
4. Record coating, insulation, temper, batch, and any other property that affects the fit.
5. Use explicit units and named dimensions in OpenSCAD.
6. Test the critical slot, clip, bend, or joint with a coupon before making the full part.

# 5. OpenSCAD fundamentals

OpenSCAD is a script-based CAD system. You describe geometry in a `.scad` text file, then preview or render it. It is especially good for dimension-driven parts, repeated geometry, fixtures, adapters, enclosures, brackets, plates, and families of related components.

Official docs: [OpenSCAD documentation](https://openscad.org/documentation.html), [User Manual](https://files.openscad.org/documentation/manual/OpenSCAD_User_Manual.html), and [Language Reference](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/The_OpenSCAD_Language).

## 5.1 Start with a cube

```scad
// A simple 40 x 25 x 8 mm block.
length = 40;
width  = 25;
thick  = 8;

cube([length, width, thick]);
```

OpenSCAD does not enforce a universal unit system in the file. The practical convention for most mechanical models is **millimeters**. Treat all bare dimensions consistently as mm unless a workflow explicitly says otherwise. Document the units in file comments and project notes.

The default `cube()` placement begins at the origin and extends in the positive X, Y, and Z directions. `center=true` instead centers the cube about the origin:

```scad
cube([40, 25, 8], center=true);
```

Knowing where a primitive begins and ends is essential when positioning it relative to another feature.

## 5.2 The coordinate system

OpenSCAD uses a 3D Cartesian coordinate system:

- **X:** left/right in the model's coordinate frame;
- **Y:** front/back;
- **Z:** vertical in the common build orientation.

A model's view can be rotated, so screen direction is not a reliable substitute for the coordinate system. Know which direction a dimension belongs to and where zero lies.

A point is written `[x, y, z]`. A translation moves a shape by that vector:

```scad
translate([10, 5, 2])
    cube([20, 10, 4]);
```

## 5.3 Primitive geometry

```scad
cube([20, 30, 4]);

cylinder(h=10, d=8);

// Radius-defined cylinder:
cylinder(h=10, r=4);

sphere(d=12);

// A 2D disk:
circle(d=20);

// A 2D rectangular outline filled as an area:
square([30, 20]);

// Polygon vertices are 2D coordinates:
polygon(points=[[0,0], [30,0], [20,15], [0,20]]);
```

A **2D shape** lives in the XY plane and has no thickness. A **3D solid** occupies volume. `linear_extrude()` and `rotate_extrude()` turn suitable 2D profiles into 3D geometry.

## 5.4 Transformations

Transformations position, orient, or scale geometry. They are usually applied outside the object they affect.

```scad
translate([20, 0, 0]) cube([10, 10, 10]);

rotate([0, 0, 45]) square([20, 5]);

scale([2, 1, 1]) cube([10, 10, 10]);

mirror([1, 0, 0]) cube([10, 10, 10]);
```

Important operations:

- `translate([x,y,z])`: move geometry.
- `rotate([x,y,z])`: rotate around axes; angles are in degrees.
- `scale([x,y,z])`: scale geometry. Nonuniform scaling can turn circles into ellipses and can change designed proportions.
- `mirror([x,y,z])`: reflect geometry across a plane described by its normal vector.
- `resize([x,y,z])`: resize geometry to target dimensions; use carefully when dimensions need engineering meaning.
- `offset(r=...)`: adjust a 2D outline outward or inward; useful in some profile workflows, but inspect the resulting contours.
- `linear_extrude(height=...)`: extend a 2D shape into a prism.
- `rotate_extrude()`: revolve a 2D profile around the Z axis to make rotational geometry.

**Order matters.** In nested transformations, the outer transform affects the transformed child geometry. When a part appears in the wrong place, temporarily simplify the transform stack and inspect one operation at a time.

## 5.5 Boolean operations: union, difference, intersection

OpenSCAD uses **Constructive Solid Geometry (CSG)** to combine simpler shapes.

```scad
// Union: combine solids.
union() {
    cube([20, 20, 5]);
    translate([10, 10, 5]) cylinder(h=10, d=8);
}

// Difference: subtract every later child from the first child.
difference() {
    cube([30, 30, 8]);
    translate([15, 15, -1]) cylinder(h=10, d=6);
}

// Intersection: keep only the common volume.
intersection() {
    cube([20, 20, 20]);
    translate([10, 10, 10]) sphere(d=20);
}
```

For `difference()`, the first child is the material to retain; later children are cutters. This is the standard pattern for holes, slots, pockets, and cutouts.

When subtracting a through-hole, make the cutting tool slightly longer than the target wall so it clearly passes through:

```scad
difference() {
    cube([40, 30, 5]);
    translate([20, 15, -0.1])
        cylinder(h=5.2, d=6);
}
```

This small overrun avoids coplanar boundary ambiguity. Do not make the cutter so large that it accidentally removes neighboring geometry.

## 5.6 Loops and arrays

Parametric parts often contain repeated holes or slots. Use loops instead of copying the same geometry manually.

```scad
plate_x = 80;
plate_y = 40;
plate_t = 5;
hole_d = 4.5;
edge = 10;

hole_positions = [
    [edge, edge],
    [plate_x-edge, edge],
    [edge, plate_y-edge],
    [plate_x-edge, plate_y-edge]
];

difference() {
    cube([plate_x, plate_y, plate_t]);
    for (p = hole_positions)
        translate([p[0], p[1], -0.1])
            cylinder(h=plate_t+0.2, d=hole_d);
}
```

The loop makes a hole at every coordinate in the list. Because the hole locations are explicitly recorded, the pattern is easier to audit than four separately copied cylinders.

Numeric ranges can generate regular patterns:

```scad
for (x = [10 : 10 : 70]) {
    translate([x, 20, 0]) cylinder(h=5, d=4);
}
```

This creates positions from 10 through 70 in steps of 10. Check boundary values rather than assuming the list has the count you intended.

## 5.7 Parameters, functions, and modules

A **parameter** is a named value used to control a model. A **module** is a reusable geometry operation. A **function** computes a value, such as a derived dimension.

```scad
plate_length = 80;
plate_width  = 45;
plate_thick  = 4;
mount_d      = 5;
edge_offset  = 8;

function hole_x() = plate_length - 2*edge_offset;

module mounting_plate() {
    difference() {
        cube([plate_length, plate_width, plate_thick]);

        for (x = [edge_offset, plate_length-edge_offset])
        for (y = [edge_offset, plate_width-edge_offset])
            translate([x, y, -0.1])
                cylinder(h=plate_thick+0.2, d=mount_d);
    }
}

mounting_plate();
```

Use descriptive names and group dimensions near the top. Avoid unexplained literal numbers scattered through complex geometry. If a value controls a fit, call it something explicit such as `radial_clearance` or `slot_extra_width` rather than merely `c`.

### OpenSCAD's variable behavior

OpenSCAD is declarative and evaluates variables in a way that differs from a typical imperative language. It is safest to think of variables as scoped, overrideable design values rather than mutable storage that changes line by line. Reassignments within a scope do not behave like ordinary sequential assignment in languages such as Python or C. Read the official language reference when using complex scoping, functions, or customizer-driven configurations.

## 5.8 Resolution and faceting

A circle in a mesh is approximated by facets. These special variables control the approximation:

- `$fn`: fixed number of fragments around a circular feature;
- `$fa`: maximum fragment angle;
- `$fs`: maximum fragment size.

For example:

```scad
$fn = 64;
cylinder(h=10, d=20);
```

A high `$fn` produces a smoother curve but increases computation and mesh complexity. Low resolution may be adequate for a rough fit test, but it can make a circular mating feature visibly polygonal or affect its measured envelope. For many parts, setting `$fa` and `$fs` gives more adaptive control than using a single huge `$fn` everywhere.

Do not confuse facet resolution with dimensional tolerance. A finely faceted 10 mm cylinder can still be the wrong size or printed out of tolerance.

## 5.9 `hull()`, `minkowski()`, and advanced geometry

- `hull()` creates the convex hull around its child geometry. It is useful for smooth transitions, rounded-ended slots, and connecting forms, but it fills concave space because a convex hull is convex.
- `minkowski()` creates a Minkowski sum, often used to round shapes by combining an object with a small sphere or other tool shape. It can be computationally expensive and can enlarge geometry in ways that need careful dimensional accounting.
- `offset()` changes a 2D outline inward or outward. Negative offsets can remove narrow features or make disconnected profiles disappear.
- `linear_extrude()` gives thickness to a 2D profile.
- `rotate_extrude()` makes a body of revolution. The 2D profile needs to be positioned correctly relative to the axis of revolution.

Use these features only when their geometric effects are understood. Always render and inspect the result, and consider making a small coupon when a derived radius or offset controls a critical fit.

## 5.10 Preview, render, and debugging

OpenSCAD's fast preview is designed for interactive inspection. It can display artifacts that are not in the final solid. **Render** performs the more complete geometry calculation and is the step to use before exporting a production mesh or profile.

Useful habits:

- Preview often while developing.
- Render before releasing an export.
- Read the console and warnings, not just the viewport.
- Use `#` to highlight a shape during debugging, `%` to show a transparent background/reference object, and `!` to isolate geometry while debugging when appropriate.
- Reduce a failing model to the smallest example that reproduces the problem.
- Check that walls, cuts, and bodies actually connect where intended.
- Avoid relying on two faces that only touch at a mathematical plane or line; such zero-thickness connections can create non-manifold geometry.

## 5.11 Useful 2D tools

```scad
// A rectangular plate with rounded outside corners.
// offset(r=...) grows/shrinks the outline; subtract the growth
// from the original rectangle to establish a rounded outline.
module rounded_rect_2d(x, y, r) {
    offset(r=r) offset(delta=-r) square([x, y]);
}

// Turn a 2D outline into a 3D panel.
linear_extrude(height=3)
    rounded_rect_2d(60, 40, 3);
```

The nested offset method is a useful pattern but should be tested with the chosen OpenSCAD version and geometry, especially for very small radii or narrow dimensions. For manufacturing profiles, inspect the final 2D contour and verify every critical radius and overall size.

## 5.12 Text and labels

OpenSCAD has a `text()` primitive. It can be extruded for raised lettering or subtracted to engrave labels. Typeface availability and glyph rendering depend on the system and the selected font.

```scad
// Raised label on the top face of a block.
linear_extrude(height=0.6)
    text("REV A", size=5, halign="center", valign="center");
```

Small text may not fabricate well. For laser cutting, verify that the lettering is a suitable vector font or outline and that the machine software interprets it as intended. For engraved labels in a 3D print, use a font size and stroke width that suit the nozzle, layer height, and material.

---

# 6. Parametric design that survives change

A good parametric model is not just a shape with numbers at the top. It encodes relationships that remain correct when the part changes size.

## 6.1 Identify primary and derived parameters

**Primary parameters** are chosen directly, such as:

- overall length, width, and thickness;
- shaft diameter;
- fastener size;
- stock thickness;
- edge distance;
- desired clearance;
- number and spacing of mounting holes.

**Derived parameters** are calculated from those values, such as:

- hole diameter = shaft diameter + clearance;
- inner panel size = outer size minus twice the wall thickness;
- overall hole-pattern span = (number of intervals) × pitch;
- slot width = measured material thickness + fit allowance;
- counterbore diameter based on a chosen fastener head.

Encode the relationship once. Do not manually update every dependent dimension each time a key parameter changes.

Example:

```scad
shaft_d = 6.0;
radial_clearance = 0.20;  // 0.20 mm per side, as an example only
hole_d = shaft_d + 2*radial_clearance;
```

The hole is 6.40 mm. The diametral difference is 0.40 mm. Always name the type of clearance so nobody interprets a per-side value as a total diameter difference.

## 6.2 Keep a clear parameter section

```scad
// ---------- Primary dimensions (mm) ----------
body_length = 80;
body_width  = 50;
body_height = 20;
wall        = 2.4;

// ---------- Interfaces ----------
shaft_d = 8;
fit_clearance_per_side = 0.20; // starting test value, not a guarantee
shaft_hole_d = shaft_d + 2*fit_clearance_per_side;

// ---------- Fabrication ----------
edge_break = 0.5;
$fn = 64;
```

Use comments for units, conventions, and assumptions. Avoid naming two variables `clearance` if one means total diametral clearance and the other means per-side clearance.

## 6.3 Avoid fragile hard-coded relationships

Fragile version:

```scad
cube([80, 50, 3]);
translate([10, 10, -1]) cylinder(h=5, d=5);
translate([70, 10, -1]) cylinder(h=5, d=5);
translate([10, 40, -1]) cylinder(h=5, d=5);
translate([70, 40, -1]) cylinder(h=5, d=5);
```

Better version:

```scad
L = 80;
W = 50;
T = 3;
edge = 10;
hole_d = 5;

hole_xs = [edge, L-edge];
hole_ys = [edge, W-edge];

difference() {
    cube([L, W, T]);
    for (x = hole_xs)
    for (y = hole_ys)
        translate([x, y, -0.1])
            cylinder(h=T+0.2, d=hole_d);
}
```

When the plate width changes, the far holes remain the chosen edge distance from the edges. The design intent is explicit.

## 6.4 Use modules as manufacturing subassemblies

A module might represent:

- a standard screw clearance hole;
- a repeated mounting slot;
- a bearing seat;
- a panel with a given wall thickness;
- a rib or gusset;
- a connector pattern;
- a family of parts that share an interface.

For example:

```scad
module through_hole(d, part_t, overshoot=0.2) {
    translate([0, 0, -overshoot/2])
        cylinder(h=part_t+overshoot, d=d);
}
```

This module assumes the feature is centered at the current XY coordinate and cuts parallel to Z. State these assumptions in its comment. A reusable module is useful only if its coordinate convention and inputs are understandable.

## 6.5 Symmetry and mirror design

If two parts are mirrored versions of one another, use `mirror()` or a parameterized left/right option rather than maintaining two unrelated files. But verify that mirrored parts still have the correct screw-head orientation, countersinks, cable exits, text, and any asymmetric interfaces.

## 6.6 Parameter validation

A parameter combination can produce impossible or nonsensical geometry. For instance, a wall can become thicker than the entire enclosure, or two holes can overlap after changing the pitch.

Use visual inspection and, where appropriate, `assert()` checks to reject invalid settings. Syntax and behavior can vary with the installed OpenSCAD version, so confirm against the version's language reference before depending on a validation expression.

Useful checks include:

- overall length, width, and thickness are positive;
- internal dimensions remain positive;
- hole centers stay within the part boundaries;
- minimum wall thickness is maintained;
- slot widths remain compatible with the stock and tool;
- a requested number of repeated features is a valid positive integer.

Do not overengineer a tiny one-off script, but do add checks when the model is intended for repeated use or other people will change its parameters.

---

# 7. Boolean geometry and reusable design patterns

## 7.1 Through-hole pattern

```scad
L = 100;
W = 60;
T = 5;
margin_x = 12;
margin_y = 12;
cols = 4;
rows = 2;
pitch_x = (L - 2*margin_x)/(cols-1);
pitch_y = (W - 2*margin_y)/(rows-1);
hole_d = 5.2;

difference() {
    cube([L, W, T]);
    for (i = [0 : cols-1])
    for (j = [0 : rows-1])
        translate([margin_x+i*pitch_x,
                   margin_y+j*pitch_y,
                   -0.1])
            cylinder(h=T+0.2, d=hole_d);
}
```

This is useful for mounting plates and fixtures. For precision drawings, decide whether edge offsets, pitches, and the resulting last-hole position are the controlling dimensions. Do not inadvertently overconstrain the pattern with inconsistent dimensions.

## 7.2 Slot with rounded ends

One method is to hull two circles. This creates a capsule-shaped 2D slot:

```scad
module slot_2d(length, width) {
    assert(length >= width, "Slot length must be at least its width");
    hull() {
        translate([-(length-width)/2, 0]) circle(d=width);
        translate([ +(length-width)/2, 0]) circle(d=width);
    }
}

linear_extrude(height=4)
    slot_2d(30, 6);
```

Be precise about what `length` means. In this example, it is the full end-to-end length, and `width` is the diameter of the rounded ends.

## 7.3 Rotational body

OpenSCAD can generate knobs, bushings, rollers, and simple turned forms by revolving a 2D profile:

```scad
// A simple stepped bushing profile, drawn in radius-versus-height space.
profile = [
    [4, 0],
    [8, 0],
    [8, 6],
    [6, 6],
    [6, 12],
    [4, 12]
];

rotate_extrude($fn=96)
    polygon(points=profile);
```

In this pattern, the first coordinate is radius from the Z axis and the second is height in the profile plane. The shape revolves around Z. For a functional bushing, include the actual bore and confirm its dimensions after export and fabrication.

## 7.4 Enclosure wall pattern

```scad
outer_x = 80;
outer_y = 60;
outer_z = 25;
wall = 2.4;
floor_t = 3;

assert(outer_x > 2*wall && outer_y > 2*wall && outer_z > floor_t,
       "Enclosure dimensions are too small for these walls");

difference() {
    cube([outer_x, outer_y, outer_z]);
    translate([wall, wall, floor_t])
        cube([outer_x-2*wall,
              outer_y-2*wall,
              outer_z-floor_t+0.1]);
}
```

This creates an open-top rectangular shell. It does not automatically include a lid, screw bosses, cable relief, gasket groove, internal ribs, or manufacturing fillets. Add those features deliberately. For 3D printing, check the slicer's wall generation and choose wall dimensions that play well with extrusion width. For CNC, the pocket depth and corner radii must match the tools available.

## 7.5 Do not assume a visual union is a valid solid

Two solids may appear connected but only touch at one point, edge, or face. Such geometry can create ambiguous or non-manifold meshes. Make intentional overlap where parts are meant to merge; avoid zero-thickness walls; render the model; and run an independent mesh check when the part is important.

---

# 8. Physical test coupons: test the fit before committing

A **test coupon** is a small, intentionally designed sample used to evaluate a material, process, dimension, or interface before fabricating the whole part. Coupons are among the most effective ways to turn a guess about fit into measured evidence.

A coupon should reproduce the specific feature that matters. A generic calibration cube is useful for some machine checks, but it does not automatically tell you how a particular hole, snap, dovetail, sheet slot, bearing seat, or fastener boss will behave.

## 8.1 Coupon design rules

1. **Test the most expensive uncertainty first.** If the main risk is whether a 6 mm shaft fits a printed bore, test that interface before printing a large housing.
2. **Change one main variable at a time** when trying to identify a cause. If you change material, orientation, slicer compensation, and CAD clearance simultaneously, the result is hard to interpret.
3. **Use the actual process.** Use the same printer, nozzle, material, layer height, orientation, laser, lens/focus method, sheet material, tool, and finishing steps as the final part whenever practical.
4. **Label each variation.** Numbers engraved or printed on the coupon prevent confusion after the pieces are removed from the build plate or laser bed.
5. **Include a reference dimension.** A known 20 mm or 50 mm span can help detect scale errors, though it does not calibrate all directions or feature types.
6. **Reproduce the real interface.** A horizontal hole, vertical hole, snap beam, or sheet joint can behave differently depending on orientation and geometry. Test the orientation that matters.
7. **Record the setup and outcome.** The coupon is only valuable if the result can be applied to later parts.
8. **Do not jump from a single coupon to universal rules.** A result belongs to a specific process/material/setup range until verified more broadly.

## 8.2 FDM fit coupon: holes for a pin or shaft

Suppose a nominal 6.00 mm shaft must fit into a printed hole. You want to determine a useful per-side clearance for your printer and material. The following OpenSCAD script makes a small plate with six holes, each with a different radial clearance. The values are deliberately a test range, not a guaranteed design recipe.

```scad
// Fit coupon for a nominal 6 mm pin.
// Units: mm. Positive clearance enlarges the hole.
// NOTE: clearance is RADIAL / PER SIDE, not diametral.

pin_d = 6.0;
clearances = [-0.2, -0.1, 0.0, 0.1, 0.2, 0.3];

coupon_w = 120;
coupon_h = 24;
plate_t = 4;
margin = 12;
pitch = 19;
hole_y = 15;
label_y = 4;
engrave_depth = 0.6;

$fn = 64;

difference() {
    cube([coupon_w, coupon_h, plate_t]);

    for (i = [0 : len(clearances)-1]) {
        xpos = margin + i*pitch;
        hole_d = pin_d + 2*clearances[i];

        translate([xpos, hole_y, -0.1])
            cylinder(h=plate_t+0.2, d=hole_d);

        translate([xpos, label_y, plate_t-engrave_depth])
            linear_extrude(height=engrave_depth+0.1)
                text(str(clearances[i]),
                     size=3,
                     halign="center",
                     valign="center");
    }
}
```

### How to use this coupon

1. Render the file and inspect it.
2. Export an STL and print it using the final part's material, nozzle, layer height, orientation, and relevant slicer settings.
3. Let the part cool and remove brims or elephant-foot artifacts only if the final design will receive the same treatment.
4. Test the actual shaft or a properly measured reference pin in each hole. Do not force a press fit that may split the coupon.
5. Record which hole gives a slip fit, sliding fit, snug locating fit, or intended interference.
6. If the final part's hole will be oriented differently, print a second coupon with that orientation.

The hole diameters in this example are `pin_d + 2 × clearance`. A clearance entry of `0.20` means a hole 0.40 mm larger than the nominal pin—0.20 mm per side when centered. A negative entry explores an interference condition. Negative-clearance values are only exploratory: real press fits depend on material elasticity, wall thickness, insertion force, grain/layer direction, and the risk of splitting the part.

**Key limitation:** if the pin itself will also be 3D-printed, its actual printed diameter may differ from nominal. Test the pair that will actually be assembled, or characterize both the pin and hole process separately.

## 8.3 Male/female interface coupon

For a snap, dovetail, keyed shaft, rail, slide, or enclosure lid, make a coupon containing a short segment of the actual interface. It should reproduce:

- mating shape and engagement depth;
- wall thickness near the fit;
- orientation relative to the build plate;
- any chamfer, lead-in, fillet, or flexure;
- the surface treatment or post-processing planned for the final piece.

A tiny straight slot may show the clearance but fail to reveal whether a long lid bows, whether a snap arm can flex enough, or whether friction increases over a long contact area. Coupons must represent the physics of the real interface, not merely its nominal width.

## 8.4 Fastener and boss coupons

Create a plate with several candidate hole diameters and boss wall thicknesses for the actual screw or insert system. Check:

- screw clearance versus a pilot hole;
- self-tapping screw behavior in the chosen polymer;
- heat-set insert dimensions and installation process;
- countersink or counterbore seating;
- cracking around the boss;
- access for the screwdriver or driver bit.

Do not infer screw strength just from whether the screw fits. Load-bearing fastener design also depends on engagement length, material, orientation, preload, temperature, and fatigue.

## 8.5 Snap-fit coupons

Snap fits are highly sensitive to beam length, thickness, deflection, material, print orientation, and fatigue. Build a coupon set with one variable changed at a time—for example, three beam lengths or three beam thicknesses. Measure assembly force and inspect for whitening, cracking, permanent set, and loss of retention after repeated cycles.

Printed polymer is anisotropic: layer adhesion can be weaker than material within a layer. Avoid assuming a snap arm is equally strong in every orientation. A coupon can test a specific design, but it does not replace safety factors or a load analysis for a critical latch.

## 8.6 Laser kerf coupon

A laser's **kerf** depends on the laser, focus, power/speed settings, material, thickness, grain or flute direction, and maintenance condition. It may also vary with cut direction. A useful calibration coupon contains:

- a known-size outer square or rectangle;
- an interior cutout of a known size;
- a series of slot widths around the expected sheet thickness;
- a small series of tab/slot pairs;
- optional horizontal and vertical test cuts if the machine/material combination may behave differently by direction.

Measure the retained piece and the cutout, then compare against the nominal geometry. Many laser workflows automatically apply an inside/outside path offset. If yours does, do not also bake the same compensation into CAD unless the workflow specifically calls for it. **Double compensation is a common source of incorrect parts.**

Label the coupon with machine, lens or focus setup when relevant, material type and thickness, material batch, settings profile, date, and CAD revision. Re-run it when the material changes, the machine's optical setup changes, or the fit matters enough to justify a fresh check.

## 8.7 Sheet-thickness and tab/slot coupon

For interlocking laser-cut or CNC-cut panels, use measured stock thickness rather than trusting the nominal label. Make a set of slots that vary by small increments around the measured thickness, then fit tabs made from the same stock/process.

Test the intended joint:

- **slip fit:** assembles and disassembles easily;
- **snug locating fit:** holds position with little play;
- **press fit:** requires controlled force and may damage brittle material if too tight;
- **glue fit:** leaves enough room for the chosen adhesive and assembly method.

A finger joint, tab-and-slot, or living hinge can behave differently in plywood, acrylic, cardboard, and composite sheet, even at nominally equal thickness. Record actual stock thickness, not just the material category.

## 8.8 CNC tool-radius and pocket coupon

A CNC end mill cannot make a mathematically sharp internal corner: the corner radius is at least the radius of the cutter, subject to the actual toolpath and machine conditions. A coupon can test:

- internal pocket corners at several cutter radii;
- hole diameters using available end mills or drilling tools;
- slot widths with the intended tool;
- pocket depth and floor finish;
- dogbone or T-bone corner reliefs for square mating parts;
- minimum wall thickness left between pockets.

A feature that fits the 2D drawing may not fit the tool. Confirm the cutter diameter and the actual CAM strategy before making the final part.

## 8.9 A coupon log template

Copy this table into the project record for each test round.

| Field | Record |
|---|---|
| Project / part | |
| Coupon ID and CAD revision | |
| Date and operator | |
| Machine and firmware/software version if relevant | |
| Process (FDM, resin, laser, CNC, etc.) | |
| Material / supplier / batch | |
| Stock thickness or filament/resin | |
| Nozzle/tool/lens and key settings | |
| Orientation, support, focus, toolpath, or finishing | |
| Nominal test values | |
| Measured values | |
| Observed fit / force / finish | |
| Selected value and reason | |
| Remaining uncertainties | |

## 8.10 When to test more than one variable

Once the basic process is characterized, a small planned experiment can be more efficient than random trial and error. For example, compare two materials across three clearances, keeping printer, orientation, and slicer settings fixed. If both material and clearance change simultaneously without a planned matrix, it becomes hard to tell which caused the improvement.

For critical parts, test more than one sample. One good coupon does not demonstrate repeatability. For high-consequence applications, define a formal inspection plan and use a qualified engineering/manufacturing process.

---

# 9. Designing for FDM and resin 3D printing

3D printing creates a solid by building layers or curing material according to a process. The geometry must be designed for the specific process; FDM/FFF, SLA/MSLA, SLS, and other technologies have different constraints.

## 9.1 Understand the slicer's role

OpenSCAD defines geometry. The **slicer** converts a 3D model into layer-by-layer toolpaths, support structures, and machine instructions. The slicer decides or controls perimeters, infill, support, orientation, layer height, extrusion width, speeds, and many other production settings.

OpenSCAD's model must not rely on a visual illusion such as two bodies touching only at a point. The slicer needs a valid, intended solid. Inspect the model in the slicer as well as in OpenSCAD.

## 9.2 FDM walls and feature sizes

FDM parts are laid down in extruded roads. Wall thickness should be considered in relation to nozzle diameter and configured line width. For example, a 0.4 mm nozzle often uses an extrusion width around that scale or somewhat larger; the exact value is slicer- and profile-dependent. A wall designed as an arbitrary 0.7 mm may be represented by one perimeter, two perimeters, a gap-fill strategy, or a different result depending on settings.

For functional walls:

- choose a thickness that maps sensibly to the intended perimeter count;
- use ribs, flanges, and box sections where they add stiffness efficiently;
- avoid very thin standing features unless they are intentional and tested;
- inspect how the slicer represents narrow gaps and small bosses;
- avoid making a hole so close to an edge that the wall becomes fragile.

There is no universal minimum wall thickness. Process, material, nozzle, layer height, orientation, and load determine what is appropriate.

## 9.3 Orientation and anisotropy

FDM strength is direction-dependent. Layers are fused to one another, but the interface between layers may be weaker than material within a layer. Think about the direction of the load relative to the layers:

- a bracket may split along layer lines if the load pries layers apart;
- a pin may bend differently depending on whether it is printed upright or on its side;
- a snap arm may fail if its flexure repeatedly pulls across layer interfaces;
- a threaded feature may work in one orientation and fail in another.

Rotate the part with function and load in mind, not solely to make the top face attractive. Support requirements, surface finish, accuracy, and print time also matter. For heavily loaded parts, test representative samples in the final orientation.

## 9.4 Overhangs, bridges, and supports

An **overhang** extends outward without enough support from the layer below. A **bridge** spans between supported regions. FDM's often-used “45-degree rule” is a starting guideline, not a physical law: the result depends on printer cooling, material, layer height, geometry, and settings.

To reduce support and improve quality:

- chamfer or slope roofs instead of using a flat unsupported ceiling;
- orient holes and slots so their ceilings are self-supporting when possible;
- use teardrop-shaped horizontal holes when that fits the function;
- split an assembly into parts if that produces better surfaces or stronger load paths;
- add support only where necessary and account for the damage or roughness after removal.

For resin printers, the limiting factors differ: peel forces, resin behavior, support contact, drainage, and post-curing can dominate. Use the specific printer/resin design guide rather than applying FDM rules.

## 9.5 Holes are often not the size you modeled

Printed holes can come out undersize or distorted because of extrusion width, cooling, layer stair-stepping, orientation, shrinkage, and first-layer effects. Do not assume a modeled 6.00 mm hole will accept a 6.00 mm shaft.

For a critical hole:

1. define the desired mating fit;
2. print a fit coupon;
3. measure the actual hole and test the mating feature;
4. adjust the model or use a post-process such as drilling/reaming when the material and application permit;
5. repeat in the same orientation and material as the final part.

Be explicit about **per-side clearance** versus **diametral clearance**. For a shaft diameter `D` and radial clearance `c`, the corresponding nominal hole diameter is `D + 2c`.

## 9.6 Elephant foot and first-layer effects

The first layers can spread outward, creating a wider base known as **elephant foot**. This can interfere with mating faces, slots, and parts intended to sit flat. Possible mitigations include slicer elephant-foot compensation, a slight chamfer at the base, adjusting first-layer setup, or designing the critical interface above the first-layer region. Verify that the solution suits the final part rather than adding random offsets.

## 9.7 Strength and stiffness

A part's strength is not determined by infill percentage alone. Important factors include:

- geometry and section depth;
- wall/perimeter count;
- infill type and percentage;
- layer adhesion and orientation;
- material grade and moisture condition;
- temperature and environmental exposure;
- stress concentration at sharp corners and abrupt thickness transitions;
- fastener preload, creep, fatigue, and repeated impacts.

Use ribs, gussets, generous transitions, and closed sections when appropriate. Avoid abrupt thickness changes where they cause stress concentration or warping. A higher infill setting cannot reliably fix a badly designed load path.

## 9.8 Material selection

Common hobby materials include PLA, PETG, ABS/ASA, nylon/PA, TPU, and various filled composites. They differ in stiffness, toughness, heat resistance, chemical resistance, moisture behavior, UV durability, print difficulty, and interlayer behavior.

- **PLA:** easy to print and often stiff, but can soften in heat and may be brittle under some loads.
- **PETG:** often more ductile and impact-tolerant than PLA, but can string and has different stiffness and creep characteristics.
- **ABS/ASA:** higher-temperature capability than basic PLA in many applications; requires attention to warping, ventilation, and the specific printer setup. ASA is often selected for UV/weather exposure, but confirm the grade's data.
- **Nylon/PA:** useful toughness and wear behavior in suitable grades, but moisture conditioning and print control matter.
- **TPU:** flexible; design dimensions and wall thickness must account for deformation.
- **Filled filament:** fiber or particulate loading can change stiffness, wear, nozzle requirements, anisotropy, and surface behavior; it is not automatically stronger in every direction.

Check the manufacturer's data sheet and validate with coupons if the part operates near a material limit. Never assume a material's advertised tensile strength applies unchanged to a printed part in every orientation.

## 9.9 Threads and fasteners

A thread is a helical ridge (external thread) or groove (internal thread) that converts rotation into axial movement and/or creates a fastening interface. Threads look superficially similar, but a shape that screws on for half a turn is not necessarily a standard, interchangeable thread. Matching requires the correct thread family, nominal size, pitch or TPI, profile, diameter system, hand, start count, tolerance/clearance, engagement length, and—on many closures—the surrounding sealing geometry.

### 9.9.1 How to read a thread callout

| Term | Meaning | Why it matters to the model |
|---|---|---|
| **Nominal diameter / major diameter** | The size associated with the thread's outside envelope; the exact meaning of a nominal designation depends on the standard | Sets the broad size family, but does not define the entire thread form |
| **Minor diameter / root diameter** | The smallest diameter of the thread form | Controls the core of an external thread and the open diameter at the roots of an internal thread |
| **Pitch diameter** | The theoretical diameter where thread ridge and groove widths are equal | A key functional dimension for thread fit; an outside-diameter measurement alone cannot establish fit |
| **Pitch** | Axial distance from one thread crest to the next corresponding crest | In metric notation, usually given in millimeters |
| **Threads per inch (TPI)** | Number of thread pitches in one inch, used in Unified and many inch-series thread systems | For ordinary single-start inch threads, pitch in inches is `1 / TPI`; multi-start threads require pitch and lead to be distinguished |
| **Lead** | Axial travel in one full revolution | For a single-start thread, lead equals pitch; for a multi-start thread, lead equals pitch × number of starts |
| **Thread angle** | Included angle between the flanks in an axial cross-section | Different families have different angles or non-symmetric profiles |
| **Crest and root** | The top and bottom of the profile | Standards truncate, flatten, or round them; do not always use a mathematically sharp V |
| **External / internal** | Thread on the outside of a shaft/neck versus inside a nut/hole/cap | Mating geometry is not a simple duplicate; the clearances are different |
| **Right-hand / left-hand** | Direction of tightening when viewed from the relevant end | Right-hand is common; left-hand must be called out when used |
| **Single-start / multi-start** | One helix versus multiple helices arranged around the same axis | A multi-start thread advances farther per turn and needs the correct lead and start geometry |
| **Thread class / tolerance class** | Standardized allowance/tolerance for the mating pair | Important in machined metal threads; printed threads often need process-specific clearance beyond nominal geometry |
| **Engagement length** | Axial length over which internal and external threads engage | Controls how many turns share load and how likely the joint is to strip or wobble |

### 9.9.2 Common thread families and their profile shapes

Choose a family before you write code or search for a library. The table is a selection aid; the controlling standard and manufacturer's drawing take precedence.

| Family / example designation | Typical profile | Typical use | Modeling cautions |
|---|---|---|---|
| **ISO metric screw thread** — e.g. `M6 × 1` | Symmetric 60° V form with standardized crest/root truncation | Metric machine screws, bolts, nuts, tapped holes | `M6` alone may not identify pitch; `M6 × 1` states 6 mm nominal diameter and 1 mm pitch. Fine pitches differ. Thread tolerance class still matters. |
| **Unified inch thread** — e.g. `1/4-20 UNC` or `1/4-28 UNF` | Symmetric 60° V form | Inch-series machine screws and fasteners | `1/4` is nominal diameter in inches; `20` or `28` is TPI; UNC is coarse and UNF is fine for that size family. Include class/designator when the fit is critical. |
| **NPT pipe thread** | Tapered pipe thread with a 60° form | North American tapered pipe joints | Nominal pipe size is not the measured outside diameter. Taper and sealing method matter; it is not interchangeable with BSP merely because diameters seem close. |
| **BSPP / BSPT pipe threads** | Whitworth-family 55° form; BSPP is parallel, BSPT is tapered | Pipe and fluid connections in systems using British Standard Pipe threads | Identify parallel `G` and tapered `R`/related designations correctly. Verify the required sealing method; don't substitute NPT. |
| **ACME** | Trapezoidal form, commonly 29° included angle in the inch ACME system | Lead screws, vises, jacks, motion mechanisms | Use an ACME-aware generator or the exact drawing; ordinary V-thread modules aren't a match. |
| **ISO metric trapezoidal** — often designated `Tr` | Trapezoidal form, 30° included angle | Metric lead screws and power transmission | Match diameter, pitch, profile, and tolerance system. Do not confuse this with inch ACME. |
| **Square thread** | Nearly square flanks | Certain power screws and mechanisms favoring efficiency | Specialized geometry; often requires a dedicated generator and clearance design. |
| **Buttress thread** | Asymmetric profile: one load flank is steep and the other is sloped | Loads acting predominantly in one axial direction; some closures | The load direction and the exact profile matter. A general-purpose symmetric V thread is not equivalent. |
| **Round / knuckle thread** | Rounded crests and roots | Dirty, rough-service, or specially specified connections | Profile dimensions are family-specific; use a dedicated standard/library where available. |
| **Garden-hose thread (GHT / NH)** — commonly `3/4-11.5 NH` in North America | Dedicated hose-coupler profile; typically straight, with a gasket/washer providing the seal | Garden hose connectors | Do not model as BSP or NPT. Thread engagement and gasket seat must both match. |
| **Bottle, jar, and closure thread** — e.g. `89/400` | Packaging-finish-specific continuous thread or other closure profile | Caps, jars, bottles, adapters, dosing/dispensing closures | The finish designation identifies a packaging interface family, not a normal machine-screw callout. Neck bead, thread run, skirt, top land, liner/gasket and closure geometry may be just as important as the helix. |
| **Self-tapping / wood screw** | Often a sharp, coarse, specialized thread with a screw-specific core and tip | Fastening into plastic, wood, or sheet metal | A standard machine-thread hole is not automatically appropriate. Often use a pilot-hole coupon or a specified insert/fastener maker's data. |

**Do not infer thread compatibility from the number of visible ridges alone.** Check the thread profile and its mating standard. A 60° machine screw, a 55° pipe thread, a trapezoidal lead screw, and a jar finish can all look helical but are not interchangeable.

### 9.9.3 Understanding `89/400` on a jar

A marking such as **`89/400`** (also written `89-400`) is normally a **packaging neck-finish designation**. The `89` identifies a nominal finish diameter of about **89 mm**; the `400` identifies the 400-series continuous-thread finish style/family. It is **not** a machine-screw designation such as `M89 × pitch`, and `400` is not the number of threads per inch. The suffix identifies a family of closure geometry, not a standalone pitch value that you can plug into a generic screw generator.

This distinction matters because a jar interface can include more than the helical ridge: its thread profile, thread run and height, neck land, bead, cap skirt, and liner/sealing surface may all affect the final fit. The package finish is a mating system. If the target is a real quart jar, do not assume that the container's capacity alone uniquely determines its finish. Identify the exact finish marking or measure the actual neck and closure.

For an `89/400` finish, a useful starting point is the **BOSL2** OpenSCAD library's `bottlecaps.scad`, which includes a `mason_neck()` module supporting `89, 400` as an example. The library documentation notes that some closure geometries—including 89-400 used by some suppliers—are based on available secondary sources and physical measurements rather than universally accessible official finish drawings. Treat the library model as a starting hypothesis, not a guaranteed fit for every jar.

Example from the BOSL2 `bottlecaps.scad` documentation:

```scad
include <BOSL2/std.scad>
include <BOSL2/bottlecaps.scad>

// Example neck geometry; verify against your actual jar.
neck_diameter = 89;  // nominal finish size, mm
neck_wall = 2;       // example wall thickness, mm
finish_type = 400;

mason_neck(neck_diameter, finish_type, neck_wall,
           style="M", bead=true);
```

For a corresponding cap, BOSL2 documents `mason_cap(diam, type, wall, ...)`. A separate, standalone cap example is:

```scad
include <BOSL2/std.scad>
include <BOSL2/bottlecaps.scad>

// Example cap geometry; test it against the real jar and liner.
cap_diameter = 89; // nominal finish size, mm
cap_wall = 2.0;    // example wall thickness, mm
finish_type = 400;

mason_cap(cap_diameter, finish_type, cap_wall,
          style="M", texture="ribbed");
```

Use the library's current documentation for the installed version, especially options affecting style, liner/seal space, top/bottom adjustment, texture, and clearance. A cap and a neck can use different thread styles in that library, but a mismatch-free preview does not prove a real closure will seal. The cap example is intended to be rendered separately from the neck unless you deliberately position the two parts apart for an assembly preview.

**Practical workflow for a jar:**

1. Record the printed or supplier finish designation (`89/400`), brand/product, and any lid identifier.
2. Measure the neck at several angular positions and heights: widest thread diameter, neck opening, thread-bearing height, shoulder/bead, and sealing surface. Do not force calipers across fragile glass edges.
3. Find the manufacturer's finish drawing, if available. Prefer a documented standard drawing over a model inferred from measurements.
4. Generate only the critical neck/cap geometry with the selected library.
5. Print a short thread/neck coupon or one inexpensive cap. Avoid printing a full container as the first fit test.
6. Test the actual closure, liner, and seal; check starting engagement, number of turns, rocking, binding, and whether it bottoms out before the seal compresses.
7. Change one parameter at a time, record measurements and revision, and test again.

### 9.9.4 Standard thread drawings versus modeled helices

In mechanical drawings, threads are often represented **conventionally**: standard line conventions and a thread callout communicate the thread standard, size, pitch/TPI, class, and depth without showing every helical surface. This is efficient for drawings, but it does not create physical thread geometry.

In 3D CAD, distinguish three cases:

- **Cosmetic or symbolic thread:** the model/drawing indicates a thread, but the underlying solid may be a plain cylinder or hole. Good for lightweight assemblies and drawings; not sufficient for printing or exporting a functional threaded part.
- **Modeled helical thread:** the real crest, root, flanks, lead, and helix are present in the solid. Needed when the exported mesh must actually include threads, such as a printable cap or bolt.
- **Simplified thread representation:** an approximation that is suitable for visual scale models but is not dimensionally standard or functional. Label it as visual-only so it is not mistaken for manufacturing geometry.

Use a recognized thread library when matching an existing standard. A hand-built helix can be educational or useful for a custom screw, but it is easy to get crest truncation, root shape, taper, lead-in, multi-start behavior, and mating clearance wrong.

### 9.9.5 OpenSCAD libraries and how to find the right code

OpenSCAD's core language provides geometry and Boolean operations, but a standard thread generally requires a library or custom geometry. Before copying code from a forum or model repository, check the library's documentation and license, thread-family support, parameter names, unit assumptions, clearance strategy, and current maintenance status.

**BOSL2** is a useful OpenSCAD library for general-purpose geometric modeling and thread generation. Its `threading.scad` documentation covers standard triangular ISO/Unified threads, trapezoidal/ACME threads, pipe threads, garden-hose connectors, buttress threads, square threads, and ball-screw-related geometries. Its `bottlecaps.scad` documentation covers several bottle and jar closure families, including Mason-jar-style necks and caps.

Typical BOSL2 includes:

```scad
include <BOSL2/std.scad>
include <BOSL2/threading.scad>
```

For a generic triangular thread, its documented module family includes `threaded_rod()` and `threaded_nut()`. For ACME/trapezoidal forms, it provides separate modules. For bottle and jar closure geometry, include `bottlecaps.scad` instead. Read the actual module documentation for required arguments—different families do not all share the same parameter conventions.

A sensible discovery workflow:

1. Search by the **standard name and designation**, e.g. `ISO metric M6x1 OpenSCAD BOSL2`, `1/4-20 UNC OpenSCAD thread library`, `NPT OpenSCAD thread`, `ACME lead screw OpenSCAD`, or `89-400 bottle thread OpenSCAD`.
2. Prefer the standard or vendor's engineering drawing to a random mesh.
3. Find a library module explicitly intended for the thread family, rather than adapting a V-thread generator to everything.
4. Open the library source and documentation; confirm units, parameters, license, current revision, and whether internal/external geometry is supported.
5. Export a short test segment, inspect it, and print/test the mating coupon before integrating it into the whole part.
6. If no trustworthy implementation exists, measure the real interface and construct a parametric approximation, but label it as measured/inferred rather than certified to a standard.

### 9.9.6 Thread fit for 3D printing

Nominal dimensions are not enough for a printed internal/external pair. The outcome depends on machine, layer height, nozzle or pixel size, orientation, material, shrinkage, first-layer effects, support strategy, and thread geometry. A printed thread may fit but still be too weak, wear quickly, leak, or strip.

- For a functional fastener, use a standard screw and a modeled clearance hole when feasible.
- For repeated assembly, consider a heat-set insert, captured nut, or metal insert designed for a specified installation method.
- If printing both sides, use a dedicated **thread-fit coupon** that varies one clearance parameter across several samples. Print the coupon with the same orientation, material, layer settings, and slicer as the final part.
- Include a lead-in chamfer or rounded entry where appropriate; avoid starting a thread at a fragile, sharp edge.
- Ensure the internal thread has enough wall thickness and that the external thread's root does not leave a dangerously thin core.
- Check that the cap or nut does not bottom on a shoulder before the intended sealing or clamping surface engages.
- Do not use a printed plastic thread as the only safety-critical retention or pressure boundary without suitable engineering validation.

### 9.9.7 Thread-fit test coupon and record

For a screw-and-nut pair, make a short coupon with several candidate clearances or hole sizes. For a package closure, test the entire neck/cap interface over the relevant height, including the sealing land or gasket. The coupon should be small, but it must preserve the features that determine function.

Record at least:

| Item | Record |
|---|---|
| Thread family / finish designation | e.g. `M6 × 1 - 6H`, `1/4-20 UNC-2B`, or `89/400` jar finish |
| Source of geometry | Standard drawing, manufacturer CAD, library name/revision, or measured approximation |
| Nominal sizes | Diameter, pitch/TPI, lead, thread type, and class where applicable |
| Critical mating measurements | Major/minor diameters as practical, thread-bearing height, sealing land, shoulder/bead, and liner thickness if relevant |
| Model parameters | Clearance/slop, wall thickness, lead-in, thread style, and other nonstandard adjustments |
| Fabrication conditions | Printer/material/orientation/layer settings, or CNC material/tool, or relevant process conditions |
| Result | Starts cleanly? Binds? Wobbles? Bottoms out? Seals? Survives repeated use? |
| Revision | Model and coupon revision that produced the result |

The goal is not merely “it turns.” The goal is a known mating interface with documented geometry and a repeatable fabrication process.

## 9.10 Resin printing considerations

Resin printing can reproduce fine details but has its own failure modes:

- unsupported walls and long thin features can bend or fail under peel forces;
- trapped resin in sealed cavities can create problems;
- holes may require drain/vent openings depending on geometry;
- support contact can scar important surfaces;
- washing and curing can change properties and dimensions;
- uncured resin and cleaning chemicals require proper handling.

Design and post-process according to the specific printer, resin, and safety data. A resin model that looks solid in OpenSCAD can be unsuitable if it traps uncured resin or cannot drain.

## 9.11 3D-print acceptance checks

Before producing a final part, confirm:

- overall dimensions and fit coupon results;
- correct units and orientation in the slicer;
- no unsupported or disconnected regions that the slicer unexpectedly removes;
- support removal access;
- reasonable wall and perimeter representation;
- no trapped cavities that are a concern for the selected process;
- the material is appropriate for temperature and load;
- the intended assembly can be performed without splitting fragile features.

---

# 10. Designing for laser cutting

Laser cutting is primarily a 2D profiling process: the beam follows a path through sheet stock. The geometry is usually represented as closed outlines or vector paths, and the laser's control software determines how it interprets colors, layers, cut order, power, and speed.

## 10.1 Think in profiles and stock thickness

For a flat part, the 2D outline is the controlling geometry. The thickness comes from the sheet stock. A laser-cut profile generally needs:

- a valid closed outer contour where a closed part is intended;
- closed internal contours for holes and cutouts;
- no duplicate overlapping vectors that cause repeated cutting;
- no accidental open segments or self-intersections;
- a known intended scale and unit convention;
- enough material around holes and narrow tabs to avoid breakage;
- fit allowances based on measured stock and kerf behavior.

If a design becomes a folded or assembled product, model the interfaces between panels—not just each face in isolation.

## 10.2 DXF and SVG workflow

OpenSCAD can export 2D geometry to DXF or SVG. Different laser software packages accept different formats and subsets of features. Check the machine workflow before choosing the export.

For a simple 2D profile, generate 2D geometry directly (for example, with `square()`, `circle()`, `polygon()`, `difference()`, and `union()`) and export the 2D model. Do not extrude it into a 3D body unless a 3D view is needed for another purpose.

A practical check sequence is:

1. Export the DXF or SVG.
2. Open it in a vector editor or the laser's design software.
3. Measure a known dimension to confirm scale.
4. Inspect every path and remove duplicates.
5. Confirm whether the machine software offsets paths for kerf.
6. Assign operation/color/layer settings according to the shop's workflow.
7. Use a small test cut in the actual material before a valuable sheet.

## 10.3 Kerf: retained geometry versus tool path

A laser does not remove zero-width material. The beam removes a narrow strip called the kerf. If a machine follows the nominal outline on its centerline with no compensation, the outside of the retained part and the inside of a cutout will be shifted relative to the nominal boundary. A controller can compensate by offsetting the path to one side or the other.

However, workflows differ. Some operators put nominal geometry into CAD and apply kerf compensation in the laser software; others use a CAM process or drawing workflow that explicitly compensates the profile. The critical rule is:

**Know which stage owns kerf compensation, and apply it exactly once.**

A kerf test coupon is much better than blindly using a value from another machine or material. Record the material, thickness, settings, and machine condition because the correct offset can change.

## 10.4 Tab-and-slot joints

For a tab/slot joint, start with the **measured sheet thickness**, then determine whether the joint should slide, locate snugly, press together, or leave room for adhesive. The relationship is not simply “slot width equals nominal sheet thickness.” Stock may vary, and the kerf and cut geometry affect the final opening.

Make a coupon with several slot widths and tabs. Choose the one that meets the required assembly behavior. For a structural assembly, also consider how the joint transfers load, the direction of the sheet grain or plies, tab-root stress concentration, fasteners, adhesive, and whether the cut edges are damaged by the process.

## 10.5 Minimum feature size and heat effects

A feature can be too small for the material and beam to reproduce reliably. Narrow tabs can char, melt, fracture, or vanish. Closely spaced cuts can overheat the region. Acrylic, plywood, paper, cardboard, fabric, and engineering sheet materials react differently.

Keep thin webs and delicate tabs as large as practical, especially if the part carries load. Use a material-specific test and the machine's known settings. Do not assume a setting that works on one plywood or acrylic thickness will work on another.

## 10.6 Material safety

Only cut materials approved by the machine manufacturer and facility. Some plastics release corrosive or toxic compounds or can damage the machine. PVC/vinyl, for example, is not appropriate for ordinary laser cutting because it can release hazardous corrosive gases. Verify the exact material composition rather than relying on a seller's vague label. Maintain exhaust, fire monitoring, and the shop's operating procedure; never leave a laser operating unattended unless the machine's approved process and facility policy explicitly permit it.

## 10.7 Folded sheet and assembled structures

OpenSCAD can describe the flat profile, but it does not automatically create a validated sheet-metal flat pattern with bend allowances and bend deductions. If a part will be bent, include:

- material thickness;
- bend radius;
- bend angle;
- bend direction;
- process-specific bend allowance/deduction;
- reliefs at corners and intersecting bends;
- the target dimensions after forming.

For precision sheet-metal work, use a suitable sheet-metal CAD/CAM workflow or a verified bend table. A flat profile alone does not guarantee that the formed part will have the intended dimensions.

---

# 11. Designing for CNC milling and routing

CNC machining removes material with a rotating or otherwise controlled cutting tool. The CAD geometry must be reachable by the selected cutter and compatible with workholding, machine travel, stock, and the CAM strategy.

## 11.1 OpenSCAD does not create the complete machining plan

A DXF exported from OpenSCAD is usually only geometry. A CAM package still needs to determine toolpaths and machining operations. Depending on the machine and job, this includes tool diameter, cutting direction, depth per pass, pocketing strategy, lead-in/out, tabs, step-over, feeds and speeds, work coordinate zero, workholding, and postprocessor.

A design that can be described as a 3D solid may still be difficult or impossible to machine with the available tools. Consider access and tool reach while modeling.

## 11.2 Internal corner radius

A round end mill leaves a radius at the inside corner of a pocket. For a cutter of diameter `D`, the nominal cutter radius is `D/2`, although the achieved geometry also depends on toolpath strategy and actual tool condition.

If a square tab must fit into a machined pocket, a sharp CAD corner will not be reproduced by an ordinary round cutter. Options include:

- add dogbone or T-bone reliefs;
- round the mating tab's corners;
- use a smaller tool if the feature, material, and machine allow it;
- redesign the joint to tolerate the internal radius.

Choose the mating strategy before releasing the profile. A corner relief changes the design geometry and can affect strength or appearance.

## 11.3 Tool diameter, reach, and aspect ratio

A cutter cannot enter a slot narrower than itself. A long, thin cutter may deflect or chatter. Deep pockets can require long-reach tools, which are more flexible and can produce poorer finish or accuracy.

Check:

- minimum slot and pocket width;
- internal corner radii;
- hole diameters and available drills/end mills;
- tool reach relative to pocket depth;
- the distance between adjacent features;
- residual wall thickness;
- collision risks between holder, spindle, workpiece, and clamps;
- whether the geometry can be machined in one setup or needs multiple orientations.

A design with deep, narrow recesses should be reviewed against actual tooling before fabrication.

## 11.4 Stock, workholding, and tabs

The workpiece must be held securely without putting clamps in the toolpath. A profile cut all the way around a part may release it before the job is finished. CAM may use **tabs**—small uncut bridges that keep the part attached until the final operation—or an onion-skin strategy that leaves a thin final layer for a finishing pass.

Design the part and CAM strategy together. Provide enough perimeter for workholding where needed; avoid placing a critical surface where a clamp must contact it; and account for tool access to the underside if both sides require machining.

## 11.5 Feeds, speeds, step-down, and finish pass

Common CNC terms:

- **Feed rate:** how quickly the tool moves relative to the work.
- **Spindle speed:** rotational speed of the cutter.
- **Chip load:** the approximate thickness of material removed per cutting edge per revolution; a major factor in tool performance.
- **Step-down:** depth of material removed per pass.
- **Step-over:** lateral spacing between adjacent passes.
- **Roughing pass:** removes bulk material efficiently while leaving stock for finishing.
- **Finishing pass:** a lighter or dedicated pass intended to improve final geometry or surface finish.
- **Climb milling / conventional milling:** two directions of cutter/work engagement with different force and finish behavior.
- **Chatter:** unstable vibration that can degrade finish, accuracy, or tool life.
- **Work coordinate / work zero:** the reference origin used by the machine/CAM setup.

These are not parameters to guess casually. Use tool/manufacturer guidance and the machine's proven settings. The correct values depend on material, cutter type, diameter, flute count, rigidity, spindle, and machine construction.

## 11.6 Tolerances and finish

A CNC router making a hobby fixture may not hold the same tolerances or surface finish as a rigid machining center with suitable tooling and inspection. Do not specify tighter tolerances than the process can deliver. If a dimension is critical, indicate it explicitly, choose a suitable process, and inspect the result using an appropriate tool.

For mating parts, a coupon can reveal practical clearance and toolpath behavior. For precision features such as bearing seats, shaft fits, or alignment bores, consider finishing operations and metrology appropriate to the required tolerance.

## 11.7 CNC-specific preflight

Before machining:

- confirm material and actual stock dimensions;
- confirm the selected tool diameter and reach;
- simulate toolpaths and inspect for collisions or uncut regions;
- verify the coordinate system and work zero;
- verify operation order and tabs/workholding;
- inspect pockets, internal corners, and undercuts;
- check the postprocessor and machine-specific output;
- make a safe test or air cut where appropriate;
- follow the machine's safety and lockout procedures.

---

# 12. Export formats: SCAD, STL, 3MF, DXF, SVG, and more

## 12.1 Keep the source model

`.scad` is the editable OpenSCAD source. It preserves parameter names, formulas, modules, comments, and the logic used to generate geometry. Exported files usually do not preserve all that design intent.

Keep a source file and generate output files from a tagged or clearly named revision. If you adjust a model after exporting, regenerate the output—do not assume the old file matches the current source.

## 12.2 STL: 3D triangle mesh

**STL** represents a surface using triangles. It is widely accepted by 3D-print slicers and many mesh-processing tools.

Advantages:
- broad support;
- simple geometry exchange;
- suitable for many ordinary 3D-print jobs.

Limitations:
- STL does not reliably carry an explicit real-world unit convention; importers commonly assume millimeters, but this must be checked;
- it does not preserve the parametric source or feature tree;
- it approximates curves with triangles;
- colors and richer manufacturing metadata are not consistently represented;
- a flawed mesh can have holes, self-intersections, flipped facets, or non-manifold edges.

Always verify the imported dimensions in the slicer. A model imported as 25.4 times too large or too small may be a unit-interpretation issue rather than a bad OpenSCAD model.

## 12.3 3MF: a richer print package

**3MF** is a newer 3D manufacturing format supported by many contemporary slicers and tools. It can carry information beyond a basic STL mesh, depending on the application and format profile. It is often convenient where the receiving workflow supports it. Do not assume every program implements every 3MF feature the same way; check the receiver's behavior.

## 12.4 DXF: 2D CAD exchange

**DXF** is commonly used to exchange 2D profiles for laser cutting and some CNC CAM workflows. DXF files can include more complex CAD entities than a simple outline, but the receiving system may support only a subset.

Before cutting or milling, verify:

- the drawing's units/scale interpretation;
- the intended 2D plane;
- that the profile contains the correct closed contours;
- there are no duplicate paths or stray points;
- the geometry is not unintentionally projected from an incorrect plane;
- the receiving CAM software interprets arcs, splines, polylines, and layers as expected.

Do not expect a DXF exported from OpenSCAD to contain a complete dimensioned mechanical drawing, title block, GD&T scheme, material callouts, or manufacturing plan.

## 12.5 SVG: vector graphics

**SVG** is a scalable vector graphics format. It is useful for 2D outlines, graphics, signage, and many laser-cutting workflows. A laser workflow may interpret strokes, fills, colors, groups, and text differently. Convert text to paths when necessary and supported by the workflow, and confirm that a line intended to be cut is not merely displayed as a thick stroke that the machine interprets unexpectedly.

## 12.6 CSG and other formats

OpenSCAD can export additional formats such as CSG for inspection/debugging and image formats for visual output. Exact format support depends on the installed OpenSCAD version and build. Consult the official export documentation or the program's export menu for the version in use.

OpenSCAD is not a typical native STEP/IGES parametric solid-modeling system. If a supplier requires a STEP solid or native feature-based CAD model, use an appropriate CAD exchange workflow and verify that the transferred geometry is sound. A mesh-to-solid conversion is not guaranteed to recover the original design intent.

## 12.7 Export from the graphical interface

Typical GUI workflow:

1. Open the `.scad` file.
2. Check the parameter values and coordinate orientation.
3. Preview the model.
4. Run full Render and read the console for errors or warnings.
5. Use the appropriate export command for STL/3MF or 2D DXF/SVG.
6. Open the exported file in the next program and verify dimensions.
7. Save a brief record of the export format, source revision, and settings.

Menu names can differ slightly by release. Treat the file extension and the export dialog as authoritative for the installed version.

## 12.8 Command-line export

OpenSCAD can be used from a terminal to automate output generation. A basic command is:

```bash
openscad -o bracket.stl bracket.scad
```

A 2D profile can be exported with a corresponding extension:

```bash
openscad -o panel.dxf panel_2d.scad
openscad -o panel.svg panel_2d.scad
```

A rendered image can be useful in a build report:

```bash
openscad -o preview.png --imgsize=1200,900 bracket.scad
```

Command-line options vary somewhat by version. Check `openscad --help` and the official command-line manual before building automation around an option. Use a dedicated 2D source or top-level model for DXF/SVG output so an unintended 3D projection is not exported.

### Variant export and parameter overrides

Command-line variable overrides are useful for generating families of parts, but they require a clear variable/default convention. Because OpenSCAD variable assignment and scoping do not behave like ordinary sequential assignment, test any `-D` override in a small script before relying on it in a production batch.

A practical approach is to keep a small set of explicit variant files or a documented customizer parameter set if reproducibility matters. Confirm that the exported geometry reflects the intended dimensions by checking its log or by measuring the imported file.

## 12.9 Export resolution and mesh quality

For a 3D mesh, confirm that circular or curved features have adequate tessellation. Higher resolution creates more triangles and can increase file size and processing time. Too little resolution can affect visual quality and the geometry of small fitting features.

For a manufacturing profile, the more important checks are often the actual dimension, curve/path validity, and receiving software's interpretation. Do not use a higher `$fn` setting as a substitute for checking scale or process tolerance.

## 12.10 Units and scale verification

Units are one of the most common handoff hazards. Establish the unit convention in the `.scad` comments and project notes. For every new export route:

1. choose a known dimension, such as a 50.00 mm edge;
2. export the file;
3. open it in the next application;
4. measure that edge in the receiving application;
5. verify orientation and overall bounding dimensions;
6. only then proceed to fabrication.

Repeat this check after changing software, file format, import settings, or machine workflow.

---

# 13. From geometry to machine instructions

## 13.1 The 3D printing route

**OpenSCAD → STL/3MF → slicer → preview/toolpath → printer instructions → print → inspection**

At the slicer stage, confirm:

- model dimensions and units;
- build-plate orientation;
- material profile;
- layer height and nozzle configuration;
- wall/perimeter count and top/bottom layers;
- infill and support strategy;
- seams, bridges, overhangs, and thin-wall handling;
- estimated time/material and whether the part fits the build volume.

The slicer's preview should show the actual layers or paths, not merely the outer silhouette. Look for missing walls, unconnected islands, unsupported features, or unexpected infill inside a cavity.

## 13.2 The laser route

**OpenSCAD 2D profile → DXF/SVG → vector/laser software → scale/path check → operation mapping → settings → test cut → final cut**

The laser controller or shop process determines which path is cut, engraved, scored, or ignored. Never assume that line color means the same thing on every laser. Confirm the machine's own layer/color convention and file-import rules.

Before running, make sure the job's actual geometry, material, thickness, and settings match the approved plan. Do a small coupon first for unfamiliar material or a critical joint.

## 13.3 The CNC route

**OpenSCAD geometry/profile → CAD/CAM import → stock and tool selection → toolpath generation → simulation → postprocessor → machine setup → machining → inspection**

The CAM operator must translate design geometry into operations. The operation strategy should account for stock size, tool geometry, workholding, cut order, roughing/finishing, work zero, feeds/speeds, and the machine's approved code dialect.

An STL or DXF alone is not a safe machining plan. Simulate and review toolpaths, and follow the machine's procedure for workholding, tool changes, spindle start, emergency stops, and safe positioning.

## 13.4 Fabrication notes for a handoff

For another person or shop, provide at least:

- part name and revision;
- units;
- fabrication method;
- material and thickness/grade;
- file format and intended operation;
- critical dimensions and tolerances;
- fit/clearance intent;
- any required finish or post-processing;
- coupon results or machine-specific notes, when relevant;
- inspection method and acceptance criteria.

A file that opens successfully is not automatically a complete manufacturing handoff.

---

# 14. Inspection, debugging, and quality control

## 14.1 Inspect the physical part, not only the model

Check the characteristics tied to function. Depending on the part, this may include:

- overall length, width, height, or thickness;
- hole/slot dimensions and center spacing;
- flatness or rocking on a reference surface;
- perpendicularity or alignment of mating faces;
- burrs, sharp edges, cracks, delamination, warping, or char;
- insertion force and retention;
- clearance in motion;
- fastener seating and tool access;
- surface quality on sealing or sliding surfaces.

For simple parts, a caliper and assembly test may be enough. For tighter tolerances, use more suitable gauges and a documented measurement procedure.

## 14.2 Measure the feature that matters

A part can have correct overall dimensions yet fail because a hole is oval, two holes are misplaced, a wall bows, or a mating face is not flat. Measure the functional feature and its relationship to the chosen datum, not just the bounding box.

## 14.3 Root-cause table

| Symptom | Possible causes | Useful next check |
|---|---|---|
| All dimensions wrong by the same scale factor | Unit/import-scale issue | Measure a known length in the receiving software |
| Outside dimensions too small | Shrinkage, kerf, toolpath compensation, model dimension, calibration | Measure stock/part and inspect process compensation |
| Printed holes undersize | Extrusion geometry, orientation, cooling, first-layer effect | Print a hole coupon in the same orientation |
| Laser slots too tight | Stock thicker than assumed, kerf/compensation, import scale | Measure stock, cut a slot/kerf coupon, review path offsets |
| CNC internal corner will not accept square tab | Cutter radius not accounted for | Check tool diameter; add corner relief or round the tab |
| Part looks correct in preview but export fails | Render geometry issue, non-manifold/zero-thickness features | Run full render, simplify model, inspect the mesh/profile |
| Parts fit individually but assembly binds | Stack-up, alignment, warping, wrong datum or uneven contact | Measure the assembly interfaces together |
| Snap tab breaks | Poor orientation, thin root, sharp corner, material/fatigue | Test a geometry/orientation coupon; redesign load path |
| Result varies between material sheets | Stock thickness or material batch variation | Measure each batch and retain coupon records |

## 14.4 Design revision control

Every released geometry should have a revision identifier. If a fit changes, record the reason and the new value. Do not silently overwrite a known-good design and lose the connection between the source file and the physical part.

Use clear filenames such as:

- `sensor_bracket_revA.scad`
- `sensor_bracket_revA.stl`
- `sensor_bracket_fit_coupon_revA.scad`
- `sensor_bracket_inspection_revA.md`

For projects under active development, use version control such as Git. Commit the source and notes; generated output files may be included or kept as release artifacts depending on team practice. The key is that a physical part can be traced back to the code and settings that generated it.

---

# 15. Worked OpenSCAD projects

These are templates for learning and adaptation. Render each, inspect the exported file, and make a test piece before using a design in a load-bearing or safety-critical application.

## Project A: Parametric mounting plate

**Goal:** a plate whose size, thickness, edge margins, hole diameter, and pattern count can be changed through named parameters.

```scad
// mounting_plate.scad
// All dimensions in mm.

L = 100;
W = 60;
T = 5;
edge_x = 12;
edge_y = 12;
cols = 4;
rows = 2;
hole_d = 5.2;
$fn = 64;

assert(L > 2*edge_x, "L must exceed twice edge_x");
assert(W > 2*edge_y, "W must exceed twice edge_y");
assert(cols >= 2 && rows >= 2, "Use at least two rows and columns");

pitch_x = (L - 2*edge_x)/(cols-1);
pitch_y = (W - 2*edge_y)/(rows-1);

difference() {
    cube([L, W, T]);

    for (i = [0:cols-1])
    for (j = [0:rows-1])
        translate([edge_x+i*pitch_x,
                   edge_y+j*pitch_y,
                   -0.1])
            cylinder(h=T+0.2, d=hole_d);
}
```

### What to learn

- Primary dimensions are explicit.
- Hole centers are generated from edge margins and hole count.
- Cutter cylinders extend slightly beyond the plate.
- Assertions protect against some invalid parameter choices.
- This is a 3D printable plate or a starting point for a plate machined from stock.

If the plate is laser-cut, use its 2D projection/profile instead of treating its `T` as a material thickness to be produced by the laser. For CNC, check whether the chosen tool can create the holes and whether the CAM operation needs drilled or milled holes.

## Project B: Laser-cut panel with mounting holes and cable slot

**Goal:** generate a 2D outline. Export as DXF or SVG, verify scale, and apply kerf compensation only in the designated stage of the workflow.

```scad
// laser_panel_2d.scad
// This is 2D profile geometry. Dimensions in mm.

panel_x = 120;
panel_y = 80;
corner_r = 4;
hole_d = 4.5;
edge_x = 12;
edge_y = 12;
slot_l = 30;
slot_w = 8;
$fn = 64;

module rounded_rect_2d(x, y, r) {
    // Standard offset-based rounded rectangle pattern.
    offset(r=r) offset(delta=-r) square([x, y]);
}

difference() {
    rounded_rect_2d(panel_x, panel_y, corner_r);

    for (x = [edge_x, panel_x-edge_x])
    for (y = [edge_y, panel_y-edge_y])
        translate([x, y]) circle(d=hole_d);

    // A centered rounded cable slot.
    translate([panel_x/2, panel_y/2])
        slot_2d(slot_l, slot_w);
}

module slot_2d(length, width) {
    assert(length >= width, "slot_l must be >= slot_w");
    hull() {
        translate([-(length-width)/2, 0]) circle(d=width);
        translate([ +(length-width)/2, 0]) circle(d=width);
    }
}
```

The module definition can be placed before its use for readability; OpenSCAD allows module definitions to be referenced elsewhere in the file. Export with the `.dxf` or `.svg` extension using your installed OpenSCAD version. Check that the laser import retains the intended 120 × 80 mm envelope and that every desired path is interpreted as a cut.

**Fabrication test:** if the hole/slot fit or edge dimension matters, cut a small coupon from the actual sheet first. This code uses nominal geometry; it does not automatically know the laser's kerf or your sheet thickness.

## Project C: Simple L-bracket for a 3D printer

**Goal:** demonstrate a functional bracket with base holes and vertical-face holes. This is a geometric learning example, not a load-rated bracket.

```scad
// l_bracket.scad
// All dimensions in mm. Validate orientation and strength before use.

width = 50;
base_depth = 35;
plate_t = 5;
up_height = 35;
mount_hole_d = 4.5;
side_edge = 12;
base_hole_y = 12;
$fn = 64;

assert(width > 2*side_edge, "Bracket width too small for hole spacing");

module bracket_body() {
    union() {
        // Horizontal foot: starts at z=0.
        cube([width, base_depth, plate_t]);

        // Vertical flange at the rear edge of the foot.
        translate([0, base_depth-plate_t, plate_t])
            cube([width, plate_t, up_height]);
    }
}

difference() {
    bracket_body();

    // Two holes in the horizontal foot, cut along Z.
    for (x = [side_edge, width-side_edge])
        translate([x, base_hole_y, -0.1])
            cylinder(h=plate_t+0.2, d=mount_hole_d);

    // Two holes in the vertical flange, cut along Y.
    for (x = [side_edge, width-side_edge])
        translate([x, base_depth+0.1, plate_t+up_height/2])
            rotate([90, 0, 0])
                cylinder(h=plate_t+0.2, d=mount_hole_d);
}
```

### What to improve before a real load

- Add gussets or ribs if appropriate, and check where they can be printed or machined.
- Avoid sharp internal corners at highly loaded transitions.
- Ensure screw heads, nuts, washers, and the tool used to tighten them have enough room.
- Check the bracket orientation against the load direction and print-layer direction.
- Prototype the mounting-hole spacing with a coupon.
- Perform a load test with a safety margin if the bracket supports expensive, heavy, hot, moving, or hazardous equipment.

## Project D: Enclosure shell

**Goal:** create a box with a floor and walls, then add ports and mounting features as parameters.

```scad
// enclosure_shell.scad
// Basic open-top shell. Dimensions in mm.
outer_x = 90;
outer_y = 65;
outer_z = 30;
wall = 2.4;
floor_t = 3;
port_d = 10;
port_x = outer_x/2;
port_z = 15;
$fn = 64;

assert(outer_x > 2*wall && outer_y > 2*wall,
       "Outer plan dimensions must exceed two wall thicknesses");
assert(outer_z > floor_t, "Height must exceed floor thickness");

difference() {
    cube([outer_x, outer_y, outer_z]);

    translate([wall, wall, floor_t])
        cube([outer_x-2*wall,
              outer_y-2*wall,
              outer_z-floor_t+0.1]);

    // Cable port through the front wall (Y direction).
    translate([port_x, -0.1, port_z])
        rotate([-90, 0, 0])
            cylinder(h=wall+0.2, d=port_d);
}
```

The port orientation and position deserve a careful render and physical verification. A finished enclosure may need corner radii, lid engagement, screw bosses, vents, sealing surfaces, wire strain relief, and thermal management. If electronics are enclosed, account for heat, electrical clearance, grounding, fire behavior, and access—not just the fit of the lid.

## Project E: Hole clearance coupon

Use the parametric coupon in [Section 8.2](#82-fdm-fit-coupon-holes-for-a-pin-or-shaft). Adapt the list of clearances to the question you need answered. For example, make a tighter range once you know the rough fit. Keep coupon code and results with the part source, not in an unrelated notebook that can be lost.

## Project F: A profile for a CNC plate

**Goal:** export a 2D outline that CAM can use. This example intentionally leaves toolpaths to the CAM package.

```scad
// cnc_plate_profile.scad
// 2D outline only. Dimensions in mm.

L = 100;
W = 55;
corner_r = 5;
center_hole_d = 12;
mount_d = 5;
edge_x = 12;
edge_y = 12;
$fn = 80;

module rounded_rect_2d(x, y, r) {
    offset(r=r) offset(delta=-r) square([x, y]);
}

difference() {
    rounded_rect_2d(L, W, corner_r);

    translate([L/2, W/2]) circle(d=center_hole_d);

    for (x = [edge_x, L-edge_x])
    for (y = [edge_y, W-edge_y])
        translate([x, y]) circle(d=mount_d);
}
```

This is a nominal profile, not a G-code program. In CAM, choose the stock, work zero, cutter, drilling or milling operation, cut depth, finishing strategy, tabs/workholding, feed/speed, and postprocessor. Check internal radii against the actual cutters. If a mating part needs square internal corners, design appropriate reliefs.

---

# 16. A repeatable project folder and revision system

A useful folder structure for a small fabrication project might be:

```text
sensor-bracket/
├── README.md
├── requirements/
│   ├── requirements.md
│   └── measurements.csv
├── cad/
│   ├── sensor_bracket.scad
│   └── fit_coupon.scad
├── exports/
│   ├── revA/
│   │   ├── sensor_bracket.stl
│   │   └── sensor_bracket.dxf
│   └── revB/
├── drawings/
│   └── sensor_bracket_revA.pdf
├── process/
│   ├── printer_settings.md
│   ├── laser_settings.md
│   └── cnc_setup.md
├── tests/
│   ├── coupon_log.md
│   └── inspection_record.md
└── photos/
```

You do not need every folder for every project. The point is to keep design intent, exported geometry, process settings, and physical validation linked together.

## 16.1 README template

```markdown
# Part / Assembly Name

## Purpose
What this part does and where it is used.

## Revision
- Current revision:
- Date:
- Change from previous revision:

## Interfaces
- Mating part or item:
- Critical dimensions:
- Fit/clearance definition:

## Fabrication
- Process:
- Material and grade:
- Stock thickness / filament / resin:
- Machine and key settings:
- Post-processing:

## Verification
- Coupon ID / result:
- Critical measurements:
- Acceptance criteria:
- Open issues:

## Outputs
- Source file:
- Export format and revision:
- Drawing:
```

## 16.2 Revision changes should have reasons

A useful revision note states what changed and why:

- “Rev B: increased the lid rail's radial clearance from 0.15 to 0.25 mm per side after the same-material coupon bound during insertion.”
- “Rev C: moved the two mounting holes to a common datum because chain dimensions caused accumulated position error.”
- “Rev D: added dogbone reliefs to accommodate the 6 mm end mill used by the shop.”

This is much more valuable than “fixed fit.” It documents the engineering decision so the value can be reused intelligently.

---

# 17. Safety and engineering limits

A correctly modeled part can still be unsafe. A geometric model does not automatically validate material strength, fatigue life, electrical safety, pressure containment, thermal behavior, or legal compliance.

Treat the following applications as requiring more than casual trial-and-error CAD:

- lifting or supporting people, vehicles, or heavy objects overhead;
- rotating machinery, high-speed parts, or components whose failure could release fragments;
- pressure vessels, compressed gas, steam, or high-pressure fluid systems;
- mains electrical insulation, battery containment, and fire-risk enclosures;
- medical, food-contact, or life-safety components;
- hot parts near their material's softening or degradation range;
- high-cycle fatigue, impact, or safety-critical latches;
- structural parts where failure can cause injury or substantial damage.

For such uses, identify design loads and failure modes, apply suitable engineering analysis and safety factors, select rated materials and processes, and arrange appropriate testing or professional review. A simple printed coupon can expose a fit problem but does not certify a structure.

Use proper eye protection, ventilation, workholding, fire controls, guarding, and material handling for the chosen fabrication process. For laser cutting and CNC, follow the shop's machine-specific procedures. For resin printing, follow the resin and solvent safety data. For FDM, consider hot surfaces, moving parts, fumes, and material-specific ventilation requirements.

---

# 18. Learning path and practice exercises

Work in small steps, and make physical artifacts at every stage. The objective is not merely to learn OpenSCAD syntax—it is to learn the chain from design intent to a measured physical result.

## Level 1: Basic geometry

1. Create a 30 × 20 × 5 mm block.
2. Add a centered through-hole.
3. Add four corner holes using a loop.
4. Render and export an STL.
5. Import it into a slicer and verify the dimensions.
6. Print it and measure length, width, thickness, and hole diameter.

**Skills:** primitives, variables, coordinate systems, `difference()`, loops, STL export, unit verification.

## Level 2: Parametric part

1. Make a mounting plate with adjustable length, width, thickness, edge distance, hole diameter, and row/column count.
2. Derive hole spacing from the dimensions and edge margins.
3. Add assertions for invalid values.
4. Change dimensions and ensure the pattern still makes sense.
5. Write down which dimensions are primary and which are derived.

**Skills:** parametric modeling, derived dimensions, modules, constraints, design intent.

## Level 3: Physical fit testing

1. Measure a real shaft, bolt, panel, or connector.
2. Model a mating feature with a named clearance parameter.
3. Generate a multi-value coupon.
4. Fabricate the coupon using the same process as the final part.
5. Test each variation and record the winner.
6. Rebuild only the affected part and verify the fit.

**Skills:** tolerance language, process variability, measurement, test planning, iteration.

## Level 4: Laser-cut assembly

1. Design a small flat panel with holes and a rounded slot.
2. Export a DXF/SVG and check its scale in the receiving software.
3. Cut a kerf and slot-width coupon in the actual sheet material.
4. Design a tab/slot joint using the measured stock thickness.
5. Assemble the parts and revise based on actual fit.

**Skills:** 2D profiles, kerf, stock variation, vector-file handoff, joint design.

## Level 5: CNC-ready geometry

1. Model a plate with a pocket, holes, and internal corners.
2. Identify the available cutter diameters.
3. Modify corners or mating tabs to accommodate the cutter radius.
4. Export a profile/solid supported by the CAM workflow.
5. Simulate the CAM operations and inspect tool access.
6. Inspect the finished part against the drawing or acceptance criteria.

**Skills:** tool access, internal radii, workholding, roughing/finishing, CAM handoff.

## Level 6: Documented component family

1. Create a standard mounting-hole module or enclosure family.
2. Generate multiple sizes from parameters.
3. Maintain source and export revisions.
4. Include coupon records and material/process settings.
5. Produce an inspection checklist for each variant.

**Skills:** reusable design, version control, release discipline, traceability.

---

# 19. Quick-reference checklists

## 19.1 Before modeling

- [ ] Have I defined the function and acceptance criteria?
- [ ] Have I identified all mating parts and critical interfaces?
- [ ] Have I measured the real part or obtained reliable specifications?
- [ ] Have I chosen datums/origin conventions that make the geometry easy to control?
- [ ] Have I selected the likely fabrication process and material?
- [ ] Have I identified which dimensions need a coupon or formal tolerance?

## 19.2 Before exporting

- [ ] Are units documented and consistent?
- [ ] Are key dimensions parameterized and derived dimensions expressed as relationships?
- [ ] Does the model render without errors?
- [ ] Are intended solids actually connected, with no accidental zero-thickness features?
- [ ] Is the selected export format appropriate for the next stage?
- [ ] Have I checked that the 2D profile lies in the intended plane?
- [ ] Have I saved the source revision that generated the export?

## 19.3 Before a 3D print

- [ ] Did I verify model size in the slicer?
- [ ] Is the orientation suitable for the load and layer strength?
- [ ] Are walls and small features compatible with the selected process/settings?
- [ ] Are holes and mating features based on a test coupon where required?
- [ ] Are support structures accessible and removable?
- [ ] Is the material suitable for heat, chemicals, moisture, UV, and mechanical loads?
- [ ] Have I inspected the sliced layer preview?

## 19.4 Before a laser cut

- [ ] Is the material approved for this laser and properly identified?
- [ ] Is the stock thickness actually measured?
- [ ] Does the imported file have the correct scale?
- [ ] Are paths closed where intended and free of duplicates?
- [ ] Is kerf compensation applied exactly once in the intended stage?
- [ ] Have I test-cut tab/slot or other critical fits?
- [ ] Are ventilation, fire watch, and machine procedures satisfied?

## 19.5 Before CNC machining

- [ ] Is the stock correct and measured?
- [ ] Are cutter diameters, radii, lengths, and reach known?
- [ ] Can the tool reach every pocket and surface?
- [ ] Have I accounted for internal radii and corner reliefs?
- [ ] Are workholding, tabs, and operation sequence safe?
- [ ] Has the CAM toolpath been simulated and inspected?
- [ ] Are the work zero, units, postprocessor, and machine setup correct?
- [ ] Is the part's tolerance realistic for the machine and setup?

## 19.6 Before declaring the part finished

- [ ] Does it meet the functional fit, not merely the visual target?
- [ ] Have critical dimensions been measured and recorded?
- [ ] Have I inspected for warping, cracks, burrs, delamination, and surface defects?
- [ ] Have I tested assembly and movement under the intended conditions?
- [ ] Have I documented the chosen dimensions and the reason for them?
- [ ] Can I reproduce this part from the source revision and process notes?

---

# 20. Glossary

This glossary is intentionally practical. Some terms have narrower, formal meanings in particular standards; consult the relevant standard when a drawing or contract depends on the formal definition.

- **AWG (American Wire Gauge):** designation system for nominal round electrical-conductor sizes; it is not a universal wire or sheet-metal gauge.
- **Accuracy:** closeness to the intended value.
- **Allowance:** intentional difference between mating dimensions at the specified material condition; consult the governing fit standard.
- **Assembly:** multiple parts working together.
- **Axis:** an imaginary line defining the center or direction of a rotational or linear feature.
- **Baseline dimensioning:** dimensions measured from a common datum.
- **Basic dimension:** theoretically exact dimension used with other controls, often GD&T.
- **Bend allowance:** length of material along the neutral region of a bend, used in flat-pattern calculations.
- **BOM:** bill of materials; component list for an assembly.
- **Boss:** raised, often cylindrical feature for fastening or locating.
- **Bore:** cylindrical internal surface or hole.
- **Bridge:** an unsupported span printed between two supports; in CNC, bridge can also refer to a residual connection or workholding feature depending on context.
- **Buttress thread:** asymmetric thread form intended to carry substantial axial load primarily in one direction.
- **CAD:** computer-aided design.
- **CAM:** computer-aided manufacturing; software to generate manufacturing operations/toolpaths.
- **Chamfer:** beveled edge or corner.
- **Clearance:** space between mating features.
- **CNC:** computer numerical control.
- **Coaxial:** sharing a common axis.
- **Concentric:** sharing a common center; formal interpretation depends on context.
- **Constraint:** a relationship limiting geometry, such as fixed distance, symmetry, or perpendicularity.
- **Continuous-thread finish:** packaging neck/cap family with a helical thread that continues around the neck; designations such as `89/400` are finish designations, not machine-screw TPI callouts.
- **Counterbore:** flat-bottomed cylindrical recess around a hole.
- **Countersink:** conical recess around a hole.
- **CSG:** constructive solid geometry; constructing models through Boolean combinations of primitives.
- **Datum:** reference used to locate or evaluate geometry.
- **Datum feature:** actual feature used to establish a datum.
- **Design intent:** the relationships and behavior the model is meant to preserve when dimensions change.
- **Diameter:** distance across a circle through its center.
- **Dimension:** numerical definition of size, position, or orientation.
- **Dimension stack-up:** accumulated effect of multiple dimensions/tolerances.
- **Dogbone relief:** local cutout that accommodates a round cutter at an internal corner.
- **Draft angle:** taper used to help remove a part from a mold/tool.
- **DXF:** Drawing Exchange Format, widely used for 2D CAD geometry exchange.
- **Datum reference frame:** coordinated reference system established from datums for measurement/control.
- **Elephant foot:** outward spread at the first layers of an FDM print.
- **Envelope:** outer boundary/overall volume occupied by the part.
- **Feature:** a distinct geometric element with functional or manufacturing significance.
- **Feature control frame:** GD&T annotation containing a geometric control and related tolerance/datum information.
- **Fillet:** rounded transition between surfaces, often concave at an internal corner.
- **Fit:** relationship between mating dimensions after manufacture.
- **Flat pattern:** flat sheet geometry used before bending/forming.
- **Flatness:** variation of a surface from a perfect plane.
- **FDM/FFF:** fused deposition modeling / fused filament fabrication; extrusion-based 3D printing.
- **GD&T:** geometric dimensioning and tolerancing.
- **G-code:** common family of numerical-control commands for machine movement and operations; dialects vary.
- **Hole basis / shaft basis:** standardized fit-system approaches where one type of feature is held as the reference basis.
- **Interference fit:** fit with intentional dimensional overlap.
- **Kerf:** width of material removed by a cutter/laser.
- **Kerf compensation:** intentional path offset to achieve the desired retained geometry.
- **Lead:** axial distance advanced in one complete revolution of a thread; equals pitch for a single-start thread but differs for multiple starts.
- **Layer height:** vertical increment between layers in layer-based 3D printing.
- **Major diameter:** largest diameter of the thread form.
- **Manifold mesh:** mesh with consistent, closed surface topology suitable for solid interpretation by downstream tools.
- **Material condition:** a feature's size relative to its specified tolerance/limits; formal terms include maximum and least material conditions.
- **Mating feature:** geometry that interfaces with another part.
- **Minkowski sum:** geometric operation used in OpenSCAD and computational geometry, often used for offsetting or rounding shapes.
- **Minor diameter:** smallest diameter of the thread form.
- **Nominal dimension:** stated target size.
- **Non-manifold geometry:** geometry with ambiguous or invalid surface connectivity for a solid, such as certain edges shared in an invalid way or open boundaries.
- **Offset:** a shifted contour or path; may refer to geometry growth/shrinkage or toolpath compensation.
- **Ordinate dimensioning:** coordinates from a common datum rather than a chain of incremental dimensions.
- **Orthographic view:** aligned 2D view of a 3D object.
- **Overhang:** portion of a layer or structure extending beyond support below it.
- **Parametric model:** model whose dimensions and relationships are controlled by named inputs and formulas.
- **Pitch:** repeated spacing; in threads, axial distance between adjacent thread forms.
- **Pitch diameter:** theoretical diameter used to characterize the functional fit of mating screw threads.
- **TPI (threads per inch):** number of thread pitches per inch for inch-series threads.
- **Pocket:** recess into a part.
- **Position tolerance:** GD&T control of a feature's location relative to datums.
- **Precision:** repeatability or closeness among repeated results.
- **Profile:** 2D outline or cross-section.
- **Projection:** mapping geometry onto a plane; OpenSCAD uses `projection()` for 2D extraction of 3D geometry.
- **Radius:** distance from a circle's center to its edge; internal machined corners also have a radius.
- **Radial clearance:** gap per side between centered cylindrical mating features.
- **Repeatability:** consistency among repeated process results.
- **Revision:** identified version of a drawing, model, or released item.
- **Rib:** thin structural feature added for stiffness.
- **Runout:** variation of a surface relative to a datum axis during rotation.
- **Section view:** drawing view showing geometry cut by a plane.
- **Shrinkage:** material size change during cooling, curing, or drying.
- **Slot:** elongated opening.
- **Snap fit:** joint where a flexible feature deflects and returns to retain the mating part.
- **STL:** triangle-mesh exchange format widely used for 3D printing.
- **Stock:** raw material before the part is manufactured.
- **Surface finish:** surface texture/condition produced by manufacturing or post-processing.
- **Taper:** gradual change in width or diameter.
- **Tolerance:** permitted variation from specified limits.
- **Toolpath:** planned movement of a cutter or print head.
- **Transition fit:** fit that may have clearance or interference depending on actual sizes.
- **True position:** common informal phrase for feature location; in GD&T, position has a specific defined meaning.
- **Undercut:** geometry not directly accessible to a simple tool approach or straight-pull process.
- **Union:** Boolean operation combining geometry.
- **Wall thickness:** thickness of a wall or shell.
- **Workholding:** methods used to restrain stock/part during machining.
- **Work zero:** selected coordinate origin for a CNC job.
- **3MF:** 3D manufacturing format that can carry richer data than a basic STL in supported workflows.

---

# 21. References and further reading

Use official documentation and machine/material-specific design guides as the primary source for version-dependent details. This guide was prepared in October 2026; software interfaces and process recommendations can change, so confirm the current documentation before relying on a specific option or dimension.

## OpenSCAD

- [OpenSCAD official documentation hub](https://openscad.org/documentation.html) — entry point for the tutorial, manual, language reference, and cheat sheet.
- [OpenSCAD User Manual](https://files.openscad.org/documentation/manual/OpenSCAD_User_Manual.html) — explains OpenSCAD's script-based CAD approach, preview/render behavior, CSG, imports, exports, and workflows.
- [OpenSCAD Language Reference](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/The_OpenSCAD_Language) — primitives, transformations, Boolean operations, loops, functions, modules, and other syntax.
- [OpenSCAD command-line documentation](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Using_OpenSCAD_in_a_command_line_environment) — command-line export and batch usage; check the installed version's `--help` output as well.

## 3D printing and fit

- [Prusa: Modeling with 3D printing in mind](https://help.prusa3d.com/article/modeling-with-3d-printing-in-mind_164135) — covers print-oriented geometry and emphasizes that tolerances depend on geometry, orientation, calibration, settings, and material.
- [UltiMaker: How to design for FFF 3D printing (PDF)](https://ultimaker.com/wp-content/uploads/2024/06/How-to-design-for-FFF-1.pdf) — design guidance for overhangs, bridges, and support reduction.
- [Formlabs: Design specifications for 3D models](https://formlabs.com/support/Design-Specs/) — resin-print design constraints; verify that guidance matches the actual printer/resin generation.

## Laser cutting

- [UCLA Design Media Arts Fabrication Lab: Working with Kerf](https://support.dma.ucla.edu/fablab/?page_id=176) — introductory explanation of kerf and process-dependent compensation. If the page is unavailable, consult the laser lab's current materials and calibration procedure.
- [Technological Education Resources: Laser cutting fit calibration](https://andrewandrade.ca/tech-edu-resources/design-fabrication/03-laser-cutting/04-material-fit-calibration.html) — practical approach to kerf/material fit coupons and recording results.

## Threads and standard closure geometry

- [BOSL2 `threading.scad` documentation](https://github.com/BelfrySCAD/BOSL2/wiki/threading.scad) — thread-family support and module syntax for ISO/Unified triangular, ACME/trapezoidal, pipe, hose, buttress, square, and other thread geometries.
- [BOSL2 `bottlecaps.scad` documentation](https://github.com/BelfrySCAD/BOSL2/wiki/bottlecaps.scad) — modules for bottle and jar necks/caps, including Mason-jar-style geometry; includes an `89/400`-style example but warns that some profiles are derived from secondary sources and measurements.
- [Continuous-thread and lug closure overview](https://www.burchbottle.com/blog/difference-between-ct-and-lug-c69851/) — explains the packaging meaning of `xx/400` and other finish-family designations. Use the specific container/closure manufacturer's drawing where fit matters.

## Gauge and stock dimensions

- [15 U.S.C. § 206 — Standard gauge for sheet and plate iron and steel](https://www.law.cornell.edu/uscode/text/15/206) — legal standard-gauge reference for iron and steel in the United States.
- [Sheet Metal Gauge Chart — Reuven Engineering Tools](https://reuven.tools/reference/sheet-metal-gauges/) — compares common steel, stainless, galvanized, and aluminum chart conventions; treat as a reference and verify the material specification from the supplier.
- [ASTM B258 — Standard nominal diameters and cross-sectional areas of AWG sizes](https://store.astm.org/standards/b258) — standard reference for solid round AWG electrical conductor dimensions and cross-sectional areas.

## Mechanical drafting and tolerancing

- [ASME: Y14.5-2018 Dimensioning and Tolerancing overview](https://www.asme.org/learning-development/find-course/essentials-y14-5-dimensioning-tolerancing/self-study) — overview of standardized dimensioning, tolerances, datums, form/orientation/location controls, and GD&T. Check the currently applicable standard and customer requirements before using it for formal design control.

## How to use these references

1. Use OpenSCAD's official docs for language syntax and export behavior.
2. Use the specific printer, laser, CNC machine, slicer, and material documentation for process constraints.
3. Use engineering standards for formal drawings, fits, and GD&T.
4. Use test coupons to validate the actual machine/material/geometry combination.
5. Keep a record of what was measured and what worked, and apply the result only to conditions it reasonably represents.

---

## Final principle

**Model the interface, not just the object. Measure the mating parts. State tolerances clearly. Test the risky fit with a small coupon. Verify the exported file. Inspect the physical result. Preserve the revision and process that worked.**

That sequence turns OpenSCAD from a way to draw shapes into a repeatable engineering and fabrication practice.
