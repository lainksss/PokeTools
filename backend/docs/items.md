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
- `charcoal`: ✅ covered by `backend/test/test_items_powerups.py::test_charcoal_charizard_flamethrower`
- `magnet`: ✅ covered by `backend/test/test_items_powerups.py::test_magnet_magnezone_thunderbolt`
- `sharp-beak`: ✅ covered by `backend/test/test_items_powerups.py::test_sharp_beak_thundurus_fly`
- `black-belt`: ✅ covered by `backend/test/test_items_powerups.py::test_black_belt_urshifu_close_combat`
- `mystic-water`: ✅ covered by `backend/test/test_items_powerups.py::test_mystic_water_kyogre_water_spout_rain_double`
- `miracle-seed`: ✅ covered by `backend/test/test_items_powerups.py::test_miracle_seed_venusaur_solar_beam`
- `never-melt-ice`: ✅ covered by `backend/test/test_items_powerups.py::test_never_melt_ice_calyrex_glacial_lance_double`
- `poison-barb`: ✅ covered by `backend/test/test_items_powerups.py::test_poison_barb_sneasler_dire_claw`
- `hard-stone`: ✅ covered by `backend/test/test_items_powerups.py::test_hard_stone_tyranitar_rock_tomb_sandstorm`
- `soft-sand`: ✅ covered by `backend/test/test_items_powerups.py::test_soft_sand_hippowdon_earthquake_double_sandstorm`

**Items present in `items.py` but not currently covered by tests**

The list below was taken from `backend/items/items.py`. These items have behaviour that can affect damage (type boosts, power modifiers, final multipliers, stat multipliers, one-use gems, etc.) but currently lack explicit unit tests in `backend/test`.

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
- `loaded-dice` # Loaded Dice causes multi-strike moves used by the holder to always hit at least four times, if possible. To add in front
- `iron-ball`
- `macho-brace`
- `air-balloon`
- `booster-energy`
- `hearthflame-mask` # only ogerpon fire can have that and he's forced to have that
- `wellspring-mask` # only ogerpon water can have that and he's forced to have that
- `cornerstone-mask` # only ogerpon rock can have that and he's forced to have that
- `rusted-shield` # only crowned zamazenta in its other form can have that and he's forced to have that
- `rusted-sword` # only crowned zacian in its other form can have that and he's forced to have that
- `mega-gems` # all megas should have that to make sure they have no item
- `booster-energy`# activate the ability of a paradox if he doesn't have its ability activated already
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
