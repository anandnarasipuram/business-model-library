# Entry schema (v0.1)

One JSON file per business model in `entries/`. Same schema for the public and the private layer
(`visibility` decides which build includes it).

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | kebab-case, matches file name |
| `name` | yes | Model name, e.g. "Shared-savings heating optimisation" |
| `aliases` | no | Other names the model goes by |
| `archetype` | yes | One of: hardware_saas, rental_leasing, shared_savings, guaranteed_savings, partner_commission, flexibility_revenue_share, tariff_bundle, submetering, tenant_energy, ev_charging, data_platform, marketplace, other |
| `sector` | yes | e.g. `energy`, `iot`, `energy+iot` |
| `summary` | yes | 1-3 sentences, plain language |
| `perspective` | yes | Whose view the entry takes. Default `product_company` |
| `how_it_makes_money` | yes | Revenue logic, no confidential numbers in public entries |
| `building_blocks` | yes | What the model needs: hardware, software, sites_assets, partners, regulation, financing, channel, data (lists of strings; empty list if not needed) |
| `stakeholder_value` | no | Who gets what value (customer, provider, partner, other) |
| `what_must_be_true` | yes | Conditions for the model to work |
| `risks_failure_causes` | yes | Known ways it fails, each tagged with `tag` and `evidence` |
| `evidence` | yes | `documented`, `inferred`, `assumed` or `speculative` for the entry as a whole |
| `outcome` | yes | `successful`, `failed`, `pivoted`, `unproven`, `niche` (outcome is separate from evidence) |
| `cases` | no | Real-world instances: `company`, `market`, `period`, `outcome`, `evidence`, `note`, `source_ids` |
| `parameters` | no | Inputs the simulation engine will use later: `key`, `label`, `unit`, `default`, `low`, `high`, `evidence` |
| `match` | yes | Matching data: `segments`, `domains` (heating, electricity, flexibility, mobility, general), `customer_capex` (none, low, high = what the customer must pay upfront) and `needs` (provider_financing, measurable_savings, installer_network, own_hardware, smart_meter) |
| `sources` | yes | List of `{id, kind, title, url, accessed}`. `kind` is `public`, `first_hand` or `press` |
| `last_verified` | yes | ISO date |
| `status` | yes | `draft`, `reviewed` |
| `visibility` | yes | `public` or `private` |

Rules
- Every factual claim in a public entry needs a source id or is tagged `assumed`/`speculative`.
- First-hand experience is a source of kind `first_hand`; keep company-confidential figures out of public entries.
- "Not covered yet" is a valid answer; never fill a gap with a guess presented as fact.
