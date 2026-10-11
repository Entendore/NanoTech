#!/usr/bin/env python3
"""
NanoLearn v5 — Interactive PySide6 Nanotechnology Learning App
================================================================
v5 additions: Deep nanites/nanobots content (expanded 3 levels), Nanobot Swarm Simulator,
Nanobot Design Lab (5 architectures with live equations), 15 new quiz questions,
10 new flashcards, 10 new glossary terms, 6 new matching pairs. Drug Release Simulator, Surface Area Calculator, Equations Reference,
Quantum Confinement Simulator, Brownian Motion Sim, CNT Chirality Explorer,
15 new quiz questions, 10 new flashcards, 10 new glossary terms.
"""

import sys, os, json, time, random, math
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextBrowser, QLineEdit, QStackedWidget,
    QFrame, QScrollArea, QProgressBar, QButtonGroup, QRadioButton,
    QMessageBox, QSizePolicy, QSlider, QTabWidget, QTextEdit,
    QCheckBox, QGridLayout, QComboBox, QSpinBox, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QSize, Signal
from PySide6.QtGui import (
    QFont, QColor, QPalette, QCursor, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient, QPainterPath, QPolygonF
)

SAVE_DIR = Path.home() / ".nanolearn"
SAVE_DIR.mkdir(exist_ok=True)
NOTES_FILE = SAVE_DIR / "notes.json"
PROGRESS_FILE = SAVE_DIR / "progress.json"
BOOKMARKS_FILE = SAVE_DIR / "bookmarks.json"
ACHIEVEMENTS_FILE = SAVE_DIR / "achievements.json"

# ─── Helpers ────────────────────────────────────────────
def load_json(path, default):
    try:
        if path.exists():
            with open(path) as f: return json.load(f)
    except: pass
    return default

def save_json(path, data):
    try:
        with open(path, "w") as f: json.dump(data, f, indent=2)
    except: pass

STYLESHEET = """
* { font-family: "Segoe UI","Helvetica Neue","Noto Sans",sans-serif; }
QMainWindow { background-color: #0d1117; }
QWidget#central { background-color: #0d1117; }
QFrame#sidebar { background-color: #010409; border-right: 1px solid #21262d; }
QLabel#appTitle { color: #58a6ff; font-size: 18px; font-weight: bold; padding: 16px 14px 2px; letter-spacing: 2px; }
QLabel#appSubtitle { color: #8b949e; font-size: 10px; padding: 0 14px 14px; font-style: italic; }
QPushButton#navBtn { color: #c9d1d9; background: transparent; border: none; border-left: 3px solid transparent; text-align: left; padding: 10px 16px; font-size: 12px; border-radius: 0; }
QPushButton#navBtn:hover { background: #161b22; color: #58a6ff; border-left-color: #58a6ff; }
QPushButton#navBtn:checked { background: #161b22; color: #58a6ff; border-left-color: #58a6ff; font-weight: bold; }
QScrollArea#contentArea { background: #0d1117; border: none; }
QLabel#pageTitle { color: #f0f6fc; font-size: 26px; font-weight: bold; padding-bottom: 6px; border-bottom: 2px solid #21262d; }
QLabel#pageIcon { font-size: 28px; margin-right: 10px; }
QTextBrowser#contentText { color: #c9d1d9; background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 18px 22px; font-size: 14px; line-height: 1.7; }
QTextBrowser#contentText h2 { color: #58a6ff; font-size: 17px; font-weight: bold; margin-top: 18px; margin-bottom: 6px; }
QTextBrowser#contentText h3 { color: #7ee787; font-size: 14px; font-weight: bold; margin-top: 12px; margin-bottom: 4px; }
QTextBrowser#contentText p { margin-bottom: 8px; }
QTextBrowser#contentText li { margin-bottom: 3px; }
QFrame#infoCard { background: #161b22; border: 1px solid #21262d; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; }
QFrame#infoCard:hover { border-color: #58a6ff; }
QLabel#cardTitle { color: #58a6ff; font-size: 14px; font-weight: bold; margin-bottom: 4px; }
QLabel#cardBody { color: #8b949e; font-size: 11px; line-height: 1.5; }
QLabel#cardEmoji { font-size: 24px; margin-right: 8px; }
QRadioButton#quizOption { color: #c9d1d9; background: #161b22; border: 1px solid #21262d; border-radius: 6px; padding: 10px 14px; font-size: 13px; margin-bottom: 6px; spacing: 8px; }
QRadioButton#quizOption:hover { border-color: #58a6ff; background: #1c2333; }
QRadioButton#quizOption::indicator { width: 14px; height: 14px; border-radius: 7px; border: 2px solid #30363d; background: #0d1117; }
QRadioButton#quizOption::indicator:checked { border-color: #58a6ff; background: #58a6ff; }
QPushButton#submitBtn { background: #238636; color: white; border: none; border-radius: 8px; padding: 10px 28px; font-size: 13px; font-weight: bold; }
QPushButton#submitBtn:hover { background: #2ea043; }
QPushButton#submitBtn:disabled { background: #21262d; color: #484f58; }
QPushButton#nextBtn { background: #1f6feb; color: white; border: none; border-radius: 8px; padding: 10px 28px; font-size: 13px; font-weight: bold; }
QPushButton#nextBtn:hover { background: #388bfd; }
QPushButton#nextBtn:disabled { background: #21262d; color: #484f58; }
QPushButton#resetBtn { background: transparent; color: #8b949e; border: 1px solid #30363d; border-radius: 8px; padding: 8px 20px; font-size: 12px; }
QPushButton#resetBtn:hover { border-color: #8b949e; color: #c9d1d9; }
QProgressBar#quizProgress { background: #21262d; border: none; border-radius: 10px; max-height: 6px; text-align: center; color: transparent; }
QProgressBar#quizProgress::chunk { background: #58a6ff; border-radius: 10px; }
QLabel#progressLabel { color: #8b949e; font-size: 11px; }
QLineEdit#searchBox { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 8px 14px; color: #c9d1d9; font-size: 12px; }
QLineEdit#searchBox:focus { border-color: #58a6ff; }
QFrame#scoreFrame { background: #161b22; border: 1px solid #238636; border-radius: 10px; padding: 18px; }
QLabel#scoreLabel { color: #7ee787; font-size: 32px; font-weight: bold; }
QLabel#scoreText { color: #8b949e; font-size: 12px; }
QLabel#glossaryTerm { color: #f0f6fc; font-size: 15px; font-weight: bold; margin-bottom: 3px; }
QLabel#glossaryDef { color: #8b949e; font-size: 12px; line-height: 1.5; }
QScrollBar:vertical { background: #0d1117; width: 7px; border-radius: 4px; }
QScrollBar::handle:vertical { background: #30363d; border-radius: 4px; min-height: 20px; }
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QSlider::groove:horizontal { background: #21262d; height: 8px; border-radius: 4px; }
QSlider::handle:horizontal { background: #58a6ff; width: 20px; height: 20px; margin: -6px 0; border-radius: 10px; border: 2px solid #388bfd; }
QSlider::handle:horizontal:hover { background: #79c0ff; }
QTabWidget::pane { border: 1px solid #21262d; border-radius: 8px; background: #161b22; }
QTabBar::tab { background: #0d1117; color: #8b949e; border: 1px solid #21262d; padding: 8px 18px; margin-right: 2px; border-top-left-radius: 6px; border-top-right-radius: 6px; font-size: 12px; }
QTabBar::tab:selected { background: #161b22; color: #58a6ff; border-bottom-color: #161b22; }
QTabBar::tab:hover { color: #c9d1d9; }
QTextEdit#noteArea { background: #161b22; border: 1px solid #21262d; border-radius: 8px; color: #c9d1d9; font-size: 13px; padding: 10px; }
QTextEdit#noteArea:focus { border-color: #58a6ff; }
QGroupBox#grpBox { color: #c9d1d9; border: 1px solid #21262d; border-radius: 8px; margin-top: 12px; padding-top: 16px; font-size: 13px; font-weight: bold; }
QGroupBox#grpBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #58a6ff; }
QComboBox#diffCombo { background: #161b22; border: 1px solid #21262d; border-radius: 6px; color: #c9d1d9; padding: 6px 12px; font-size: 12px; }
QComboBox#diffCombo::drop-down { border: none; }
QComboBox QAbstractItemView { background: #161b22; color: #c9d1d9; selection-background-color: #1f6feb; }

QLabel#badgeLabel { color: #f0f6fc; font-size: 11px; background: #21262d; border-radius: 10px; padding: 4px 10px; border: 1px solid #30363d; }
QLabel#badgeLabel.earned { background: #1c2333; border: 1px solid #a371f7; color: #d2a8ff; }
QLabel#bookmarkBadge { color: #ffa657; font-size: 18px; }
QFrame#bookmarkCard { background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 10px 14px; }
QLabel#confidenceLabel { color: #f0f6fc; font-size: 13px; font-weight: bold; }
QLabel#ratingStar { font-size: 22px; }
"""

SCALE_DATA = [
    (0.1, "Hydrogen Atom", "~0.1 nm", "A single hydrogen atom — the smallest and most abundant element in the universe. At this scale, quantum mechanics dominates entirely. Electrons exist as probability clouds, not particles orbiting a nucleus.", "#a371f7"),
    (0.34, "Carbon-Carbon Bond", "0.154 nm", "The covalent bond between two carbon atoms is about 0.154 nm. This is the fundamental building block of all organic chemistry and life itself.", "#79c0ff"),
    (2, "DNA Double Helix", "~2 nm wide", "DNA, the molecule of life, has a diameter of about 2 nanometers. If uncoiled, the DNA from a single human cell would stretch about 2 meters long.", "#7ee787"),
    (5, "Smallest CNT", "1–4 nm diameter", "Single-walled carbon nanotubes can be as thin as 1 nm. They are essentially rolled-up graphene sheets — cylinders of carbon just one atom thick.", "#58a6ff"),
    (10, "Cell Membrane Thickness", "~5–10 nm", "The lipid bilayer that forms every cell membrane is about 5–10 nm thick. This incredibly thin barrier controls everything entering or leaving the cell.", "#d2a8ff"),
    (20, "Antibody Protein", "~12 nm", "Y-shaped antibody proteins are about 12 nm tall. They are produced by your immune system to identify and neutralize pathogens like viruses and bacteria.", "#f78166"),
    (50, "Quantum Dot", "2–10 nm", "Quantum dots are semiconductor nanocrystals whose optical properties change with size. A 2 nm CdSe dot glows blue, while a 6 nm one glows red — quantum confinement in action!", "#f778ba"),
    (100, "Virus (HIV)", "~120 nm", "HIV is about 120 nm in diameter. Most viruses range from 20–300 nm, making them perfect examples of biological nanomachines that hijack cells.", "#ff7b72"),
    (400, "Wavelength of Light", "400–700 nm", "Visible light ranges from ~400 nm (violet) to ~700 nm (red). Objects smaller than the wavelength of light cannot be seen with traditional optical microscopes.", "#ffa657"),
    (1000, "Bacterium (E. coli)", "~1000 nm (1 µm)", "E. coli bacteria are about 1 micrometer (1000 nm) long. They are among the smallest living organisms visible under a light microscope.", "#d29922"),
    (2500, "Mitochondrion", "1–10 µm", "Mitochondria, the powerhouses of cells, are 1–10 micrometers long. They generate ATP — the energy currency that powers all cellular processes.", "#e3b341"),
    (7000, "Red Blood Cell", "~7 µm", "Human red blood cells are about 7 µm in diameter. They must squeeze through capillaries only 3–5 µm wide, deforming their characteristic biconcave shape.", "#da3633"),
    (10000, "White Blood Cell", "10–15 µm", "White blood cells (leukocytes) are 10–15 µm. They patrol your bloodstream, seeking and destroying pathogens using nanoscale receptor molecules.", "#bc8cff"),
    (80000, "Human Hair", "~80 µm (80,000 nm)", "A typical human hair is about 80 micrometers (80,000 nm) in diameter. That means roughly 80,000 atoms could line up across the width of a single hair.", "#8b949e"),
]

GOLD_NP_DATA = [
    (5,  "#520527", "Deep Purple",   "5 nm gold nanoparticles absorb green light strongly, reflecting deep purple. At this size, quantum confinement is extreme — electron energy levels are widely spaced."),
    (10, "#8B1A4A", "Purple-Red",    "At 10 nm, the surface plasmon resonance shifts. The collective oscillation of conduction electrons produces this rich purple-red color."),
    (20, "#CC2936", "Red",            "20 nm is the classic 'red gold' — the most commonly seen gold nanoparticle color. The SPR peak is around 520 nm, absorbing green and reflecting red."),
    (40, "#E85D04", "Orange-Red",     "As particles grow to 40 nm, the SPR peak broadens and red-shifts. More light wavelengths are absorbed, shifting the perceived color toward orange."),
    (60, "#F48C06", "Orange",         "At 60 nm, the particles begin to scatter light significantly (Mie scattering). The balance between absorption and scattering shifts the color further."),
    (80, "#FAA307", "Yellow-Orange",  "80 nm gold nanoparticles exhibit strong forward scattering. The color is now predominantly yellow-orange due to the broadened SPR peak."),
    (100,"#FFBA08", "Gold/Yellow",    "At 100 nm, gold nanoparticles start to look more like bulk gold. The SPR peak has shifted far into the red, reflecting yellow-gold light."),
]

INTRO_B = """<h2>What is Nanotechnology?</h2>
<p>Nanotechnology is the science of working with materials at the nanoscale — between 1 and 100 nanometers. One nanometer is one billionth of a meter. To picture this, think of a human hair: it's about 80,000 nanometers wide. A sheet of paper is about 100,000 nanometers thick.</p>
<p>At this tiny scale, ordinary materials start behaving in extraordinary ways. Gold, which is always shiny and yellow in bulk, can appear red or purple as nanoparticles. Materials that are normally insulators can become conductors, and opaque substances can become transparent.</p>
<h2>Why Does Size Matter?</h2>
<p>When things get very small, two important things happen. First, the surface area becomes huge compared to the volume — imagine cutting a cube into smaller and smaller pieces, the total surface area grows enormously. This means more of the material is exposed for chemical reactions.</p>
<p>Second, quantum mechanics takes over. The rules of classical physics (like those governing a bouncing ball) give way to quantum rules (like electrons existing as probability clouds). This creates the unique properties that make nanotechnology so exciting.</p>
<h2>Nanotechnology in Your Daily Life</h2>
<p>You already use nanotechnology every day! The sunscreen that protects your skin uses zinc oxide or titanium dioxide nanoparticles. The anti-stain coating on your clothing relies on nano-sized fibers. Your smartphone's processor has transistors only a few nanometers wide. Even some car tires use nanoparticles to improve durability.</p>"""

INTRO_I = """<h2>Top-Down vs. Bottom-Up Approaches</h2>
<h3>Top-Down Fabrication</h3>
<p>Think of sculpting: you start with a large block of marble and chip away to create a statue. In nanotechnology, top-down means starting with bulk material and removing parts until you get nanostructures. The main tool here is <b>lithography</b> — using light to etch patterns onto materials.</p>
<p>Today's most advanced chips use <b>EUV (Extreme Ultraviolet) lithography</b> at 13.5 nm wavelength to create transistors as small as 3 nm. However, this approach faces fundamental limits: you can't carve features smaller than the wavelength of light you're using without increasingly complex tricks.</p>
<h3>Bottom-Up Fabrication</h3>
<p>Think of LEGO: you build structures brick by brick. Bottom-up nanotechnology builds structures atom by atom or molecule by molecule. Nature does this brilliantly — proteins self-assemble from amino acids, and DNA coils into precise double helices.</p>
<p>Key techniques include <b>self-assembly</b> (molecules spontaneously organizing), <b>chemical vapor deposition</b> (growing materials from gas-phase precursors), and <b>molecular beam epitaxy</b> (spraying individual atoms in a vacuum). The bottom-up approach can theoretically create perfect structures, but controlling the process remains extremely challenging.</p>
<h2>Quantum Effects at the Nanoscale</h2>
<h3>Quantum Confinement</h3>
<p>When a material's size becomes comparable to the de Broglie wavelength of its electrons (typically 1-10 nm for semiconductors), the continuous energy bands of bulk material split into discrete levels — much like the energy levels in an atom. This is quantum confinement.</p>
<p>The practical consequence is dramatic: a semiconductor's bandgap (and thus its color, conductivity, and reactivity) can be precisely tuned just by changing its size. A 2 nm cadmium selenide quantum dot emits blue light; a 6 nm one emits red light — same material, different size, different color.</p>
<h3>Surface Plasmon Resonance</h3>
<p>In metallic nanoparticles (especially gold and silver), incident light causes the free electrons on the surface to oscillate collectively — this is surface plasmon resonance. The resonance frequency depends on the particle's size, shape, and surrounding medium. For gold nanospheres in water, the SPR peak shifts from ~520 nm (red, 20 nm particles) to ~580 nm (orange-yellow, 100 nm particles).</p>"""

INTRO_A = """<h2>Advanced Quantum Phenomena</h2>
<h3>Casimir Effect</h3>
<p>In the quantum vacuum, even "empty" space has zero-point energy fluctuations. When two conducting plates are placed within nanometers of each other, the vacuum fluctuations between them are restricted, creating a net attractive force — the Casimir effect. This force becomes significant at distances below 100 nm and must be accounted for in MEMS/NEMS design. It has been proposed as an energy source for nanoscale actuators, though practical applications remain theoretical.</p>
<h3>Kondo Effect in Nanostructures</h3>
<p>When a magnetic impurity is embedded in a metallic nanostructure, conduction electrons form a correlated many-body state that screens the impurity's spin. This leads to a resistance minimum at low temperatures (the Kondo temperature). In nanoscale quantum dots, the Kondo effect can be tuned by gate voltages, making it a powerful probe of strongly correlated electron physics.</p>
<h3>Coulomb Blockade</h3>
<p>In nanostructures smaller than ~10 nm, adding a single electron requires energy e²/2C (where C is the capacitance). At low temperatures, this energy barrier prevents electron flow — the Coulomb blockade. Single-electron transistors exploit this effect, switching on and off with the addition or removal of one electron.</p>
<h2>Computational Nanotechnology</h2>
<p>Modern nanotechnology research relies heavily on computational methods. <b>Density Functional Theory (DFT)</b> calculates electronic structure from first principles, predicting material properties before synthesis. <b>Molecular Dynamics (MD)</b> simulations track the motion of thousands of atoms over nanosecond timescales. <b>Machine learning</b> models like DeepMind's GNoME have predicted 2.2 million new crystal structures, accelerating materials discovery by centuries.</p>"""

NANITES_B = """<h2>What Are Nanites and Nanobots?</h2>
<p>Nanites (also called nanorobots or nanobots) are machines designed to operate at the nanoscale, typically between 1 nanometer and 10 micrometers in size. The term "nanite" gained popularity through science fiction, but real nanoscale machines already exist in nature and in laboratories around the world.</p>
<p>Think of a nanite as a robot so small that thousands of them could fit on the period at the end of this sentence. Unlike a factory robot, a nanite works in a world dominated by Brownian motion, viscosity, and quantum effects — a world where water feels like thick syrup and inertia is irrelevant.</p>

<h2>Anatomy of a Nanobot</h2>
<p>Every theoretical nanobot needs several key components to function, whether it is built from DNA, proteins, or synthetic materials:</p>
<h3>1. Power Source</h3>
<p>A nanobot needs energy to move, sense, and act. Biological nanomachines use ATP (adenosine triphosphate) — the universal energy currency of life. A single ATP molecule releases about 5 x 10<sup>-20</sup> joules when hydrolyzed. For synthetic nanobots, proposed power sources include glucose oxidation (like cells do), external magnetic fields, enzymatic fuel cells, and even light-activated molecular switches. The challenge is enormous: at the nanoscale, energy must be harvested and used within a volume smaller than a bacterium.</p>
<h3>2. Sensors</h3>
<p>A nanobot must perceive its environment to be useful. Nature provides elegant solutions: receptors on cell surfaces can detect single molecules with incredible specificity. Antibodies can identify particular proteins with dissociation constants K<sub>d</sub> as low as 10<sup>-12</sup> M. Synthetic nanobots could use DNA aptamers (selected to bind specific targets), quantum dots (whose fluorescence changes with local chemistry), or molecular probes that change shape when they encounter a target molecule. The fundamental limit of sensing is set by thermodynamic noise — the same Brownian motion that jiggles particles also creates a noise floor.</p>
<h3>3. Actuators / Manipulators</h3>
<p>What does a nanobot "do" with its environment? Biological nanomachines use shape-changing proteins: kinesin walks along microtubules, ATP synthase rotates like a turbine, and ribosomes assemble proteins from mRNA instructions. DNA nanobots use strand displacement — one DNA strand invades and replaces another, changing the structure. Synthetic approaches include rotaxane molecular switches, light-activated azobenzene hinges, and catalytic nanoparticles that break down specific molecules. The key insight is that at the nanoscale, chemical binding forces dominate over mechanical forces, so the most effective "hands" are chemical rather than mechanical.</p>
<h3>4. Communication</h3>
<p>A single nanobot is limited. But a swarm of millions could perform complex tasks — if they can communicate. In nature, bacteria communicate via quorum sensing: they release small signaling molecules that accumulate until a threshold concentration triggers a coordinated response. Synthetic nanobots could use chemical signaling, acoustic pulses, or even light emission. The communication range is limited by diffusion: a chemical signal travels roughly sqrt(2Dt) in time t, where D is the diffusion coefficient.</p>

<h2>Real Nanomachines That Exist Today</h2>
<h3>DNA Nanobots (DNA Origami Walkers)</h3>
<p>Scientists have built walking robots from DNA strands. These "DNA walkers" move along DNA tracks by sequentially binding and releasing footholds — each step powered by strand displacement. In 2018, researchers at Arizona State University created DNA nanobots that targeted tumor blood vessels in mice, delivering a blood-clotting drug that starved the tumors. This was one of the first demonstrations of therapeutic nanorobots in a living animal.</p>
<h3>Molecular Motors</h3>
<p>Nature invented nanomachines billions of years ago. Your body contains trillions of them: ATP synthase in mitochondria spins at up to 10,000 RPM, producing the ATP that powers every cell. Kinesin proteins "walk" along microtubule tracks carrying cargo across the cell. Bacterial flagella rotate at hundreds of RPM, propelling bacteria through fluid. The 2016 Nobel Prize in Chemistry was awarded to Jean-Pierre Sauvage, Fraser Stoddart, and Bernard Feringa for designing and synthesizing artificial molecular machines — including a molecular car with four "wheels."</p>
<h3>Microswimmers and Nanopropellers</h3>
<p>Researchers have built helical magnetic nanopropellers that spin through bodily fluids when guided by external rotating magnetic fields. These microswimmers are typically 200 nm to 3 micrometers long and can be steered in three dimensions. At low Reynolds number (Re << 1, the regime all nanobots operate in), reciprocal motion gets you nowhere — you must move asymmetrically (like a corkscrew or a flexible tail) to make progress through viscous fluid. This is called the "scallop theorem": a scallop that opens and closes symmetrically cannot swim at low Re.</p>
<h3>Xenobots — Living Machines</h3>
<p>In 2020, researchers at Tufts and Vermont created xenobots — the world's first living robots, designed by a supercomputer algorithm and built from frog (Xenopus) skin and heart cells. These ~1 mm machines can walk, swim, push payloads, and even self-replicate by gathering loose cells. While larger than true nanites, xenobots demonstrate that biological materials can be organized into functional machines with capabilities beyond what synthetic materials currently achieve.</p>

<h2>Nanobots vs. Nanoparticles: What Is the Difference?</h2>
<p>A crucial distinction for understanding nanites: a nanoparticle is a passive particle with useful properties (a gold nanoparticle absorbs light, a lipid nanoparticle carries drugs). A nanobot is an <b>active</b> machine — it senses, decides, and acts. Most "nanomedicine" today uses passive nanoparticles. True nanobots that can make autonomous decisions and perform complex tasks remain largely experimental. The field is gradually moving from passive to active nanosystems.</p>"""

NANITES_I = """<h2>The Physics of Nanobot Motion</h2>
<h3>Low Reynolds Number Hydrodynamics</h3>
<p>At the nanoscale, the Reynolds number Re = rho v L / eta is extraordinarily small — typically 10<sup>-5</sup> to 10<sup>-2</sup> for a nanobot in water. This means viscous forces completely dominate over inertial forces. A nanobot that stops propelling itself stops moving within microseconds. There is no coasting, no momentum, no inertia-based strategies. Everything must be done through continuous force application against the surrounding fluid.</p>
<p>The drag force on a spherical nanobot of radius r moving at velocity v through a fluid of viscosity eta is given by Stokes' law:</p>
<h3>Stokes' Drag: F<sub>drag</sub> = 6 pi eta r v</h3>
<p>For a nanobot with r = 500 nm moving at v = 10 micrometers/s in water (eta = 8.9 x 10<sup>-4</sup> Pa s): F<sub>drag</sub> = 6 x pi x 8.9 x 10<sup>-4</sup> x 5 x 10<sup>-7</sup> x 10<sup>-5</sup> = 8.4 x 10<sup>-14</sup> N. This is roughly the force exerted by a single kinesin motor protein. The power required is P = F v = 8.4 x 10<sup>-19</sup> W — about 1 ATP hydrolysis per second.</p>

<h3>Active Propulsion vs. Brownian Motion</h3>
<p>A nanobot at temperature T experiences random Brownian displacements with diffusion coefficient D = k<sub>B</sub>T / (6 pi eta r). For a 100 nm particle at 310 K (body temperature): D = 1.38 x 10<sup>-23</sup> x 310 / (6 x pi x 8.9 x 10<sup>-4</sup> x 10<sup>-7</sup>) = 2.55 x 10<sup>-12</sup> m<sup>2</sup>/s. The mean displacement in one second is sqrt(2D x 1) = 2.26 micrometers — this is how far random thermal motion carries the particle. An actively propelled nanobot moving at 10 micrometers/s travels further in one second than Brownian motion carries it. The Peclet number Pe = vL/D compares these: Pe >> 1 means propulsion dominates, Pe << 1 means diffusion dominates.</p>
<h3>Peclet Number: Pe = v L / D</h3>
<p>For our example: Pe = 10<sup>-5</sup> x 10<sup>-6</sup> / 2.55 x 10<sup>-12</sup> = 3.9. Since Pe is close to 1, both active propulsion and Brownian motion matter significantly. This is why nanobot navigation is so challenging — you are fighting against random thermal noise at every moment.</p>

<h2>Nanobot Navigation and Control</h2>
<h3>Magnetic Steering</h3>
<p>The most practical method for controlling nanobots in the body is external magnetic fields. A magnetic nanoparticle with magnetic moment m in a field gradient experiences a force F = m x gradient(B). Rotating magnetic fields can cause helical nanobots to spin and propel themselves like corkscrews. The advantage is that magnetic fields penetrate tissue deeply without causing harm. Current magnetic nanobot systems achieve steering precision of about 100 micrometers — sufficient for targeting tumors but not individual cells.</p>

<h3>Chemotaxis — Following Chemical Gradients</h3>
<p>Bacteria perform chemotaxis by comparing chemical concentrations over time and biasing their random walk toward higher concentrations. For a nanobot, the gradient detection limit is set by receptor noise: the minimum detectable concentration difference over a distance L is approximately delta c ~ 1 / (N x a), where N is the number of receptor binding events per second and a is the effective sensing area. Bacteria can detect gradients as shallow as 1% across their body length — synthetic nanobots are not yet this sensitive.</p>

<h2>Nanobot Sensing Equations</h2>
<h3>Antibody-Antigen Binding Equilibrium</h3>
<p>The key equation governing molecular recognition on a nanobot surface is the binding equilibrium: K<sub>d</sub> = [A][B] / [AB], where K<sub>d</sub> is the dissociation constant, [A] is the free antibody concentration, [B] is the free antigen concentration, and [AB] is the bound complex. A lower K<sub>d</sub> means tighter binding. Strong antibodies have K<sub>d</sub> ~ 10<sup>-9</sup> to 10<sup>-12</sup> M. At equilibrium, the fraction of occupied receptors is: theta = [B] / (K<sub>d</sub> + [B]). This means a nanobot sensor is most sensitive when the target concentration is near K<sub>d</sub>.</p>
<h3>Receptor-Ligand Kinetics</h3>
<p>The on-rate k<sub>on</sub> and off-rate k<sub>off</sub> determine how quickly a nanobot sensor responds: K<sub>d</sub> = k<sub>off</sub> / k<sub>on</sub>. Typical values: k<sub>on</sub> ~ 10<sup>5</sup> to 10<sup>8</sup> M<sup>-1</sup>s<sup>-1</sup>, k<sub>off</sub> ~ 10<sup>-3</sup> to 10<sup>-6</sup> s<sup>-1</sup>. The response time is roughly 1/k<sub>off</sub> — from seconds to minutes. A nanobot must linger near its target long enough for binding to reach equilibrium.</p>

<h2>Swarm Intelligence for Nanobots</h2>
<p>Individual nanobots are limited in capability, but a swarm of millions could perform tasks impossible for any single unit. Swarm algorithms inspired by nature include:</p>
<ul>
<li><b>Reynolds Flocking</b>: Three simple rules — separation (avoid neighbors), alignment (match neighbor velocity), cohesion (move toward group center) — create realistic swarm behavior.</li>
<li><b>Ant Colony Optimization</b>: Nanobots deposit chemical trails that attract others, naturally finding optimal paths through complex environments.</li>
<li><b>Gradient Climbing</b>: Each nanobot measures a local chemical gradient and moves uphill, collectively homing in on a tumor or infection site.</li>
<li><b>Quorum Sensing</b>: Like bacteria, nanobots release signaling molecules. When the local concentration exceeds a threshold, the swarm switches behavior — for example, releasing a drug only when enough nanobots have accumulated at the target.</li>
</ul>
<p>The communication speed is limited by diffusion. A chemical signal diffuses a distance d in time t ~ d<sup>2</sup> / (2D). For D = 10<sup>-9</sup> m<sup>2</sup>/s, a signal travels 100 micrometers in about 5 seconds. This sets the fundamental speed limit for chemical communication between nanobots.</p>"""

