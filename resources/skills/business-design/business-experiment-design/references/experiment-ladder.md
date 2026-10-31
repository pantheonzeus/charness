# Experiment Ladder — cheap/weak → costly/strong

A curated subset of the experiments in Bland & Osterwalder, *Testing Business Ideas* (2019), which describes 44 of them. Cost and strength grades here are our own relative ratings (Low/Med/High), set for B2B and industrial contexts. They aren't the book's numbers. Pick the cheapest rung that can falsify the hypothesis in question.

## Discovery — "is there something here?"
| Experiment | Tests | Cost | Evidence | Note |
|---|---|---|---|---|
| Customer interviews (problem) | D | Low | Weak | Past behaviour only ("last time you…"), never "would you…" |
| Expert / partner / supplier interviews | F, V | Low | Weak | Good for cost-to-serve and partner willingness |
| Sales-force / support-ticket analysis | D | Low | Medium | Real complaints with frequency, which is better than opinions |
| Search-trend / forum / review mining | D | Low | Weak–Med | Agent-friendly (see `agent-augmented-discovery`); cite every source |
| A day in the life (observation) | D, F | Med | Medium | Shows workarounds that interviews miss |
| Online ad / link tracking | D | Low | Medium | Message × segment click-through |
| Explainer video / brochure / data sheet | D, V | Low | Medium | B2B: send to buyers, measure follow-up requests |
| Paper / storyboard prototype | D | Low | Weak | Comprehension, not demand |

## Validation — "will they commit?"
| Experiment | Tests | Cost | Evidence | Note |
|---|---|---|---|---|
| Simple landing page + sign-up | D | Low | Medium | One segment, one message per page |
| Fake door / feature stub | D | Low | Medium | Disclose honestly after the click |
| Split test (price or message) | D, V | Med | Medium–Strong | Needs traffic; B2B often lacks it |
| Mock sale / pre-sale | V | Med | Strong | Refund path mandatory |
| Letter of intent | V | Med | Strong (B2B) | Named signatory with budget authority |
| Paid pilot / proof of value | V, F | High | Strong | The B2B gold standard. Define success KPIs in the contract |
| Concierge MVP (humans deliver by hand) | D, V, F | Med | Strong | Real cost-to-serve data, great before automating with agents |
| Wizard of Oz (looks automated, human behind) | D, F | Med | Strong | Classic way to test an agent-delivered service before building the agent |
| Single-feature MVP | D, V, F | High | Strong | Only after the cheaper rungs passed |
| Crowdfunding | D, V | Med | Strong | B2C/prosumer only |

## Sequencing rules
1. A pass on a weak rung buys a test on a stronger rung, never a launch.
2. Viability hypotheses (price, willingness to pay, partner economics) need at least one Strong-rung pass before a launch gate.
3. Concierge and Wizard-of-Oz tests come before automating with agents. They give the cost-to-serve baseline the `ai-native-business-model` needs.
