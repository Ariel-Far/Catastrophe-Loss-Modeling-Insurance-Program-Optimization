# Your Showcase Package — What Each File Is & How to Use It

You now have a **designed, professional showcase** — not rudimentary code, but materials
built to impress both technical reviewers and non-technical decision-makers (recruiters,
hiring managers, clients). Three formats, one story.

---

## The three showcase pieces

### 1. `Ariel_Farzan_Case_Study.pdf` — **LEAD WITH THIS**
A polished two-page visual case study designed like a consulting/actuarial tear-sheet.
It opens with the *human problem* (a CFO, a risk manager, and a broker who each want a
different answer), walks through your method, shows the loss exhibits, and lands on your
recommendation — including the "Three stakeholders, three answers" decision panel that
makes a non-technical person instantly get why you're valuable.

**Use it for:**
- **LinkedIn** → attach as media on the project entry (shows as a visual card)
- **Handshake** → attach to applications where allowed
- **Email to recruiters/clients** → this is the thing you send
- **Portfolio link** → host it or link the PDF directly

### 2. `risk_simulator.html` — **the "wow, it's live" piece**
An interactive dashboard where someone moves sliders (fire frequency, earthquake
likelihood, severity) and watches the Monte Carlo re-price the risk in real time, with a
live insurance-program comparison that auto-flags the recommended option. This is the
cutting-edge element that signals you build *real, working* tools.

**Use it for:**
- **Host it free** on GitHub Pages, Netlify, or Vercel, then link it from your LinkedIn
  project and resume ("Interactive demo: [link]")
- **Screen-share it in interviews** — let them drive. Nothing lands harder than handing
  someone the controls.
- Works in any modern browser; needs internet for the chart library to load.

### 3. `case_study.html` — the web version of the PDF
Same content as the PDF, as a responsive web page. Host it as your portfolio page, or
keep the PDF as the primary and this as a backup/web format.

---

## Supporting files (the proof underneath)
- `cat_loss_model.py` — the actual Python analysis (load → fit → simulate → compare → plot)
- `Loss_Run_20241231.xlsx` — the historical loss data
- `exhibit_losses_by_peril.png` — the loss-distribution exhibit
- `README.md` — technical readme for the code

Keep these ready to share when someone technical asks "can I see the code?" — they're
your credibility backup.

---

## How to deploy the interactive dashboard (free, ~5 min)

**Easiest — GitHub Pages:**
1. Create a free GitHub account + a new public repository.
2. Upload `risk_simulator.html` (rename it `index.html`).
3. Repo Settings → Pages → set source to `main` branch → Save.
4. Your live link appears in ~1 minute: `https://[username].github.io/[repo]/`
5. Put that link on LinkedIn, your resume, and in applications.

**Alternative — Netlify Drop:** go to app.netlify.com/drop and drag the HTML file in.
Instant public link, no account needed to start.

---

## The pitch, in one line
> "I built a catastrophe-loss model that prices insurance decisions on tail risk —
> here's the one-page case study, and here's a live demo you can drive yourself."

That sentence + the PDF + the live link is a stronger portfolio than 95% of students
and most early freelancers will show. Lead with the story, prove it with the demo,
back it with the code.

---

## Stay accurate
Everything here is true: a **Runner-Up** Aon-sponsored case competition project that you
**rebuilt and extended in Python**. You can walk through every step — the distribution
fitting, the simulation, the tail-risk reasoning — in any interview. That defensibility
is what makes it powerful. Never inflate it; you don't need to.