NANITES_A = """<h2>Advanced Nanite Architectures</h2>
<h3>DNA Strand Displacement Circuits</h3>
<p>DNA nanobots compute using strand displacement reactions: an input DNA strand invades a double-stranded complex, displacing the incumbent strand and triggering a cascade. This implements Boolean logic gates (AND, OR, NOT) entirely in DNA chemistry. Researchers have built DNA circuits with over 100 gates that can perform complex medical decision-making — for example, releasing a drug cargo only when two or more cancer biomarkers are simultaneously detected above threshold concentrations. The key advantage is that the computation happens in the same biochemical environment as the sensing and actuation, eliminating the need for external electronics.</p>
<p>The kinetics of strand displacement follow a bimolecular rate law: rate = k<sub>sd</sub> [input] [complex], where k<sub>sd</sub> ~ 10<sup>5</sup> to 10<sup>7</sup> M<sup>-1</sup>s<sup>-1</sup> depending on the toehold length. Longer toehold strands (more unpaired bases) react faster because they provide more initial binding sites. This tunable reaction rate allows engineers to set timing delays, create oscillatory circuits, and build sequential logic.</p>

<h3>Biological-Synthetic Hybrid Nanobots</h3>
<p>The most promising near-term path to functional nanobots involves engineering living cells rather than building synthetic machines from scratch. Synthetic biology techniques can program bacteria to: (1) produce therapeutic molecules on demand inside tumors, (2) sense and respond to specific biochemical signals with genetic circuits, (3) form biofilms with engineered mechanical properties, and (4) communicate via engineered quorum sensing systems. These "living medicines" bypass the manufacturing challenge of building nanoscale actuators and power sources by leveraging billions of years of evolutionary optimization.</p>
<p>The design framework uses transcriptional regulation: promoter R -> gene expression rate = k<sub>max</sub> x [activator]<sup>n</sup> / (K<sub>d</sub><sup>n</sup> + [activator]<sup>n</sup>), where n is the Hill coefficient (cooperativity). With n = 2-4, genetic circuits can achieve sharp switching behavior — essentially digital logic gates built from proteins and DNA.</p>

<h3>Theoretical Molecular Assemblers</h3>
<p>Eric Drexler's original 1986 vision in "Engines of Creation" proposed molecular assemblers — nanomachines that position reactive molecules to build structures atom by atom. While this remains theoretical, DNA-guided assembly has demonstrated proof of concept: DNA strands can template the placement of gold nanoparticles, carbon nanotubes, and proteins at specific positions with nanometer precision. The fundamental challenge is scaling from static 2D arrangements to programmable 3D manufacturing. The Stewart platform, a parallel kinematic mechanism used in macroscopic robotics, has been proposed as a nanoscale manipulator architecture with six degrees of freedom.</p>

<h2>Self-Replication and the Reproduction Equation</h2>
<p>A key theoretical capability of advanced nanobots is self-replication. If each nanobot can produce a copy of itself in time T<sub>rep</sub>, then the population grows as: N(t) = N<sub>0</sub> x 2<sup>t/T_rep</sup>. Starting from a single nanobot with T<sub>rep</sub> = 100 seconds, you would have 10<sup>12</sup> nanobots in just 40 minutes. This exponential growth is both the promise (manufacturing) and the peril (grey goo scenario) of self-replicating nanomachines. The fundamental limit is set by the time needed to synthesize all component molecules, position them correctly, and verify the structure.</p>
<p>In 2021, xenobots demonstrated a primitive form of self-replication: they could gather loose frog cells in their environment and assemble them into new xenobots — a kinematic self-replication process not seen in any known organism. This was limited to one generation, but it proved that biological machines can self-replicate without genetic material being directly copied.</p>

<h2>Nanobot Biocompatibility and Clearance</h2>
<p>For medical nanobots, biocompatibility is essential. The body has evolved sophisticated defenses: the reticuloendothelial system (RES) identifies and removes foreign nanoparticles, opsonin proteins tag nanoparticles for destruction, and the kidneys filter particles below ~6 nm. Engineering nanobots to evade these defenses while remaining safe is a central challenge. Strategies include PEGylation (coating with polyethylene glycol to resist protein adsorption), biomimetic coatings (wrapping in cell membranes to appear "self"), and size optimization (100-200 nm avoids both renal clearance and rapid RES uptake).</p>
<p>The circulation half-life of a nanoparticle follows: t<sub>1/2</sub> ~ V<sub>blood</sub> / (CL<sub>hepatic</sub> + CL<sub>renal</sub> + CL<sub>other</sub>), where CL terms are clearance rates. PEGylated nanoparticles can achieve half-lives of 15-20 hours in humans, compared to minutes for uncoated particles. This gives nanobots a therapeutic window to reach their target before being cleared.</p>

<h2>Computational Design of Nanobots</h2>
<p>Modern nanobot research increasingly relies on computational tools. Molecular dynamics (MD) simulations track the motion of thousands of atoms over nanosecond timescales, revealing how nanobot components move and interact. Rosetta and similar protein design software can engineer custom molecular sensors and actuators. Machine learning models predict how nanoparticle surface chemistry affects biological interactions, accelerating the design of stealthy, targeted nanobots. The integration of AI-driven design with automated DNA synthesis is creating a rapid prototyping cycle: design on computer, synthesize DNA, test in vitro, feed results back to AI.</p>"""

APPS_B = """<h2>Nanotechnology in Medicine</h2>
<p>Nanomedicine is already saving lives. Nanoparticle drug carriers can deliver chemotherapy directly to tumors, reducing side effects. The first nanomedicine, Doxil, wraps chemo drugs in fatty nanoparticles. Gold nanoparticles are being tested to heat and destroy cancer cells when zapped with infrared light.</p>
<h2>Nanotechnology in Electronics</h2>
<p>Your smartphone exists because of nanotechnology. The chips inside have billions of transistors, each only 3-5 nanometers wide. Engineers use extreme ultraviolet light to print these microscopic circuits onto silicon wafers.</p>
<h2>Nanotechnology in Energy</h2>
<p>Solar panels with nanostructured coatings capture more sunlight. New batteries with nanoparticle electrodes store much more energy, which could make electric cars go 5x farther on a single charge. Nanotech filters can purify water by removing contaminants at the molecular level.</p>
<h2>Nanotechnology in Everyday Products</h2>
<p>Look around: anti-fog coatings on glasses, wrinkle-resistant fabrics, scratch-resistant car paint, stronger tennis rackets — all use nanotechnology. Even some food products use nanoparticles to improve nutrition.</p>"""

APPS_I = """<h2>Advanced Medical Applications</h2>
<h3>Quantum Dot Diagnostics</h3>
<p>Quantum dots can label specific proteins with extraordinary sensitivity, detecting cancer biomarkers years before symptoms appear. Unlike organic dyes that bleach quickly, quantum dots are stable for months and can be tuned to emit any color by changing their size.</p>
<h3>Lab-on-a-Chip</h3>
<p>Integrating nanofluidic channels with biosensors creates devices that perform complete blood analyses from a single drop. These microfluidic/nanofluidic chips can sequence DNA, detect pathogens, and measure drug levels — all in a device the size of a credit card.</p>
<h2>Advanced Electronics</h2>
<h3>Neuromorphic Computing</h3>
<p>Memristive nanodevices mimic brain synapses, enabling chips that process information 1000x more efficiently than conventional processors. IBM, Intel, and HP have built prototype neuromorphic chips with millions of artificial synapses.</p>
<h3>Carbon Nanotube Electronics</h3>
<p>CNTs can be metallic or semiconducting depending on their structure. Semiconducting CNTs offer superior electron mobility compared to silicon. Several companies have demonstrated CNT-based microprocessors, though manufacturing challenges remain.</p>
<h2>Environmental Applications</h2>
<p>Titanium dioxide nanoparticles catalyze pollutant breakdown under UV light. Nanofiltration membranes with precisely sized pores can desalinate water and remove pharmaceutical residues. Carbon nanomaterials are being developed for CO₂ capture and hydrogen storage.</p>"""

APPS_A = """<h2>Cutting-Edge Applications</h2>
<h3>CRISPR + Nanoparticle Delivery</h3>
<p>While CRISPR can edit genes, getting CRISPR components into the right cells is the bottleneck. Lipid nanoparticle delivery systems (proven by COVID vaccines) are being adapted to deliver CRISPR to specific organs. This combination could cure genetic diseases like sickle cell anemia, cystic fibrosis, and Huntington's disease.</p>
<h3>Brain-Computer Interfaces</h3>
<p>Nanoscale electrodes could enable high-bandwidth brain-computer interfaces. Current BCIs use 20 µm electrodes; nanoscale probes could provide 1000x more neural connections. Graphene and carbon nanotube electrodes show superior biocompatibility and signal quality compared to traditional metal electrodes.</p>
<h3>Quantum Nanosensors</h3>
<p>NV centers in diamond nanoparticles enable room-temperature quantum sensing at nanometer resolution. Potential applications include: MRI at the cellular level (detecting individual protein molecules), navigation without GPS (measuring Earth's magnetic field at the atomic level), and detecting single photons for quantum communication.</p>
<h3>Nano-Enhanced Metamaterials</h3>
<p>Metamaterials with nanoscale features can manipulate light and sound in ways impossible with natural materials. Applications include: invisibility cloaks (bending light around objects), perfect lenses (breaking the diffraction limit), and vibration damping at specific frequencies for noise cancellation.</p>"""

HISTORY_B = """<h2>The Key Moments</h2>
<p><b>1959</b> — Physicist Richard Feynman gives his famous talk "There's Plenty of Room at the Bottom," envisioning a future where we manipulate individual atoms.</p>
<p><b>1974</b> — Norio Taniguchi coins the term "nanotechnology."</p>
<p><b>1981</b> — The Scanning Tunneling Microscope is invented, letting scientists see individual atoms for the first time.</p>
<p><b>1985</b> — Buckminsterfullerene (C₆₀, "buckyballs") are discovered — a whole new form of carbon.</p>
<p><b>1991</b> — Sumio Iijima discovers carbon nanotubes at NEC in Japan.</p>
<p><b>2000</b> — The US National Nanotechnology Initiative launches with $500M funding.</p>
<p><b>2004</b> — Graphene is isolated using sticky tape by Geim and Novoselov (Nobel Prize 2010).</p>
<p><b>2020</b> — mRNA COVID vaccines demonstrate lipid nanoparticle delivery to the world.</p>"""

HISTORY_I = """<h2>The Pioneers in Detail</h2>
<h3>Richard Feynman (1959)</h3>
<p>Feynman's lecture at Caltech described manipulating atoms directly, storing all books in a tiny cube, and building microscopic machines. He offered $1,000 prizes for the first person to build a tiny electric motor and for writing a book page at 1/25,000 scale. Both prizes were claimed within decades.</p>
<h3>K. Eric Drexler (1981-1986)</h3>
<p>Drexler's 1986 book "Engines of Creation" brought nanotechnology to the public. He proposed molecular assemblers — nanomachines building objects atom by atom — and warned about "grey goo." While controversial, his work catalyzed serious global investment in nano research.</p>
<h2>Materials Revolution Timeline</h2>
<p><b>1985</b> — Kroto, Curl, Smalley discover C₆₀ (Nobel 1996). This opened the field of fullerene chemistry.</p>
<p><b>1991</b> — Iijima's carbon nanotube discovery launched the most-studied nanomaterial in history.</p>
<p><b>2004</b> — Graphene isolation was remarkably simple (Scotch tape!) but transformative. A single-atom-thick material with extraordinary properties.</p>
<p><b>2012</b> — Borophene (2D boron) and phosphorene expand the 2D materials family beyond carbon.</p>
<p><b>2023</b> — IBM demonstrates 2 nm chip technology with 50 billion transistors.</p>"""

HISTORY_A = """<h2>Deep Dive: The Science Behind the Discoveries</h2>
<h3>Why the STM Was Revolutionary</h3>
<p>Binnig and Rohrer's STM works by bringing a needle tip within 1 nm of a surface. A voltage applied between tip and surface allows electrons to "tunnel" across the gap. The tunneling current is exquisitely sensitive to distance (changing 10x per 0.1 nm), enabling atomic-resolution imaging. The STM can also move individual atoms — Don Eigler famously wrote "IBM" with 35 xenon atoms in 1989.</p>
<h3>The Graphene Discovery Story</h3>
<p>Geim and Novoselov's technique was deceptively simple: press adhesive tape against graphite, peel it off, and repeat until you get a single layer. The key insight was that single-layer graphene was stable at room temperature — contradicting theoretical predictions that 2D materials would be thermodynamically unstable. Graphene's linear dispersion relation (E = hv|k|) means electrons behave as massless Dirac fermions, moving at ~10⁶ m/s.</p>
<h3>From Buckyballs to Nanotubes to Graphene</h3>
<p>The discovery of C₆₀ in 1985 showed that carbon could form curved structures beyond graphite and diamond. Iijima's observation of CNTs in 1991 (inside an arc-discharge fullerene reactor) extended this to cylinders. Graphene in 2004 completed the family — the flat parent of all sp² carbon nanomaterials. Together, these discoveries created an entirely new field of carbon nanoscience.</p>"""

SAFETY_B = """<h2>Why Nanotechnology Safety Matters</h2>
<p>The same properties that make nanomaterials useful — tiny size, high reactivity, ability to enter cells — also make them potentially hazardous if not handled properly. Understanding these risks is essential for responsible development.</p>
<h2>Health Concerns</h2>
<p><b>Inhalation:</b> Airborne nanoparticles can be inhaled deep into lungs. Carbon nanotubes resemble asbestos fibers in shape, raising concerns about lung disease.</p>
<p><b>Skin contact:</b> Some nanoparticles in cosmetics (zinc oxide, titanium dioxide in sunscreen) are considered safe on healthy skin, but long-term studies continue.</p>
<p><b>Body accumulation:</b> Nanoparticles can cross the blood-brain barrier and accumulate in organs like the liver and kidneys.</p>
<h2>Environmental Impact</h2>
<p>Silver nanoparticles (used for antimicrobial properties) can be toxic to aquatic life even at very low concentrations. Nanoparticles from consumer products wash into waterways, and their long-term environmental effects are still being studied.</p>"""

SAFETY_I = """<h2>Detailed Risk Analysis</h2>
<h3>Nanoparticle Toxicology</h3>
<p>The high surface-area-to-volume ratio of nanoparticles means they carry more reactive sites per unit mass than bulk materials. This reactivity, while useful for catalysis, also means nanoparticles can: generate reactive oxygen species (ROS) that damage cells, interact with DNA and proteins in unpredictable ways, and bypass the body's normal defense mechanisms designed for larger particles.</p>
<h3>Environmental Fate and Transport</h3>
<p>Fullerenes (C₆₀) cause oxidative stress in fish brains. Titanium dioxide nanoparticles from sunscreens accumulate in sediments. Cerium oxide from diesel fuel additives persists in soils for years. Standard environmental testing protocols were not designed for nanomaterials, creating regulatory gaps.</p>
<h2>Regulatory Landscape</h2>
<p>The EU requires special labeling for nanomaterials under REACH. The FDA has issued guidance (not binding rules) for nanomaterials in food, drugs, and cosmetics. ISO Technical Committee 229 has developed 100+ standards for nanotech terminology, measurement, and safety. Comprehensive nano-specific legislation remains absent in most countries.</p>"""

SAFETY_A = """<h2>Advanced Safety Topics</h2>
<h3>Omics-Based Risk Assessment</h3>
<p>Traditional toxicology measures LD50 and organ weights. Modern nanotoxicology uses transcriptomics (gene expression), proteomics (protein levels), and metabolomics (metabolic profiles) to understand how nanoparticles perturb biological systems at the molecular level. This systems biology approach can detect subtle effects invisible to conventional methods.</p>
<h3>Safer-by-Design Principles</h3>
<p>Rather than testing for safety after development, researchers are applying safer-by-design: choosing less toxic materials (e.g., zinc oxide instead of quantum dots for cosmetics), engineering surface coatings that prevent ROS generation, designing biodegradable nanoparticles (e.g., using FDA-approved lipids), and controlling size and shape to minimize cellular uptake when not needed.</p>
<h3>Environmental Risk Modeling</h3>
<p>Predictive models estimate nanoparticle release from products, environmental concentrations, and ecological impacts. Key challenges include: modeling nanoparticle transformation in the environment (aggregation, dissolution, surface modification), understanding bioaccumulation in food chains, and developing lifecycle assessments for nanoproducts from manufacture to disposal.</p>"""

FUTURE_B = """<h2>What's Coming Next?</h2>
<h3>Medical Nanobots</h3>
<p>Within 10-20 years, we may see the first clinical trials of programmable nanorobots for drug delivery. These would navigate your bloodstream, deliver medicine to specific cells, and report back diagnostic information.</p>
<h3>Better Batteries</h3>
<p>Nanotechnology could make electric car batteries 5x more powerful. Nanostructured silicon anodes store much more lithium than current graphite anodes, potentially extending range from 300 miles to 1,500 miles.</p>
<h3>Clean Water for Everyone</h3>
<p>Nanofiltration membranes could provide cheap, efficient water purification. This technology could bring clean drinking water to billions of people who currently lack access.</p>
<h3>Smarter Electronics</h3>
<p>Quantum dots already make TV displays more colorful. Future nanoscale devices could enable computers that think more like human brains, using much less energy.</p>"""

FUTURE_I = """<h2>Converging Technologies</h2>
<h3>AI + Nanotechnology</h3>
<p>Machine learning is accelerating nanotechnology at unprecedented rates. AI models predict material properties before synthesis, screen millions of candidates, and optimize manufacturing conditions. Self-driving labs use AI to design, execute, and analyze experiments autonomously. DeepMind's GNoME predicted 2.2 million crystal structures — 800 years of human work.</p>
<h3>Brain-Computer Interfaces</h3>
<p>Nanoscale electrodes could enable high-bandwidth BCIs. Current Neuralink electrodes are ~20 µm; nanoscale probes could provide 1000x more connections. This could restore motor function, treat neurological diseases, and eventually augment human cognition — the "neural lace" concept.</p>
<h3>Gene Therapy + Nanoparticles</h3>
<p>CRISPR gene editing combined with LNP delivery could cure hereditary diseases. Early clinical trials show promise for sickle cell disease, transthyretin amyloidosis, and certain cancers. The key challenge is targeting specific organs — liver targeting is solved, but lung, brain, and muscle targeting remain active research areas.</p>"""

FUTURE_A = """<h2>Frontier Research</h2>
<h3>Molecular Manufacturing</h3>
<p>The ultimate goal — building macroscopic objects atom by atom — remains decades away. But progress is real: DNA origami creates 3D structures with hundreds of addressable positions. Ribosome-like molecular machines synthesize arbitrary polymers with atomic precision. If achieved, molecular manufacturing would transform economics by making most manufactured goods virtually free to produce.</p>
<h3>Topological Quantum Computing</h3>
<p>Engineered nanoscale structures called topological qubits could enable error-corrected quantum computation within 15-20 years. Unlike conventional qubits, topological qubits are inherently protected from decoherence by the topology of their quantum state. Microsoft's approach uses semiconductor nanowires with proximitized superconductors.</p>
<h3>Programmable Matter</h3>
<p>Nanoscale actuators and sensors embedded in bulk materials could create "programmable matter" — materials that change shape, color, stiffness, or optical properties on command. Metamaterials with reconfigurable nanostructures could switch between being transparent and reflective, stiff and flexible, or hydrophobic and hydrophilic, all under electronic control.</p>"""


# ─── NEW TOPIC: Quantum Mechanics ──────────────────────
QUANTUM_B = """<h2>Why Quantum Mechanics Matters at the Nanoscale</h2>
<h3>Two Faces of Nature: Wave-Particle Duality</h3>
<p>At the scale of everyday objects, things are either particles (a baseball) or waves (sound). But at the nanoscale — roughly 1–100 nanometers — matter exhibits <b>wave-particle duality</b>. Electrons, atoms, and even entire molecules behave as both particles and waves simultaneously. A beam of electrons fired at a thin crystal produces a diffraction pattern, just like light passing through a grating. This is not a metaphor — it is the fundamental nature of reality at this scale. The famous double-slit experiment demonstrates that even single electrons create interference patterns when both slits are open, as if each electron travels through both slits at once.</p>

<h3>The Heisenberg Uncertainty Principle</h3>
<p>Werner Heisenberg showed that certain pairs of physical properties cannot both be known to arbitrary precision simultaneously. The most relevant form for nanotechnology is the position-momentum uncertainty relation: the product of the uncertainty in position (Δx) and the uncertainty in momentum (Δp) must always be greater than or equal to ℏ/2 (where ℏ = h/2π is the reduced Planck constant, approximately 1.055 × 10<sup>-34</sup> J·s). This means that confining an electron to a smaller space forces it to have higher momentum uncertainty — and therefore higher kinetic energy. This is the physical origin of <b>quantum confinement</b>, the phenomenon that gives quantum dots their size-dependent colors and makes nanostructures behave fundamentally differently from bulk materials.</p>

<h3>The Photoelectric Effect and Photon Energy</h3>
<p>When light hits a metal surface, it can eject electrons — but only if each photon carries enough energy. Einstein explained this with E = hν (energy equals Planck's constant times frequency), proving that light comes in discrete packets called photons. At the nanoscale, this means that the energy of light interactions depends on wavelength: UV photons (~4 eV) can break chemical bonds, while infrared photons (~0.1 eV) can only cause vibrations. Nanoparticles interact with light very differently depending on their size because their electronic energy levels are quantized, not continuous.</p>

<h3>Quantum Tunneling: Passing Through Walls</h3>
<p>One of the strangest predictions of quantum mechanics is <b>tunneling</b>: a particle can pass through a potential energy barrier even if it doesn't have enough classical energy to go over it. The probability decreases exponentially with barrier thickness and the square root of barrier height. This is not theoretical speculation — tunneling is the operating principle behind scanning tunneling microscopes (which image individual atoms), flash memory (which stores data by trapping electrons), and nuclear fusion in the Sun (where protons tunnel through their electrostatic repulsion). In nanotechnology, tunneling is both a tool and a challenge — it limits how thin we can make insulating layers in transistors.</p>"""

QUANTUM_I = """<h2>Mathematical Framework of Nanoscale Quantum Mechanics</h2>
<h3>The de Broglie Wavelength</h3>
<p>Louis de Broglie proposed that every moving particle has an associated wavelength given by <b>λ = h/p = h/(mv)</b>, where h = 6.626 × 10<sup>-34</sup> J·s is Planck's constant, m is the particle mass, and v is its velocity. For an electron moving at 1 × 10<sup>6</sup> m/s (typical in atoms), λ ≈ 0.73 nm — comparable to atomic spacing. This is why electron diffraction works in crystals. For a 1 nm gold nanoparticle (mass ≈ 3.3 × 10<sup>-22</sup> kg) moving at thermal velocity at 300K, λ ≈ 0.003 nm — far too small to matter. The de Broglie wavelength explains <i>why</i> quantum effects dominate for electrons at the nanoscale but not for heavier objects: the wavelength must be comparable to the physical dimensions of the system for quantum effects to be significant.</p>

<h3>The Schrödinger Equation</h3>
<p>The time-dependent Schrödinger equation, <b>iℏ∂ψ/∂t = Ĥψ</b>, is the fundamental equation governing quantum systems. Here, ψ (psi) is the wavefunction — a complex-valued function that contains all information about the system. The Hamiltonian operator Ĥ represents the total energy (kinetic + potential). For a particle in a one-dimensional box of width L with infinite walls, the solutions are standing waves: ψ<sub>n</sub>(x) = √(2/L) sin(nπx/L), where n = 1, 2, 3, ... The corresponding energy levels are discrete: <b>E<sub>n</sub> = n²π²ℏ²/(2mL²)</b>. For an electron in a 2 nm box, E₁ ≈ 0.094 eV, E₂ ≈ 0.376 eV, E₃ ≈ 0.846 eV. The spacing between levels increases as L decreases — this is quantum confinement, and it is the reason quantum dots have size-dependent optical and electronic properties.</p>

<h3>Quantum Tunneling Probability</h3>
<p>The transmission coefficient (probability of tunneling) through a rectangular barrier of height V and width L for a particle with energy E < V is approximately: <b>T ≈ exp(-2κL)</b>, where <b>κ = √(2m(V-E))/ℏ</b>. For an electron tunneling through a 1 nm barrier with V-E = 1 eV, κ ≈ 5.12 × 10<sup>9</sup> m<sup>-1</sup>, giving T ≈ exp(-10.24) ≈ 3.6 × 10<sup>-5</sup>. Doubling the barrier width to 2 nm gives T ≈ (3.6 × 10<sup>-5</sup>)² ≈ 1.3 × 10<sup>-9</sup> — an exponential suppression. This extreme sensitivity to barrier dimensions is why tunneling is negligible at macroscopic scales but dominant at the nanoscale, and why scanning tunneling microscopes can achieve sub-angstrom resolution.</p>

<h3>The Hydrogen Atom and Quantum Numbers</h3>
<p>The hydrogen atom is the simplest quantum system with analytic solutions. Its energy levels depend only on the principal quantum number n: E<sub>n</sub> = -13.6/n² eV. The full state is described by four quantum numbers: n (energy level, 1,2,3,...), l (orbital angular momentum, 0 to n-1), m<sub>l</sub> (magnetic quantum number, -l to +l), and m<sub>s</sub> (spin, ±1/2). The wavefunctions are products of radial functions (associated Laguerre polynomials) and angular functions (spherical harmonics). Understanding hydrogen-like orbitals is essential for nanotechnology because chemical bonds, band structures, and nanoparticle electronic properties all derive from these atomic wavefunctions overlapping in space.</p>"""

QUANTUM_A = """<h2>Advanced Quantum Phenomena in Nanostructures</h2>
<h3>Quantum Confinement in Different Dimensions</h3>
<p>The dimensionality of confinement fundamentally changes the density of states (DOS) — the number of available states per unit energy per unit volume. In 3D (bulk material), D(E) ∝ √E (continuous). Confining one dimension (quantum well, 2D) gives D(E) = constant (step function). Confining two dimensions (quantum wire, 1D) gives D(E) ∝ 1/√E (with divergences called van Hove singularities). Confining all three dimensions (quantum dot, 0D) gives D(E) = discrete delta functions — completely quantized energy levels like an artificial atom. This progression from continuous to discrete states is what enables quantum dots to have size-tunable fluorescence, quantum wells to form the basis of laser diodes, and nanowires to have unique electronic transport properties. The effective mass approximation allows us to model these systems using the bulk effective mass m* instead of the free electron mass, giving E<sub>n</sub> = n²π²ℏ²/(2m*L²) for each confined dimension.</p>

<h3>Coulomb Blockade and Single-Electron Effects</h3>
<p>When a nanostructure is small enough that adding a single electron significantly changes its electrostatic energy, the <b>Coulomb blockade</b> effect occurs. The charging energy is <b>E<sub>c</sub> = e²/(2C)</b>, where C is the total capacitance of the island. For E<sub>c</sub> to be observable, it must exceed the thermal energy kT. At room temperature (kT ≈ 26 meV), this requires C < 3 aF (attofarads = 10<sup>-18</sup> F), corresponding to islands smaller than ~5 nm. At 4.2 K (liquid helium), islands up to ~50 nm work. The condition E<sub>c</sub> > kT means that electrons tunnel one at a time — the hallmark of single-electron transistors. The current-voltage characteristic shows a "Coulomb gap" near zero bias where no current flows. This is used in ultra-sensitive electrometers (detecting charges as small as 10<sup>-6</sup> e) and is being explored for quantum computing qubits based on charge states.</p>

<h3>The Quantum Hall Effect</h3>
<p>When a 2D electron gas (as in a GaAs/AlGaAs heterostructure) is placed in a strong magnetic field at low temperature, the Hall conductance becomes quantized in integer multiples of e²/h ≈ 38.7 µS (the conductance quantum). The longitudinal resistance drops to zero at these plateaus. The integer quantum Hall effect (Klitzing, 1985 Nobel Prize) arises because the magnetic field quantizes the electron cyclotron orbits into Landau levels. Even more remarkable is the <b>fractional quantum Hall effect</b> (Tsui, Stormer, Laughlin, 1998 Nobel Prize), where plateaus appear at fractional values like 1/3, 2/5, 2/3 of e²/h, explained by electron-electron interactions forming fractionally-charged quasiparticles. These effects are used to define the resistance standard (the von Klitzing constant R<sub>K</sub> = h/e² ≈ 25812.8 Ω) and are platforms for studying topological quantum states relevant to fault-tolerant quantum computing.</p>

<h3>Kubo Gap in Metallic Nanoparticles</h3>
<p>In bulk metals, the energy levels form continuous bands. But as a metal particle shrinks below ~2 nm, the discrete spacing between energy levels (the <b>Kubo gap</b>) δ = 4E<sub>F</sub>/(3N) becomes significant. For a gold nanoparticle with N electrons, E<sub>F</sub> ≈ 5.5 eV, so δ ≈ 7.3/N eV. A 2 nm gold particle has ~250 atoms and ~1000 conduction electrons, giving δ ≈ 7 meV. When δ approaches kT, the electronic properties change: the particle loses its metallic character, electrical conductivity drops, and the optical absorption spectrum shows discrete transitions rather than the broad plasmon band. This transition from metallic to molecular character is a direct consequence of quantum confinement and defines the boundary between "nanoparticle" and "cluster" regimes in metal nanoscience.</p>"""


# ─── NEW TOPIC: Nanoelectronics ───────────────────────
NANOELEC_B = """<h2>Electronics at the Nanoscale</h2>
<h3>Moore's Law and the Nanoscale Frontier</h3>
<p>Gordon Moore observed in 1965 that the number of transistors on a chip doubles approximately every two years. Modern processors like Apple's M4 and AMD's Zen 5 use transistors with gate lengths of just 3–5 nanometers — roughly 15–25 silicon atoms wide. At this scale, traditional transistor physics breaks down: quantum tunneling causes current to leak through the gate oxide, and variability in atomic positions causes significant device-to-device variation. IBM demonstrated 2 nm process technology with 50 billion transistors, while research has pushed below 1 nm using carbon nanotubes and 2D materials like MoS₂. The question is no longer "can we make it smaller?" but "does making it smaller still improve performance?" as quantum effects increasingly dominate.</p>

<h3>How a Nanoscale Transistor Works</h3>
<p>A modern MOSFET (Metal-Oxide-Semiconductor Field-Effect Transistor) is essentially a nanoscale switch. The gate electrode sits above a thin insulating layer (high-k dielectric, ~1-2 nm thick), which sits above the channel. Applying voltage to the gate creates an electric field that attracts or repels charge carriers in the channel, turning current flow on or off. In a 3 nm FinFET, the gate wraps around three sides of a thin silicon fin (~5 nm wide, ~30 nm tall) for better electrostatic control. In Gate-All-Around (GAA) nanosheet transistors (Samsung's 3nm node), the gate completely surrounds the silicon channel, providing the best possible control over the current — essential for preventing quantum tunneling leakage.</p>

<h3>Beyond Silicon: New Nanoelectronic Materials</h3>
<p>Silicon is reaching its physical limits, and several nanomaterials are being developed as replacements. <b>Carbon nanotubes</b> can carry 1000x more current than copper and switch 5x faster than silicon. <b>Graphene</b> has electron mobility 100x higher than silicon but lacks a bandgap, making it hard to turn off. <b>Transition metal dichalcogenides</b> (TMDs) like MoS₂ and WS₂ are semiconductors that work at the atomic limit — a single monolayer of MoS₂ is only 0.65 nm thick but functions as a working transistor channel. <b>Black phosphorus</b> offers a thickness-dependent bandgap from 0.3 eV (bulk) to 2.0 eV (monolayer), tunable for different applications from infrared detectors to high-speed logic.</p>

<h3>Memory Technologies at the Nanoscale</h3>
<p>Modern NAND flash memory stores data by trapping electrons in a nanoscale "floating gate" — a tiny island of polysilicon only ~10 nm across, surrounded by insulating oxide. 3D NAND stacks 200+ layers vertically, with each layer containing billions of these nanoscale charge traps. Newer approaches like <b>ReRAM</b> (Resistive RAM) use nanoscale filaments of metal atoms that grow and dissolve to change resistance. <b>MRAM</b> (Magnetoresistive RAM) uses electron spin — the orientation of magnetic domains in nanoscale tunnel junctions — to store bits non-volatilely. These technologies all rely on controlling matter at the nanometer scale to store and retrieve digital information.</p>"""

