**Items Test Coverage**

This document lists held items implemented in `backend/items/items.py` and whether they are currently exercised by unit tests in `backend/test`.

How to update: when you add a test that depends on an item's damage behaviour, mark it as tested (✅) and reference the test that covers it.

**Tested items (present in tests)**

- `meadow-plate`: ✅ covered by `backend/test/test_calcs.py::test_case_1`
- `assault-vest`: ✅ covered by `backend/test/test_calcs.py` (several cases)
- `life-orb`: ✅ covered by `backend/test/test_calcs.py::test_case_2`
- `eviolite`: ✅ covered by `backend/test/test_calcs.py` and `backend/test/test_kyogre_simple.py`
- `choice-specs`: ✅ covered by `backend/test/test_calcs.py` (several cases)
- `choice-band`: ✅ covered by `backend/test/test_calcs.py` and `backend/test/test_garchomp_golem.py`

**Items present in `items.py` but not currently covered by tests**

The list below was taken from `backend/items/items.py`. These items have behaviour that can affect damage (type boosts, power modifiers, final multipliers, stat multipliers, one-use gems, etc.) but currently lack explicit unit tests in `backend/test`.

- `charcoal`
- `magnet`
- `sharp-beak`
- `black-belt`
- `mystic-water`
- `miracle-seed`
- `never-melt-ice`
- `poison-barb`
- `hard-stone`
- `soft-sand`
- `spell-tag`
- `twisted-spoon`
- `dragon-fang`
- `black-glasses`
- `metal-coat`
- `silk-scarf`
- `silver-powder`
- `fairy-feather`
- `odd-incense`
- `rose-incense`
- `sea-incense`
- `wave-incense`
- `rock-incense`
- `full-incense`
- `flame-plate`
- `splash-plate`
- `zap-plate`
- `icicle-plate`
- `fist-plate`
- `toxic-plate`
- `earth-plate`
- `sky-plate`
- `mind-plate`
- `insect-plate`
- `stone-plate`
- `spooky-plate`
- `draco-plate`
- `dread-plate`
- `iron-plate`
- `pixie-plate`
- `adamant-orb`
- `lustrous-orb`
- `griseous-orb`
- `soul-dew`
- `deep-sea-tooth`
- `deep-sea-scale`
- `light-ball`
- `thick-club`
- `muscle-band`
- `wise-glasses`
- `expert-belt`
- `normal-gem`
- `loaded-dice`
- `iron-ball`
- `macho-brace`
- `air-balloon`
- `booster-energy`
- `hearthflame-mask`
- `wellspring-mask`
- `cornerstone-mask`
- `chople-berry`
- `coba-berry`
- `kebia-berry`
- `shuca-berry`
- `charti-berry`
- `tanga-berry`
- `kasib-berry`
- `haban-berry`
- `colbur-berry`
- `babiri-berry`
- `occa-berry`
- `passho-berry`
- `wacan-berry`
- `rindo-berry`
- `yache-berry`
- `roseli-berry`
- `payapa-berry`
- `chilan-berry`
