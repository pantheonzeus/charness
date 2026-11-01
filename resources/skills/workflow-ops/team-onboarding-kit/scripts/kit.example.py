"""Example kit config. Copy to <run-dir>/kit.py and fill in for the engagement.

Everything engagement-specific lives here: names, dates, client, wording. The scripts and template stay generic.
Media keys (A1, V1, I1, QX, ...) are the keys in jobs.json / artifacts.json.
"""

NOTEBOOK_URL = "https://notebooklm.google.com/notebook/<notebook-id>"

ENGAGEMENT = dict(
    key="acme-sprint",                       # localStorage namespace; unique per kit
    title="Acme · Service Concept Sprint",
    subtitle="Acme · Service Concept Sprint · prep week 2–6 Mar · sprint 9–20 Mar",
    banner="Confidential: client engagement. For you only; don't forward outside the core team.",
    prep_label="2–6 Mar",
    sprint_label="9–20 Mar",
    ready_by="Friday 6 Mar",
    playbook=None,                           # path to a shared playbook HTML to copy into the kit, or None
)

# One line per media key: what the listener gets from it.
MEDIA_DESC = {
    "V1": "The sprint in two minutes.",
    "A1": "Why the client wants this, what we deliver, how the days run, who owns what.",
    "A2": "All core concepts on one running example.",
    "A3": "The red team: the client's strongest objections and our replies.",
    "I1": "The sprint on one page.",
}

# Library order (all media); each person's path picks from these.
ORDER = ["V1", "A1", "I1", "A2", "A3"]

# Day label → ISO date, used to highlight "today".
DATES = {"Mon 2": "2027-03-02", "Tue 3": "2027-03-03", "Wed 4": "2027-03-04", "Thu 5": "2027-03-05", "Fri 6": "2027-03-06",
         "Mon 9": "2027-03-09", "Fri 13": "2027-03-13", "Fri 20": "2027-03-20"}

PEOPLE = {
    "alex": dict(
        name="Alex", full="Alex Example", role="Engagement lead · technology",
        owns="The technical concept, architecture fit and the decision log.",
        others="Sam owns the service design and the research sessions.",
        promise="No basics: the frontier, the contested evidence and the objections. You also check the material before the team relies on it.",
        quiz="QA",                           # quiz key in artifacts.json, or None
        week=[
            dict(day="Mon 2", title="Check the material, then the frontier", min=30, media=["V1", "A3"],
                 doing=["Check V1 and the first 5 minutes of A1 before the team starts",
                        "Settle the open scope decisions with the account lead"]),
            dict(day="Tue 3", title="Know the concept cold", min=60, media=["A2"],
                 doing=["Draft the templates the client will react to on day 1"]),
        ],
        sprint={"Mon 9": "Open the kick-off; get the final decision-maker named.",
                "Fri 13": "Run the checkpoint to a written decision; send the sponsor one-pager.",
                "Fri 20": "Lead the final walkthrough; ask for the go/no-go in the room."},
        ready=["I can explain the concept in 60 seconds without notes",
               "I have a one-line reply to each objection in A3"],
        ask=["Which source gives the strongest counter-evidence to our approach?",
             "Which of our claims rest only on vendor or secondary sources?"],
        reading=[("Building effective agents (Anthropic)", "https://www.anthropic.com/research/building-effective-agents",
                  "When an agent is needed and when a workflow is enough.")]),
    "sam": dict(
        name="Sam", full="Sam Example", role="Senior service designer",
        owns="The service blueprint, the interviews and the prototype test.",
        others="Alex owns the technical concept and the decision log.",
        promise="Designing a service with the new technology in it, step by step. About 40 minutes a day.",
        quiz="QS",
        week=[
            dict(day="Mon 2", title="The whole picture", min=25, media=["V1", "A1", "I1"],
                 doing=["Draft the straw-man success criteria"]),
        ],
        sprint={"Mon 9": "Set up the work-in-progress board; capture the working agreement.",
                "Fri 20": "Present the blueprint and what the test broke and fixed."},
        ready=["I can draw the future-state blueprint with its oversight lane"],
        ask=["Write a test script for the prototype session: roles, request, what to log."],
        reading=[]),
}