NANOELEC_I = """<h2>Quantum Nanoelectronic Devices</h2>
<h3>Single-Electron Transistors (SETs)</h3>
<p>A <b>single-electron transistor</b> consists of a tiny conductive island (1–10 nm) connected to source and drain electrodes through two tunnel junctions, with a gate electrode capacitively coupled to the island. Current flows only when the gate voltage aligns discrete charge states, allowing electrons to tunnel one at a time. The key physics is <b>Coulomb blockade</b>: the charging energy E<sub>c</sub> = e²/(2C) must exceed the thermal energy kT for the effect to be observable. At T = 4.2 K, a 5 nm island with C ≈ 0.5 aF gives E<sub>c</sub> ≈ 160 meV ≫ kT ≈ 0.36 meV. SETs can detect charges as small as 10<sup>-6</sup> e, making them the most sensitive electrometers ever built. Challenges for room-temperature operation include fabricating islands small enough (C < 3 aF) and managing background charge fluctuations from nearby impurities.</p>

<h3>Quantum Dot Cellular Automata (QDCA)</h3>
<p>QDCA is a radical approach to computing that uses arrangements of quantum dots to encode binary information in charge configurations rather than current flow. A basic QDCA cell consists of four quantum dots at the corners of a square, with two mobile electrons. Coulomb repulsion forces the electrons into diagonal positions, creating two stable polarization states (representing 0 and 1). Adjacent cells interact through Coulomb forces, propagating information without any current flow. This means essentially zero dynamic power dissipation — a huge advantage over CMOS. Clocked QDCA arrays have been demonstrated experimentally, and simulations suggest clocking frequencies up to 1 THz. The challenge is fabrication: each dot must be ~10 nm across with ~20 nm cell-to-cell spacing, requiring sub-10 nm lithographic precision over large areas.</p>

<h3>Memristors: The Fourth Circuit Element</h3>
<p>Predicted by Leon Chua in 1971 and first demonstrated by HP Labs in 2008, the <b>memristor</b> (memory resistor) is a two-terminal device whose resistance depends on the history of current that has flowed through it. The fundamental relationship is <b>v = M(q)·i</b>, where M(q) = dΦ<sub>m</sub>/dq is the memristance, a function of the charge q that has passed through the device. In practical devices, a nanoscale filament of metal ions grows through an oxide layer (e.g., TaO<sub>x</sub>), lowering resistance (ON state), or dissolves, raising resistance (OFF state). The resistance ratio can exceed 10<sup>6</sup>:1. Memristors are crucial for <b>neuromorphic computing</b>: their analog resistance states mimic synaptic weights, and their physics naturally implements spike-timing-dependent plasticity (STDP), the biological learning rule. HP's "memristor crossbar" architecture can achieve 10<sup>12</sup> operations per watt — 1000x more efficient than conventional von Neumann architectures for neural network inference.</p>

<h3>Tunneling Magnetoresistance (TMR)</h3>
<p>In a magnetic tunnel junction (MTJ), two ferromagnetic layers are separated by a thin insulating barrier (~1–2 nm of MgO). Electrons tunnel through the barrier, and the tunneling probability depends on the relative orientation of the magnetization in the two layers — a phenomenon called <b>tunneling magnetoresistance</b>. When the magnetizations are parallel, tunneling is easy (low resistance); when antiparallel, tunneling is harder (high resistance). Modern MgO-based MTJs achieve TMR ratios > 600% at room temperature. This effect is the basis of <b>MRAM</b> technology, where the magnetic orientation stores a bit. Spin-transfer torque (STT) and spin-orbit torque (SOT) switching mechanisms use nanoscale current pulses (~10<sup>6</sup> A/cm²) to flip the magnetic state, enabling write energies of ~1 fJ per bit — 100x less than SRAM.</p>"""

NANOELEC_A = """<h2>Frontier Nanoelectronic Concepts</h2>
<h3>Spintronics: Using Electron Spin</h3>
<p>Conventional electronics uses only the charge of electrons. <b>Spintronics</b> (spin electronics) also exploits the electron's intrinsic angular momentum (spin, ±ℏ/2). The <b>giant magnetoresistance</b> (GMR) effect, discovered in 1988 by Fert and Grunberg (Nobel 2007), occurs in multilayer structures of alternating ferromagnetic and non-magnetic layers, each a few nanometers thick. The resistance changes dramatically depending on whether adjacent magnetic layers are parallel or antiparallel: <b>ΔR/R ∝ (M₁ · M₂)</b>. GMR read heads revolutionized hard disk drives, enabling terabyte-capacity drives. Beyond GMR, the <b>spin Hall effect</b> converts charge current to spin current, and <b>topological insulators</b> (like Bi₂Se₃) conduct spin-polarized electrons on their surface while being insulating in the bulk. The ultimate goal is a <b>spin field-effect transistor</b> (Datta-Das, 1990) that switches current by manipulating electron spin rather than charge, potentially operating at much lower power than CMOS.</p>

<h3>Majorana Fermions in Nanowires</h3>
<p>Majorana fermions are their own antiparticles — exotic quasiparticles that can emerge at the ends of semiconductor nanowires (InSb or InAs) with strong spin-orbit coupling, placed on a superconducting substrate and in a magnetic field. First observed in 2012 at Delft, these <b>Majorana zero modes</b> are protected by topology: local perturbations cannot destroy them, making them naturally fault-tolerant qubits. In a "topological qubit," quantum information is stored non-locally between two spatially separated Majorana modes, making it immune to local decoherence. Microsoft's quantum computing strategy is entirely based on this approach. The challenges are formidable: devices must operate at ~20 mK, require sub-100 nm nanowire fabrication, and the unambiguous detection of Majorana modes remains an active research debate with recent controversies about alternative explanations (e.g., trivial Andreev bound states) for observed signatures.</p>

<h3>The Landauer Formula and Quantum Conductance</h3>
<p>The <b>Landauer formula</b> provides a fundamental limit on how much current a perfect nanoscale conductor can carry: <b>G = (2e²/h) × T</b>, where G is the conductance, T is the transmission probability (0 to 1), and the factor of 2 accounts for spin degeneracy. The quantum of conductance G₀ = 2e²/h ≈ 77.5 µS (or 1/(12.9 kΩ)) is the maximum conductance of a single conduction channel. A carbon nanotube with two conducting channels has a minimum resistance of h/4e² ≈ 6.45 kΩ — this is NOT zero, unlike macroscopic wires. The Landauer formula implies a fundamental minimum resistance for nanoscale conductors, setting limits on how small electronic devices can be. It also connects to information theory: each quantum channel dissipates at least kT·ln(2) of energy per bit of information processed, establishing a thermodynamic lower bound for nanoelectronic computation.</p>

<h3>Valleytronics and 2D Material Electronics</h3>
<p>Beyond charge and spin, electrons in certain crystals carry a "valley" index — a quantum number related to which local minimum (valley) in the conduction band they occupy. <b>Valleytronics</b> exploits this degree of freedom as an additional information carrier. In transition metal dichalcogenides (MoS₂, WS₂, WSe₂), the K and K' valleys in the Brillouin zone can be selectively addressed using circularly polarized light, and valley polarization can be maintained for nanoseconds — long enough for information processing. In graphene, the valleys are at the K and K' points, and valley-polarized currents can be generated using strain engineering or atomic-scale defects. Combining valleytronics with spintronics in the same 2D material could enable four-state logic (spin × valley), doubling the information density per device. Hexagonal boron nitride (h-BN) serves as an ideal atomically-flat insulating substrate for these devices, providing a defect-free interface that preserves the intrinsic electronic properties of the 2D channel material.</p>"""


# ─── NEW TOPIC: Nanophotonics ─────────────────────────
NANOPHOTO_B = """<h2>Light and Nanotechnology</h2>
<h3>The Diffraction Limit</h3>
<p>Conventional optics cannot focus light to a spot smaller than roughly half its wavelength, known as the <b>diffraction limit</b>: d ≈ λ/(2n·sinα), where n is the refractive index and α is the half-angle of the cone of light. For visible light (400–700 nm), this means the smallest resolvable feature is ~200 nm — far larger than most nanostructures of interest. This is why you cannot see individual atoms or molecules with an optical microscope, no matter how powerful the lens. Nanophotonics is the field dedicated to manipulating light at scales below this limit, using surface plasmons, evanescent waves, and nanoscale resonators to confine and control light at the nanometer scale, well beyond what traditional optics allows.</p>

<h3>What Are Surface Plasmons?</h3>
<p>Surface plasmons are collective oscillations of free electrons at the interface between a metal (like gold or silver) and a dielectric (like glass or water). When light hits a metal nanoparticle, the electric field pushes electrons back and forth. If the light frequency matches the natural frequency of electron oscillation, <b>resonance</b> occurs — this is <b>surface plasmon resonance</b> (SPR). At resonance, the nanoparticle absorbs and scatters light very strongly, creating vivid colors. This is why gold nanoparticles are red (not gold-colored!), why medieval stained glass has beautiful colors, and why the Lycurgus Cup appears green in reflected light but red in transmitted light — it contains gold and silver nanoparticles from Roman times.</p>

<h3>Nanophotonics in Everyday Technology</h3>
<p>Nanophotonic devices are already ubiquitous. The colorful, shifting patterns on holographic security features on banknotes and passports are created by nanoscale diffraction gratings. Your smartphone's OLED display uses organic layers just ~100 nm thick that emit light through nanoscale structures. Anti-reflective coatings on camera lenses are precisely engineered multilayer films where each layer is a specific fraction of a wavelength thick. Quantum dot TVs (QLED) use semiconductor nanocrystals (2–10 nm) that emit pure, saturated colors determined by their size — blue from 2 nm CdSe dots, red from 6 nm ones. Optical fiber communications rely on total internal reflection at the nanoscale-smooth interface between the fiber core and cladding.</p>

<h3>Nanoplasmonics: Light on a Chip</h3>
<p>Surface plasmon polaritons (SPPs) can propagate along metal-dielectric interfaces with wavelengths much shorter than free-space light. This means light can be confined to regions far smaller than the diffraction limit — down to ~10 nm for gap plasmons between two metal surfaces. This "squeezing" of light enables ultra-compact optical components: waveguides only 50 nm wide, lenses just 100 nm across, and sensors that detect single molecules by the change in plasmon resonance when a molecule binds to a metal surface. The tradeoff is that plasmons lose energy quickly (propagation lengths of ~10–100 µm), so plasmonic circuits must be very short, making them ideal for on-chip signal routing between nanoscale components rather than long-distance communication.</p>"""

NANOPHOTO_I = """<h2>Mathematical Foundations of Nanophotonics</h2>
<h3>Surface Plasmon Resonance Condition</h3>
<p>For a spherical nanoparticle much smaller than the wavelength of light (the quasi-static approximation), the surface plasmon resonance occurs when the real part of the metal's dielectric function satisfies: <b>ε<sub>m</sub>(ω) = -2ε<sub>d</sub></b>, where ε<sub>m</sub> is the metal dielectric function and ε<sub>d</sub> is the surrounding dielectric constant. For gold in water (ε<sub>d</sub> ≈ 1.77), this gives ε<sub>m</sub> ≈ -3.54, which occurs at a wavelength of ~520 nm for small spheres. The extinction cross-section at resonance is: σ<sub>ext</sub> = 24πa³ε<sub>d</sub><sup>3/2</sup> × ε<sub>m</sub>''/[(ε<sub>m</sub>'+2ε<sub>d</sub>)² + (ε<sub>m</sub>'')²], where a is the particle radius and ε<sub>m</sub>' and ε<sub>m</sub>'' are the real and imaginary parts. This formula explains why gold nanoparticles of ~20 nm diameter appear red: they strongly absorb green light (~520 nm) and transmit/reflect red.</p>

<h3>The Drude Model for Metal Optical Properties</h3>
<p>The frequency-dependent dielectric function of a metal is described by the <b>Drude model</b>: <b>ε(ω) = ε<sub>∞</sub> - ω<sub>p</sub>²/(ω² + iγω)</b>, where ω<sub>p</sub> = √(ne²/ε₀m*) is the plasma frequency, γ = 1/τ is the damping rate (τ is the electron scattering time), and ε<sub>∞</sub> accounts for interband transitions. For gold: ω<sub>p</sub> ≈ 9.0 eV, γ ≈ 0.07 eV, ε<sub>∞</sub> ≈ 9.5. The plasma frequency determines the boundary between reflective (ω < ω<sub>p</sub>) and transparent (ω > ω<sub>p</sub>) behavior — this is why metals are shiny at visible frequencies but transparent to X-rays. The damping rate γ determines the width of the plasmon resonance: smaller γ means sharper, stronger resonance, which is why silver (γ ≈ 0.02 eV) has stronger plasmon effects than gold.</p>

<h3>Mie Scattering Theory</h3>
<p>For particles comparable to the wavelength of light, the simple quasi-static approximation fails, and <b>Mie theory</b> provides the exact solution to Maxwell's equations for spherical particles. The key parameter is the size parameter: <b>x = 2πr/λ</b>. For x ≪ 1 (Rayleigh regime), scattering ∝ λ<sup>-4</sup> (blue sky, red sunset). For x ≈ 1 (Mie regime), scattering becomes complex with multiple peaks and strong angular dependence. For x ≫ 1, geometric optics applies. Gold nanoparticles transition from Rayleigh to Mie behavior around 40–80 nm diameter: below 40 nm, the color is dominated by absorption (dipole SPR peak); above 80 nm, higher-order modes appear (quadrupole, octupole) and scattering dominates over absorption, shifting the perceived color from red to orange to yellow.</p>

<h3>Evanescent Waves and Near-Field Optics</h3>
<p>When light undergoes total internal reflection at a dielectric interface, the electromagnetic field does not abruptly stop at the boundary. Instead, an <b>evanescent wave</b> decays exponentially into the lower-index medium: <b>E(z) = E₀·exp(-κz)</b>, where κ = (2π/λ)√(n₁²sin²θ - n₂²) is the decay constant. For visible light at a glass-air interface, the penetration depth 1/κ is typically 100–200 nm. Evanescent waves carry no energy away from the interface but can interact with nearby nanostructures. This is the basis of <b>near-field scanning optical microscopy</b> (NSOM/SNOM), which achieves ~20 nm resolution by placing a nanoscale optical fiber tip within the evanescent field, and of surface plasmon resonance sensors that detect molecular binding through evanescent field perturbations.</p>"""

NANOPHOTO_A = """<h2>Frontier Nanophotonics and Metamaterials</h2>
<h3>Negative Refraction and Metamaterials</h3>
<p>A <b>metamaterial</b> is an artificial structure with features smaller than the wavelength of light, engineered to have optical properties not found in nature. The most famous example is a material with simultaneously negative electric permittivity (ε) and magnetic permeability (μ), giving a <b>negative refractive index</b>: <b>n = -√(εμ)</b>. In such materials, light bends the "wrong" way at interfaces, leading to remarkable effects: a flat slab of negative-index material can focus light to a point (a "Veselago lens"), and the phase velocity is opposite to the direction of energy flow. First demonstrated at microwave frequencies in 2001 (Shelby, Smith, Schultz), negative index metamaterials have since been achieved at infrared and visible wavelengths using nanoscale split-ring resonators (for negative μ) and nanowire arrays (for negative ε). The challenge at optical frequencies is that magnetic response requires structural features far smaller than the wavelength.</p>

<h3>Superlensing and the Perfect Lens</h3>
<p>In 2000, Sir John Pendry proposed that a thin slab of negative-index material could act as a "perfect lens," amplifying evanescent waves that normally decay and thus reconstructing an image with resolution beyond the diffraction limit. The physics is that negative-ε material supports surface plasmons that resonantly enhance the evanescent fields. <b>Superlenses</b> using thin silver films (35 nm) have experimentally demonstrated resolution of λ/6 (~70 nm for 436 nm light). More practical are <b>hyperlenses</b> made from cylindrical alternating metal-dielectric layers, which have demonstrated resolution down to 130 nm. The ultimate limit comes from material losses (the imaginary part of ε), which damp the evanescent wave amplification. Current research focuses on gain-assisted metamaterials and active plasmonic structures to overcome loss limitations.</p>

<h3>Transformation Optics and Cloaking</h3>
<p><b>Transformation optics</b> is a powerful design paradigm based on the mathematical equivalence between coordinate transformations and material properties. If you want to bend light around an object to make it invisible, you mathematically "compress" the space occupied by the object and map it to a shell around it. The required material properties are derived from the Jacobian of this coordinate transformation. For a simplified 2D cylindrical cloak, the required permittivity and permeability are anisotropic and range continuously from the free-space value to zero. The first experimental cloaking demonstration (2006, Duke University) used split-ring resonators at microwave frequencies to guide waves around a copper cylinder, reducing its scattering cross-section. At optical frequencies, 3D cloaking remains extremely challenging because the required materials have parameters that are difficult to engineer at the nanoscale. Alternative approaches include "carpet cloaking" (hiding objects under a reflecting surface) and "plasmonic cloaking" (using scattering cancellation from a metamaterial coating).</p>

<h3>Photonic Crystals and the Purcell Effect</h3>
<p>A <b>photonic crystal</b> is a periodic dielectric structure with features spaced at half the wavelength of light, creating a "photonic bandgap" — a range of frequencies where light cannot propagate, analogous to the electronic bandgap in semiconductors. The condition for a photonic bandgap is governed by the Bragg condition: <b>2d·n·cosθ = mλ</b>, where d is the lattice spacing, n is the average refractive index, and m is an integer. Photonic crystals can confine light to extremely small volumes for long durations, enhancing light-matter interaction by orders of magnitude. The <b>Purcell factor</b> quantifies this enhancement: F<sub>P</sub> = (3/4π²)(λ/n)³(Q/V), where Q is the quality factor and V is the mode volume. For a photonic crystal cavity with Q = 10⁶ and V = (λ/n)³, F<sub>P</sub> ≈ 10⁵, meaning a quantum emitter (atom, quantum dot) inside the cavity will emit photons 100,000x faster than in free space. This enables ultra-low-threshold lasers, single-photon sources for quantum communication, and strong coupling regimes for quantum information processing.</p>"""


FLASHCARDS = [
    ("Nanometer", "One billionth of a meter (10⁻⁹ m). About 3-4 atoms wide.", "B"),
    ("Top-Down Fabrication", "Starting with bulk material and removing parts to create nanostructures. Example: lithography in chip manufacturing.", "B"),
    ("Bottom-Up Fabrication", "Building structures atom by atom or molecule by molecule. Example: self-assembly, chemical vapor deposition.", "B"),
    ("Quantum Confinement", "When material dimensions approach the de Broglie wavelength, energy levels become discrete rather than continuous. This changes optical, electrical, and magnetic properties.", "I"),
    ("Surface Plasmon Resonance", "Collective oscillation of conduction electrons on a nanoparticle surface when excited by light. Responsible for gold nanoparticle colors.", "I"),
    ("Carbon Nanotube", "Cylindrical graphene sheet. Tensile strength >100 GPa, 100x stronger than steel at 1/6 the density. Can be metallic or semiconducting.", "B"),
    ("Graphene", "Single-atom-thick 2D carbon lattice. Electron mobility 100x silicon. Isolated 2004 by Geim & Novoselov (Nobel 2010).", "B"),
    ("Quantum Dot", "Semiconductor nanocrystal (2-10 nm) with size-tunable fluorescence. Used in displays, solar cells, bio-imaging.", "I"),
    ("Lipid Nanoparticle (LNP)", "50-100 nm vesicle that delivers fragile molecules like mRNA. Key technology behind COVID-19 vaccines.", "I"),
    ("DNA Origami", "Folding DNA strands into precise 2D/3D nanoscale shapes. Invented 2006 by Paul Rothemund. Used for nanobots and drug delivery.", "I"),
    ("Molecular Motor", "Protein or synthetic machine converting energy into mechanical motion at nanoscale. ATP synthase rotates at 1000s of RPM. 2016 Nobel: Feringa & Sauvage.", "A"),
    ("Grey Goo", "Hypothetical scenario of self-replicating nanomachines consuming all matter. Coined by Eric Drexler. Science fiction but influenced safety research.", "B"),
    ("Memristor", "Passive element that remembers charge history. Mimics synaptic behavior for neuromorphic computing. First demonstrated by HP Labs 2008.", "A"),
    ("CRISPR-Cas9", "Gene-editing tool adapted from bacterial immunity. Nanoparticle delivery enables precise genetic corrections in living organisms.", "I"),
    ("Scanning Tunneling Microscope", "Images surfaces at atomic level by measuring tunneling current. Invented 1981 by Binnig & Rohrer. Nobel 1986.", "B"),
    ("Perovskite", "Crystal structure (ABX₃) used in nanoscale solar cells achieving >26% efficiency at low manufacturing cost.", "A"),
    ("Xenobot", "First living robot (2020) — <1mm biological machine from frog cells, designed by supercomputer. Can move, self-heal, cooperate.", "I"),
    ("Buckminsterfullerene", "C₆₀ — 60 carbon atoms in soccer-ball shape. Discovered 1985. Nobel 1996 to Kroto, Curl, Smalley. Opened new nanomaterial class.", "B"),
    ("NV Center in Diamond", "Nitrogen-vacancy defect in diamond enabling room-temperature quantum sensing at nm resolution. Potential for cellular-level MRI.", "A"),
    ("Blood-Brain Barrier", "Selective barrier separating blood from brain. Nanoparticles can cross it, enabling drug delivery to treat neurological diseases.", "I"),
    ("de Broglie Wavelength", "λ = h/p = h/(mv). Every moving particle has an associated wavelength. For an electron at 10⁶ m/s, λ ≈ 0.73 nm.", "I"),
    ("Heisenberg Uncertainty Principle", "Δx · Δp ≥ ℏ/2. You cannot simultaneously know the exact position and exact momentum of a particle.", "I"),
    ("Particle in a Box", "E_n = n²π²ℏ²/(2mL²). Quantum confinement model showing that energy levels are discrete and spacing increases as L decreases.", "I"),
    ("Coulomb Blockade", "E_c = e²/(2C). When the energy to add one electron exceeds kT, electrons tunnel one at a time. Basis of single-electron transistors.", "A"),
    ("Drude Model", "ε(ω) = 1 - ωp²/(ω²+iγω). Describes frequency-dependent dielectric function of metals using plasma frequency and damping rate.", "I"),
    ("Mie Scattering", "Exact solution to Maxwell's equations for spherical particles. Size parameter x = 2πr/λ determines Rayleigh (x<<1) vs Mie (x≈1) regime.", "A"),
    ("Landauer Formula", "G = (2e²/h) × T. Quantum of conductance G₀ = 77.5 µS per conduction channel. Sets fundamental resistance limit for nanoscale wires.", "A"),
    ("Stokes-Einstein Equation", "D = kT/(6πηr). Relates diffusion coefficient to temperature, viscosity, and particle radius. Critical for nanoparticle transport in fluids.", "I"),
    ("Photonic Crystal", "Periodic dielectric structure creating photonic bandgap (2d·n·cosθ = mλ). Controls light propagation analogous to semiconductor bandgaps.", "A"),
    ("Transformation Optics", "Design paradigm using coordinate transformations to derive material properties for cloaking, lensing, and wave guiding. Basis of metamaterial design.", "A"),
    ("Nanobot", "Active nanoscale machine that senses, decides, and acts autonomously. Distinguished from passive nanoparticles by its ability to perform complex tasks.", "B"),
    ("Stokes Drag", "F = 6πηrv. Viscous drag force on a sphere of radius r at velocity v in fluid of viscosity η. Dominates nanoscale motion.", "I"),
    ("Reynolds Number", "Re = ρvL/η. At nanoscale Re ~ 10^-5 to 10^-2: viscous forces dominate, no inertia, no coasting.", "I"),
    ("Peclet Number", "Pe = vL/D. Compares active propulsion to Brownian diffusion. Pe >> 1 = propulsion dominates, Pe << 1 = diffusion dominates.", "I"),
    ("Scallop Theorem", "At low Re, reciprocal (back-and-forth) motion produces zero net displacement. Nanobots need non-reciprocal motion (corkscrews, flexible tails) to swim.", "I"),
    ("DNA Strand Displacement", "Input DNA strand displaces bound strand, triggering cascades. Implements Boolean logic (AND/OR/NOT) entirely in DNA chemistry. Rate: k_sd ~ 10^5-10^7 M^-1s^-1.", "A"),
    ("Dissociation Constant", "Kd = [A][B]/[AB] = k_off/k_on. Measures binding affinity. Strong antibodies: Kd ~ 10^-9 to 10^-12 M. Sensor most sensitive when [target] ~ Kd.", "I"),
    ("PEGylation", "Coating nanoparticles with PEG chains to resist opsonin adsorption. Extends blood circulation half-life from minutes to 15-20 hours.", "A"),
    ("Chemotaxis", "Movement toward higher chemical concentration. Bacteria detect gradients as shallow as 1% over body length. Key for nanobot tumor targeting.", "I"),
    ("Quorum Sensing", "Bacteria release signaling molecules; when concentration exceeds threshold, coordinated behavior triggers. Potential nanobot swarm communication method.", "I"),
]


MATCHING_PAIRS = [
    ("Graphene", "Single-atom-thick carbon sheet"),
    ("C₆₀", "Buckminsterfullerene / Buckyball"),
    ("LNP", "mRNA vaccine delivery vehicle"),
    ("STM", "Atomic-resolution microscope"),
    ("DNA Origami", "Folded-DNA nanoscale shapes"),
    ("Quantum Dot", "Size-tunable fluorescent crystal"),
    ("CRISPR", "Gene-editing molecular tool"),
    ("Memristor", "Memory resistor for neuromorphic chips"),
    ("Xenobot", "Living robot from frog cells"),
    ("Grey Goo", "Drexler's self-replication scenario"),
    ("Perovskite", "High-efficiency solar crystal"),
    ("NV Center", "Diamond quantum sensor"),
    ("Stokes Drag", "F = 6πηrv viscous force"),
    ("Reynolds Number", "Ratio of inertial to viscous forces"),
    ("PEGylation", "Stealth coating for nanoparticles"),
    ("Scallop Theorem", "No reciprocal swimming at low Re"),
    ("Peclet Number", "Propulsion vs diffusion comparison"),
    ("Chemotaxis", "Following chemical gradients"),
]


QUIZ_DATA = [
    {"q": "How many meters is one nanometer?", "o": ["10⁻⁶ m","10⁻⁹ m","10⁻¹² m","10⁻³ m"], "c": 1, "e": "1 nm = 10⁻⁹ m — one billionth of a meter, about 3-4 atoms wide.", "d": "B"},
    {"q": "Who gave the lecture 'There's Plenty of Room at the Bottom'?", "o": ["Einstein","Feynman","Bohr","Drexler"], "c": 1, "e": "Richard Feynman at Caltech, 1959 — the founding vision of nanotechnology.", "d": "B"},
    {"q": "What color do 20 nm gold nanoparticles appear?", "o": ["Gold/yellow","Silver","Red or purple","Blue"], "c": 2, "e": "Surface plasmon resonance makes 20 nm gold nanoparticles appear red due to quantum effects.", "d": "B"},
    {"q": "What is ~100x stronger than steel at 1/6 the weight?", "o": ["Graphene","Titanium","Kevlar","Carbon Nanotubes"], "c": 3, "e": "CNTs have tensile strength >100 GPa — over 100x stronger than steel.", "d": "B"},
    {"q": "What delivered mRNA in COVID-19 vaccines?", "o": ["Quantum dots","Lipid nanoparticles","Carbon nanotubes","DNA origami"], "c": 1, "e": "LNPs encapsulated fragile mRNA, enabling cellular delivery for Pfizer & Moderna vaccines.", "d": "B"},
    {"q": "What is the 'grey goo' scenario?", "o": ["Chemical pollution","Self-replicating nanomachines consuming matter","Nanoparticle brain accumulation","Environmental contamination"], "c": 1, "e": "Eric Drexler's hypothetical scenario of失控 self-replicating nanomachines. Science fiction.", "d": "B"},
    {"q": "Who coined 'nanotechnology' in 1974?", "o": ["Drexler","Feynman","Taniguchi","Binnig"], "c": 2, "e": "Norio Taniguchi used it for semiconductor processes below 1 micron.", "d": "B"},
    {"q": "What is graphene?", "o": ["3D carbon crystal","Single-atom carbon sheet","Carbon nanotube","Fullerene"], "c": 1, "e": "Graphene is a 2D sheet of carbon atoms. Electron mobility 100x silicon.", "d": "B"},
    {"q": "What size are modern CPU transistors (2024)?", "o": ["14 nm","7 nm","3-5 nm","0.5 nm"], "c": 2, "e": "Modern processors use 3-5 nm transistors. IBM demonstrated 2 nm with 50B transistors.", "d": "B"},
    {"q": "What are xenobots?", "o": ["Silicon nanorobots","Living robots from frog cells","AI nanosensors","Quantum devices"], "c": 1, "e": "Created 2020 from frog cells, designed by supercomputer. They move, self-heal, cooperate.", "d": "B"},
    {"q": "What causes gold nanoparticles to change color with size?", "o": ["Chemical reactions","Surface plasmon resonance","Oxidation","Crystal structure change"], "c": 1, "e": "SPR — collective electron oscillation on the nanoparticle surface shifts with size.", "d": "I"},
    {"q": "What is quantum confinement?", "o": ["Trapping light in a box","Discrete energy levels when material approaches de Broglie wavelength","Containing radiation","Limiting atom movement"], "c": 1, "e": "When dimensions approach electron wavelength, continuous bands become discrete levels, changing optical/electronic properties.", "d": "I"},
    {"q": "What does DNA origami create?", "o": ["Genetic sequences","2D/3D nanoscale shapes from DNA","Synthetic genes","Protein structures"], "c": 1, "e": "Paul Rothemund (2006) invented folding DNA into precise nanoscale shapes for machines and delivery.", "d": "I"},
    {"q": "Which microscope images individual atoms?", "o": ["Optical microscope","Electron microscope","Scanning Tunneling Microscope","X-ray microscope"], "c": 2, "e": "STM measures tunneling current between tip and surface at atomic resolution. Binnig & Rohrer, Nobel 1986.", "d": "I"},
    {"q": "What is a memristor?", "o": ["Memory stick","Resistor that remembers charge history","Microprocessor","Memory card"], "c": 1, "e": "Memristors mimic synaptic behavior, enabling neuromorphic computing 1000x more efficient than conventional processors.", "d": "I"},
    {"q": "What efficiency do perovskite solar cells achieve?", "o": ["10%","18%",">26%","35%"], "c": 2, "e": "Nanoscale perovskite cells exceed 26%, rivaling silicon at a fraction of the cost.", "d": "I"},
    {"q": "What can nanoparticles cross that most drugs cannot?", "o": ["Cell wall only","Blood-brain barrier","Nuclear membrane","Bone matrix"], "c": 1, "e": "Nanoparticles can cross the BBB, enabling drug delivery for Alzheimer's, Parkinson's, and brain tumors.", "d": "I"},
    {"q": "What did DeepMind's GNoME achieve?", "o": ["Built a nanorobot","Predicted 2.2M new crystal structures","Invented a CNT","Created a quantum computer"], "c": 1, "e": "AI predicted 2.2M crystal structures (380K synthesizable) — equivalent to ~800 years of experimental work.", "d": "I"},
    {"q": "What is the typical diameter range of a lipid nanoparticle used in mRNA vaccines?", "o": ["10-30 nm","50-100 nm","200-500 nm","1-5 nm"], "c": 1, "e": "LNPs used in mRNA vaccines are 50-100 nm — large enough to carry mRNA but small enough for efficient cellular uptake via endocytosis.", "d": "I"},
    {"q": "What are LNPs primarily composed of?", "o": ["Proteins","Lipid bilayers","Carbon","Silicon"], "c": 1, "e": "Lipid nanoparticles are spherical vesicles of lipid bilayers, 50-100 nm in diameter.", "d": "I"},
    {"q": "What is the de Broglie wavelength of an electron in a quantum dot?", "o": ["Much larger than the dot","Comparable to the dot size","Much smaller than the dot","Undefined"], "c": 1, "e": "Confinement occurs when the de Broglie wavelength ≈ particle size, causing discrete energy levels.", "d": "A"},
    {"q": "What determines if a CNT is metallic or semiconducting?", "o": ["Length","Chirality (roll-up angle)","Diameter","Temperature"], "c": 1, "e": "The (n,m) chirality indices determine band structure. 1/3 of orientations are metallic, 2/3 are semiconducting.", "d": "A"},
    {"q": "What is the Casimir effect?", "o": ["Light bending","Force between nanostructures from quantum vacuum fluctuations","Magnetic attraction","Chemical bonding"], "c": 1, "e": "Zero-point energy fluctuations in the quantum vacuum create measurable forces between closely spaced nanostructures.", "d": "A"},
    {"q": "What is a nitrogen-vacancy center in diamond?", "o": ["Diamond defect for jewelry","Quantum sensor operating at room temperature","Carbon impurity","Manufacturing defect"], "c": 1, "e": "NV centers enable room-temperature quantum sensing with nm spatial resolution — potential for cellular MRI.", "d": "A"},
    {"q": "In molecular beam epitaxy, what is grown?", "o": ["Bacteria","Crystal layers one atom at a time","DNA strands","Polymers"], "c": 1, "e": "MBE grows crystalline layers with atomic precision in ultra-high vacuum, essential for quantum devices.", "d": "A"},
    {"q": "What is the main challenge in scaling nanotech manufacturing?", "o": ["Too expensive","Properties don't always translate from lab to bulk","No demand","Too dangerous"], "c": 1, "e": "Nanoscale properties often depend on uniformity. Bulk manufacturing introduces defects that degrade performance.", "d": "A"},
    {"q": "What quantum computing architecture uses nanoscale defects?", "o": ["Superconducting only","Diamond NV centers","Optical only","Ion traps only"], "c": 1, "e": "Diamond NV centers are a leading room-temperature qubit platform for quantum computing and sensing.", "d": "A"},
    {"q": "What is Mie scattering in nanoparticles?", "o": ["Light absorption only","Size-dependent light scattering for particles > wavelength/10","Sound wave reflection","Electron diffraction"], "c": 1, "e": "For particles comparable to wavelength, Mie theory describes complex scattering patterns beyond simple Rayleigh scattering.", "d": "A"},
    {"q": "What self-assembly driving force is most common?", "o": ["Magnetic force","Thermodynamic free energy minimization","Gravity","Nuclear force"], "c": 1, "e": "Self-assembly is driven by systems minimizing Gibbs free energy — enthalpy and entropy contributions.", "d": "A"},
    {"q": "What is the Kondo effect in nanostructures?", "o": ["Superconductivity","Screening of magnetic impurities at low temperature","Light emission","Heat conduction"], "c": 1, "e": "In nanostructures, conduction electrons screen magnetic impurity spins, causing resistance minimum at low T.", "d": "A"},
    {"q": "What is the de Broglie wavelength of an electron moving at 1 × 10⁶ m/s?", "o": ["~0.73 nm", "~7.3 nm", "~0.073 nm", "~73 nm"], "c": 0, "e": "λ = h/(mv) = 6.626e-34/(9.109e-31 × 1e6) ≈ 0.727 nm — comparable to atomic spacing.", "d": "I"},
    {"q": "For a particle in a 1D box, the ground state energy E₁ is proportional to:", "o": ["1/L", "1/L²", "L²", "1/√L"], "c": 1, "e": "E₁ = π²ℏ²/(2mL²) ∝ 1/L². Halving the box width quadruples the ground state energy.", "d": "I"},
    {"q": "What condition must be met for Coulomb blockade to be observable?", "o": ["E_c > ℏω", "E_c > kT", "E_c > mc²", "E_c > hf"], "c": 1, "e": "The charging energy must exceed thermal energy: E_c = e²/(2C) > kT ≈ 26 meV at room temperature.", "d": "A"},
    {"q": "In the Drude model, the plasma frequency ωp depends on:", "o": ["Temperature only", "Electron density n and effective mass m*", "Wavelength of incident light", "Size of the nanoparticle"], "c": 1, "e": "ωp = √(ne²/ε₀m*). Higher electron density and lower effective mass give higher plasma frequency.", "d": "I"},
    {"q": "A carbon nanotube with chirality (n,m) is metallic if:", "o": ["n = m", "(2n + m) mod 3 = 0", "n > m", "(n + m) mod 2 = 0"], "c": 1, "e": "When (2n+m) is divisible by 3, the band gap closes and the CNT is metallic. Otherwise it's semiconducting.", "d": "A"},
    {"q": "What is the quantum of conductance G₀?", "o": ["e²/h", "2e²/h", "h/e²", "h/2e²"], "c": 1, "e": "G₀ = 2e²/h ≈ 77.5 µS (factor of 2 for spin). This is the Landauer formula's conductance per channel.", "d": "A"},
    {"q": "The Stokes-Einstein relation gives diffusion coefficient D as:", "o": ["D = kT/(3πηr)", "D = kT/(6πηr)", "D = kT/(πηr)", "D = 2kT/(3πηr)"], "c": 1, "e": "D = kT/(6πηr). Larger particles and higher viscosity reduce diffusion. Higher temperature increases it.", "d": "I"},
    {"q": "What determines if a metamaterial has negative refractive index?", "o": ["Only ε < 0", "Only μ < 0", "Both ε < 0 and μ < 0", "High refractive index > 3"], "c": 2, "e": "n = -√(εμ). Both permittivity and permeability must be negative simultaneously for negative refraction.", "d": "A"},
    {"q": "The tunneling probability T ≈ exp(-2κL) depends on barrier:", "o": ["Width linearly", "Width exponentially and height via square root", "Height linearly only", "Neither width nor height"], "c": 1, "e": "κ = √(2m(V-E))/ℏ, so T depends exponentially on barrier width and exponentially on √(barrier height).", "d": "I"},
    {"q": "What is the Kubo gap?", "o": ["Energy gap in semiconductors", "Level spacing in small metallic nanoparticles", "Bandgap of graphene", "Superconducting gap"], "c": 1, "e": "δ = 4E_F/(3N). As metallic particles shrink below ~2 nm, discrete level spacing becomes significant.", "d": "A"},
    {"q": "In a quantum dot, the density of states is:", "o": ["Continuous ∝ √E", "Step function", "Discrete delta functions", "∝ 1/√E"], "c": 2, "e": "In 0D (fully confined), D(E) is a series of discrete peaks — like an artificial atom.", "d": "A"},
    {"q": "The Purcell enhancement factor for a photonic crystal cavity scales as:", "o": ["Q × V", "Q/V", "V/Q", "√(Q/V)"], "c": 1, "e": "F_P = (3/4π²)(λ/n)³(Q/V). High Q and small mode volume V give large enhancement.", "d": "A"},
    {"q": "Memristance M(q) relates which quantities?", "o": ["Voltage and current", "Magnetic flux and charge", "Resistance and capacitance", "Electric field and displacement"], "c": 1, "e": "M(q) = dΦ_m/dq. The memristor links magnetic flux linkage Φ_m to charge q — the missing circuit element.", "d": "I"},
    {"q": "Giant magnetoresistance (GMR) occurs in structures with:", "o": ["Single ferromagnetic layer", "Alternating ferromagnetic/non-magnetic nanolayers", "Superconducting layers", "Dielectric multilayers"], "c": 1, "e": "GMR requires multilayers of ferromagnetic (Co, Fe, Ni) and non-magnetic (Cr, Cu) metals, each a few nm thick.", "d": "I"},
    {"q": "The Mie scattering parameter x = 2πr/λ indicates which regime when x << 1?", "o": ["Geometric optics", "Mie regime", "Rayleigh regime", "Resonance regime"], "c": 2, "e": "x << 1 is the Rayleigh regime where scattering ∝ λ⁻⁴. x ≈ 1 is Mie regime, x >> 1 is geometric optics.", "d": "A"},
    {"q": "At the nanoscale, what is the Reynolds number typically?", "o": ["10^3 - 10^5 (turbulent)", "10^-5 - 10^-2 (viscous dominated)", "1 - 10 (transitional)", "0 (no fluid flow)"], "c": 1, "e": "At the nanoscale, Re = rho*v*L/eta is extremely small (10^-5 to 10^-2), meaning viscous forces completely dominate over inertia. There is no coasting.", "d": "I"},
    {"q": "What is the Stokes drag force on a nanobot?", "o": ["F = ma", "F = 6 pi eta r v", "F = kT/r", "F = eE"], "c": 1, "e": "F_drag = 6 pi eta r v (Stokes' law). For a 500 nm nanobot at 10 um/s in water, this is ~8.4 x 10^-14 N — about the force of one kinesin motor.", "d": "I"},
    {"q": "What does the Peclet number (Pe = vL/D) tell us about a nanobot?", "o": ["Its temperature", "Whether propulsion or diffusion dominates motion", "Its magnetic moment", "Its chemical reactivity"], "c": 1, "e": "Pe >> 1 means active propulsion dominates. Pe << 1 means Brownian diffusion dominates. Pe ~ 1 means both are comparable — making navigation challenging.", "d": "I"},
    {"q": "What is the 'scallop theorem' in nanobot locomotion?", "o": ["Nanobots cannot swim at all", "Reciprocal motion cannot produce net displacement at low Reynolds number", "Nanobots can only move in circles", "Only biological nanobots can swim"], "c": 1, "e": "At low Re, any reciprocal (time-reversible) motion produces zero net displacement. Nanobots must use non-reciprocal motion (corkscrews, flexible tails) to swim.", "d": "I"},
    {"q": "How does a DNA nanobot perform computation?", "o": ["Using silicon transistors", "Through strand displacement reactions implementing Boolean logic", "By emitting light pulses", "Through magnetic switching"], "c": 1, "e": "DNA strand displacement: an input strand invades a complex, displacing a bound strand and triggering cascades. This implements AND, OR, NOT gates entirely in DNA chemistry.", "d": "A"},
    {"q": "What is PEGylation in nanobot design?", "o": ["Adding PEG molecules to resist protein adsorption and immune clearance", "Embedding gold in the nanobot shell", "Programming DNA sequences", "Attaching magnetic particles"], "c": 0, "e": "PEGylation coats nanoparticles with polyethylene glycol chains, making them 'stealthy' by resisting opsonin adsorption. This extends circulation half-life from minutes to 15-20 hours.", "d": "A"},
    {"q": "What equation governs the self-replication of nanobots?", "o": ["N(t) = N0 + kt", "N(t) = N0 x 2^(t/T_rep)", "N(t) = N0 e^(-kt)", "N(t) = N0 sin(wt)"], "c": 1, "e": "Exponential doubling: N(t) = N0 x 2^(t/T_rep). With T_rep = 100s, one nanobot becomes 10^12 in just 40 minutes. This is both promise and peril.", "d": "A"},
    {"q": "What is the dissociation constant Kd in nanobot sensing?", "o": ["The speed of nanobot motion", "Kd = [A][B]/[AB] — measures binding affinity (lower = tighter binding)", "The energy required for propulsion", "The diffusion coefficient of the nanobot"], "c": 1, "e": "Kd = k_off/k_on. Strong antibodies have Kd ~ 10^-9 to 10^-12 M. A nanobot sensor is most sensitive when the target concentration equals Kd.", "d": "I"},
    {"q": "How do magnetic nanobots achieve propulsion?", "o": ["Solar panels", "External rotating magnetic fields cause helical nanobots to spin like corkscrews", "Internal combustion", "Electric motors"], "c": 1, "e": "Helical magnetic nanobots rotate in response to external rotating magnetic fields, propelling themselves through viscous fluid. Magnetic fields penetrate tissue deeply and safely.", "d": "I"},
    {"q": "What is the fundamental speed limit for chemical communication between nanobots?", "o": ["Speed of light", "Set by diffusion: t ~ d^2 / (2D), about 5 seconds for 100 um", "Speed of sound", "Unlimited"], "c": 1, "e": "Chemical signals diffuse. For D = 10^-9 m^2/s, a signal travels 100 um in ~5 seconds. This limits how fast nanobot swarms can coordinate.", "d": "A"},
    {"q": "What makes a nanobot different from a nanoparticle?", "o": ["Its size", "A nanobot senses, decides, and acts actively; a nanoparticle is passive", "Its color", "Its material composition"], "c": 1, "e": "Nanoparticles are passive (a gold NP absorbs light, an LNP carries drugs). Nanobots are active machines that can make autonomous decisions and perform complex tasks.", "d": "B"},
    {"q": "How much energy does one ATP hydrolysis release?", "o": ["~5 x 10^-20 J", "~5 x 10^-10 J", "~5 x 10^-30 J", "~5 x 10^-5 J"], "c": 0, "e": "One ATP molecule releases about 5 x 10^-20 J (or ~20 kT at body temperature). A nanobot moving at 10 um/s needs roughly 1 ATP/s — remarkably efficient.", "d": "I"},
    {"q": "What is the typical steering precision of magnetic nanobots today?", "o": ["1 nm", "~100 micrometers", "1 mm", "10 cm"], "c": 1, "e": "Current magnetic steering achieves ~100 um precision — sufficient for targeting tumors but not individual cells. Improving this is a major research goal.", "d": "I"},
    {"q": "What was significant about the 2021 xenobot self-replication?", "o": ["They used DNA", "Kinematic self-replication without copying genetic material — gathering loose cells to assemble copies", "They were made of metal", "They replicated infinitely"], "c": 1, "e": "Xenobots gathered loose frog cells and assembled them into new xenobots — kinematic self-replication never seen in known organisms. Limited to one generation.", "d": "I"},
    {"q": "What does the Hill coefficient (n) in genetic circuits control?", "o": ["Nanobot size", "Sharpness of the switching response — higher n means more digital (all-or-none) behavior", "Swarm speed", "Binding affinity"], "c": 1, "e": "With Hill coefficient n = 2-4, genetic circuits achieve sharp switching — essentially digital logic gates. Higher n means a more abrupt transition from OFF to ON.", "d": "A"},
]


GLOSSARY_DATA = [
    ("Nanometer (nm)", "A unit of length equal to 10⁻⁹ meters. Roughly 3-4 atoms wide. Human hair ≈ 80,000 nm."),
    ("Nanoparticle", "Particle 1-100 nm with unique properties from quantum effects and high surface-area-to-volume ratio."),
    ("Nanorobot / Nanite", "Theoretical/experimental microscopic machine (0.1-10 µm) for nanoscale tasks."),
    ("Carbon Nanotube (CNT)", "Cylindrical carbon molecule. 100+ GPa strength, exceptional conductivity. SWCNT or MWCNT."),
    ("Graphene", "Single-atom-thick 2D carbon sheet. Thinnest, strongest, most conductive material known."),
    ("Quantum Dot", "Semiconductor nanocrystal (2-10 nm) with size-tunable fluorescence."),
    ("Buckminsterfullerene (C₆₀)", "60 carbon atoms in soccer-ball shape. Discovered 1985, Nobel 1996."),
    ("DNA Origami", "Folding DNA into 2D/3D nanoscale shapes. Invented by Rothemund, 2006."),
    ("Lipid Nanoparticle (LNP)", "50-100 nm lipid vesicle for molecular delivery. Key to mRNA vaccines."),
    ("Scanning Tunneling Microscope (STM)", "Atomic-resolution imaging via tunneling current. Binnig & Rohrer, 1981."),
    ("Top-Down Fabrication", "Carving nanostructures from bulk material (lithography, etching)."),
    ("Bottom-Up Fabrication", "Building atom by atom (self-assembly, CVD, MBE)."),
    ("Grey Goo", "Drexler's hypothetical scenario of self-replicating nanomachines. Science fiction."),
    ("Photothermal Therapy", "Using light-absorbing nanoparticles (gold) to destroy cancer cells with heat."),
    ("Memristor", "Resistor remembering charge history. Enables neuromorphic computing. HP Labs, 2008."),
    ("Perovskite", "ABX₃ crystal for >26% efficient nanoscale solar cells at low cost."),
    ("Self-Assembly", "Components spontaneously organizing into ordered structures via thermodynamic minimization."),
    ("Blood-Brain Barrier (BBB)", "Selective barrier nanoparticles can cross for brain drug delivery."),
    ("CRISPR-Cas9", "Gene-editing tool. Nanoparticle delivery enables in vivo genetic modifications."),
    ("Surface Plasmon Resonance (SPR)", "Collective electron oscillation on nanoparticle surfaces. Causes gold NP colors."),
    ("Quantum Confinement", "Discrete energy levels when material size ≈ de Broglie wavelength. Changes optical/electronic properties."),
    ("Chirality (CNT)", "(n,m) indices determining if a carbon nanotube is metallic or semiconducting."),
    ("NV Center", "Nitrogen-vacancy defect in diamond for room-temperature quantum sensing at nm resolution."),
    ("Kondo Effect", "Screening of magnetic impurities in nanostructures causing resistance minimum at low temperature."),
    ("Mie Scattering", "Size-dependent light scattering for nanoparticles comparable to light wavelength."),
    ("de Broglie Wavelength", "The wavelength λ = h/p associated with a particle of momentum p. At the nanoscale, this wavelength becomes comparable to structure sizes, making quantum effects significant."),
    ("Heisenberg Uncertainty Principle", "The fundamental limit Δx·Δp ≥ ℏ/2 on simultaneously knowing position and momentum. Directly causes quantum confinement effects in nanostructures."),
    ("Particle in a Box", "Quantum mechanics model where a particle is confined to a region of width L, yielding discrete energy levels E_n = n²π²ℏ²/(2mL²)."),
    ("Coulomb Blockade", "Suppression of electron tunneling at low temperatures due to the discrete charging energy E_c = e²/(2C) of a nanoscale island."),
    ("Drude Model", "Classical model of metal optical properties: ε(ω) = 1 - ωp²/(ω²+iγω). Describes plasma frequency, damping, and frequency-dependent dielectric response."),
    ("Mie Scattering", "Exact analytical solution to Maxwell's equations for light scattering by spherical particles of any size. Key parameter: x = 2πr/λ."),
    ("Surface Plasmon Polariton", "Electromagnetic wave coupled to electron oscillations propagating along a metal-dielectric interface. Enables sub-diffraction-limit light confinement."),
    ("Photonic Crystal", "Nanostructured material with periodic dielectric constant, creating photonic bandgaps that control light propagation like semiconductor bandgaps control electrons."),
    ("Spintronics", "Electronics that exploits electron spin in addition to charge. Key phenomena include GMR, TMR, spin Hall effect, and topological insulator surface states."),
    ("Metamaterial", "Artificial nanostructured material with optical/electromagnetic properties not found in nature, such as negative refractive index from engineered ε and μ."),
    ("Stokes Drag", "F = 6πηrv. The viscous drag on a spherical nanoparticle of radius r moving at velocity v through fluid of viscosity η. Dominant force at the nanoscale."),
    ("Reynolds Number (Re)", "Re = ρvL/η. At nanoscale Re ~ 10^-5 to 10^-2, meaning viscous forces completely dominate. No inertia, no coasting."),
    ("Peclet Number (Pe)", "Pe = vL/D. Ratio of advective to diffusive transport. Determines whether a nanobot's active propulsion or Brownian diffusion dominates its motion."),
    ("Scallop Theorem", "Purcell's principle: at low Reynolds number, any time-reversible (reciprocal) motion produces zero net displacement. Nanobots must use non-reciprocal gaits."),
    ("PEGylation", "Coating nanoparticles with polyethylene glycol to create a hydration layer that resists protein adsorption. Extends circulation half-life from minutes to 15-20 hours."),
    ("Quorum Sensing", "Cell-to-cell communication via diffusible signaling molecules. When concentration exceeds a threshold, population-level behavior is triggered. Key concept for nanobot swarm coordination."),
    ("Chemotaxis", "Directed movement along a chemical gradient. At the nanoscale, gradient detection is limited by receptor binding noise. Bacteria detect gradients as shallow as ~1% over their body length."),
    ("DNA Strand Displacement", "A DNA computation mechanism where an input strand invades and displaces a bound strand from a double-stranded complex, implementing logic gates in DNA chemistry."),
    ("Dissociation Constant (Kd)", "Kd = k_off/k_on = [A][B]/[AB]. Measures molecular binding affinity. Lower Kd = tighter binding. Nanobot sensors are most sensitive when target concentration ~ Kd."),
    ("Hill Coefficient", "Cooperativity parameter n in the Hill equation. Higher n (2-4) produces sharper switching in genetic circuits, enabling digital-like logic from analog biological components."),
]

# ─── Content pages config ──────────────────────────────
CONTENT_PAGES = [
    ("📏", "Introduction", [(INTRO_B,"Beginner"),(INTRO_I,"Intermediate"),(INTRO_A,"Advanced")]),
    ("🤖", "Nanites", [(NANITES_B,"Beginner"),(NANITES_I,"Intermediate"),(NANITES_A,"Advanced")]),
    ("💊", "Applications", [(APPS_B,"Beginner"),(APPS_I,"Intermediate"),(APPS_A,"Advanced")]),
    ("📜", "History", [(HISTORY_B,"Beginner"),(HISTORY_I,"Intermediate"),(HISTORY_A,"Advanced")]),
    ("🧪", "Safety & Ethics", [(SAFETY_B,"Beginner"),(SAFETY_I,"Intermediate"),(SAFETY_A,"Advanced")]),
    ("🚀", "The Future", [(FUTURE_B,"Beginner"),(FUTURE_I,"Intermediate"),(FUTURE_A,"Advanced")]),
    ("⚛️", "Quantum Mechanics", [(QUANTUM_B,"Beginner"),(QUANTUM_I,"Intermediate"),(QUANTUM_A,"Advanced")]),
    ("💾", "Nanoelectronics", [(NANOELEC_B,"Beginner"),(NANOELEC_I,"Intermediate"),(NANOELEC_A,"Advanced")]),
    ("🌈", "Nanophotonics", [(NANOPHOTO_B,"Beginner"),(NANOPHOTO_I,"Intermediate"),(NANOPHOTO_A,"Advanced")]),
]

NAV_ITEMS = [
    ("🏠", "Home"),
    ("📏", "Introduction"),
    ("🤖", "Nanites"),
    ("💊", "Applications"),
    ("📜", "History"),
    ("🧪", "Safety & Ethics"),
    ("🚀", "The Future"),
    ("⚛️", "Quantum Mech"),
    ("💾", "Nanoelectronics"),
    ("🌈", "Nanophotonics"),
    ("🔍", "Size Explorer"),
    ("🎨", "Nanoparticle Lab"),
    ("🔌", "Quantum Sim"),
    ("🌊", "Brownian Motion"),
    ("🔗", "CNT Explorer"),
    ("🃏", "Flashcards"),
    ("🧩", "Matching Game"),
    ("🧠", "Quiz"),
    ("📖", "Glossary"),
    ("💉", "Drug Release Sim"),
    ("📐", "Surface Area Calc"),
    ("📋", "Equations"),
    ("🤖", "Swarm Sim"),
    ("🧠", "Design Lab"),
    ("⭐", "Achievements"),
    ("📑", "Bookmarks"),
    ("📝", "My Notes"),
    ("📊", "Dashboard"),
]

class CanvasCircle(QWidget):
    """Custom widget that draws a colored circle (for nanoparticle lab)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._color = QColor("#CC2936")
        self._size_nm = 20
        self.setFixedSize(200, 200)

    def set_color(self, hex_color, size_nm):
        self._color = QColor(hex_color)
        self._size_nm = size_nm
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Glow
        glow = QRadialGradient(100, 100, 95)
        glow.setColorAt(0, QColor(self._color))
        glow.setColorAt(0.7, QColor(self._color.red(), self._color.green(), self._color.blue(), 80))
        glow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(glow))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(5, 5, 190, 190)
        # Core
        display = min(max(self._size_nm * 1.5, 30), 120)
        core = QRadialGradient(100 - display*0.15, 100 - display*0.15, display*0.6)
        core.setColorAt(0, QColor(255, 255, 255, 60))
        core.setColorAt(0.5, QColor(self._color))
        core.setColorAt(1, QColor(self._color.red()//2, self._color.green()//2, self._color.blue()//2))
        p.setBrush(QBrush(core))
        p.drawEllipse(int(100-display), int(100-display), int(display*2), int(display*2))
        p.end()


class ScaleBarWidget(QWidget):
    """Draws a proportional scale comparison bar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._entries = []
        self.setFixedHeight(60)

    def set_entries(self, entries):
        self._entries = entries
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        if not self._entries:
            p.end(); return
        # Find range
        log_min = math.log10(self._entries[0][0])
        log_max = math.log10(self._entries[-1][0])
        log_range = log_max - log_min if log_max != log_min else 1
        bar_y = 30
        # Draw bar background
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(33, 38, 45))
        p.drawRoundedRect(10, bar_y, w-20, 12, 6, 6)
        # Draw gradient bar
        grad = QLinearGradient(10, 0, w-10, 0)
        grad.setColorAt(0, QColor(163, 113, 247))
        grad.setColorAt(0.3, QColor(88, 166, 255))
        grad.setColorAt(0.6, QColor(126, 231, 135))
        grad.setColorAt(1, QColor(139, 148, 158))
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(10, bar_y, w-20, 12, 6, 6)
        # Draw markers
        p.setPen(QPen(QColor(240, 246, 252), 1))
        for size_val, name, _, _, color in self._entries:
            frac = (math.log10(size_val) - log_min) / log_range
            x = int(10 + frac * (w - 20))
            p.drawLine(x, bar_y - 4, x, bar_y + 16)
        p.end()


# ═══════════════════════════════════════════════════════════
#  PAGE: Home
# ═══════════════════════════════════════════════════════════

def make_card(layout, emoji, title, body):
    card = QFrame(); card.setObjectName("infoCard")
    cl = QHBoxLayout(card); cl.setContentsMargins(14,12,14,12)
    icon = QLabel(emoji); icon.setObjectName("cardEmoji"); icon.setFixedSize(36,36); icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
    tl = QVBoxLayout(); tl.setSpacing(2)
    t = QLabel(title); t.setObjectName("cardTitle")
    b = QLabel(body); b.setObjectName("cardBody"); b.setWordWrap(True)
    tl.addWidget(t); tl.addWidget(b)
    cl.addWidget(icon); cl.addLayout(tl, 1)
    layout.addWidget(card)

class HomePage(QWidget):
    def __init__(self, nav_callback=None):
        super().__init__()
        self.nav_callback = nav_callback
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        banner = QFrame()
        banner.setStyleSheet("QFrame{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0d1b3e,stop:0.5 #161b22,stop:1 #0d1b3e);border:1px solid #21262d;border-radius:12px;}")
        bl = QVBoxLayout(banner); bl.setContentsMargins(28,24,28,24); bl.setSpacing(6)
        t = QLabel("🔬  Welcome to NanoLearn v5"); t.setStyleSheet("color:#58a6ff;font-size:22px;font-weight:bold;")
        s = QLabel("Your interactive guide to nanotechnology & nanobots — beginner to advanced, with 2 new nanobot simulators, expanded content, flashcards, games, and quizzes."); s.setStyleSheet("color:#c9d1d9;font-size:13px;"); s.setWordWrap(True)
        bl.addWidget(t); bl.addWidget(s); layout.addWidget(banner); layout.addSpacing(16)

        # Learning path
        path_frame = QFrame(); path_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        pl = QVBoxLayout(path_frame); pl.setContentsMargins(16,14,16,14); pl.setSpacing(8)
        pt = QLabel("📍  Learning Path"); pt.setStyleSheet("color:#58a6ff;font-size:15px;font-weight:bold;")
        pd = QLabel("Each content page has 3 difficulty levels. Start with Beginner, progress through Intermediate, then tackle Advanced. Use the interactive tools to explore concepts hands-on.")
        pd.setStyleSheet("color:#8b949e;font-size:12px;"); pd.setWordWrap(True)
        pl.addWidget(pt); pl.addWidget(pd); layout.addWidget(path_frame); layout.addSpacing(12)

        cards = QVBoxLayout(); cards.setSpacing(8)
        make_card(cards, "📏", "Introduction + Size Explorer", "Learn the fundamentals, then interactively explore the scale of the nanoworld with the Size Explorer slider.")
        make_card(cards, "🤖", "Nanites & Nanoparticle Lab", "Understand nanorobots from DNA origami to xenobots. Experiment with the Nanoparticle Color Lab to see quantum effects live.")
        make_card(cards, "🃏", "Flashcards & Matching Game", "Memorize 20 key terms with flip-to-reveal flashcards. Test your connections with the matching puzzle.")
        make_card(cards, "🧠", "Quiz (30 Questions, 3 Levels)", "Test your knowledge with filtered quizzes. Review mistakes and track your best scores on the Dashboard.")
        make_card(cards, "📝", "Personal Notes", "Take notes on each topic. All notes are auto-saved locally for your next session.")
        make_card(cards, "📊", "Progress Dashboard", "Track pages visited, quiz scores, flashcards mastered, and your overall learning progress.")
        make_card(cards, "⚛️", "Quantum Mech + Simulator", "Learn quantum mechanics at the nanoscale with equations like E_n = n²π²ℏ²/(2mL²). Use the Quantum Confinement Simulator to see energy levels shift live.")
        make_card(cards, "🌊", "Brownian Motion Sim", "Watch nanoparticles jiggle due to thermal collisions. Adjust temperature and particle size to see the Stokes-Einstein relation in action.")
        make_card(cards, "🔗", "CNT Chirality Explorer", "Input (n,m) chirality indices and discover if a carbon nanotube is metallic or semiconducting. See the chiral vector on a graphene lattice.")
        make_card(cards, "💉", "Drug Release Simulator", "Compare Higuchi, zero-order, and first-order drug release kinetics with adjustable parameters and live plots.")
        make_card(cards, "📐", "Surface Area Calculator", "See why nanoparticles are so reactive — visualize the enormous surface-area-to-volume ratio difference.")
        make_card(cards, "⭐", "Achievements & Bookmarks", "Unlock badges as you learn. Bookmark key pages for quick revisits. Rate your confidence on each topic.")
        make_card(cards, "📝", "Personal Notes", "Take notes on each topic. All notes are auto-saved locally for your next session.")
        make_card(cards, "🤖", "Nanobot Swarm Simulator", "Watch nanobots navigate through body fluid! Compare swarm intelligence, Brownian motion, and chemotaxis. See how coordination improves tumor targeting.")
        make_card(cards, "🧠", "Nanobot Design Lab", "Explore 5 real nanobot architectures: DNA nanobots, magnetic swimmers, biological hybrids, gold nanoshells, and lipid nanoparticles with live equations.")
        layout.addLayout(cards); layout.addStretch()

# ═══════════════════════════════════════════════════════════
#  PAGE: Content with Difficulty Tabs
# ═══════════════════════════════════════════════════════════

class TabbedContentPage(QWidget):
    def __init__(self, title, icon, levels, page_id, notes_data, progress_data):
        super().__init__()
        self.page_id = page_id
        self.notes_data = notes_data
        self.progress_data = progress_data
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)

        header = QHBoxLayout()
        il = QLabel(icon); il.setStyleSheet("font-size:26px;")
        tl = QLabel(title); tl.setObjectName("pageTitle"); tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        # Difficulty badge
        diff_label = QLabel("  B / I / A  ")
        diff_label.setStyleSheet("background:#1f6feb;color:white;border-radius:12px;padding:3px 10px;font-size:11px;font-weight:bold;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(diff_label)
        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        for html, label in levels:
            browser = QTextBrowser(); browser.setObjectName("contentText")
            browser.setHtml(html); browser.setOpenExternalLinks(False)
            self.tabs.addTab(browser, label)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

        # Self-assessment
        assess_frame = QFrame(); assess_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px 12px;}")
        afl = QHBoxLayout(assess_frame); afl.setSpacing(8)
        at = QLabel("Rate your understanding:"); at.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        afl.addWidget(at)
        self.rating_btns = []
        for i in range(1, 6):
            btn = QPushButton("★" * i); btn.setFixedSize(80, 28)
            current = self.progress_data.get("ratings", {}).get(page_id, 0)
            btn.setStyleSheet(f"QPushButton{{background:{'#23863622' if i <= current else '#0d1117'};color:{'#7ee787' if i <= current else '#484f58'};border:1px solid {'#238636' if i <= current else '#21262d'};border-radius:6px;font-size:12px;}}")
            btn.clicked.connect(lambda checked, rating=i, b=btn: self._rate(rating))
            afl.addWidget(btn); self.rating_btns.append((btn, i))
        afl.addStretch()
        layout.addWidget(assess_frame)

        # Notes section
        notes_frame = QFrame(); notes_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        nfl = QVBoxLayout(notes_frame); nfl.setContentsMargins(12,10,12,10); nfl.setSpacing(6)
        nt = QLabel("📝  My Notes on this Topic"); nt.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.note_area = QTextEdit(); self.note_area.setObjectName("noteArea")
        self.note_area.setPlaceholderText("Type your notes here... They are auto-saved.")
        self.note_area.setMaximumHeight(120)
        saved = self.notes_data.get(page_id, "")
        if saved: self.note_area.setPlainText(saved)
        self.note_area.textChanged.connect(self._save_note)
        nfl.addWidget(nt); nfl.addWidget(self.note_area)
        layout.addWidget(notes_frame)
        layout.addStretch()

        # Mark page visited
        if "visited" not in self.progress_data:
            self.progress_data["visited"] = []
        if page_id not in self.progress_data["visited"]:
            self.progress_data["visited"].append(page_id)
        # Track highest tab
        if "max_tab" not in self.progress_data:
            self.progress_data["max_tab"] = {}
        self._on_tab_changed(0)

    def _rate(self, rating):
        self.progress_data.setdefault("ratings", {})[self.page_id] = rating
        for btn, i in self.rating_btns:
            if i <= rating:
                btn.setStyleSheet("QPushButton{background:#23863622;color:#7ee787;border:1px solid #238636;border-radius:6px;font-size:12px;}")
            else:
                btn.setStyleSheet("QPushButton{background:#0d1117;color:#484f58;border:1px solid #21262d;border-radius:6px;font-size:12px;}")

    def _on_tab_changed(self, idx):
        tab_names = ["Beginner", "Intermediate", "Advanced"]
        if 0 <= idx < len(tab_names):
            key = f"{self.page_id}_tab"
            current = self.progress_data.get("max_tab", {}).get(key, 0)
            if idx > current:
                self.progress_data.setdefault("max_tab", {})[key] = idx

    def _save_note(self):
        self.notes_data[self.page_id] = self.note_area.toPlainText()
        save_json(NOTES_FILE, self.notes_data)

# ═══════════════════════════════════════════════════════════
#  PAGE: Size Scale Explorer (Interactive)
# ═══════════════════════════════════════════════════════════

class SizeExplorerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🔍"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Interactive Size Scale Explorer"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Drag the slider to explore objects at different scales — from a single atom (0.1 nm) to a human hair (80,000 nm). Watch how properties change as you zoom through the nanoscale.")
        desc.setStyleSheet("color:#8b949e;font-size:13px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Scale bar
        self.scale_bar = ScaleBarWidget()
        self.scale_bar.set_entries([(s,n,_,_,c) for s,n,_,_,c in SCALE_DATA])
        layout.addWidget(self.scale_bar)

        # Slider
        sl_layout = QHBoxLayout(); sl_layout.setSpacing(16)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, len(SCALE_DATA)-1)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self._on_slider)
        sl_layout.addWidget(QLabel("0.1 nm")); sl_layout.addWidget(self.slider, 1); sl_layout.addWidget(QLabel("80 µm"))
        layout.addLayout(sl_layout)

        # Info display
        self.info_frame = QFrame(); self.info_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:20px;}")
        self.info_layout = QVBoxLayout(self.info_frame); self.info_layout.setSpacing(10)
        self.name_label = QLabel(); self.name_label.setStyleSheet("font-size:22px;font-weight:bold;")
        self.size_label = QLabel(); self.size_label.setStyleSheet("color:#58a6ff;font-size:16px;font-weight:bold;")
        self.desc_label = QLabel(); self.desc_label.setStyleSheet("color:#c9d1d9;font-size:13px;line-height:1.6;"); self.desc_label.setWordWrap(True)
        # Comparison
        self.comp_label = QLabel(); self.comp_label.setStyleSheet("color:#8b949e;font-size:12px;font-style:italic;"); self.comp_label.setWordWrap(True)
        self.info_layout.addWidget(self.name_label); self.info_layout.addWidget(self.size_label)
        self.info_layout.addWidget(self.desc_label); self.info_layout.addWidget(self.comp_label)
        layout.addWidget(self.info_frame)
        layout.addStretch()
        self._on_slider(0)

    def _on_slider(self, idx):
        size, name, size_str, desc, color = SCALE_DATA[idx]
        self.name_label.setText(f"<span style='color:{color}'>{name}</span>")
        self.size_label.setText(f"Size: {size_str}  ({size:,} nm)")
        self.desc_label.setText(desc)
        # Comparison
        comparisons = []
        hair_ratio = 80000 / size
        if hair_ratio > 1:
            if hair_ratio > 1000:
                comparisons.append(f"You could fit ~{hair_ratio:,.0f} of these across a human hair")
            else:
                comparisons.append(f"About {hair_ratio:,.0f}x smaller than a human hair")
        if idx > 0:
            prev_size = SCALE_DATA[idx-1][0]
            ratio = size / prev_size
            comparisons.append(f"{ratio:.0f}x larger than {SCALE_DATA[idx-1][1]}")
        if idx < len(SCALE_DATA)-1:
            next_size = SCALE_DATA[idx+1][0]
            ratio = next_size / size
            comparisons.append(f"{ratio:.0f}x smaller than {SCALE_DATA[idx+1][1]}")
        self.comp_label.setText(" | ".join(comparisons))

# ═══════════════════════════════════════════════════════════
#  PAGE: Nanoparticle Color Lab (Interactive)
# ═══════════════════════════════════════════════════════════

class NanoparticleLabPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🎨"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Nanoparticle Color Lab"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Explore how quantum confinement changes the color of gold nanoparticles! Drag the slider to change the particle size and watch the color shift — a real quantum mechanical effect called surface plasmon resonance.")
        desc.setStyleSheet("color:#8b949e;font-size:13px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Main area: circle + controls side by side
        main_area = QHBoxLayout(); main_area.setSpacing(20)

        # Left: circle display
        left = QVBoxLayout(); left.setSpacing(10)
        circle_frame = QFrame(); circle_frame.setStyleSheet("QFrame{background:#010409;border:1px solid #21262d;border-radius:12px;}")
        cl = QVBoxLayout(circle_frame); cl.setContentsMargins(20,20,20,20); cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.circle = CanvasCircle(); cl.addWidget(self.circle, 0, Qt.AlignmentFlag.AlignCenter)
        self.circle_size_label = QLabel("20 nm"); self.circle_size_label.setStyleSheet("color:#f0f6fc;font-size:18px;font-weight:bold;")
        self.circle_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.circle_size_label)
        left.addWidget(circle_frame)
        main_area.addLayout(left, 1)

        # Right: slider + info
        right = QVBoxLayout(); right.setSpacing(12)
        sl_frame = QFrame(); sl_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        rl = QVBoxLayout(sl_frame); rl.setSpacing(12)
        st = QLabel("Particle Diameter"); st.setStyleSheet("color:#58a6ff;font-size:14px;font-weight:bold;")
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(5, 100)
        self.slider.setValue(20)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(5)
        self.slider.valueChanged.connect(self._on_slider)
        self.size_display = QLabel("20 nm"); self.size_display.setStyleSheet("color:#f0f6fc;font-size:16px;font-weight:bold;")
        self.size_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(st); rl.addWidget(self.slider); rl.addWidget(self.size_display)
        right.addWidget(sl_frame)

        # Info box
        info_frame = QFrame(); info_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        il2 = QVBoxLayout(info_frame); il2.setSpacing(8)
        self.color_name = QLabel(); self.color_name.setStyleSheet("font-size:16px;font-weight:bold;")
        self.explanation = QLabel(); self.explanation.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.6;"); self.explanation.setWordWrap(True)
        # Physics note
        physics = QLabel("⚡ <b>Physics:</b> As gold nanoparticles shrink below ~100 nm, the mean free path of electrons becomes comparable to the particle size. This restricts electron movement, shifting the surface plasmon resonance frequency and changing the observed color.")
        physics.setStyleSheet("color:#8b949e;font-size:11px;border-left:3px solid #f78166;padding:8px 12px;background:#1c2333;border-radius:0 6px 6px 0;")
        physics.setWordWrap(True)
        il2.addWidget(self.color_name); il2.addWidget(self.explanation); il2.addWidget(physics)
        right.addWidget(info_frame)
        right.addStretch()
        main_area.addLayout(right, 1)
        layout.addLayout(main_area)

        # Size comparison strip
        strip_frame = QFrame(); strip_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        strl = QHBoxLayout(strip_frame); strl.setSpacing(6)
        strl.addWidget(QLabel("Scale:")); strl.addWidget(QLabel("Atom"))
        # Draw mini color dots
        for sz, col, name, _ in GOLD_NP_DATA:
            dot = QLabel("●"); dot.setStyleSheet(f"color:{col};font-size:18px;")
            dot.setToolTip(f"{sz} nm — {name}")
            strl.addWidget(dot)
        strl.addWidget(QLabel("Bulk Gold"))
        strl.addStretch()
        layout.addWidget(strip_frame)
        layout.addStretch()
        self._on_slider(20)

    def _on_slider(self, val):
        # Find closest data point
        closest = min(GOLD_NP_DATA, key=lambda x: abs(x[0]-val))
        sz, color, name, explanation = closest
        self.circle.set_color(color, val)
        self.circle_size_label.setText(f"{val} nm")
        self.size_display.setText(f"{val} nm")
        self.color_name.setText(f"<span style='color:{color}'>{name}</span> ({val} nm)")
        self.explanation.setText(explanation)

# ═══════════════════════════════════════════════════════════
#  PAGE: Flashcards
# ═══════════════════════════════════════════════════════════

class FlashcardPage(QWidget):
    def __init__(self, progress_data):
        super().__init__()
        self.progress_data = progress_data
        if "flashcards" not in self.progress_data:
            self.progress_data["flashcards"] = {"known": [], "unknown": []}
        self.current_idx = 0
        self.shuffled = list(range(len(FLASHCARDS)))
        random.shuffle(self.shuffled)
        self.is_flipped = False
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🃏"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Flashcard Deck"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        # Stats
        self.stats_label = QLabel(); self.stats_label.setStyleSheet("color:#7ee787;font-size:13px;font-weight:bold;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(self.stats_label)
        layout.addLayout(header)

        # Filter
        filter_layout = QHBoxLayout(); filter_layout.setSpacing(10)
        self.filter_combo = QComboBox(); self.filter_combo.setObjectName("diffCombo")
        self.filter_combo.addItems(["All Cards", "Beginner", "Intermediate", "Advanced", "Known", "Unknown"])
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        filter_layout.addWidget(QLabel("Filter:")); filter_layout.addWidget(self.filter_combo); filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Card display
        self.card_frame = QFrame(); self.card_frame.setStyleSheet("QFrame{background:#161b22;border:2px solid #21262d;border-radius:14px;min-height:220px;}")
        self.card_layout = QVBoxLayout(self.card_frame); self.card_layout.setContentsMargins(30,24,30,24); self.card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_front = QLabel(); self.card_front.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_front.setStyleSheet("color:#f0f6fc;font-size:24px;font-weight:bold;")
        self.card_back = QLabel(); self.card_back.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_back.setStyleSheet("color:#8b949e;font-size:14px;"); self.card_back.setWordWrap(True)
        self.card_back.setVisible(False)
        self.card_diff = QLabel(); self.card_diff.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_diff.setStyleSheet("font-size:11px;padding:4px 10px;border-radius:10px;")
        self.card_layout.addWidget(self.card_diff); self.card_layout.addSpacing(10)
        self.card_layout.addWidget(self.card_front); self.card_layout.addWidget(self.card_back)
        self.card_layout.addSpacing(10)
        tap_hint = QLabel("Click card to flip"); tap_hint.setStyleSheet("color:#484f58;font-size:11px;font-style:italic;")
        tap_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_layout.addWidget(tap_hint)
        self.card_frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.card_frame.mousePressEvent = self._flip
        layout.addWidget(self.card_frame, 1)

        # Buttons
        btn_layout = QHBoxLayout(); btn_layout.setSpacing(10)
        self.prev_btn = QPushButton("← Previous"); self.prev_btn.setObjectName("resetBtn")
        self.prev_btn.clicked.connect(self._prev); btn_layout.addWidget(self.prev_btn)
        self.unknown_btn = QPushButton("😕  Don't Know"); self.unknown_btn.setObjectName("resetBtn")
        self.unknown_btn.setStyleSheet("background:transparent;color:#ff7b72;border:1px solid #da3633;border-radius:8px;padding:10px 20px;font-size:12px;")
        self.unknown_btn.clicked.connect(self._mark_unknown); btn_layout.addWidget(self.unknown_btn)
        self.known_btn = QPushButton("✅  Know It"); self.known_btn.setObjectName("submitBtn")
        self.known_btn.clicked.connect(self._mark_known); btn_layout.addWidget(self.known_btn)
        self.next_btn = QPushButton("Next  →"); self.next_btn.setObjectName("resetBtn")
        self.next_btn.clicked.connect(self._next); btn_layout.addWidget(self.next_btn)
        layout.addLayout(btn_layout)

        # Progress bar
        self.progress = QProgressBar(); self.progress.setObjectName("quizProgress")
        self.progress.setRange(0, len(self.filtered_indices) if hasattr(self, 'filtered_indices') else len(FLASHCARDS))
        layout.addWidget(self.progress)
        self._show_card()
        self._update_stats()

    def _apply_filter(self, idx):
        filters = [None, "B", "I", "A", "known", "unknown"]
        f = filters[idx]
        self.filtered_indices = []
        for i, (term, defn, diff) in enumerate(FLASHCARDS):
            if f is None:
                self.filtered_indices.append(i)
            elif f in ("known", "unknown"):
                list_key = f
                if i in self.progress_data["flashcards"][list_key]:
                    self.filtered_indices.append(i)
            elif diff == f:
                self.filtered_indices.append(i)
        if not self.filtered_indices:
            self.filtered_indices = list(range(len(FLASHCARDS)))
        self.current_idx = 0
        self.is_flipped = False
        self.progress.setRange(0, len(self.filtered_indices))
        self._show_card()

    def _show_card(self):
        if not hasattr(self, 'filtered_indices'):
            self._apply_filter(0); return
        if not self.filtered_indices:
            self.card_front.setText("No cards match this filter.")
            self.card_back.setText(""); self.card_back.setVisible(False)
            self.card_diff.setText(""); return
        real_idx = self.filtered_indices[self.current_idx % len(self.filtered_indices)]
        term, defn, diff = FLASHCARDS[real_idx]
        self.is_flipped = False
        self.card_front.setText(term)
        self.card_front.setVisible(True)
        self.card_back.setText(defn); self.card_back.setVisible(False)
        diff_colors = {"B": ("#238636", "Beginner"), "I": ("#1f6feb", "Intermediate"), "A": ("#a371f7", "Advanced")}
        dc, dl = diff_colors.get(diff, ("#8b949e", diff))
        self.card_diff.setText(f"  {dl}  "); self.card_diff.setStyleSheet(f"font-size:11px;padding:4px 10px;border-radius:10px;background:{dc}22;color:{dc};font-weight:bold;border:1px solid {dc}44;")
        self.card_frame.setStyleSheet("QFrame{background:#161b22;border:2px solid #21262d;border-radius:14px;min-height:220px;}")
        self.progress.setValue(self.current_idx % len(self.filtered_indices))

    def _flip(self, event=None):
        self.is_flipped = not self.is_flipped
        self.card_front.setVisible(not self.is_flipped)
        self.card_back.setVisible(self.is_flipped)
        border = "#58a6ff" if self.is_flipped else "#21262d"
        self.card_frame.setStyleSheet(f"QFrame{{background:#161b22;border:2px solid {border};border-radius:14px;min-height:220px;}}")

    def _mark_known(self):
        real_idx = self.filtered_indices[self.current_idx % len(self.filtered_indices)]
        if real_idx not in self.progress_data["flashcards"]["known"]:
            self.progress_data["flashcards"]["known"].append(real_idx)
        if real_idx in self.progress_data["flashcards"]["unknown"]:
            self.progress_data["flashcards"]["unknown"].remove(real_idx)
        self._update_stats(); self._next()

    def _mark_unknown(self):
        real_idx = self.filtered_indices[self.current_idx % len(self.filtered_indices)]
        if real_idx not in self.progress_data["flashcards"]["unknown"]:
            self.progress_data["flashcards"]["unknown"].append(real_idx)
        if real_idx in self.progress_data["flashcards"]["known"]:
            self.progress_data["flashcards"]["known"].remove(real_idx)
        self._update_stats(); self._next()

    def _next(self):
        if not self.filtered_indices: return
        self.current_idx = (self.current_idx + 1) % len(self.filtered_indices)
        self._show_card()

    def _prev(self):
        if not self.filtered_indices: return
        self.current_idx = (self.current_idx - 1) % len(self.filtered_indices)
        self._show_card()

    def _update_stats(self):
        known = len(self.progress_data["flashcards"]["known"])
        total = len(FLASHCARDS)
        pct = known/total*100 if total else 0
        self.stats_label.setText(f"Mastered: {known}/{total} ({pct:.0f}%)")

# ═══════════════════════════════════════════════════════════
#  PAGE: Matching Game
# ═══════════════════════════════════════════════════════════

class MatchButton(QPushButton):
    def __init__(self, text, pair_id, side, parent=None):
        super().__init__(text, parent)
        self.pair_id = pair_id
        self.side = side  # "term" or "def"
        self.matched = False
        self.selected = False
        self._base_style = ""

class MatchingGamePage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected = None
        self.matched_pairs = set()
        self.attempts = 0
        self.start_time = time.time()
        self._build_ui()
        self._new_game()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🧩"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Matching Game"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.score_label = QLabel(); self.score_label.setStyleSheet("color:#7ee787;font-size:13px;font-weight:bold;")
        self.timer_label = QLabel(); self.timer_label.setStyleSheet("color:#8b949e;font-size:12px;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(self.score_label); header.addWidget(self.timer_label)
        layout.addLayout(header)

        desc = QLabel("Click a term on the left, then click its matching definition on the right. Match all pairs as fast as you can!")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Game grid
        self.grid_layout = QGridLayout(); self.grid_layout.setSpacing(8)
        self.grid_widget = QWidget(); self.grid_widget.setLayout(self.grid_layout)
        layout.addWidget(self.grid_widget, 1)

        # New game button
        self.new_btn = QPushButton("🔄  New Game"); self.new_btn.setObjectName("resetBtn")
        self.new_btn.clicked.connect(self._new_game)
        layout.addWidget(self.new_btn, 0, Qt.AlignmentFlag.AlignCenter)
        self._timer = QTimer(); self._timer.timeout.connect(self._update_timer); self._timer.start(1000)

    def _new_game(self):
        # Clear
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0); w = item.widget()
            if w: w.deleteLater()
        self.selected = None; self.matched_pairs = set(); self.attempts = 0
        self.start_time = time.time()
        # Pick 6 random pairs
        pairs = random.sample(MATCHING_PAIRS, min(6, len(MATCHING_PAIRS)))
        terms = [(t, i) for i, (t, d) in enumerate(pairs)]
        defs = [(d, i) for i, (t, d) in enumerate(pairs)]
        random.shuffle(defs)
        self.buttons = []
        for row, (text, pid) in enumerate(terms):
            btn = MatchButton(text, pid, "term")
            btn.setObjectName("navBtn")
            btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:1px solid #21262d;border-radius:8px;background:#161b22;}")
            btn.clicked.connect(lambda checked, b=btn: self._on_click(b))
            self.grid_layout.addWidget(btn, row, 0)
            self.buttons.append(btn)
        for row, (text, pid) in enumerate(defs):
            btn = MatchButton(text, pid, "def")
            btn.setObjectName("navBtn")
            btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:1px solid #21262d;border-radius:8px;background:#161b22;font-size:11px;}")
            btn.clicked.connect(lambda checked, b=btn: self._on_click(b))
            self.grid_layout.addWidget(btn, row, 1)
            self.buttons.append(btn)
        self._update_score()

    def _on_click(self, btn):
        if btn.matched: return
        if self.selected is None:
            self.selected = btn; btn.selected = True
            btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:2px solid #58a6ff;border-radius:8px;background:#1c2333;color:#58a6ff;}")
        elif self.selected.side == btn.side:
            # Deselect old, select new
            self.selected.selected = False
            self._reset_btn_style(self.selected)
            self.selected = btn; btn.selected = True
            btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:2px solid #58a6ff;border-radius:8px;background:#1c2333;color:#58a6ff;}")
        else:
            self.attempts += 1
            if self.selected.pair_id == btn.pair_id:
                # Match!
                self.selected.matched = True; btn.matched = True
                self.selected.selected = False
                self._reset_btn_style(self.selected, matched=True)
                self._reset_btn_style(btn, matched=True)
                self.selected = None
                self.matched_pairs.add(btn.pair_id)
            else:
                # Wrong
                self.selected.selected = False
                old = self.selected; self.selected = None
                # Flash red briefly
                old.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:2px solid #da3633;border-radius:8px;background:#2d1215;color:#ff7b72;}")
                btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:2px solid #da3633;border-radius:8px;background:#2d1215;color:#ff7b72;}")
                QTimer.singleShot(500, lambda: (self._reset_btn_style(old), self._reset_btn_style(btn)))
            self._update_score()
            if len(self.matched_pairs) == 6:
                self._timer.stop()
                elapsed = time.time() - self.start_time
                mins, secs = int(elapsed)//60, int(elapsed)%60
                QMessageBox.information(self, "🎉 Congratulations!",
                    f"You matched all 6 pairs!\n\nTime: {mins}m {secs}s\nAttempts: {self.attempts}\nAccuracy: {6/self.attempts*100:.0f}%")

    def _reset_btn_style(self, btn, matched=False):
        if matched:
            btn.setStyleSheet("QPushButton#navBtn{text-align:center;padding:12px 8px;border:1px solid #238636;border-radius:8px;background:#0d2818;color:#7ee787;}")
        else:
            fs = "font-size:11px;" if btn.side == "def" else ""
            btn.setStyleSheet(f"QPushButton#navBtn{{text-align:center;padding:12px 8px;border:1px solid #21262d;border-radius:8px;background:#161b22;{fs}}}")

    def _update_score(self):
        self.score_label.setText(f"Matched: {len(self.matched_pairs)}/6  |  Attempts: {self.attempts}")

    def _update_timer(self):
        elapsed = time.time() - self.start_time
        m, s = int(elapsed)//60, int(elapsed)%60
        self.timer_label.setText(f"⏱ {m:02d}:{s:02d}")

# ═══════════════════════════════════════════════════════════
#  PAGE: Enhanced Quiz (difficulty filter, review mode)
# ═══════════════════════════════════════════════════════════

class EnhancedQuizPage(QWidget):
    def __init__(self, progress_data):
        super().__init__()
        self.progress_data = progress_data
        self.all_questions = list(range(len(QUIZ_DATA)))
        self.questions = self.all_questions[:]
        self.current = 0; self.score = 0; self.answered = False; self.wrong_ids = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(12)
        header = QHBoxLayout()
        il = QLabel("🧠"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Knowledge Quiz"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        # Controls row
        ctrl = QHBoxLayout(); ctrl.setSpacing(10)
        ctrl.addWidget(QLabel("Difficulty:"))
        self.diff_combo = QComboBox(); self.diff_combo.setObjectName("diffCombo")
        self.diff_combo.addItems(["All Levels", "Beginner", "Intermediate", "Advanced"])
        self.diff_combo.currentIndexChanged.connect(self._filter_questions)
        ctrl.addWidget(self.diff_combo)
        self.review_btn = QPushButton("🔄 Review Mistakes (0)"); self.review_btn.setObjectName("resetBtn")
        self.review_btn.clicked.connect(self._review_mode); ctrl.addWidget(self.review_btn)
        self.start_btn = QPushButton("Start Quiz"); self.start_btn.setObjectName("submitBtn")
        self.start_btn.clicked.connect(self._start_quiz); ctrl.addWidget(self.start_btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.progress_bar = QProgressBar(); self.progress_bar.setObjectName("quizProgress")
        self.progress_bar.setRange(0, len(self.questions)); layout.addWidget(self.progress_bar)
        self.progress_label = QLabel(); self.progress_label.setObjectName("progressLabel")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.progress_label)
        self.question_label = QLabel(); self.question_label.setObjectName("questionText")
        self.question_label.setWordWrap(True); layout.addWidget(self.question_label)

        self.button_group = QButtonGroup(self); self.option_buttons = []
        for i in range(4):
            rb = QRadioButton(); rb.setObjectName("quizOption")
            self.button_group.addButton(rb, i); self.option_buttons.append(rb); layout.addWidget(rb)

        self.explanation_label = QLabel(); self.explanation_label.setWordWrap(True)
        self.explanation_label.setStyleSheet("background:#1c2333;border:1px solid #30363d;border-radius:8px;padding:10px 14px;color:#c9d1d9;font-size:12px;")
        self.explanation_label.setVisible(False); layout.addWidget(self.explanation_label)

        btn_layout = QHBoxLayout(); btn_layout.setSpacing(10)
        self.submit_btn = QPushButton("Submit"); self.submit_btn.setObjectName("submitBtn")
        self.submit_btn.clicked.connect(self._submit); btn_layout.addWidget(self.submit_btn)
        self.next_btn = QPushButton("Next  →"); self.next_btn.setObjectName("nextBtn")
        self.next_btn.clicked.connect(self._next); self.next_btn.setEnabled(False); btn_layout.addWidget(self.next_btn)
        self.reset_btn = QPushButton("Reset"); self.reset_btn.setObjectName("resetBtn")
        self.reset_btn.clicked.connect(self._reset); btn_layout.addWidget(self.reset_btn)
        btn_layout.addStretch(); layout.addLayout(btn_layout)

        self.score_frame = QFrame(); self.score_frame.setObjectName("scoreFrame")
        sf = QVBoxLayout(self.score_frame); sf.setContentsMargins(18,18,18,18); sf.setSpacing(4)
        self.score_value = QLabel(); self.score_value.setObjectName("scoreLabel"); self.score_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_desc = QLabel(); self.score_desc.setObjectName("scoreText"); self.score_desc.setAlignment(Qt.AlignmentFlag.AlignCenter); self.score_desc.setWordWrap(True)
        sf.addWidget(self.score_value); sf.addWidget(self.score_desc)
        self.score_frame.setVisible(False); layout.addWidget(self.score_frame)
        layout.addStretch()
        self._show_setup()

    def _filter_questions(self, idx):
        diffs = [None, "B", "I", "A"]
        d = diffs[idx]
        self.questions = [i for i, q in enumerate(QUIZ_DATA) if d is None or q["d"] == d]
        self.progress_bar.setRange(0, max(len(self.questions), 1))
        if not self.questions: self.questions = self.all_questions[:]

    def _review_mode(self):
        self.questions = self.wrong_ids[:]
        if not self.questions:
            QMessageBox.information(self, "Review Mode", "No mistakes to review! Great job! 🎉"); return
        self.progress_bar.setRange(0, len(self.questions))
        self._start_quiz()

    def _show_setup(self):
        self.question_label.setText("Select a difficulty and click 'Start Quiz'.")
        for b in self.option_buttons: b.setVisible(False)
        self.submit_btn.setVisible(False); self.next_btn.setVisible(False)
        self.explanation_label.setVisible(False); self.score_frame.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"{len(self.questions)} questions ready")

    def _start_quiz(self):
        self.current = 0; self.score = 0; self.answered = False; self.wrong_ids = []
        for b in self.option_buttons: b.setVisible(True)
        self.submit_btn.setVisible(True); self.submit_btn.setEnabled(True)
        self.next_btn.setVisible(True); self.next_btn.setEnabled(False)
        self.question_label.setVisible(True); self.score_frame.setVisible(False)
        self._show_question()

    def _show_question(self):
        if self.current >= len(self.questions):
            self._show_results(); return
        q = QUIZ_DATA[self.questions[self.current]]
        self.question_label.setText(f"Q{self.current+1}. [{q['d']}] {q['q']}")
        for i, opt in enumerate(q["o"]):
            self.option_buttons[i].setText(f"  {chr(65+i)}.  {opt}")
            self.option_buttons[i].setEnabled(True); self.option_buttons[i].setChecked(False)
        self.answered = False; self.submit_btn.setEnabled(True); self.next_btn.setEnabled(False)
        self.explanation_label.setVisible(False)
        self.progress_bar.setValue(self.current)
        self.progress_label.setText(f"Question {self.current+1} of {len(self.questions)}")

    def _submit(self):
        if self.answered: return
        sel = self.button_group.checkedId()
        if sel < 0: return
        self.answered = True
        q = QUIZ_DATA[self.questions[self.current]]
        if sel == q["c"]:
            self.score += 1
            self.explanation_label.setStyleSheet("background:#0d2818;border:1px solid #238636;border-radius:8px;padding:10px 14px;color:#7ee787;font-size:12px;")
            self.explanation_label.setText(f"✅ Correct! {q['e']}")
        else:
            self.wrong_ids.append(self.questions[self.current])
            self.explanation_label.setStyleSheet("background:#2d1215;border:1px solid #da3633;border-radius:8px;padding:10px 14px;color:#ff7b72;font-size:12px;")
            self.explanation_label.setText(f"❌ Answer: {chr(65+q['c'])}. {q['e']}")
        self.explanation_label.setVisible(True)
        for b in self.option_buttons: b.setEnabled(False)
        self.submit_btn.setEnabled(False); self.next_btn.setEnabled(True)
        self.review_btn.setText(f"🔄 Review Mistakes ({len(self.wrong_ids)})")

    def _next(self):
        self.current += 1; self._show_question()

    def _show_results(self):
        self.question_label.setVisible(False)
        for b in self.option_buttons: b.setVisible(False)
        self.submit_btn.setVisible(False); self.next_btn.setVisible(False)
        self.explanation_label.setVisible(False)
        self.progress_bar.setValue(len(self.questions))
        self.progress_label.setText("Quiz Complete!")
        self.score_frame.setVisible(True)
        pct = self.score/max(len(self.questions),1)*100
        self.score_value.setText(f"{self.score} / {len(self.questions)}")
        msgs = [(90,"Expert! 🌟"),(70,"Solid understanding! 🎓"),(50,"Good effort! 📚"),(0,"Keep learning! 💪")]
        msg = next(m for t,m in msgs if pct >= t)
        self.score_desc.setText(f"{msg} ({pct:.0f}%)")
        # Save best score
        key = f"quiz_best_{len(self.questions)}"
        prev = self.progress_data.get(key, 0)
        if self.score > prev:
            self.progress_data[key] = self.score

    def _reset(self):
        self._show_setup()

# ═══════════════════════════════════════════════════════════
#  PAGE: Glossary
# ═══════════════════════════════════════════════════════════

class GlossaryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📖"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Glossary"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        count = QLabel(f"{len(GLOSSARY_DATA)} terms"); count.setStyleSheet("color:#8b949e;font-size:12px;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(count)
        layout.addLayout(header)

        self.search_box = QLineEdit(); self.search_box.setObjectName("searchBox")
        self.search_box.setPlaceholderText("🔍  Search terms..."); self.search_box.textChanged.connect(self._filter)
        layout.addWidget(self.search_box)

        container = QVBoxLayout(); container.setSpacing(4); container.setContentsMargins(0,0,0,0)
        self.frames = []
        for term, defn in GLOSSARY_DATA:
            f = QFrame(); f.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;}")
            fl = QVBoxLayout(f); fl.setContentsMargins(14,10,14,10); fl.setSpacing(3)
            t = QLabel(term); t.setObjectName("glossaryTerm")
            d = QLabel(defn); d.setObjectName("glossaryDef"); d.setWordWrap(True)
            fl.addWidget(t); fl.addWidget(d)
            container.addWidget(f); self.frames.append((f, term.lower(), defn.lower()))
        layout.addLayout(container); layout.addStretch()

    def _filter(self, text):
        q = text.lower().strip()
        for f, t, d in self.frames:
            f.setVisible(not q or q in t or q in d)

# ═══════════════════════════════════════════════════════════
#  PAGE: Notes Hub
# ═══════════════════════════════════════════════════════════

class NotesPage(QWidget):
    def __init__(self, notes_data, progress_data=None):
        super().__init__()
        self.notes_data = notes_data
        self.progress_data = progress_data or {}
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📝"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("My Notes"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl); layout.addLayout(header)

        desc = QLabel("All your notes from each topic, collected in one place. Edit them here or on the individual topic pages — changes sync automatically.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        self.note_editor = QTextEdit(); self.note_editor.setObjectName("noteArea")
        self.note_editor.setPlaceholderText("Select a topic below...")
        layout.addWidget(self.note_editor, 1)

        self.topic_btns = QHBoxLayout(); self.topic_btns.setSpacing(8)
        self.topic_map = {}
        topics = ["introduction","nanites","applications","history","safety","future","quantum","nanoelectronics","nanophotonics"]
        labels = ["📏 Intro","🤖 Nanites","💊 Apps","📜 History","🧪 Safety","🚀 Future","⚛️ Quantum","💾 Nanoelec","🌈 Nanophoto"]
        for topic, label in zip(topics, labels):
            btn = QPushButton(label); btn.setObjectName("resetBtn")
            btn.clicked.connect(lambda checked, t=topic: self._load_topic(t))
            self.topic_btns.addWidget(btn); self.topic_map[label] = topic
        layout.addLayout(self.topic_btns)

        # Export button
        export_row = QHBoxLayout(); export_row.addStretch()
        self.export_btn = QPushButton("💾 Export All Notes to File"); self.export_btn.setObjectName("submitBtn")
        self.export_btn.clicked.connect(self._export)
        export_row.addWidget(self.export_btn); export_row.addStretch()
        layout.addLayout(export_row)

    def _load_topic(self, topic):
        self._current_topic = topic
        self.note_editor.setPlainText(self.notes_data.get(topic, ""))
        self.note_editor.textChanged.disconnect()
        self.note_editor.textChanged.connect(self._save)

    def _export(self):
        if not hasattr(self, '_current_topic') or not self.notes_data.get(self._current_topic, "").strip():
            # Export all notes
            export_path = str(SAVE_DIR / "nanolearn_notes_export.txt")
            with open(export_path, "w") as f:
                for topic, notes in self.notes_data.items():
                    if notes.strip():
                        f.write(f"=== {topic.upper()} ===\n{notes}\n\n")
            QMessageBox.information(self, "Notes Exported", f"All notes saved to:\n{export_path}")
        else:
            export_path = str(SAVE_DIR / f"nanolearn_{self._current_topic}_notes.txt")
            with open(export_path, "w") as f:
                f.write(f"=== {self._current_topic.upper()} ===\n")
                f.write(self.note_editor.toPlainText())
            QMessageBox.information(self, "Note Exported", f"Saved to:\n{export_path}")

    def _save(self):
        if hasattr(self, '_current_topic'):
            self.notes_data[self._current_topic] = self.note_editor.toPlainText()
            save_json(NOTES_FILE, self.notes_data)

# ═══════════════════════════════════════════════════════════
#  PAGE: Progress Dashboard
# ═══════════════════════════════════════════════════════════

class DashboardPage(QWidget):
    def __init__(self, progress_data, notes_data):
        super().__init__()
        self.progress_data = progress_data
        self.notes_data = notes_data
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📊"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Progress Dashboard"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl); layout.addLayout(header)

        # Stats grid
        grid = QGridLayout(); grid.setSpacing(12)

        # Pages visited
        visited = self.progress_data.get("visited", [])
        total_content = 9
        card1 = self._stat_card("📚", "Pages Visited", f"{len(visited)} / {total_content}", f"{len(visited)/total_content*100:.0f}% complete", "#58a6ff")
        grid.addWidget(card1, 0, 0)

        # Max difficulty reached
        max_tabs = self.progress_data.get("max_tab", {})
        levels_reached = {"Beginner":0, "Intermediate":0, "Advanced":0}
        for key, val in max_tabs.items():
            for i, lvl in enumerate(["Beginner","Intermediate","Advanced"]):
                if val >= i: levels_reached[lvl] += 1
        adv_count = levels_reached["Advanced"]
        card2 = self._stat_card("📈", "Advanced Reached", f"{adv_count} / {total_content}", "Highest difficulty tab opened", "#a371f7")
        grid.addWidget(card2, 0, 1)

        # Flashcards
        fc = self.progress_data.get("flashcards", {})
        known = len(fc.get("known", []))
        card3 = self._stat_card("🃏", "Flashcards Mastered", f"{known} / {len(FLASHCARDS)}", f"{known/len(FLASHCARDS)*100:.0f}% memorized", "#7ee787")
        grid.addWidget(card3, 0, 2)

        # Quiz scores
        quiz_scores = [(k.replace("quiz_best_",""), v) for k,v in self.progress_data.items() if k.startswith("quiz_best_")]
        score_text = " | ".join(f"{n}q: {v}/{n}" for n,v in sorted(quiz_scores)) if quiz_scores else "No quiz completed yet"
        best_pct = max((v/n*100 for n,v in quiz_scores), default=0)
        card4 = self._stat_card("🧠", "Quiz Best Scores", f"{best_pct:.0f}%", score_text, "#f78166")
        grid.addWidget(card4, 1, 0)

        # Notes
        notes_count = len([v for v in self.notes_data.values() if v.strip()])
        card5 = self._stat_card("📝", "Notes Written", f"{notes_count} pages", "Topics with personal notes", "#d2a8ff")
        grid.addWidget(card5, 1, 1)

        # Overall progress
        overall = (len(visited)/total_content*30 + known/len(FLASHCARDS)*30 + best_pct/100*20 + levels_reached["Advanced"]/total_content*20)
        overall_color = "#7ee787" if overall >= 70 else "#ffa657" if overall >= 40 else "#ff7b72"
        card6 = self._stat_card("🏆", "Overall Progress", f"{overall:.0f}%", "Pages + Flashcards + Quiz + Difficulty", overall_color)
        grid.addWidget(card6, 1, 2)
        layout.addLayout(grid)

        # Detail: page-by-page
        detail = QFrame(); detail.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        dl = QVBoxLayout(detail); dl.setContentsMargins(16,14,16,14); dl.setSpacing(8)
        dt = QLabel("📋  Page-by-Page Detail"); dt.setStyleSheet("color:#58a6ff;font-size:14px;font-weight:bold;")
        dl.addWidget(dt)
        topics = [("introduction","📏 Introduction"),("nanites","🤖 Nanites"),("applications","💊 Applications"),
                  ("history","📜 History"),("safety","🧪 Safety"),("future","🚀 Future"),
                  ("quantum","⚛️ Quantum Mech"),("nanoelectronics","💾 Nanoelectronics"),("nanophotonics","🌈 Nanophotonics")]
        ratings = self.progress_data.get("ratings", {})
        for tid, tname in topics:
            visited_mark = "✅" if tid in visited else "⬜"
            max_tab = max_tabs.get(f"{tid}_tab", -1)
            tab_names = ["Beginner","Intermediate","Advanced"]
            level_str = tab_names[max_tab] if max_tab >= 0 else "Not started"
            has_note = "📝" if self.notes_data.get(tid, "").strip() else ""
            rating = ratings.get(tid, 0)
            stars = "★" * rating + "☆" * (5 - rating) if rating else ""
            row = QLabel(f"  {visited_mark}  {tname}  —  {level_str}  {has_note}  {stars}")
            row.setStyleSheet("color:#c9d1d9;font-size:12px;padding:4px 0;")
            dl.addWidget(row)
        layout.addWidget(detail)
        layout.addStretch()

    def _stat_card(self, emoji, title, value, subtitle, color):
        card = QFrame(); card.setStyleSheet(f"QFrame{{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:14px;}}")
        cl = QVBoxLayout(card); cl.setSpacing(4); cl.setContentsMargins(14,12,14,12)
        e = QLabel(emoji); e.setStyleSheet("font-size:22px;")
        t = QLabel(title); t.setStyleSheet("color:#8b949e;font-size:11px;")
        v = QLabel(value); v.setStyleSheet(f"color:{color};font-size:20px;font-weight:bold;")
        s = QLabel(subtitle); s.setStyleSheet("color:#484f58;font-size:10px;"); s.setWordWrap(True)
        cl.addWidget(e); cl.addWidget(t); cl.addWidget(v); cl.addWidget(s)
        return card

# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Quantum Confinement Simulator
# ═══════════════════════════════════════════════════════════

class EnergyLevelDiagram(QWidget):
    """Draws quantum energy levels for particle-in-a-box."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._levels = []  # list of (n, energy_eV, color)
        self.setFixedSize(350, 320)

    def set_levels(self, levels):
        self._levels = levels
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # Background
        p.fillRect(0, 0, w, h, QColor("#010409"))
        # Draw box walls
        p.setPen(QPen(QColor("#58a6ff"), 2))
        box_left, box_right = 60, w - 30
        box_top, box_bottom = 20, h - 40
        p.drawLine(box_left, box_top, box_left, box_bottom)
        p.drawLine(box_right, box_top, box_right, box_bottom)
        p.drawLine(box_left, box_bottom, box_right, box_bottom)
        # Labels
        p.setPen(QColor("#8b949e"))
        p.setFont(QFont("Segoe UI", 8))
        p.drawText(box_left - 55, box_bottom // 2 + 4, "Energy")
        p.drawText((box_left + box_right) // 2 - 15, h - 8, "Position x")

        if not self._levels:
            p.end(); return

        max_e = self._levels[-1][1] * 1.1 if self._levels else 1
        draw_h = box_bottom - box_top - 20
        # Draw levels
        for n, eV, color in self._levels:
            y = box_bottom - 10 - int((eV / max_e) * draw_h)
            y = max(box_top + 5, min(box_bottom - 10, y))
            p.setPen(QPen(QColor(color), 3))
            line_w = int((box_right - box_left) * 0.7)
            x_start = (box_left + box_right) // 2 - line_w // 2
            p.drawLine(x_start, y, x_start + line_w, y)
            # Label
            p.setPen(QColor(color))
            p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            p.drawText(box_right + 3, y + 4, f"n={n}")
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(x_start - 50, y + 4, f"{eV:.3f} eV")
        p.end()


class QuantumConfinementSimPage(QWidget):
    def __init__(self):
        super().__init__()
        self._hbar = 1.0546e-34  # J·s
        self._me = 9.109e-31     # kg
        self._eV = 1.602e-19     # J
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🔌"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Quantum Confinement Simulator"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Explore the particle-in-a-box model — the foundation of quantum confinement. Adjust the well width and particle type to see how energy levels change. This is the physics behind quantum dots, nanowires, and ultrathin films.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Equation box
        eq_frame = QFrame(); eq_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px 16px;}")
        eql = QVBoxLayout(eq_frame); eql.setSpacing(4)
        eq_title = QLabel("Equations"); eq_title.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        eq1 = QLabel("E_n = n² π² ℏ² / (2 m L²)     λ_n = 2L / n     T = E_n / k_B")
        eq1.setStyleSheet("color:#f0f6fc;font-size:13px;font-family:monospace;")
        eql.addWidget(eq_title); eql.addWidget(eq1)
        layout.addWidget(eq_frame)

        # Controls
        ctrl = QHBoxLayout(); ctrl.setSpacing(20)
        # Well width
        w_frame = QFrame(); w_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        wl = QVBoxLayout(w_frame); wl.setSpacing(6)
        wt = QLabel("Well Width (L)"); wt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(5, 100)  # 0.5 nm to 10.0 nm (value/10)
        self.width_slider.setValue(20); self.width_slider.setTickInterval(10)
        self.width_slider.valueChanged.connect(self._update)
        self.width_label = QLabel("2.0 nm"); self.width_label.setStyleSheet("color:#f0f6fc;font-size:14px;font-weight:bold;")
        self.width_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wl.addWidget(wt); wl.addWidget(self.width_slider); wl.addWidget(self.width_label)
        ctrl.addWidget(w_frame, 1)

        # Particle type
        p_frame = QFrame(); p_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        pl = QVBoxLayout(p_frame); pl.setSpacing(6)
        pt = QLabel("Particle Mass"); pt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        self.mass_combo = QComboBox(); self.mass_combo.setObjectName("diffCombo")
        self.mass_combo.addItems(["Electron (m_e)", "Effective mass GaAs (0.067 m_e)", "Proton (m_p)"])
        self.mass_combo.currentIndexChanged.connect(self._update)
        pl.addWidget(pt); pl.addWidget(self.mass_combo)
        ctrl.addWidget(p_frame, 1)

        # Number of levels
        n_frame = QFrame(); n_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        nl = QVBoxLayout(n_frame); nl.setSpacing(6)
        nt = QLabel("Levels to Show"); nt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        self.n_spin = QSpinBox(); self.n_spin.setRange(3, 10); self.n_spin.setValue(5)
        self.n_spin.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:6px;color:#c9d1d9;padding:4px 8px;font-size:13px;")
        self.n_spin.valueChanged.connect(self._update)
        nl.addWidget(nt); nl.addWidget(self.n_spin)
        ctrl.addWidget(n_frame)
        layout.addLayout(ctrl)

        # Main display: diagram + results
        main_row = QHBoxLayout(); main_row.setSpacing(16)
        self.diagram = EnergyLevelDiagram()
        main_row.addWidget(self.diagram)

        # Results panel
        res_frame = QFrame(); res_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;}")
        rl = QVBoxLayout(res_frame); rl.setSpacing(6)
        rt = QLabel("Calculated Values"); rt.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.results_label = QLabel(); self.results_label.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.7;")
        self.results_label.setWordWrap(True)
        rl.addWidget(rt); rl.addWidget(self.results_label)
        main_row.addWidget(res_frame, 1)
        layout.addLayout(main_row)

        # Physics insight
        self.insight = QLabel(); self.insight.setWordWrap(True)
        self.insight.setStyleSheet("color:#8b949e;font-size:11px;border-left:3px solid #f78166;padding:8px 12px;background:#1c2333;border-radius:0 6px 6px 0;")
        layout.addWidget(self.insight)
        layout.addStretch()
        self._update()

    def _update(self):
        L_nm = self.width_slider.value() / 10.0
        L = L_nm * 1e-9
        self.width_label.setText(f"{L_nm:.1f} nm")
        masses = [self._me, 0.067 * self._me, 1.673e-27]
        mass_names = ["Electron", "GaAs e⁻ (m*=0.067 m_e)", "Proton"]
        mass = masses[self.mass_combo.currentIndex()]
        mass_name = mass_names[self.mass_combo.currentIndex()]
        n_levels = self.n_spin.value()

        levels = []
        colors = ["#79c0ff", "#58a6ff", "#7ee787", "#ffa657", "#f78166", "#d2a8ff", "#ff7b72", "#f778ba", "#e3b341", "#a371f7"]
        results_text = f"<b>Well width:</b> L = {L_nm:.1f} nm<br><b>Particle:</b> {mass_name}<br><b>Mass:</b> {mass:.3e} kg<br><br>"
        k_B = 1.381e-23
        for n in range(1, n_levels + 1):
            E = (n**2 * math.pi**2 * self._hbar**2) / (2 * mass * L**2)
            E_eV = E / self._eV
            wavelength = 2 * L / n
            T_equiv = E / k_B
            color = colors[(n - 1) % len(colors)]
            levels.append((n, E_eV, color))
            results_text += f"<span style='color:{color}'>n={n}:</span> E = {E_eV:.4f} eV  |  λ = {wavelength*1e9:.2f} nm  |  T_eq = {T_equiv:.0f} K<br>"

        self.diagram.set_levels(levels)
        self.results_label.setText(results_text)

        # Insight
        E1_eV = levels[0][1] if levels else 0
        spacing = levels[1][1] - levels[0][1] if len(levels) > 1 else 0
        if L_nm < 1:
            ins = f"⚡ Ultra-strong confinement! E₁ = {E1_eV:.2f} eV, level spacing = {spacing:.2f} eV. At this scale, quantum effects completely dominate — the material behaves like an artificial atom with widely spaced discrete levels."
        elif L_nm < 3:
            ins = f"⚡ Strong quantum confinement. E₁ = {E1_eV:.3f} eV. Level spacing ({spacing:.3f} eV) is comparable to thermal energy at room temperature (0.026 eV), so thermal excitation between levels is significant."
        elif L_nm < 7:
            ins = f"📊 Moderate confinement. E₁ = {E1_eV:.4f} eV with spacing {spacing:.4f} eV. This is the quantum dot regime — size-tunable optical properties are observed, similar to real semiconductor quantum dots."
        else:
            ins = f"📊 Weak confinement. E₁ = {E1_eV:.6f} eV with tight spacing ({spacing:.6f} eV). Levels approach a continuum — the material behaves more like bulk. The quantum effects are subtle."
        self.insight.setText(ins)


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Brownian Motion Simulator
# ═══════════════════════════════════════════════════════════

class BrownianCanvas(QWidget):
    """Custom widget that simulates Brownian motion of nanoparticles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []  # list of [x, y, vx, vy, color]
        self.setMinimumSize(400, 300)
        self._trail_mode = False

    def set_particles(self, particles):
        self.particles = particles
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#010409"))
        # Grid
        p.setPen(QPen(QColor(33, 38, 45), 1))
        for x in range(0, w, 40):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, 40):
            p.drawLine(0, y, w, y)
        # Draw particles
        for px, py, _, _, color in self.particles:
            ix, iy = int(px % w), int(py % h)
            # Glow
            glow = QRadialGradient(ix, iy, 12)
            gc = QColor(color)
            glow.setColorAt(0, QColor(gc.red(), gc.green(), gc.blue(), 120))
            glow.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(ix - 12, iy - 12, 24, 24)
            # Core
            p.setBrush(QColor(color))
            p.drawEllipse(ix - 4, iy - 4, 8, 8)
        p.end()


class BrownianMotionSimPage(QWidget):
    def __init__(self):
        super().__init__()
        self.k_B = 1.381e-23
        self.eta = 8.9e-4  # water viscosity at 25°C
        self.num_particles = 30
        self.particles = []
        self.running = False
        self.step_count = 0
        self.start_positions = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🌊"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Brownian Motion Simulator"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Watch nanoparticles jiggle randomly due to thermal collisions with water molecules! This is Brownian motion, first observed by Robert Brown in 1827 and explained by Einstein in 1905. The diffusion coefficient follows the Stokes-Einstein relation.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Equation
        eq = QLabel("D = k_B T / (6 π η r)     MSD = 2 d D t  (d = 2 for 2D)")
        eq.setStyleSheet("color:#f0f6fc;font-size:13px;font-family:monospace;background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px 14px;")
        layout.addWidget(eq)

        # Controls
        ctrl = QHBoxLayout(); ctrl.setSpacing(16)
        # Temperature
        t_frame = QFrame(); t_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        tl2 = QVBoxLayout(t_frame); tl2.setSpacing(4)
        tl2.addWidget(QLabel("Temperature"))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(100, 1000); self.temp_slider.setValue(300)
        self.temp_slider.valueChanged.connect(self._on_param_change)
        self.temp_label = QLabel("300 K"); self.temp_label.setStyleSheet("color:#f0f6fc;font-size:13px;font-weight:bold;")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tl2.addWidget(self.temp_slider); tl2.addWidget(self.temp_label)
        ctrl.addWidget(t_frame, 1)

        # Particle size
        s_frame = QFrame(); s_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        sl = QVBoxLayout(s_frame); sl.setSpacing(4)
        sl.addWidget(QLabel("Particle Radius"))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 100); self.size_slider.setValue(10)
        self.size_slider.valueChanged.connect(self._on_param_change)
        self.size_label = QLabel("10 nm"); self.size_label.setStyleSheet("color:#f0f6fc;font-size:13px;font-weight:bold;")
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(self.size_slider); sl.addWidget(self.size_label)
        ctrl.addWidget(s_frame, 1)

        # Buttons
        btn_frame = QFrame(); btn_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        bl = QVBoxLayout(btn_frame); bl.setSpacing(6)
        self.start_btn = QPushButton("▶ Start"); self.start_btn.setObjectName("submitBtn")
        self.start_btn.clicked.connect(self._toggle_run); bl.addWidget(self.start_btn)
        self.reset_btn = QPushButton("↺ Reset"); self.reset_btn.setObjectName("resetBtn")
        self.reset_btn.clicked.connect(self._reset); bl.addWidget(self.reset_btn)
        ctrl.addWidget(btn_frame)
        layout.addLayout(ctrl)

        # Canvas + stats
        main_row = QHBoxLayout(); main_row.setSpacing(14)
        self.canvas = BrownianCanvas()
        self.canvas.setStyleSheet("border:1px solid #21262d;border-radius:8px;")
        main_row.addWidget(self.canvas, 1)

        # Stats
        stat_frame = QFrame(); stat_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;}")
        stl = QVBoxLayout(stat_frame); stl.setSpacing(6)
        st = QLabel("Statistics"); st.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.stats_label = QLabel(); self.stats_label.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.7;")
        self.stats_label.setWordWrap(True)
        stl.addWidget(st); stl.addWidget(self.stats_label)
        # D display
        self.d_label = QLabel(); self.d_label.setStyleSheet("color:#7ee787;font-size:14px;font-weight:bold;")
        self.d_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stl.addWidget(self.d_label)
        main_row.addWidget(stat_frame)
        layout.addLayout(main_row)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self._init_particles()
        self._on_param_change()

    def _init_particles(self):
        w = max(self.canvas.width(), 400)
        h = max(self.canvas.height(), 300)
        colors = ["#58a6ff","#7ee787","#ffa657","#f78166","#d2a8ff","#f778ba","#79c0ff","#a371f7"]
        self.particles = []
        self.start_positions = []
        for i in range(self.num_particles):
            x = random.uniform(20, w - 20)
            y = random.uniform(20, h - 20)
            self.particles.append([x, y, 0, 0, colors[i % len(colors)]])
            self.start_positions.append((x, y))
        self.canvas.set_particles(self.particles)
        self.step_count = 0

    def _calc_D(self):
        T = self.temp_slider.value()
        r = self.size_slider.value() * 1e-9  # nm to m
        D = self.k_B * T / (6 * math.pi * self.eta * r)
        return D, T, r

    def _on_param_change(self):
        D, T, r = self._calc_D()
        self.temp_label.setText(f"{T} K")
        self.size_label.setText(f"{self.size_slider.value()} nm")
        self.d_label.setText(f"D = {D:.3e} m²/s")
        self.stats_label.setText(
            f"<b>Temperature:</b> {T} K<br>"
            f"<b>Radius:</b> {r*1e9:.0f} nm<br>"
            f"<b>Viscosity:</b> {self.eta:.1e} Pa·s<br>"
            f"<b>Diffusion coeff:</b> {D:.2e} m²/s<br>"
            f"<b>Steps:</b> {self.step_count}"
        )

    def _toggle_run(self):
        if self.running:
            self.timer.stop()
            self.running = False
            self.start_btn.setText("▶ Start")
        else:
            self.timer.start(33)  # ~30 fps
            self.running = True
            self.start_btn.setText("⏸ Pause")

    def _reset(self):
        self.timer.stop()
        self.running = False
        self.start_btn.setText("▶ Start")
        self._init_particles()
        self._on_param_change()

    def _step(self):
        D, T, r = self._calc_D()
        w = max(self.canvas.width(), 400)
        h = max(self.canvas.height(), 300)
        # Scale factor: map real D to pixel movement
        # Typical D for 10nm at 300K: ~2.4e-11 m²/s
        # In 33ms, RMS displacement = sqrt(2*d*D*dt) in meters
        # We scale to make it visually meaningful (amplify by ~1e9)
        dt = 0.033
        scale = 5e8  # visual amplification
        rms = math.sqrt(4 * D * dt) * scale  # 2D

        for i, p in enumerate(self.particles):
            dx = random.gauss(0, rms)
            dy = random.gauss(0, rms)
            p[0] = (p[0] + dx) % w
            p[1] = (p[1] + dy) % h

        self.step_count += 1
        self.canvas.set_particles(self.particles)

        if self.step_count % 5 == 0:
            self._on_param_change()


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: CNT Chirality Explorer
# ═══════════════════════════════════════════════════════════

class GrapheneLatticeWidget(QWidget):
    """Draws a 2D graphene lattice with chiral vector."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.n = 10; self.m = 10
        self.setFixedSize(340, 300)

    def set_chirality(self, n, m):
        self.n = n; self.m = m
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#010409"))

        # Draw hexagonal lattice (simplified)
        a = 14  # pixel spacing
        cx, cy = w // 2, h // 2
        p.setPen(QPen(QColor("#21262d"), 1))
        # Draw grid of hexagons
        for row in range(-8, 9):
            for col in range(-8, 9):
                x0 = cx + col * a * 1.5
                y0 = cy + row * a * math.sqrt(3) + (col % 2) * a * math.sqrt(3) / 2
                if -20 < x0 < w + 20 and -20 < y0 < h + 20:
                    self._draw_hex(p, x0, y0, a * 0.6)

        # Draw basis vectors a1 and a2
        a1_len = a * 3
        a2_len = a * 3
        # a1 = (a1_len, 0), a2 = (a1_len/2, a1_len*sqrt(3)/2)
        a1x, a1y = a1_len, 0
        a2x, a2y = a1_len / 2, a1_len * math.sqrt(3) / 2

        # Draw a1, a2
        p.setPen(QPen(QColor("#484f58"), 2))
        p.drawLine(cx, cy, cx + int(a1x), cy + int(a1y))
        p.drawLine(cx, cy, cx + int(a2x), cy + int(a2y))
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QColor("#484f58"))
        p.drawText(cx + int(a1x) + 4, cy - 4, "a₁")
        p.drawText(cx + int(a2x) + 4, cy + int(a2y), "a₂")

        # Draw chiral vector Ch = n*a1 + m*a2
        chx = self.n * a1x + self.m * a2x
        chy = self.n * a1y + self.m * a2y
        # Scale to fit
        max_len = math.sqrt(chx**2 + chy**2)
        if max_len > 0:
            scale = min(120 / max_len, 1.0)
            chx *= scale; chy *= scale

        is_metal = (2 * self.n + self.m) % 3 == 0
        vec_color = "#ffa657" if is_metal else "#58a6ff"
        p.setPen(QPen(QColor(vec_color), 3))
        p.drawLine(cx, cy, cx + int(chx), cy + int(chy))

        # Arrowhead
        angle = math.atan2(chy, chx)
        arr_len = 10
        p.drawLine(cx + int(chx), cy + int(chy),
                   cx + int(chx - arr_len * math.cos(angle - 0.4)), cy + int(chy - arr_len * math.sin(angle - 0.4)))
        p.drawLine(cx + int(chx), cy + int(chy),
                   cx + int(chx - arr_len * math.cos(angle + 0.4)), cy + int(chy - arr_len * math.sin(angle + 0.4)))

        p.setPen(QColor(vec_color))
        p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        p.drawText(cx + int(chx/2) + 8, cy + int(chy/2) - 8, f"C_({self.n},{self.m})")
        p.end()

    def _draw_hex(self, p, cx, cy, r):
        pts = []
        for i in range(6):
            angle = math.pi / 6 + i * math.pi / 3
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        for i in range(6):
            x1, y1 = pts[i]; x2, y2 = pts[(i+1) % 6]
            p.drawLine(int(x1), int(y1), int(x2), int(y2))


class CNTChiralityExplorerPage(QWidget):
    def __init__(self):
        super().__init__()
        self._a_cc = 0.246  # nm, carbon-carbon distance in graphene
        self._gamma0 = 2.7  # eV, tight-binding overlap
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🔗"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("CNT Chirality Explorer"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Carbon nanotubes are defined by their chirality indices (n,m). These determine whether the tube is metallic or semiconducting, its diameter, band gap, and chiral angle. Explore how different (n,m) values create different nanotubes!")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Controls
        ctrl = QHBoxLayout(); ctrl.setSpacing(16)
        # n index
        n_frame = QFrame(); n_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        nl = QVBoxLayout(n_frame); nl.setSpacing(6)
        nt = QLabel("n index"); nt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        self.n_spin = QSpinBox(); self.n_spin.setRange(0, 20); self.n_spin.setValue(10)
        self.n_spin.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:6px;color:#c9d1d9;padding:6px;font-size:14px;")
        self.n_spin.valueChanged.connect(self._update)
        nl.addWidget(nt); nl.addWidget(self.n_spin)
        ctrl.addWidget(n_frame)

        # m index
        m_frame = QFrame(); m_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        ml = QVBoxLayout(m_frame); ml.setSpacing(6)
        mt = QLabel("m index"); mt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        self.m_spin = QSpinBox(); self.m_spin.setRange(0, 20); self.m_spin.setValue(10)
        self.m_spin.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:6px;color:#c9d1d9;padding:6px;font-size:14px;")
        self.m_spin.valueChanged.connect(self._update)
        ml.addWidget(mt); ml.addWidget(self.m_spin)
        ctrl.addWidget(m_frame)

        # Presets
        p_frame = QFrame(); p_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        pl = QVBoxLayout(p_frame); pl.setSpacing(6)
        pt = QLabel("Presets"); pt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        presets = QHBoxLayout()
        for name, n, m in [("Armchair (10,10)", 10, 10), ("Zigzag (15,0)", 15, 0), ("Chiral (12,5)", 12, 5), ("Semi (11,3)", 11, 3)]:
            btn = QPushButton(name.split("(")[0].strip())
            btn.setStyleSheet("QPushButton{background:#21262d;color:#c9d1d9;border:1px solid #30363d;border-radius:6px;padding:6px 8px;font-size:10px;}")
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, nn=n, mm=m: self._set_preset(nn, mm))
            presets.addWidget(btn)
        pl.addWidget(pt); pl.addLayout(presets)
        ctrl.addWidget(p_frame, 1)
        layout.addLayout(ctrl)

        # Main: lattice + results
        main_row = QHBoxLayout(); main_row.setSpacing(16)
        self.lattice = GrapheneLatticeWidget()
        main_row.addWidget(self.lattice)

        # Results
        res_frame = QFrame(); res_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;}")
        rl = QVBoxLayout(res_frame); rl.setSpacing(6)
        rt = QLabel("Properties"); rt.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.type_label = QLabel(); self.type_label.setStyleSheet("font-size:18px;font-weight:bold;")
        self.type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results = QLabel(); self.results.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.7;")
        self.results.setWordWrap(True)
        rl.addWidget(rt); rl.addWidget(self.type_label); rl.addWidget(self.results)
        main_row.addWidget(res_frame, 1)
        layout.addLayout(main_row)

        # Insight
        self.insight = QLabel(); self.insight.setWordWrap(True)
        self.insight.setStyleSheet("color:#8b949e;font-size:11px;border-left:3px solid #a371f7;padding:8px 12px;background:#1c2333;border-radius:0 6px 6px 0;")
        layout.addWidget(self.insight)
        layout.addStretch()
        self._update()

    def _set_preset(self, n, m):
        self.n_spin.setValue(n); self.m_spin.setValue(m)

    def _update(self):
        n, m = self.n_spin.value(), self.m_spin.value()
        self.lattice.set_chirality(n, m)

        # Calculate properties
        C = self._a_cc * math.sqrt(n**2 + n*m + m**2)  # circumference in nm
        d_t = C / math.pi  # diameter
        theta = math.degrees(math.atan2(math.sqrt(3) * m, 2 * n + m))  # chiral angle
        is_metal = (2 * n + m) % 3 == 0

        if is_metal:
            self.type_label.setText("⚡ METALLIC")
            self.type_label.setStyleSheet("font-size:18px;font-weight:bold;color:#ffa657;")
            Eg = 0
            type_detail = "Zero or near-zero band gap. Conducts electricity."
        else:
            Eg = 2 * self._a_cc * self._gamma0 / d_t if d_t > 0 else 0
            self.type_label.setText("🔵 SEMICONDUCTING")
            self.type_label.setStyleSheet("font-size:18px;font-weight:bold;color:#58a6ff;")
            type_detail = f"Band gap = {Eg:.3f} eV. Can be turned on/off like a switch."

        # Determine type name
        if m == 0:
            cnt_type = "Zigzag"
        elif n == m:
            cnt_type = "Armchair"
        else:
            cnt_type = "Chiral"

        self.results.setText(
            f"<b>Type:</b> {cnt_type}<br>"
            f"<b>Circumference:</b> {C:.3f} nm<br>"
            f"<b>Diameter:</b> {d_t:.3f} nm<br>"
            f"<b>Chiral angle:</b> {theta:.1f}°<br>"
            f"<b>(2n+m) mod 3:</b> {(2*n+m)%3}<br>"
            f"<b>Band gap:</b> {Eg:.4f} eV<br>"
            f"{type_detail}"
        )

        # Insight
        if n == m:
            ins = f"Armchair nanotubes (n=n) are always metallic because (2n+n) mod 3 = 3n mod 3 = 0. The (10,10) armchair tube has a diameter of {d_t:.2f} nm and is one of the most studied CNTs for interconnects."
        elif m == 0:
            mod_val = (2*n) % 3
            if mod_val == 0:
                ins = f"Zigzag nanotube (n,0) with (2n+0) mod 3 = 0, so it's metallic. Zigzag tubes have chiral angle θ = 0° — the carbon hexagons align with the tube axis."
            else:
                ins = f"Zigzag semiconducting tube. (2×{n}) mod 3 = {mod_val} ≠ 0. The band gap E_g ≈ 2aγ₀/d = {Eg:.3f} eV, which decreases with larger diameter — a direct consequence of quantum confinement weakening."
        else:
            ins = f"Chiral nanotube with θ = {theta:.1f}°. About 1/3 of all (n,m) combinations are metallic (when 2n+m is divisible by 3), 2/3 are semiconducting. This 2:1 ratio is crucial for CNT electronics — separating metallic from semiconducting tubes remains a major manufacturing challenge."

        self.insight.setText(ins)



# ═══════════════════════════════════════════════════════════
#  MAIN WINDOW (v3)
# ═══════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Drug Release Kinetics Simulator
# ═══════════════════════════════════════════════════════════

class ReleasePlotWidget(QWidget):
    """Draws drug release curves with QPainter."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._curves = []  # list of (points, color, label)
        self.setMinimumSize(500, 280)

    def set_curves(self, curves):
        self._curves = curves
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#010409"))

        margin_l, margin_b, margin_t, margin_r = 65, 45, 30, 20
        pw = w - margin_l - margin_r
        ph = h - margin_t - margin_b

        # Grid
        p.setPen(QPen(QColor("#21262d"), 1))
        for i in range(11):
            x = margin_l + int(pw * i / 10)
            p.drawLine(x, margin_t, x, margin_t + ph)
            y = margin_t + int(ph * i / 10)
            p.drawLine(margin_l, y, margin_l + pw, y)

        # Axes
        p.setPen(QPen(QColor("#484f58"), 2))
        p.drawLine(margin_l, margin_t, margin_l, margin_t + ph)
        p.drawLine(margin_l, margin_t + ph, margin_l + pw, margin_t + ph)

        # Labels
        p.setPen(QColor("#8b949e"))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(margin_l + pw // 2 - 30, h - 5, "Time (hours)")
        p.drawText(5, margin_t + ph // 2 + 5, "Release %")
        for i in range(11):
            x = margin_l + int(pw * i / 10)
            p.drawText(x - 8, margin_t + ph + 18, str(i * 10))
            y = margin_t + ph - int(ph * i / 10)
            p.drawText(margin_l - 35, y + 4, f"{i * 10}%")

        # Curves
        legend_y = margin_t + 10
        for points, color, label in self._curves:
            if len(points) < 2: continue
            path = QPainterPath()
            for i, (t, frac) in enumerate(points):
                x = margin_l + int(pw * min(t / 100.0, 1.0))
                y = margin_t + ph - int(ph * min(frac, 1.0))
                if i == 0: path.moveTo(x, y)
                else: path.lineTo(x, y)
            p.setPen(QPen(QColor(color), 2))
            p.drawPath(path)
            # Legend
            p.setPen(QPen(QColor(color), 2))
            p.drawLine(margin_l + pw - 140, legend_y, margin_l + pw - 115, legend_y)
            p.setPen(QColor(color))
            p.setFont(QFont("Segoe UI", 9))
            p.drawText(margin_l + pw - 110, legend_y + 4, label)
            legend_y += 18
        p.end()


class DrugReleaseSimPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("💉"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Drug Release Kinetics Simulator"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Explore how nanoparticles release drugs over time! Different release models describe different physical mechanisms: diffusion-controlled (Higuchi), constant-rate (zero-order), and concentration-dependent (first-order). Adjust parameters and compare models side by side.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Equation reference
        eq = QLabel("Higuchi: M_t/M_inf = k_H * sqrt(t)  |  Zero-order: M_t/M_inf = k_0 * t  |  First-order: M_t/M_inf = 1 - e^(-k_1 * t)")
        eq.setStyleSheet("color:#f0f6fc;font-size:11px;font-family:monospace;background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px 14px;")
        eq.setWordWrap(True)
        layout.addWidget(eq)

        # Model checkboxes + sliders
        ctrl = QHBoxLayout(); ctrl.setSpacing(12)
        # Left: model selection
        model_frame = QFrame(); model_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        ml = QVBoxLayout(model_frame); ml.setSpacing(8)
        mt = QLabel("Release Models"); mt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        ml.addWidget(mt)
        self.higuchi_cb = QCheckBox("Higuchi (Diffusion)"); self.higuchi_cb.setChecked(True)
        self.higuchi_cb.setStyleSheet("color:#c9d1d9;font-size:12px;")
        self.zero_cb = QCheckBox("Zero-Order (Constant Rate)"); self.zero_cb.setChecked(True)
        self.zero_cb.setStyleSheet("color:#c9d1d9;font-size:12px;")
        self.first_cb = QCheckBox("First-Order (Exponential)"); self.first_cb.setChecked(True)
        self.first_cb.setStyleSheet("color:#c9d1d9;font-size:12px;")
        for cb in [self.higuchi_cb, self.zero_cb, self.first_cb]:
            cb.stateChanged.connect(self._update)
            ml.addWidget(cb)
        ctrl.addWidget(model_frame)

        # Right: parameter sliders
        param_frame = QFrame(); param_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        pl = QVBoxLayout(param_frame); pl.setSpacing(8)
        pt = QLabel("Parameters"); pt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        pl.addWidget(pt)

        # k_H slider
        kh_l = QLabel("k_H (Higuchi rate):"); kh_l.setStyleSheet("color:#8b949e;font-size:11px;")
        self.kh_slider = QSlider(Qt.Orientation.Horizontal); self.kh_slider.setRange(1,20); self.kh_slider.setValue(10)
        self.kh_label = QLabel("0.10 h^-1/2"); self.kh_label.setStyleSheet("color:#f0f6fc;font-size:12px;font-weight:bold;")
        self.kh_slider.valueChanged.connect(self._update)
        pl.addWidget(kh_l); pl.addWidget(self.kh_slider); pl.addWidget(self.kh_label)

        # k_0 slider
        k0_l = QLabel("k_0 (Zero-order rate):"); k0_l.setStyleSheet("color:#8b949e;font-size:11px;")
        self.k0_slider = QSlider(Qt.Orientation.Horizontal); self.k0_slider.setRange(1,20); self.k0_slider.setValue(5)
        self.k0_label = QLabel("0.05 h^-1"); self.k0_label.setStyleSheet("color:#f0f6fc;font-size:12px;font-weight:bold;")
        self.k0_slider.valueChanged.connect(self._update)
        pl.addWidget(k0_l); pl.addWidget(self.k0_slider); pl.addWidget(self.k0_label)

        # k_1 slider
        k1_l = QLabel("k_1 (First-order rate):"); k1_l.setStyleSheet("color:#8b949e;font-size:11px;")
        self.k1_slider = QSlider(Qt.Orientation.Horizontal); self.k1_slider.setRange(1,50); self.k1_slider.setValue(10)
        self.k1_label = QLabel("0.10 h^-1"); self.k1_label.setStyleSheet("color:#f0f6fc;font-size:12px;font-weight:bold;")
        self.k1_slider.valueChanged.connect(self._update)
        pl.addWidget(k1_l); pl.addWidget(self.k1_slider); pl.addWidget(self.k1_label)

        ctrl.addWidget(param_frame, 1)
        layout.addLayout(ctrl)

        # Plot
        self.plot = ReleasePlotWidget()
        layout.addWidget(self.plot, 1)

        # Insight
        self.insight = QLabel(); self.insight.setWordWrap(True)
        self.insight.setStyleSheet("color:#8b949e;font-size:11px;border-left:3px solid #7ee787;padding:8px 12px;background:#1c2333;border-radius:0 6px 6px 0;")
        layout.addWidget(self.insight)
        layout.addStretch()
        self._update()

    def _update(self):
        kH = self.kh_slider.value() / 100.0
        k0 = self.k0_slider.value() / 100.0
        k1 = self.k1_slider.value() / 100.0
        self.kh_label.setText(f"{kH:.2f} h^-1/2")
        self.k0_label.setText(f"{k0:.2f} h^-1")
        self.k1_label.setText(f"{k1:.2f} h^-1")

        curves = []
        N = 200
        t_max = 100

        if self.higuchi_cb.isChecked():
            pts = []
            for i in range(N):
                t = t_max * i / (N - 1)
                frac = min(kH * math.sqrt(t), 1.0)
                pts.append((t, frac))
            curves.append((pts, "#58a6ff", "Higuchi"))

        if self.zero_cb.isChecked():
            pts = []
            for i in range(N):
                t = t_max * i / (N - 1)
                frac = min(k0 * t, 1.0)
                pts.append((t, frac))
            curves.append((pts, "#7ee787", "Zero-order"))

        if self.first_cb.isChecked():
            pts = []
            for i in range(N):
                t = t_max * i / (N - 1)
                frac = 1.0 - math.exp(-k1 * t)
                pts.append((t, frac))
            curves.append((pts, "#ffa657", "First-order"))

        self.plot.set_curves(curves)

        # 50% release time comparison
        def find_t50(model_func):
            for t in [i * 0.1 for i in range(1, 1000)]:
                if model_func(t) >= 0.5:
                    return t
            return None

        parts = []
        if self.higuchi_cb.isChecked():
            t50 = find_t50(lambda t: min(kH * math.sqrt(t), 1.0))
            if t50: parts.append(f"Higuchi t50 = {t50:.1f} h")
        if self.zero_cb.isChecked():
            t50 = find_t50(lambda t: min(k0 * t, 1.0))
            if t50: parts.append(f"Zero-order t50 = {t50:.1f} h")
        if self.first_cb.isChecked():
            t50 = find_t50(lambda t: 1.0 - math.exp(-k1 * t))
            if t50: parts.append(f"First-order t50 = {t50:.1f} h")

        self.insight.setText("📊 " + " | ".join(parts) + " — The Higuchi model shows characteristic square-root-of-time dependence (fast initial, then slowing). Zero-order gives ideal constant release. First-order slows exponentially as drug concentration drops.")


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Nanoparticle Surface Area Calculator
# ═══════════════════════════════════════════════════════════

class SurfaceAreaViz(QWidget):
    """Visualizes nanoparticle vs bulk surface area with circles."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bulk_r = 50; self._nano_r = 50; self._count = 1
        self.setFixedSize(350, 300)

    def set_params(self, bulk_r, nano_r, count):
        self._bulk_r = bulk_r; self._nano_r = nano_r; self._count = min(count, 200)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#010409"))

        # Draw bulk particle
        cx, cy = 90, 140
        r = min(self._bulk_r, 70)
        grad = QRadialGradient(cx - r*0.2, cy - r*0.2, r)
        grad.setColorAt(0, QColor("#79c0ff"))
        grad.setColorAt(1, QColor("#1f6feb"))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor("#58a6ff"), 2))
        p.drawEllipse(cx - r, cy - r, r*2, r*2)
        p.setPen(QColor("#8b949e"))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(cx - 20, cy + r + 18, "Bulk")

        # Draw nano particles
        nano_display = max(self._nano_r, 3)
        nano_display = min(nano_display, 25)
        base_x = 210
        cols = int(math.sqrt(self._count))
        spacing = nano_display * 2 + 4
        for i in range(min(self._count, 100)):
            row = i // max(cols, 1)
            col = i % max(cols, 1)
            nx = base_x + col * spacing
            ny = 40 + row * spacing
            if ny > h - 30: break
            grad2 = QRadialGradient(nx - 1, ny - 1, nano_display)
            grad2.setColorAt(0, QColor("#ffa657"))
            grad2.setColorAt(1, QColor("#d29922"))
            p.setBrush(QBrush(grad2))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(nx - nano_display), int(ny - nano_display),
                         int(nano_display * 2), int(nano_display * 2))

        p.setPen(QColor("#8b949e"))
        p.drawText(base_x, h - 10, f"Nano ({self._count}x)")
        p.end()


class SurfaceAreaCalcPage(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📐"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Nanoparticle Surface Area Calculator"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Why are nanoparticles so much more reactive than bulk material? The answer is surface-area-to-volume ratio. As particles shrink, a larger fraction of atoms sits on the surface. This directly impacts catalysis, drug delivery efficiency, and chemical reactivity.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Equation
        eq = QLabel("SA/V = 3/r (sphere)  |  Total SA = N × 4πr²  |  N = V_bulk / V_nano = (R/r)³")
        eq.setStyleSheet("color:#f0f6fc;font-size:11px;font-family:monospace;background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px 14px;")
        layout.addWidget(eq)

        ctrl = QHBoxLayout(); ctrl.setSpacing(16)
        # Bulk radius
        bf = QFrame(); bf.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        bl = QVBoxLayout(bf); bl.setSpacing(6)
        bl.addWidget(QLabel("Bulk Radius (nm)"))
        self.bulk_spin = QSpinBox(); self.bulk_spin.setRange(10, 10000); self.bulk_spin.setValue(1000)
        self.bulk_spin.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:6px;color:#c9d1d9;padding:6px;font-size:13px;")
        self.bulk_spin.valueChanged.connect(self._update); bl.addWidget(self.bulk_spin)
        ctrl.addWidget(bf)

        # Nano radius
        nf = QFrame(); nf.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        nl = QVBoxLayout(nf); nl.setSpacing(6)
        nl.addWidget(QLabel("Nano Radius (nm)"))
        self.nano_spin = QSpinBox(); self.nano_spin.setRange(1, 500); self.nano_spin.setValue(10)
        self.nano_spin.setStyleSheet("background:#0d1117;border:1px solid #21262d;border-radius:6px;color:#c9d1d9;padding:6px;font-size:13px;")
        self.nano_spin.valueChanged.connect(self._update); nl.addWidget(self.nano_spin)
        ctrl.addWidget(nf)

        # Material
        mf = QFrame(); mf.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        ml = QVBoxLayout(mf); ml.setSpacing(6)
        ml.addWidget(QLabel("Material"))
        self.mat_combo = QComboBox(); self.mat_combo.setObjectName("diffCombo")
        self.mat_combo.addItems(["Gold (19.3 g/cm³)", "Silver (10.5 g/cm³)", "Iron (7.87 g/cm³)", "Silica (2.65 g/cm³)", "TiO₂ (4.23 g/cm³)"])
        ml.addWidget(self.mat_combo)
        ctrl.addWidget(mf, 1)
        layout.addLayout(ctrl)

        # Viz + results
        row = QHBoxLayout(); row.setSpacing(16)
        self.viz = SurfaceAreaViz()
        row.addWidget(self.viz)

        res_frame = QFrame(); res_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;}")
        rl = QVBoxLayout(res_frame); rl.setSpacing(6)
        rt = QLabel("Results"); rt.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.results = QLabel(); self.results.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.8;")
        self.results.setWordWrap(True)
        rl.addWidget(rt); rl.addWidget(self.results)
        row.addWidget(res_frame, 1)
        layout.addLayout(row)

        self.insight = QLabel(); self.insight.setWordWrap(True)
        self.insight.setStyleSheet("color:#8b949e;font-size:11px;border-left:3px solid #f78166;padding:8px 12px;background:#1c2333;border-radius:0 6px 6px 0;")
        layout.addWidget(self.insight)
        layout.addStretch()
        self._update()

    def _update(self):
        R = self.bulk_spin.value()  # nm
        r = self.nano_spin.value()  # nm
        if r == 0: return
        ratio = R / r
        N = ratio ** 3
        sa_v_bulk = 3.0 / R  # 1/nm
        sa_v_nano = 3.0 / r   # 1/nm
        sa_ratio = sa_v_nano / sa_v_bulk  # = R/r

        self.viz.set_params(min(R / 15, 70), max(r / 1.5, 3), min(N, 100))

        self.results.setText(
            f"<b>Number of NPs from 1 bulk:</b> {N:.0f}<br>"
            f"<b>Bulk SA/V:</b> {sa_v_bulk:.4f} nm⁻¹<br>"
            f"<b>Nano SA/V:</b> {sa_v_nano:.4f} nm⁻¹<br>"
            f"<b>SA increase factor:</b> <span style='color:#ffa657;font-weight:bold'>{sa_ratio:.0f}x</span><br>"
            f"<b>Nano total SA:</b> {N * 4 * math.pi * r**2:.2e} nm²<br>"
            f"<b>Bulk total SA:</b> {4 * math.pi * R**2:.2e} nm²<br>"
            f"<b>SA increase total:</b> <span style='color:#7ee787;font-weight:bold'>{N * r / R:.0f}x</span>"
        )

        if sa_ratio > 100:
            ins = f"A {r} nm nanoparticle has {sa_ratio:.0f}x more surface area per volume than a {R} nm bulk particle. This enormous ratio means {sa_ratio:.0f}x more atoms are available for chemical reactions, making nanocatalysts dramatically more efficient. In drug delivery, this allows much higher drug loading per unit mass."
        elif sa_ratio > 10:
            ins = f"The {sa_ratio:.0f}x surface-area-to-volume ratio increase at {r} nm drives higher reactivity and better drug loading compared to bulk. Most nanomedicine applications use particles below 200 nm specifically for this reason."
        else:
            ins = f"At {r} nm, the surface-area advantage over {R} nm bulk is {sa_ratio:.1f}x — modest. For significant nanoscale effects, particles typically need to be below 100 nm."
        self.insight.setText(ins)


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Equation Reference Sheet
# ═══════════════════════════════════════════════════════════

EQUATIONS_HTML = """<h2>Key Equations in Nanotechnology</h2>

<h3>Quantum Mechanics</h3>
<p><b>de Broglie wavelength:</b> λ = h/(mv) — relates particle momentum to wavelength</p>
<p><b>Heisenberg uncertainty:</b> Δx · Δp ≥ ℏ/2 — fundamental measurement limit</p>
<p><b>Particle in a box:</b> E<sub>n</sub> = n²π²ℏ²/(2mL²) — quantum confinement energy levels</p>
<p><b>Tunneling probability:</b> T ≈ exp(-2κL), κ = √(2m(V-E))/ℏ — barrier penetration</p>
<p><b>Coulomb blockade:</b> E<sub>c</sub> = e²/(2C) — single-electron charging energy</p>

<h3>Plasmonics & Optics</h3>
<p><b>SPR condition (sphere):</b> ε<sub>m</sub>(ω) = -2ε<sub>d</sub> — resonance for small nanoparticles</p>
<p><b>Drude model:</b> ε(ω) = 1 - ω<sub>p</sub>²/(ω²+iγω) — metal dielectric function</p>
<p><b>Mie parameter:</b> x = 2πr/λ — determines scattering regime</p>
<p><b>Rayleigh scattering:</b> I ∝ 1/λ⁴ — why small particles scatter blue light</p>

<h3>Nanoelectronics</h3>
<p><b>Landauer formula:</b> G = (2e²/h) × T — quantum conductance per channel (G₀ ≈ 77.5 µS)</p>
<p><b>Memristance:</b> v = M(q) · i — charge-history-dependent resistance</p>
<p><b>GMR effect:</b> ΔR/R ∝ (M₁ · M₂) — spin-dependent scattering in multilayers</p>

<h3>Transport & Diffusion</h3>
<p><b>Stokes-Einstein:</b> D = k<sub>B</sub>T/(6πηr) — nanoparticle diffusion in fluids</p>
<p><b>Mean square displacement:</b> ⟨r²⟩ = 2dDt (d=dimensions) — Brownian motion</p>

<h3>Photonic Crystals</h3>
<p><b>Bragg condition:</b> 2d·n·cosθ = mλ — photonic bandgap formation</p>
<p><b>Purcell factor:</b> F<sub>P</sub> = (3/4π²)(λ/n)³(Q/V) — spontaneous emission enhancement</p>

<h3>Carbon Nanotubes</h3>
<p><b>Circumference:</b> C = a√(n² + nm + m²), a = 0.246 nm — CNT size from chirality</p>
<p><b>Metallic condition:</b> (2n + m) mod 3 = 0 — determines CNT electronic type</p>
<p><b>Band gap:</b> E<sub>g</sub> ≈ 2aγ₀/d<sub>t</sub> — semiconducting CNT band gap (γ₀ ≈ 2.7 eV)</p>

<h3>Drug Release Kinetics</h3>
<p><b>Higuchi model:</b> M<sub>t</sub>/M<sub>∞</sub> = k<sub>H</sub>√t — diffusion-controlled release</p>
<p><b>Zero-order:</b> M<sub>t</sub>/M<sub>∞</sub> = k₀t — constant release rate (ideal)</p>
<p><b>First-order:</b> M<sub>t</sub>/M<sub>∞</sub> = 1 - e<sup>-k₁t</sup> — concentration-dependent release</p>

<h3>Surface Area</h3>
<p><b>SA/V ratio (sphere):</b> 3/r — inversely proportional to radius</p>
<p><b>Total SA of N spheres:</b> N × 4πr² = (R/r)³ × 4πr² — nanoscale amplification</p>
"""

class EquationRefPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📋"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Equation Reference Sheet"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Quick reference for all key equations used in this app, organized by topic. Click on any equation topic in the content pages to see full derivations and explanations.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        browser = QTextBrowser(); browser.setObjectName("contentText")
        browser.setHtml(EQUATIONS_HTML)
        layout.addWidget(browser, 1)


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Achievements / Badges
# ═══════════════════════════════════════════════════════════

ACHIEVEMENTS = [
    ("🌟", "First Steps", "Visit your first content page", "visit_1"),
    ("📖", "Bookworm", "Visit all 9 content pages", "visit_all"),
    ("🧠", "Quiz Taker", "Complete your first quiz", "quiz_1"),
    ("🎯", "Sharp Mind", "Score 90%+ on any quiz", "quiz_90"),
    ("🃏", "Card Shark", "Master 15 flashcards", "flash_15"),
    ("🃏", "Card Master", "Master all 30 flashcards", "flash_all"),
    ("📝", "Note Taker", "Write notes on 3+ topics", "notes_3"),
    ("🔬", "Explorer", "Use all 5 interactive simulations", "sims_all"),
    ("⚡", "Deep Diver", "Open an Advanced tab on any topic", "adv_tab"),
    ("🏆", "Completionist", "Unlock all other achievements", "all_achievements"),
]


class AchievementsPage(QWidget):
    def __init__(self, progress_data):
        super().__init__()
        self.progress_data = progress_data
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("⭐"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Achievements"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.count_label = QLabel(); self.count_label.setStyleSheet("color:#7ee787;font-size:13px;font-weight:bold;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(self.count_label)
        layout.addLayout(header)

        desc = QLabel("Unlock badges by exploring content, taking quizzes, and using interactive tools. Each achievement represents a learning milestone!")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        container = QVBoxLayout(); container.setSpacing(10)
        self.badge_frames = []
        for emoji, name, desc_text, key in ACHIEVEMENTS:
            earned = self.progress_data.get("achievements", {}).get(key, False)
            f = QFrame()
            f.setStyleSheet(f"QFrame{{background:#161b22;border:1px solid {'#a371f7' if earned else '#21262d'};border-radius:10px;padding:14px 16px;}}")
            fl = QHBoxLayout(f); fl.setSpacing(14)
            e = QLabel(emoji); e.setStyleSheet(f"font-size:28px;{'opacity:1;' if earned else 'opacity:0.3;'}")
            info = QVBoxLayout(); info.setSpacing(2)
            n = QLabel(name); n.setStyleSheet(f"color:{'#d2a8ff' if earned else '#484f58'};font-size:15px;font-weight:bold;")
            d = QLabel(desc_text); d.setStyleSheet(f"color:{'#c9d1d9' if earned else '#30363d'};font-size:12px;")
            info.addWidget(n); info.addWidget(d)
            status = QLabel("✅ Earned!" if earned else "🔒 Locked")
            status.setStyleSheet(f"color:{'#7ee787' if earned else '#484f58'};font-size:11px;font-weight:bold;")
            fl.addWidget(e); fl.addLayout(info, 1); fl.addWidget(status)
            container.addWidget(f)
            self.badge_frames.append((f, key, emoji, name, desc_text, status, e, n, d))
        layout.addLayout(container)
        layout.addStretch()
        self._update_counts()

    def _update_counts(self):
        earned = sum(1 for _, key, *_ in self.badge_frames
                     if self.progress_data.get("achievements", {}).get(key, False))
        total = len(ACHIEVEMENTS)
        self.count_label.setText(f"{earned}/{total} unlocked")
        # Check completionist
        if earned == total - 1:
            self.progress_data.setdefault("achievements", {})["all_achievements"] = True


# ═══════════════════════════════════════════════════════════
#  NEW PAGE: Bookmarks
# ═══════════════════════════════════════════════════════════

class BookmarksPage(QWidget):
    def __init__(self, nav_callback=None, notes_data=None, progress_data=None):
        super().__init__()
        self.nav_callback = nav_callback
        self.notes_data = notes_data or {}
        self.progress_data = progress_data or {}
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("📑"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Bookmarks"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.count_label = QLabel(); self.count_label.setStyleSheet("color:#ffa657;font-size:13px;font-weight:bold;")
        header.addWidget(il); header.addWidget(tl); header.addWidget(self.count_label)
        layout.addLayout(header)

        desc = QLabel("Your bookmarked sections and saved highlights. Bookmark pages from the sidebar or navigate to them here.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Quick bookmark buttons
        qf = QFrame(); qf.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:12px;}")
        ql = QVBoxLayout(qf); ql.setSpacing(6)
        qt = QLabel("Quick Bookmark"); qt.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        ql.addWidget(qt)
        bm_row = QHBoxLayout(); bm_row.setSpacing(8)
        bookmarkable = ["📏 Intro","🤖 Nanites","💊 Apps","⚛️ Quantum","💾 Nanoelec","🌈 Nanophoto","🔌 Quantum Sim","🌊 Brownian","🔗 CNT","📋 Equations","💉 Drug Release","📐 Surface Area"]
        for label in bookmarkable:
            btn = QPushButton(label); btn.setObjectName("resetBtn")
            btn.clicked.connect(lambda checked, l=label: self._add_bookmark(l))
            bm_row.addWidget(btn)
        ql.addLayout(bm_row)
        layout.addWidget(qf)

        # Bookmarks list
        self.bm_container = QVBoxLayout(); self.bm_container.setSpacing(6)
        layout.addLayout(self.bm_container)
        layout.addStretch()
        self._refresh()

    def _add_bookmark(self, label):
        bookmarks = self.progress_data.get("bookmarks", [])
        if label not in bookmarks:
            bookmarks.append(label)
            self.progress_data["bookmarks"] = bookmarks
            self._refresh()

    def _refresh(self):
        while self.bm_container.count():
            item = self.bm_container.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        bookmarks = self.progress_data.get("bookmarks", [])
        self.count_label.setText(f"{len(bookmarks)} saved")
        if not bookmarks:
            empty = QLabel("No bookmarks yet. Use the Quick Bookmark buttons above or explore content to save your place.")
            empty.setStyleSheet("color:#484f58;font-size:12px;font-style:italic;"); empty.setWordWrap(True)
            self.bm_container.addWidget(empty)
            return
        for i, bm in enumerate(bookmarks):
            f = QFrame(); f.setObjectName("bookmarkCard")
            fl = QHBoxLayout(f); fl.setContentsMargins(14, 10, 14, 10)
            icon = QLabel("📑"); icon.setStyleSheet("font-size:18px;")
            lbl = QLabel(bm); lbl.setStyleSheet("color:#f0f6fc;font-size:13px;")
            lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            del_btn = QPushButton("✕"); del_btn.setStyleSheet("QPushButton{background:transparent;color:#ff7b72;border:none;font-size:14px;}")
            del_btn.clicked.connect(lambda checked, idx=i: self._remove(idx))
            fl.addWidget(icon); fl.addWidget(lbl, 1); fl.addWidget(del_btn)
            self.bm_container.addWidget(f)

    def _remove(self, idx):
        bookmarks = self.progress_data.get("bookmarks", [])
        if 0 <= idx < len(bookmarks):
            bookmarks.pop(idx)
            self.progress_data["bookmarks"] = bookmarks
            self._refresh()


# ═══════════════════════════════════════════════════════════
#  NEW: Nanobot Swarm Simulator
# ═══════════════════════════════════════════════════════════

class SwarmCanvas(QWidget):
    """Animated canvas showing nanobot swarm behavior."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bots = []  # list of [x, y, vx, vy, angle, color, state]
        self.targets = []  # list of [x, y, radius, color]
        self.setMinimumSize(450, 350)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        # Background
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0, QColor("#050a15"))
        bg.setColorAt(1, QColor("#0d1117"))
        p.fillRect(0, 0, w, h, QBrush(bg))
        # Grid (representing tissue/body fluid)
        p.setPen(QPen(QColor(20, 25, 35), 1))
        for x in range(0, w, 35):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, 35):
            p.drawLine(0, y, w, y)

        # Draw targets (tumor cells / delivery sites)
        for tx, ty, tr, tc in self.targets:
            glow = QRadialGradient(int(tx), int(ty), int(tr * 2.5))
            gc = QColor(tc)
            glow.setColorAt(0, QColor(gc.red(), gc.green(), gc.blue(), 50))
            glow.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(tx - tr * 2.5), int(ty - tr * 2.5), int(tr * 5), int(tr * 5))
            p.setBrush(QColor(gc.red(), gc.green(), gc.blue(), 80))
            p.setPen(QPen(QColor(tc), 1))
            p.drawEllipse(int(tx - tr), int(ty - tr), int(tr * 2), int(tr * 2))

        # Draw nanobots
        for bx, by, vx, vy, angle, color, state in self.bots:
            ix, iy = int(bx), int(by)
            # Glow based on state
            if state == "targeting":
                glow_color = QColor("#58a6ff")
            elif state == "delivering":
                glow_color = QColor("#7ee787")
            else:
                glow_color = QColor(color)
            glow = QRadialGradient(ix, iy, 14)
            glow.setColorAt(0, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 100))
            glow.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(ix - 14, iy - 14, 28, 28)
            # Body (triangle pointing in direction of motion)
            p.setBrush(QColor(color))
            p.setPen(QPen(QColor(255, 255, 255, 60), 1))
            a = angle
            size = 6
            pts = [
                QPointF(ix + size * math.cos(a), iy + size * math.sin(a)),
                QPointF(ix + size * 0.6 * math.cos(a + 2.4), iy + size * 0.6 * math.sin(a + 2.4)),
                QPointF(ix + size * 0.6 * math.cos(a - 2.4), iy + size * 0.6 * math.sin(a - 2.4)),
            ]
            p.drawPolygon(QPolygonF(pts))
        p.end()


class NanobotSwarmSimPage(QWidget):
    def __init__(self):
        super().__init__()
        self.bots = []
        self.targets = []
        self.running = False
        self.step_count = 0
        self.delivered = 0
        self.mode = "swarm"  # "swarm", "random", "chemotaxis"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🤖"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Nanobot Swarm Simulator"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Watch nanobots navigate through body fluid to reach a tumor target! Toggle between random Brownian motion, swarm intelligence, and chemotaxis modes. See how coordination dramatically improves targeting efficiency at the nanoscale.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Equations
        eq = QLabel("Stokes Drag: F = 6πηrv  |  Pe = vL/D  |  Re = ρvL/η  |  Diffusion: MSD = 2dDt")
        eq.setStyleSheet("color:#f0f6fc;font-size:11px;font-family:monospace;background:#161b22;border:1px solid #21262d;border-radius:8px;padding:8px 14px;")
        eq.setWordWrap(True)
        layout.addWidget(eq)

        # Controls row
        ctrl = QHBoxLayout(); ctrl.setSpacing(12)

        # Mode selection
        mode_frame = QFrame(); mode_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        ml = QVBoxLayout(mode_frame); ml.setSpacing(6)
        mt = QLabel("Navigation Mode"); mt.setStyleSheet("color:#58a6ff;font-size:12px;font-weight:bold;")
        ml.addWidget(mt)
        self.mode_combo = QComboBox(); self.mode_combo.setObjectName("diffCombo")
        self.mode_combo.addItems(["Swarm Intelligence", "Random (Brownian)", "Chemotaxis"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        ml.addWidget(self.mode_combo)
        ctrl.addWidget(mode_frame, 1)

        # Bot count
        count_frame = QFrame(); count_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        cl = QVBoxLayout(count_frame); cl.setSpacing(4)
        cl.addWidget(QLabel("Nanobot Count"))
        self.count_slider = QSlider(Qt.Orientation.Horizontal)
        self.count_slider.setRange(5, 80); self.count_slider.setValue(25)
        self.count_label = QLabel("25"); self.count_label.setStyleSheet("color:#f0f6fc;font-size:13px;font-weight:bold;")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_slider.valueChanged.connect(lambda v: self.count_label.setText(str(v)))
        cl.addWidget(self.count_slider); cl.addWidget(self.count_label)
        ctrl.addWidget(count_frame, 1)

        # Propulsion strength
        prop_frame = QFrame(); prop_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        pl2 = QVBoxLayout(prop_frame); pl2.setSpacing(4)
        pl2.addWidget(QLabel("Propulsion Force"))
        self.prop_slider = QSlider(Qt.Orientation.Horizontal)
        self.prop_slider.setRange(1, 100); self.prop_slider.setValue(40)
        self.prop_label = QLabel("40%"); self.prop_label.setStyleSheet("color:#f0f6fc;font-size:13px;font-weight:bold;")
        self.prop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prop_slider.valueChanged.connect(lambda v: self.prop_label.setText(str(v) + "%"))
        pl2.addWidget(self.prop_slider); pl2.addWidget(self.prop_label)
        ctrl.addWidget(prop_frame, 1)

        # Buttons
        btn_frame = QFrame(); btn_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:10px;}")
        bl = QVBoxLayout(btn_frame); bl.setSpacing(6)
        self.start_btn = QPushButton("▶ Start"); self.start_btn.setObjectName("submitBtn")
        self.start_btn.clicked.connect(self._toggle_run); bl.addWidget(self.start_btn)
        self.reset_btn = QPushButton("↺ Reset"); self.reset_btn.setObjectName("resetBtn")
        self.reset_btn.clicked.connect(self._reset); bl.addWidget(self.reset_btn)
        ctrl.addWidget(btn_frame)
        layout.addLayout(ctrl)

        # Canvas + stats
        main_row = QHBoxLayout(); main_row.setSpacing(14)
        self.canvas = SwarmCanvas()
        self.canvas.setStyleSheet("border:1px solid #21262d;border-radius:8px;")
        main_row.addWidget(self.canvas, 1)

        stat_frame = QFrame(); stat_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:8px;padding:14px;}")
        stl = QVBoxLayout(stat_frame); stl.setSpacing(6)
        st = QLabel("Swarm Statistics"); st.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        self.stats_label = QLabel(); self.stats_label.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.7;")
        self.stats_label.setWordWrap(True)
        stl.addWidget(st); stl.addWidget(self.stats_label)

        # Legend
        legend = QLabel("Legend:")
        legend.setStyleSheet("color:#8b949e;font-size:11px;font-weight:bold;margin-top:8px;")
        stl.addWidget(legend)
        for color, label in [("#ff7b72", "Tumor Target"), ("#58a6ff", "Targeting"), ("#7ee787", "Delivering"), ("#ffa657", "Random")]:
            row = QHBoxLayout()
            dot = QLabel("●"); dot.setStyleSheet(f"color:{color};font-size:14px;")
            txt = QLabel(label); txt.setStyleSheet("color:#8b949e;font-size:11px;")
            row.addWidget(dot); row.addWidget(txt); row.addStretch()
            stl.addLayout(row)

        main_row.addWidget(stat_frame)
        layout.addLayout(main_row)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self._init_scene()

    def _init_scene(self):
        w = max(self.canvas.width(), 450)
        h = max(self.canvas.height(), 350)
        n = self.count_slider.value()
        colors = ["#58a6ff", "#79c0ff", "#a371f7", "#d2a8ff", "#f778ba", "#ffa657"]
        self.bots = []
        for i in range(n):
            x = random.uniform(30, w - 30)
            y = random.uniform(30, h - 30)
            angle = random.uniform(0, 2 * math.pi)
            self.bots.append([x, y, 0.0, 0.0, angle, colors[i % len(colors)], "random"])
        # Targets (tumor)
        tx, ty = w * 0.75, h * 0.5
        self.targets = [[tx, ty, 30, "#ff7b72"]]
        self.canvas.bots = self.bots
        self.canvas.targets = self.targets
        self.canvas.update()

    def _on_mode_change(self, idx):
        modes = ["swarm", "random", "chemotaxis"]
        self.mode = modes[idx] if idx < len(modes) else "swarm"

    def _toggle_run(self):
        if self.running:
            self.timer.stop()
            self.running = False
            self.start_btn.setText("▶ Start")
        else:
            self.timer.start(33)  # ~30 fps
            self.running = True
            self.start_btn.setText("⏸ Pause")

    def _reset(self):
        self.timer.stop()
        self.running = False
        self.start_btn.setText("▶ Start")
        self.step_count = 0
        self.delivered = 0
        self._init_scene()
        self._update_stats()

    def _step(self):
        self.step_count += 1
        w = max(self.canvas.width(), 450)
        h = max(self.canvas.height(), 350)
        prop = self.prop_slider.value() / 100.0
        tx, ty, tr, _ = self.targets[0]

        for bot in self.bots:
            bx, by, bvx, bvy, angle, color, state = bot

            # Base Brownian noise
            noise_x = random.gauss(0, 1.5)
            noise_y = random.gauss(0, 1.5)

            if self.mode == "random":
                # Pure Brownian motion + slight random propulsion
                fx = noise_x + random.gauss(0, 0.5)
                fy = noise_y + random.gauss(0, 0.5)
                bot[6] = "random"

            elif self.mode == "swarm":
                # Reynolds flocking + target attraction
                # Separation
                sep_x, sep_y, sep_count = 0, 0, 0
                # Alignment & Cohesion
                ali_x, ali_y, coh_x, coh_y, n_count = 0, 0, 0, 0, 0
                for other in self.bots:
                    if other is bot: continue
                    dx = bx - other[0]
                    dy = by - other[1]
                    dist = math.sqrt(dx*dx + dy*dy) + 0.01
                    if dist < 40:
                        sep_x += dx / dist
                        sep_y += dy / dist
                        sep_count += 1
                    if dist < 100:
                        ali_x += other[2]
                        ali_y += other[3]
                        coh_x += other[0]
                        coh_y += other[1]
                        n_count += 1

                if sep_count > 0:
                    sep_x /= sep_count; sep_y /= sep_count
                if n_count > 0:
                    ali_x /= n_count; ali_y /= n_count
                    coh_x = coh_x / n_count - bx
                    coh_y = coh_y / n_count - by

                # Target attraction
                dx_t = tx - bx
                dy_t = ty - by
                dist_t = math.sqrt(dx_t*dx_t + dy_t*dy_t) + 0.01
                target_fx = dx_t / dist_t * 2.0
                target_fy = dy_t / dist_t * 2.0

                fx = (sep_x * 1.5 + ali_x * 0.5 + coh_x * 0.3 + target_fx * 2.0) * prop + noise_x
                fy = (sep_y * 1.5 + ali_y * 0.5 + coh_y * 0.3 + target_fy * 2.0) * prop + noise_y

                if dist_t < 50:
                    bot[6] = "targeting"
                if dist_t < tr + 5:
                    bot[6] = "delivering"
                    self.delivered += 1

            elif self.mode == "chemotaxis":
                # Follow chemical gradient toward target
                dx_t = tx - bx
                dy_t = ty - by
                dist_t = math.sqrt(dx_t*dx_t + dy_t*dy_t) + 0.01
                # Gradient: stronger when closer
                grad_strength = 3.0 * prop / (1 + dist_t * 0.01)
                fx = dx_t / dist_t * grad_strength + noise_x * 1.2
                fy = dy_t / dist_t * grad_strength + noise_y * 1.2
                if dist_t < 60:
                    bot[6] = "targeting"
                if dist_t < tr + 5:
                    bot[6] = "delivering"
                    self.delivered += 1
            else:
                fx, fy = noise_x, noise_y

            # Update velocity with drag (low Re: no inertia)
            drag = 0.85
            bot[2] = fx * drag
            bot[3] = fy * drag

            # Update position
            new_x = bx + bot[2]
            new_y = by + bot[3]

            # Boundary wrapping
            if new_x < 5: new_x = w - 5
            if new_x > w - 5: new_x = 5
            if new_y < 5: new_y = h - 5
            if new_y > h - 5: new_y = 5
            bot[0] = new_x
            bot[1] = new_y

            # Update angle
            speed = math.sqrt(bot[2]**2 + bot[3]**2)
            if speed > 0.1:
                bot[4] = math.atan2(bot[3], bot[2])

        self.canvas.bots = self.bots
        self.canvas.update()
        if self.step_count % 10 == 0:
            self._update_stats()

    def _update_stats(self):
        n = len(self.bots)
        targeting = sum(1 for b in self.bots if b[6] == "targeting")
        delivering = sum(1 for b in self.bots if b[6] == "delivering")
        random_c = sum(1 for b in self.bots if b[6] == "random")
        avg_speed = sum(math.sqrt(b[2]**2 + b[3]**2) for b in self.bots) / max(n, 1)
        # Compute avg distance to target
        tx, ty = self.targets[0][0], self.targets[0][1]
        avg_dist = sum(math.sqrt((b[0]-tx)**2 + (b[1]-ty)**2) for b in self.bots) / max(n, 1)

        text = (
            f"Step: {self.step_count}\n"
            f"Nanobots: {n}\n"
            f"Mode: {self.mode.title()}\n\n"
            f"Targeting: {targeting}\n"
            f"Delivering: {delivering}\n"
            f"Wandering: {random_c}\n\n"
            f"Avg Speed: {avg_speed:.1f} px/step\n"
            f"Avg Distance: {avg_dist:.0f} px\n"
            f"Total Deliveries: {self.delivered}"
        )
        self.stats_label.setText(text)


# ═══════════════════════════════════════════════════════════
#  NEW: Nanobot Design Lab
# ═══════════════════════════════════════════════════════════



class BotVizWidget(QWidget):
    """Draws a simple nanobot visualization."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._bot_type = ""
        self._color = "#58a6ff"
        self.setMinimumSize(100, 100)

    def set_bot(self, bot_type, color):
        self._bot_type = bot_type
        self._color = QColor(color)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#010409"))
        cx, cy = w // 2, h // 2

        if "DNA" in self._bot_type:
            # Draw DNA helix representation
            for i in range(30):
                t = i * 0.4
                x1 = cx + int(30 * math.cos(t))
                y1 = 10 + i * 4
                x2 = cx - int(30 * math.cos(t))
                y2 = y1
                if y1 > h - 5: break
                p.setPen(QPen(QColor(88, 166, 255, 150), 2))
                p.drawLine(x1, y1, x2, y2)
                p.setPen(QPen(QColor(163, 113, 247, 150), 2))
                p.drawPoint(x1, y1)
                p.drawPoint(x2, y2)
        elif "Magnetic" in self._bot_type:
            # Draw helix
            p.setPen(QPen(self._color, 3))
            path = QPainterPath()
            for i in range(60):
                t = i * 0.15
                x = cx + int(15 * math.cos(t))
                y = 10 + i * 2
                if y > h - 5: break
                if i == 0: path.moveTo(x, y)
                else: path.lineTo(x, y)
            p.drawPath(path)
            # Arrow
            p.setBrush(QColor("#ff7b72"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(cx - 4, h - 20, 8, 8)
        elif "Biological" in self._bot_type:
            # Draw bacterium shape
            body_w, body_h = 60, 25
            p.setBrush(QColor(126, 231, 135, 80))
            p.setPen(QPen(QColor(126, 231, 135), 2))
            p.drawRoundedRect(cx - body_w//2, cy - body_h//2, body_w, body_h, body_h//2, body_h//2)
            # Flagella
            p.setPen(QPen(QColor(126, 231, 135, 120), 1))
            for j in range(3):
                pts = QPainterPath()
                for i in range(20):
                    t = i * 0.3
                    x = cx - body_w//2 - 5 - i * 2 + int(5 * math.sin(t + j * 2))
                    y = cy - 5 + j * 5 + int(3 * math.cos(t * 1.5))
                    if i == 0: pts.moveTo(x, y)
                    else: pts.lineTo(x, y)
                p.drawPath(pts)
        elif "Gold" in self._bot_type:
            # Gold nanoshell (concentric circles)
            p.setBrush(QColor(255, 166, 87, 60))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(cx - 35, cy - 35, 70, 70)
            p.setBrush(QColor(250, 163, 7, 100))
            p.drawEllipse(cx - 25, cy - 25, 50, 50)
            p.setBrush(QColor(255, 186, 8, 180))
            p.drawEllipse(cx - 15, cy - 15, 30, 30)
            # Light rays
            p.setPen(QPen(QColor(255, 186, 8, 80), 1))
            for a in range(0, 360, 30):
                rad = math.radians(a)
                p.drawLine(cx + int(18 * math.cos(rad)), cy + int(18 * math.sin(rad)),
                           cx + int(40 * math.cos(rad)), cy + int(40 * math.sin(rad)))
        elif "Lipid" in self._bot_type:
            # LNP (vesicle)
            p.setBrush(QColor(210, 168, 255, 40))
            p.setPen(QPen(QColor(210, 168, 255, 150), 2))
            p.drawEllipse(cx - 30, cy - 30, 60, 60)
            # Inner cargo
            p.setBrush(QColor(163, 113, 247, 80))
            p.setPen(Qt.PenStyle.NoPen)
            for _ in range(5):
                rx = cx + random.randint(-15, 15)
                ry = cy + random.randint(-15, 15)
                p.drawEllipse(rx, ry, 4, 4)
            # PEG chains
            p.setPen(QPen(QColor(210, 168, 255, 60), 1))
            for a in range(0, 360, 45):
                rad = math.radians(a)
                sx = cx + int(28 * math.cos(rad))
                sy = cy + int(28 * math.sin(rad))
                for k in range(3):
                    ex = sx + int(6 * math.cos(rad + 0.3 * (k - 1)))
                    ey = sy + int(6 * math.sin(rad + 0.3 * (k - 1)))
                    p.drawLine(sx, sy, ex, ey)
                    sx, sy = ex, ey

        p.end()

class NanobotDesignLabPage(QWidget):
    """Interactive nanobot design explorer — configure components, see equations and specs."""

    DESIGNS = {
        "DNA Nanobot": {
            "size_um": 0.1, "speed": 0.01, "payload": "small molecules",
            "power": "ATP / strand displacement", "sensing": "DNA aptamers",
            "propulsion": "Diffusion + DNA walker", "lifetime": "hours",
            "color": "#58a6ff",
            "desc": "Built from folded DNA strands using DNA origami. Walks along DNA tracks via strand displacement. Can carry drug molecules and sense specific mRNA sequences. The 2018 Ido Bachelet experiment used DNA nanobots to target tumors in mice.",
            "eqs": "Strand displacement rate: k_sd ~ 10^5-10^7 M^-1 s^-1\nToehold length: 6-12 nt (longer = faster)\nWalker step: ~10 nm per step\nEnergy per step: ~5-20 kT (from hybridization)"
        },
        "Magnetic Microswimmer": {
            "size_um": 1.0, "speed": 20.0, "payload": "drugs, genes",
            "power": "External rotating B field", "sensing": "magnetic resonance",
            "propulsion": "Helical corkscrew rotation", "lifetime": "days (external power)",
            "color": "#f78166",
            "desc": "A helical nanopropeller made from magnetic materials, driven by external rotating magnetic fields. The helical shape is essential: at low Re, non-reciprocal motion is required (scallop theorem). Steering precision ~100 um. Can navigate through bodily fluids including blood.",
            "eqs": "Propulsion: F = m x grad(B)\nHelical pitch: 1-5 um\nRotation: 5-50 Hz (external)\nRe ~ 10^-4 (viscous dominated)\nStokes drag: F = 6 pi eta r v"
        },
        "Biological Hybrid (E. coli)": {
            "size_um": 2.0, "speed": 30.0, "payload": "proteins, enzymes",
            "power": "Glucose metabolism (ATP)", "sensing": "chemoreceptors",
            "propulsion": "Flagellar rotation (~200 Hz)", "lifetime": "days (self-powered)",
            "color": "#7ee787",
            "desc": "Engineered bacteria programmed with synthetic gene circuits. Self-powered by metabolizing glucose. Flagella rotate at ~200 Hz. Can sense chemical gradients (chemotaxis), produce therapeutic molecules on demand, and communicate via quorum sensing. Most practical near-term nanobot platform.",
            "eqs": "Flagellar thrust: F ~ 0.5 pN\nSpeed: 20-30 um/s\nChemotaxis sensitivity: ~1% gradient\nKd (receptor): 10^-6 to 10^-9 M\nATP per glucose: ~30 molecules"
        },
        "Gold Nanoshell Bot": {
            "size_um": 0.15, "speed": 0.1, "payload": "heat (photothermal)",
            "power": "Near-infrared laser", "sensing": "SPR spectral shift",
            "propulsion": "Diffusion (passive targeting)", "lifetime": "weeks (inert)",
            "color": "#ffa657",
            "desc": "A gold-coated nanoparticle (silica core, gold shell) that absorbs near-infrared light and converts it to heat. Used for photothermal therapy: accumulate at tumor site, then zap with NIR laser to kill cancer cells. Surface plasmon resonance is tuned by shell thickness to ~800 nm (tissue-transparent window).",
            "eqs": "SPR wavelength: lambda_SPR ~ 700-900 nm\nTemperature rise: dT ~ P_abs / (4 pi kappa r)\nAbsorption cross-section: sigma_abs ~ 10^-14 m^2\nEfficacy: >50% light-to-heat\nShell thickness: 5-20 nm"
        },
        "Lipid Nanoparticle (LNP)": {
            "size_um": 0.08, "speed": 0.01, "payload": "mRNA, siRNA, drugs",
            "power": "None (passive)", "sensing": "cell uptake (endocytosis)",
            "propulsion": "Blood circulation (passive)", "lifetime": "hours (before clearance)",
            "color": "#d2a8ff",
            "desc": "The workhorse of modern nanomedicine. LNPs are lipid vesicles 50-100 nm that encapsulate fragile molecules. The Pfizer and Moderna COVID-19 vaccines used LNPs to deliver mRNA to cells. Four lipid components: ionizable lipid (encapsulation + endosomal escape), PEG-lipid (stealth), cholesterol (stability), helper phospholipid (structure).",
            "eqs": "Size: 50-100 nm (optimal for endocytosis)\nCirculation t1/2: 15-20h (PEGylated)\nEncapsulation efficiency: >90%\nEndosomal escape: pH-triggered\nZeta potential: -10 to -30 mV"
        },
    }

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0); layout.setSpacing(14)
        header = QHBoxLayout()
        il = QLabel("🧠"); il.setStyleSheet("font-size:26px;")
        tl = QLabel("Nanobot Design Lab"); tl.setObjectName("pageTitle")
        tl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        header.addWidget(il); header.addWidget(tl)
        layout.addLayout(header)

        desc = QLabel("Explore different nanobot architectures! Select a design to see its components, specifications, equations, and real-world applications. Compare how DNA nanobots, magnetic swimmers, biological hybrids, gold nanoshells, and lipid nanoparticles differ in their approach to nanoscale tasks.")
        desc.setStyleSheet("color:#8b949e;font-size:12px;"); desc.setWordWrap(True)
        layout.addWidget(desc)

        # Design selector
        sel_row = QHBoxLayout(); sel_row.setSpacing(8)
        sel_label = QLabel("Select Design:"); sel_label.setStyleSheet("color:#58a6ff;font-size:13px;font-weight:bold;")
        sel_row.addWidget(sel_label)
        self.design_combo = QComboBox(); self.design_combo.setObjectName("diffCombo")
        for name in self.DESIGNS:
            self.design_combo.addItem(name)
        self.design_combo.currentTextChanged.connect(self._update_display)
        sel_row.addWidget(self.design_combo, 1)
        layout.addLayout(sel_row)

        # Main content area
        content = QHBoxLayout(); content.setSpacing(14)

        # Left: spec card
        left_frame = QFrame(); left_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        left_layout = QVBoxLayout(left_frame); left_layout.setSpacing(10)
        self.design_title = QLabel(); self.design_title.setStyleSheet("font-size:18px;font-weight:bold;color:#f0f6fc;")
        left_layout.addWidget(self.design_title)

        # Nanobot visualization
        self.bot_viz = BotVizWidget(); self.bot_viz.setFixedHeight(120)
        self.bot_viz.setStyleSheet("border:1px solid #21262d;border-radius:8px;background:#010409;")
        left_layout.addWidget(self.bot_viz)

        self.design_desc = QLabel(); self.design_desc.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.6;")
        self.design_desc.setWordWrap(True)
        left_layout.addWidget(self.design_desc)
        content.addWidget(left_frame, 1)

        # Right: specs table + equations
        right_frame = QFrame(); right_frame.setStyleSheet("QFrame{background:#161b22;border:1px solid #21262d;border-radius:10px;padding:16px;}")
        right_layout = QVBoxLayout(right_frame); right_layout.setSpacing(10)

        # Specs
        specs_title = QLabel("Specifications"); specs_title.setStyleSheet("color:#58a6ff;font-size:14px;font-weight:bold;")
        right_layout.addWidget(specs_title)

        self.specs_label = QLabel(); self.specs_label.setStyleSheet("color:#c9d1d9;font-size:12px;line-height:1.8;")
        self.specs_label.setWordWrap(True)
        right_layout.addWidget(self.specs_label)

        sep = QFrame(); sep.setStyleSheet("background:#21262d;max-height:1px;"); sep.setFixedHeight(1)
        right_layout.addWidget(sep)

        # Equations
        eq_title = QLabel("Key Equations"); eq_title.setStyleSheet("color:#7ee787;font-size:14px;font-weight:bold;")
        right_layout.addWidget(eq_title)

        self.eq_label = QLabel(); self.eq_label.setStyleSheet("color:#c9d1d9;font-size:11px;font-family:monospace;line-height:1.8;background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:10px 12px;")
        self.eq_label.setWordWrap(True)
        right_layout.addWidget(self.eq_label)

        # Comparison hint
        self.compare_label = QLabel(); self.compare_label.setStyleSheet("color:#8b949e;font-size:11px;font-style:italic;")
        self.compare_label.setWordWrap(True)
        right_layout.addWidget(self.compare_label)

        right_layout.addStretch()
        content.addWidget(right_frame, 1)
        layout.addLayout(content)

        self._update_display(self.design_combo.currentText())

    def _update_display(self, name):
        d = self.DESIGNS.get(name)
        if not d: return
        self.design_title.setText(f'<span style="color:{d["color"]}">●</span> {name}')
        self.design_desc.setText(d["desc"])

        specs = (
            f'<table style="color:#c9d1d9;font-size:12px;line-height:2;">'
            f'<tr><td style="color:#8b949e;">Size:</td><td><b>{d["size_um"]} µm ({d["size_um"]*1000:.0f} nm)</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Speed:</td><td><b>{d["speed"]} µm/s</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Payload:</td><td><b>{d["payload"]}</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Power:</td><td><b>{d["power"]}</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Sensing:</td><td><b>{d["sensing"]}</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Propulsion:</td><td><b>{d["propulsion"]}</b></td></tr>'
            f'<tr><td style="color:#8b949e;">Lifetime:</td><td><b>{d["lifetime"]}</b></td></tr>'
            f'</table>'
        )
        self.specs_label.setText(specs)
        self.eq_label.setText(d["eqs"])

        # Compute Re and Pe for comparison
        eta = 8.9e-4
        rho = 1000
        k_B = 1.381e-23
        T = 310
        r = d["size_um"] * 1e-6 / 2
        v = d["speed"] * 1e-6
        Re = rho * v * (d["size_um"] * 1e-6) / eta if v > 0 else 0
        D = k_B * T / (6 * math.pi * eta * r) if r > 0 else 0
        Pe = v * (d["size_um"] * 1e-6) / D if D > 0 else 0
        self.compare_label.setText(
            f"Computed at body temp (310 K, water):\n"
            f"  Re = {Re:.2e} (viscous {'dominates' if Re < 1 else 'significant'})\n"
            f"  D = {D:.2e} m\u00b2/s (diffusion coefficient)\n"
            f"  Pe = {Pe:.2e} ({'diffusion' if Pe < 1 else 'propulsion'} dominated)"
        )

        # Update bot visualization
        self.bot_viz.set_bot(name, d["color"])


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NanoLearn v5 — Nanotechnology & Nanites")
        self.setMinimumSize(QSize(1050, 720))
        self.resize(1250, 820)
        self.setStyleSheet(STYLESHEET)

        self.notes_data = load_json(NOTES_FILE, {})
        self.progress_data = load_json(PROGRESS_FILE, {})

        central = QWidget(); central.setObjectName("central")
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame(); sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(210)
        sl = QVBoxLayout(sidebar); sl.setContentsMargins(0,0,0,0); sl.setSpacing(0)

        at = QLabel("NanoLearn"); at.setObjectName("appTitle")
        asub = QLabel("Nanotech & Nanites"); asub.setObjectName("appSubtitle")
        sl.addWidget(at); sl.addWidget(asub); sl.addSpacing(6)

        self.global_search = QLineEdit(); self.global_search.setObjectName("searchBox")
        self.global_search.setPlaceholderText("🔍 Search...")
        self.global_search.setFixedWidth(186)
        self.global_search.textChanged.connect(self._global_search)
        sl.addWidget(self.global_search); sl.addSpacing(4)

        sep = QFrame(); sep.setStyleSheet("background:#21262d;max-height:1px;"); sep.setFixedHeight(1)
        sl.addWidget(sep); sl.addSpacing(2)

        self.nav_buttons = []
        self.nav_group = QButtonGroup(self); self.nav_group.setExclusive(True)
        for i, (icon, label) in enumerate(NAV_ITEMS):
            btn = QPushButton(f"  {icon}   {label}")
            btn.setObjectName("navBtn"); btn.setCheckable(True)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.nav_group.addButton(btn, i)
            sl.addWidget(btn); self.nav_buttons.append(btn)
            if i == 0: btn.setChecked(True)

        sl.addStretch()
        ver = QLabel("v5.0 — 2025"); ver.setStyleSheet("color:#484f58;font-size:10px;padding:10px 14px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(ver)
        main_layout.addWidget(sidebar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:#0d1117;border:none;")

        # Create all pages
        page_ids = ["introduction", "nanites", "applications", "history", "safety", "future",
                     "quantum", "nanoelectronics", "nanophotonics"]
        content_pages = []
        for idx, (icon, title, levels) in enumerate(CONTENT_PAGES):
            cp = TabbedContentPage(title, icon, levels, page_ids[idx], self.notes_data, self.progress_data)
            content_pages.append(cp)

        # Load bookmarks/achievements
        self.bookmarks_data = load_json(BOOKMARKS_FILE, [])

        self.pages = [
            HomePage(),
            *content_pages,
            SizeExplorerPage(),
            NanoparticleLabPage(),
            QuantumConfinementSimPage(),
            BrownianMotionSimPage(),
            CNTChiralityExplorerPage(),
            DrugReleaseSimPage(),
            SurfaceAreaCalcPage(),
            EquationRefPage(),
            NanobotSwarmSimPage(),
            NanobotDesignLabPage(),
            AchievementsPage(self.progress_data),
            BookmarksPage(),
            FlashcardPage(self.progress_data),
            MatchingGamePage(),
            EnhancedQuizPage(self.progress_data),
            GlossaryPage(),
            NotesPage(self.notes_data, self.progress_data),
            DashboardPage(self.progress_data, self.notes_data),
        ]

        for page in self.pages:
            scroll = QScrollArea(); scroll.setObjectName("contentArea")
            scroll.setWidgetResizable(True); scroll.setWidget(page)
            self.stack.addWidget(scroll)

        main_layout.addWidget(self.stack, 1)
        self.nav_group.idClicked.connect(self._navigate)

        self._save_timer = QTimer()
        self._save_timer.timeout.connect(self._auto_save)
        self._save_timer.start(5000)

    def _navigate(self, idx):
        self._check_achievements(idx)

    def _check_achievements(self, idx):
        ach = self.progress_data.setdefault("achievements", {})
        # Visit tracking
        content_indices = list(range(1, 10))  # 9 content pages
        if idx in content_indices:
            visited = self.progress_data.get("visited", [])
            if len(visited) >= 1: ach["visit_1"] = True
            if len(visited) >= 9: ach["visit_all"] = True
        # Sim tracking
        sim_indices = [11, 12, 13, 14, 15, 17, 18, 19]  # Size, NanoLab, Quantum, Brownian, CNT, Drug, SurfaceArea, Swarm, DesignLab
        if idx in sim_indices:
            sims_used = self.progress_data.get("sims_used", [])
            if idx not in sims_used: sims_used.append(idx)
            self.progress_data["sims_used"] = sims_used
            if len(sims_used) >= 5: ach["sims_all"] = True
        # Flashcard tracking
        fc_known = len(self.progress_data.get("flashcards", {}).get("known", []))
        if fc_known >= 15: ach["flash_15"] = True
        if fc_known >= 30: ach["flash_all"] = True
        # Notes tracking
        notes_count = len([v for v in self.notes_data.values() if v.strip()])
        if notes_count >= 3: ach["notes_3"] = True
        self.stack.setCurrentIndex(idx)

    def _global_search(self, text):
        q = text.lower().strip()
        for i, (icon, label) in enumerate(NAV_ITEMS):
            if not q or q in label.lower():
                self.nav_buttons[i].setVisible(True)
            else:
                self.nav_buttons[i].setVisible(False)

    def _auto_save(self):
        save_json(PROGRESS_FILE, self.progress_data)

    def closeEvent(self, event):
        save_json(NOTES_FILE, self.notes_data)
        save_json(PROGRESS_FILE, self.progress_data)
        save_json(BOOKMARKS_FILE, self.bookmarks_data)
        event.accept()


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Set up library paths for PySide6
    import os
    _venv_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".venv", "lib")
    if os.path.isdir(_venv_lib):
        _current = os.environ.get("LD_LIBRARY_PATH", "")
        if _venv_lib not in _current:
            os.environ["LD_LIBRARY_PATH"] = f"{_venv_lib}:{_current}" if _current else _venv_lib
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#161b22"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#21262d"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#c9d1d9"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1f6feb"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
