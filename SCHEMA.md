# Data shape

*Generated 2026-09-15T13:14:32Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **1,382,774 observations** across 300 partition(s), in **20 series**
  - `ansm.shortages.fr` — 1,830 rows, **291 entities**
  - `fda.citations.drugs` — 2,614 rows, **206 entities**
  - `fda.citations.history` — 123,285 rows, **4848 entities**
  - `fda.complianceactions.drugs` — 17,538 rows, **2710 entities**
  - `fda.decrs.excluded` — 273 rows, **21 entities**
  - `fda.decrs.registrations` — 275,223 rows, **10085 entities**
  - `fda.devices.shortages` — 2,910 rows, **138 entities**
  - `fda.drugsfda.cohort-status` — 5,980 rows, **303 entities**
  - `fda.importalert.66-40` — 13,477 rows, **451 entities**
  - `fda.importalert.66-41` — 37,660 rows, **1794 entities**
  - `fda.importrefusals.recent` — 27,453 rows, **1790 entities**
  - `fda.inspections.drugs` — 60,375 rows, **7537 entities**
  - `fda.inspections.history` — 213,273 rows, **15729 entities**
  - `fda.outsourcing.facilities` — 2,126 rows, **97 entities**
  - `fda.productcodes.reference` — 6,004 rows, **375 entities**
  - `fda.recalls.cder` — 13,998 rows, **562 entities**
  - `fda.refusals.backfill` — 392,012 rows, **31253 entities**
  - `fda.rems.approved` — 715 rows, **72 entities**
  - `fda.shortages.current` — 165,360 rows, **1919 entities**
  - `tga.shortages.au` — 20,668 rows, **985 entities**
- Raw: 1079 file(s), 27,508,532 bytes on disk, 5 capture date(s), 2026-09-02 → 2026-09-10

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `ansm.shortages.fr` | weekly | 1 | git | none | ANSM public information; see https://ansm.sante.fr/page/docu |
| `fda.citations.drugs` | weekly | 1 | git | parties_only | US federal work, no copyright in the US |
| `fda.citations.history` | quarterly | 18 | git | parties_only | US federal work, no copyright in the US |
| `fda.complianceactions.drugs` | weekly | 1 | git | parties_only | US federal work, no copyright in the US |
| `fda.decrs.excluded` | monthly | 1 | object | present | US federal government work, public domain |
| `fda.decrs.registrations` | monthly | 1 | object | present | US federal government work, public domain |
| `fda.devices.shortages` | weekly | 1 | git | none | US federal work, no copyright in the US |
| `fda.drugsfda.cohort-status` | monthly | 304 | git | none | US federal work, no copyright in the US; https://open.fda.go |
| `fda.importalert.66-40` | weekly | 1 | git | none | US federal work, no copyright in the US |
| `fda.importalert.66-41` | monthly | 1 | git | none | US federal work, no copyright in the US |
| `fda.importrefusals.recent` | weekly | 1 | git | parties_only | US federal work, no copyright in the US |
| `fda.inspections.drugs` | weekly | 1 | git | parties_only | US federal work, no copyright in the US |
| `fda.inspections.history` | quarterly | 14 | git | parties_only | US federal work, no copyright in the US |
| `fda.nsde.marketing` | monthly | 1 | git | none | US federal work, no copyright in the US; https://open.fda.go |
| `fda.outsourcing.facilities` | monthly | 1 | object | present | US federal work, no copyright in the US |
| `fda.productcodes.reference` | monthly | 4 | git | none | US federal work, no copyright in the US |
| `fda.recalls.cder` | weekly | 5 | git | parties_only | US federal work, no copyright in the US |
| `fda.refusals.backfill` | quarterly | 31 | git | parties_only | US federal work, no copyright in the US |
| `fda.rems.approved` | monthly | 1 | git | none | US federal work, no copyright in the US |
| `fda.shortages.current` | weekly | 2 | git | none | US federal work, no copyright in the US; https://open.fda.go |
| `tga.shortages.au` | weekly | 1 | git | none | Australian Government (TGA); site content CC BY 4.0 unless m |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **ansm.shortages.fr** `feed:ansm_shortages`, `med:acadione-250-mg-comprim-drag-ifi-tiopronine`, `med:acide-ac-tylsalicylique-75-mg-comprim-gastro-r-sistant-acide-ac-`; **fda.citations.drugs** `feed:citations`, `firm:1000110034`, `firm:1000110912`; **fda.citations.history** `feed:citations`, `firm:1000034649`, `firm:1000036852`; **fda.complianceactions.drugs** `feed:compliance_actions`, `firm:1000049118`, `firm:1000071237`; **fda.decrs.excluded** `duns:074300557`, `duns:117450324`, `duns:118240178`; **fda.decrs.registrations** `duns:007910702`, `duns:013147097`, `duns:017329950`; **fda.devices.shortages** `device:BYS`, `device:DTZ`, `device:DXT`; **fda.drugsfda.cohort-status** `molecule:acetaminophen`, `molecule:acetazolamide`, `molecule:acyclovir-sodium`; **fda.importalert.66-40** `alert:total`, `country:armenia/firm:babikian-healthcare-products`, `country:aruba/firm:aruba-aloe-balm-n-v`; **fda.importalert.66-41** `alert:total`, `country:aa-ghana/firm:henacent-limited`, `country:ab-canada/firm:canada-prescriptions-plus`; **fda.importrefusals.recent** `feed:import_refusals`, `firm:1000110364`, `firm:1000113495`; **fda.inspections.drugs** `feed:inspections`, `firm:1000021877`, `firm:1000022237`; **fda.inspections.history** `feed:inspections`, `firm:1000021877`, `firm:1000022036`; **fda.outsourcing.facilities** `facility:503b-outsourcing-facility-one-llc-west-palm-beach-fl`, `facility:ajenat-pharmaceuticals-llc-largo-fl`, `facility:anazaohealth-corporation-las-vegas-nv`; **fda.productcodes.reference** `pcb:indid-classid-classdesc`, `pcb:indid-classid-classdesc/code:00`, `pcb:indid-classid-classdesc/code:02`; **fda.recalls.cder** `feed:recalls`, `firm:1000036852`, `firm:1000076625`; **fda.refusals.backfill** `feed:import_refusals`, `firm:1000028832`, `firm:1000036852`; **fda.rems.approved** `feed:fda_rems`, `rems:adasuve-loxapine-aerosol-powder-nda-022549`, `rems:alvimopan-shared-system-rems-shared-system-rems`; **fda.shortages.current** `drug:acetaminophen-oxycodone-hydrochloride-tablet/category:analgesia-addiction`, `drug:acetaminophen-oxycodone-hydrochloride-tablet/ndc:60951060270`, `drug:acetaminophen-oxycodone-hydrochloride-tablet/ndc:60951060285`; **tga.shortages.au** `artg:100517`, `artg:100703`, `artg:101685`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `action_injunction` | fda.complianceactions.drugs | 48 | 48 | bool | count | 1 | `1` |
| `action_none` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `41` … `41` |
| `action_open` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `36` … `36` |
| `action_other` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `5` … `5` |
| `action_regulatory_meeting` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `6` … `6` |
| `action_seizure` | fda.complianceactions.drugs | 24 | 24 | bool | count | 1 | `1` |
| `action_status` | fda.outsourcing.facilities | 192 | 96 | text | text | 22 | `FMD-145 Letter Issued 6/`, `FMD-145 Letter Issued 6/`, `FMD-145 Letter Issued 6/` |
| `action_taken` | fda.complianceactions.drugs | 2,922 | 2709 | number | yyyymmdd | 1730 | `20081001` … `20260904` |
| `action_untitled_letter` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `3` … `3` |
| `action_warning_letter` | fda.complianceactions.drugs, fda.outsourcing.facilities | 2,852 | 2677 | number | count | 2 | `1` … `5` |
| `active_ingredient` | tga.shortages.au | 1,968 | 984 | text | text | 405 | `Adalimumab`, `Albumin`, `American house dust mite` |
| `active_ingredients` | fda.rems.approved | 71 | 71 | text | text | 70 | `Copper`, `Crovalimab-akkz`, `Iberdomide` |
| `additional_info` | fda.devices.shortages | 18 | 6 | text | text | 5 | `Angiographic control syr`, `Neurosurgical patties, s`, `Oxygenator devices inten` |
| `address` | fda.decrs.excluded, fda.decrs.registrations | 31,345 | 10105 | text | text | 10421 | `# 5-5-35/169/1, Plot No-`, `#1 Haiyan Road, Xintai, `, `#1 Heilman Avenue, Willo` |
| `approved` | fda.rems.approved | 71 | 71 | text | state | 1 | `yes` |
| `approved_at` | fda.rems.approved | 71 | 71 | date | date | 68 | `2009-12-11` … `2026-08-13` |
| `atc_level1` | tga.shortages.au | 1,964 | 982 | text | text | 14 | `Alimentary tract and met`, `Antineoplastic and immun`, `Antiparasitic products, ` |
| `availability` | fda.devices.shortages, fda.shortages.current, tga.shortages.au | 17,148 | 2158 | text | text | 11 | `0`, `1`, `2` |
| `category` | fda.devices.shortages | 414 | 137 | text | text | 27 | `ANESTHESIOLOGY - Divisio`, `Anesthesiology - Anesthe`, `Anesthesiology – Anesthe` |
| `cfr` | fda.citations.drugs, fda.citations.history | 40,481 | 4919 | text |  | 370 | `21 CFR 211.100(a)`, `21 CFR 211.100(b)`, `21 CFR 211.101(a)` |
| `cfr_part` | fda.citations.drugs, fda.citations.history | 8,943 | 4919 | number | part | 11 | `211` … `760` |
| `citation` | fda.citations.drugs, fda.citations.history | 8,583 | 4919 | bool | count | 1 | `1` |
| `citation_topic` | fda.citations.drugs, fda.citations.history | 41,775 | 4919 | text |  | 654 | `>50% of members not at R`, `Absence of Written Proce`, `Accelerated stability st` |
| `classification` | fda.inspections.drugs, fda.inspections.history | 39,240 | 18907 | number | ordinal | 3 | `0` … `2` |
| `compliance_action` | fda.complianceactions.drugs | 2,922 | 2709 | bool | count | 1 | `1` |
| `contact_person_fp` | fda.outsourcing.facilities | 192 | 96 | text | id | 88 | `0b200f97d93a`, `0cd59a5ef5a7`, `0cdef494661f` |
| `contact_phone_fp` | fda.outsourcing.facilities | 192 | 96 | text | id | 90 | `00000402cb44`, `0203a7e2a724`, `02a6497df176` |
| `date_posted` | fda.devices.shortages | 393 | 131 | text | text | 2 | `3/13/2026`, `6/16/2026` |
| `date_raw` | fda.devices.shortages | 18 | 6 | text | text | 5 | `2023/09/11 Initial 2025/`, `2024/11/15 Initial 2025/`, `2026/03/13 Initial` |
| `deleted_date` | tga.shortages.au | 556 | 278 | date | date | 131 | `2024-01-31` … `2027-12-31` |
| `devices_discontinued` | fda.devices.shortages | 3 | 1 | number | count | 1 | `145` … `145` |
| `devices_in_shortage` | fda.devices.shortages | 3 | 1 | number | count | 1 | `6` … `6` |
| `domain` | ansm.shortages.fr | 290 | 290 | text | text | 49 | `Addictologie, Neurologie`, `Allergologie`, `Allergologie, Infectiolo` |
| `dose_form` | tga.shortages.au | 1,968 | 984 | text | text | 52 | `Capsule`, `Capsule, enteric`, `Capsule, hard` |
| `duns` | fda.decrs.excluded, fda.decrs.registrations | 31,423 | 10105 | number | text | 10478 | `000000000` … `989968644` |
| `duration_days` | tga.shortages.au | 408 | 204 | number | count | 113 | `0` … `6538` |
| `exclusion_flag` | fda.decrs.excluded, fda.decrs.registrations | 30,305 | 10105 | text | text | 2 | `E`, `N` |
| `facilities_registered` | fda.outsourcing.facilities | 2 | 1 | number | count | 1 | `96` … `96` |
| `facility_name` | fda.outsourcing.facilities | 192 | 96 | text | text | 96 | `503B Outsourcing Facilit`, `Ajenat Pharmaceuticals, `, `AnazaoHealth Corporation` |
| `feed_records_total` | fda.citations.drugs, fda.citations.history, fda.complianceactions.drugs, fda.importrefusals.recent, fda.inspections.drugs, fda.inspections.history, fda.recalls.cder, fda.refusals.backfill, fda.shortages.current | 195 | 6 | number | count | 80 | `408` … `532484` |
| `fei` | fda.decrs.excluded, fda.decrs.registrations | 29,663 | 9890 | number | text | 9890 | `0000000360` … `8129176060` |
| `firm_key` | fda.citations.drugs, fda.citations.history, fda.complianceactions.drugs, fda.importrefusals.recent, fda.inspections.drugs, fda.inspections.history, fda.recalls.cder, fda.refusals.backfill | 112,268 | 50313 | text |  | 42324 | `0944 AMP AMPELOKIPI SPEE`, `1 A`, `1 GLOBE HEALTH INSTITUTE` |
| `firm_name` | fda.decrs.excluded, fda.decrs.registrations | 30,761 | 10105 | text | text | 7795 | `1201258 Ontario Inc.`, `1256 Cattle Company`, `1Link LLC dba USA Diagno` |
| `firms_listed` | fda.importalert.66-40, fda.importalert.66-41 | 17 | 1 | number | count | 3 | `448` … `1793` |
| `first_listed` | fda.importalert.66-40, fda.importalert.66-41, fda.shortages.current | 37,871 | 3810 | number | yyyymmdd | 1311 | `20090910` … `20260909` |
| `flag_communication_plan` | fda.rems.approved | 71 | 71 | text | state | 2 | `no`, `yes` |
| `flag_etasu` | fda.rems.approved | 71 | 71 | text | state | 2 | `no`, `yes` |
| `flag_implementation_system` | fda.rems.approved | 71 | 71 | text | state | 2 | `no`, `yes` |
| `flag_medication_guide` | fda.rems.approved | 71 | 71 | text | state | 2 | `no`, `yes` |
| `form_483_issued` | fda.outsourcing.facilities | 192 | 96 | text | text | 4 | `483`, `N/A`, `No` |
| `import_refusal` | fda.importrefusals.recent, fda.refusals.backfill | 59,778 | 32057 | bool | count | 1 | `1` |
| `in_category` | fda.shortages.current | 6,475 | 322 | bool | bool | 1 | `1` |
| `initial_registration` | fda.outsourcing.facilities | 192 | 96 | text | text | 94 | `1/11/2023`, `1/12/2015`, `1/14/2015` |
| `inspected` | fda.inspections.drugs, fda.inspections.history | 39,054 | 18907 | bool | count | 1 | `1` |
| `inspection_end` | fda.inspections.drugs, fda.inspections.history | 39,054 | 18907 | number | yyyymmdd | 4519 | `20081001` … `20260819` |
| `intends_sterile_from_bulk` | fda.outsourcing.facilities | 192 | 96 | text | text | 2 | `No`, `Yes` |
| `is_class_i` | fda.recalls.cder | 2,003 | 559 | bool | bool | 2 | `0`, `1` |
| `is_drug_or_biologic` | fda.importrefusals.recent, fda.refusals.backfill | 59,830 | 32057 | bool | bool | 2 | `0`, `1` |
| `is_foreign` | fda.complianceactions.drugs, fda.importrefusals.recent, fda.inspections.drugs, fda.inspections.history, fda.refusals.backfill | 101,754 | 49719 | bool | bool | 2 | `0`, `1` |
| `is_gmp` | fda.citations.drugs, fda.citations.history | 8,914 | 4919 | bool | bool | 2 | `0`, `1` |
| `is_human_drug` | fda.importrefusals.recent, fda.refusals.backfill | 60,750 | 32057 | bool | bool | 2 | `0`, `1` |
| `is_injectable` | fda.shortages.current | 20,831 | 1596 | bool | bool | 2 | `0`, `1` |
| `is_oai` | fda.inspections.drugs, fda.inspections.history | 39,095 | 18907 | bool | bool | 2 | `0`, `1` |
| `label` | fda.citations.drugs, fda.citations.history, fda.complianceactions.drugs, fda.importrefusals.recent, fda.inspections.drugs, fda.inspections.history, fda.productcodes.reference, fda.recalls.cder, fda.refusals.backfill | 116,830 | 50712 | text |  | 47443 | `"Agropharm" Ltd`, `"Eliava Biopreparations"`, `"Orhei-Vit" JSC` |
| `last_inspection` | fda.outsourcing.facilities | 192 | 96 | text | text | 49 | `1/14/2026`, `1/28/2026`, `10/30/2025` |
| `last_update` | fda.shortages.current | 20,831 | 1596 | number | yyyymmdd | 141 | `20230428` … `20260909` |
| `last_updated` | fda.rems.approved, tga.shortages.au | 2,039 | 1055 | date | date | 376 | `2008-10-01` … `2026-09-10` |
| `listed` | fda.devices.shortages, fda.importalert.66-40, fda.importalert.66-41, fda.productcodes.reference, fda.shortages.current | 39,766 | 4318 | text | state | 3 | `1`, `device`, `discontinued` |
| `made_by` | fda.shortages.current | 18,685 | 1431 | text |  | 128 | `ABBVIE`, `ACCORD HEALTHCARE`, `ACTAVIS` |
| `manufacturer` | fda.devices.shortages | 396 | 131 | text | text | 29 | `AirLife`, `Angelini Pharma Inc.`, `Baxter Healthcare Corpor` |
| `most_recent_registration` | fda.outsourcing.facilities | 192 | 96 | text | text | 52 | `1/1/2026`, `1/10/2026`, `1/15/2026` |
| `operations` | fda.decrs.registrations | 30,694 | 10085 | text | text | 181 | `ANALYSIS`, `ANALYSIS; API MANUFACTUR`, `ANALYSIS; API MANUFACTUR` |
| `patient_impact` | tga.shortages.au | 4 | 2 | text | text | 1 | `SEVERE` |
| `product` | ansm.shortages.fr | 291 | 290 | text | text | 291 | `Acadione 250 mg, comprim`, `Acide acétylsalicylique `, `Actosolv 100 000 UI et 6` |
| `product_code` | fda.devices.shortages | 411 | 137 | text | text | 59 | `BSR (STYLET, TRACHEAL TU`, `BTR (TUBE, TRACHEAL (W/W`, `BYD (CONDENSER, HEAT AND` |
| `product_count` | fda.rems.approved | 71 | 71 | number | count | 13 | `1` … `36900` |
| `product_entries` | fda.importalert.66-40, fda.importalert.66-41 | 17,040 | 2214 | number | count | 66 | `2` … `253` |
| `products_discontinued` | fda.drugsfda.cohort-status | 1,323 | 278 | number | count | 69 | `1` … `401` |
| `products_ever` | fda.drugsfda.cohort-status | 1,442 | 303 | number | count | 98 | `0` … `536` |
| `products_marketed` | fda.drugsfda.cohort-status | 1,442 | 303 | number | count | 62 | `0` … `147` |
| `products_otc` | fda.drugsfda.cohort-status | 66 | 14 | number | count | 8 | `1` … `24` |
| `products_prescription` | fda.drugsfda.cohort-status | 1,391 | 292 | number | count | 59 | `1` … `147` |
| `products_tentative` | fda.drugsfda.cohort-status | 316 | 67 | number | count | 8 | `1` … `15` |
| `reason` | fda.devices.shortages | 429 | 137 | text | text | 24 | `Device on backorder (i.e`, `Discontinuance of the ma`, `Discontinuance of the ma` |
| `recall` | fda.recalls.cder | 1,989 | 561 | bool | count | 1 | `1` |
| `recall_class` | fda.recalls.cder | 2,016 | 559 | number | class | 3 | `1` … `3` |
| `recall_conducted` | fda.outsourcing.facilities | 192 | 96 | text | text | 2 | `N/A`, `No` |
| `recall_initiated` | fda.recalls.cder | 1,989 | 561 | number | yyyymmdd | 830 | `20220104` … `20260903` |
| `recall_terminated` | fda.recalls.cder | 1,993 | 561 | bool | bool | 2 | `0`, `1` |
| `records_anticipated` | tga.shortages.au | 4 | 1 | number | count | 1 | `93` … `93` |
| `records_current` | tga.shortages.au | 4 | 1 | number | count | 1 | `409` … `409` |
| `records_discontinued` | ansm.shortages.fr, tga.shortages.au | 5 | 2 | number | count | 2 | `16` … `278` |
| `records_resolved` | ansm.shortages.fr, tga.shortages.au | 5 | 2 | number | count | 2 | `89` … `204` |
| `records_rupture` | ansm.shortages.fr | 1 | 1 | number | count | 1 | `47` … `47` |
| `records_tension` | ansm.shortages.fr | 1 | 1 | number | count | 1 | `139` … `139` |
| `records_total` | ansm.shortages.fr, tga.shortages.au | 5 | 2 | number | count | 2 | `291` … `984` |
| `refused_at` | fda.importrefusals.recent, fda.refusals.backfill | 59,778 | 32057 | number | yyyymmdd | 6328 | `20011001` … `20260903` |
| `registered` | fda.outsourcing.facilities | 192 | 96 | text | state | 1 | `yes` |
| `registrant_duns` | fda.decrs.registrations | 30,578 | 10085 | number | text | 7052 | `000000000` … `989968644` |
| `registrant_name` | fda.decrs.registrations | 30,485 | 10085 | text | text | 6789 | `1201258 Ontario Inc. O/A`, `1256 Cattle Company`, `1Link LLC dba USA Diagno` |
| `registration_expires` | fda.decrs.registrations | 30,242 | 10085 | text | text | 1 | `12/31/2026` |
| `rems_approved_total` | fda.rems.approved | 1 | 1 | number | count | 1 | `71` … `71` |
| `rems_name` | fda.rems.approved | 71 | 71 | text | text | 71 | `Adasuve ( loxapine ), ae`, `Alvimopan Shared System `, `Aqvesme ( mitapivat ), t` |
| `resolved_at` | ansm.shortages.fr | 89 | 89 | date | date | 64 | `2025-07-25` … `2026-09-08` |
| `resolved_with_duration` | tga.shortages.au | 4 | 1 | number | count | 1 | `204` … `204` |
| `rows_listed` | fda.productcodes.reference | 16 | 4 | number | count | 4 | `80` … `1159` |
| `shortage_end` | tga.shortages.au | 1,968 | 984 | text | date | 157 | `2022-08-23`, `2025-12-05`, `2025-12-12` |
| `shortage_impact` | tga.shortages.au | 1,968 | 984 | text | text | 3 | `Critical`, `Low`, `Medium` |
| `shortage_start` | tga.shortages.au | 1,968 | 984 | date | date | 416 | `2003-01-01` … `2028-01-01` |
| `sold_by` | fda.shortages.current | 20,857 | 1596 | text |  | 131 | `ABBVIE`, `ACCORD HEALTHCARE`, `ACTAVIS` |
| `status` | ansm.shortages.fr, tga.shortages.au | 2,258 | 1274 | text | state | 6 | `anticipated`, `current`, `discontinued` |
| `status_code` | fda.shortages.current | 20,831 | 1596 | number | code | 3 | `0` … `2` |
| `status_fr` | ansm.shortages.fr | 290 | 290 | text | text | 4 | `Arrêt de commercialisati`, `Remise à disposition`, `Rupture de stock` |
| `substance` | ansm.shortages.fr | 285 | 285 | text | text | 227 | `acide acétylsalicylique`, `acide ascorbique, ascorb`, `acide glutamique, calciu` |
| `total_flag_communication_plan` | fda.rems.approved | 1 | 1 | number | count | 1 | `17` … `17` |
| `total_flag_etasu` | fda.rems.approved | 1 | 1 | number | count | 1 | `59` … `59` |
| `total_flag_implementation_system` | fda.rems.approved | 1 | 1 | number | count | 1 | `58` … `58` |
| `total_flag_medication_guide` | fda.rems.approved | 1 | 1 | number | count | 1 | `9` … `9` |
| `trade_name` | fda.devices.shortages, tga.shortages.au | 2,364 | 1115 | text | text | 1115 | `(SKU# 39575NA)`, `(SKU# 7198D, 7197D, 7196`, `(SKU# 8881225224)` |
| `updated_at` | ansm.shortages.fr | 290 | 290 | date | date | 165 | `2021-05-19` … `2026-09-09` |

## Partitions

- `derived/observations/2001-10.csv.gz`
- `derived/observations/2001-11.csv.gz`
- `derived/observations/2001-12.csv.gz`
- `derived/observations/2002-01.csv.gz`
- `derived/observations/2002-02.csv.gz`
- `derived/observations/2002-03.csv.gz`
- `derived/observations/2002-04.csv.gz`
- `derived/observations/2002-05.csv.gz`
- `derived/observations/2002-06.csv.gz`
- `derived/observations/2002-07.csv.gz`
- `derived/observations/2002-08.csv.gz`
- `derived/observations/2002-09.csv.gz`
- `derived/observations/2002-10.csv.gz`
- `derived/observations/2002-11.csv.gz`
- `derived/observations/2002-12.csv.gz`
- `derived/observations/2003-01.csv.gz`
- `derived/observations/2003-02.csv.gz`
- `derived/observations/2003-03.csv.gz`
- `derived/observations/2003-04.csv.gz`
- `derived/observations/2003-05.csv.gz`
- `derived/observations/2003-06.csv.gz`
- `derived/observations/2003-07.csv.gz`
- `derived/observations/2003-08.csv.gz`
- `derived/observations/2003-09.csv.gz`
- `derived/observations/2003-10.csv.gz`
- `derived/observations/2003-11.csv.gz`
- `derived/observations/2003-12.csv.gz`
- `derived/observations/2004-01.csv.gz`
- `derived/observations/2004-02.csv.gz`
- `derived/observations/2004-03.csv.gz`
- `derived/observations/2004-04.csv.gz`
- `derived/observations/2004-05.csv.gz`
- `derived/observations/2004-06.csv.gz`
- `derived/observations/2004-07.csv.gz`
- `derived/observations/2004-08.csv.gz`
- `derived/observations/2004-09.csv.gz`
- `derived/observations/2004-10.csv.gz`
- `derived/observations/2004-11.csv.gz`
- `derived/observations/2004-12.csv.gz`
- `derived/observations/2005-01.csv.gz`
- `derived/observations/2005-02.csv.gz`
- `derived/observations/2005-03.csv.gz`
- `derived/observations/2005-04.csv.gz`
- `derived/observations/2005-05.csv.gz`
- `derived/observations/2005-06.csv.gz`
- `derived/observations/2005-07.csv.gz`
- `derived/observations/2005-08.csv.gz`
- `derived/observations/2005-09.csv.gz`
- `derived/observations/2005-10.csv.gz`
- `derived/observations/2005-11.csv.gz`
- `derived/observations/2005-12.csv.gz`
- `derived/observations/2006-01.csv.gz`
- `derived/observations/2006-02.csv.gz`
- `derived/observations/2006-03.csv.gz`
- `derived/observations/2006-04.csv.gz`
- `derived/observations/2006-05.csv.gz`
- `derived/observations/2006-06.csv.gz`
- `derived/observations/2006-07.csv.gz`
- `derived/observations/2006-08.csv.gz`
- `derived/observations/2006-09.csv.gz`
- `derived/observations/2006-10.csv.gz`
- `derived/observations/2006-11.csv.gz`
- `derived/observations/2006-12.csv.gz`
- `derived/observations/2007-01.csv.gz`
- `derived/observations/2007-02.csv.gz`
- `derived/observations/2007-03.csv.gz`
- `derived/observations/2007-04.csv.gz`
- `derived/observations/2007-05.csv.gz`
- `derived/observations/2007-06.csv.gz`
- `derived/observations/2007-07.csv.gz`
- `derived/observations/2007-08.csv.gz`
- `derived/observations/2007-09.csv.gz`
- `derived/observations/2007-10.csv.gz`
- `derived/observations/2007-11.csv.gz`
- `derived/observations/2007-12.csv.gz`
- `derived/observations/2008-01.csv.gz`
- `derived/observations/2008-02.csv.gz`
- `derived/observations/2008-03.csv.gz`
- `derived/observations/2008-04.csv.gz`
- `derived/observations/2008-05.csv.gz`
- `derived/observations/2008-06.csv.gz`
- `derived/observations/2008-07.csv.gz`
- `derived/observations/2008-08.csv.gz`
- `derived/observations/2008-09.csv.gz`
- `derived/observations/2008-10.csv.gz`
- `derived/observations/2008-11.csv.gz`
- `derived/observations/2008-12.csv.gz`
- `derived/observations/2009-01.csv.gz`
- `derived/observations/2009-02.csv.gz`
- `derived/observations/2009-03.csv.gz`
- `derived/observations/2009-04.csv.gz`
- `derived/observations/2009-05.csv.gz`
- `derived/observations/2009-06.csv.gz`
- `derived/observations/2009-07.csv.gz`
- `derived/observations/2009-08.csv.gz`
- `derived/observations/2009-09.csv.gz`
- `derived/observations/2009-10.csv.gz`
- `derived/observations/2009-11.csv.gz`
- `derived/observations/2009-12.csv.gz`
- `derived/observations/2010-01.csv.gz`
- `derived/observations/2010-02.csv.gz`
- `derived/observations/2010-03.csv.gz`
- `derived/observations/2010-04.csv.gz`
- `derived/observations/2010-05.csv.gz`
- `derived/observations/2010-06.csv.gz`
- `derived/observations/2010-07.csv.gz`
- `derived/observations/2010-08.csv.gz`
- `derived/observations/2010-09.csv.gz`
- `derived/observations/2010-10.csv.gz`
- `derived/observations/2010-11.csv.gz`
- `derived/observations/2010-12.csv.gz`
- `derived/observations/2011-01.csv.gz`
- `derived/observations/2011-02.csv.gz`
- `derived/observations/2011-03.csv.gz`
- `derived/observations/2011-04.csv.gz`
- `derived/observations/2011-05.csv.gz`
- `derived/observations/2011-06.csv.gz`
- `derived/observations/2011-07.csv.gz`
- `derived/observations/2011-08.csv.gz`
- `derived/observations/2011-09.csv.gz`
- `derived/observations/2011-10.csv.gz`
- `derived/observations/2011-11.csv.gz`
- `derived/observations/2011-12.csv.gz`
- `derived/observations/2012-01.csv.gz`
- `derived/observations/2012-02.csv.gz`
- `derived/observations/2012-03.csv.gz`
- `derived/observations/2012-04.csv.gz`
- `derived/observations/2012-05.csv.gz`
- `derived/observations/2012-06.csv.gz`
- `derived/observations/2012-07.csv.gz`
- `derived/observations/2012-08.csv.gz`
- `derived/observations/2012-09.csv.gz`
- `derived/observations/2012-10.csv.gz`
- `derived/observations/2012-11.csv.gz`
- `derived/observations/2012-12.csv.gz`
- `derived/observations/2013-01.csv.gz`
- `derived/observations/2013-02.csv.gz`
- `derived/observations/2013-03.csv.gz`
- `derived/observations/2013-04.csv.gz`
- `derived/observations/2013-05.csv.gz`
- `derived/observations/2013-06.csv.gz`
- `derived/observations/2013-07.csv.gz`
- `derived/observations/2013-08.csv.gz`
- `derived/observations/2013-09.csv.gz`
- `derived/observations/2013-10.csv.gz`
- `derived/observations/2013-11.csv.gz`
- `derived/observations/2013-12.csv.gz`
- `derived/observations/2014-01.csv.gz`
- `derived/observations/2014-02.csv.gz`
- `derived/observations/2014-03.csv.gz`
- `derived/observations/2014-04.csv.gz`
- `derived/observations/2014-05.csv.gz`
- `derived/observations/2014-06.csv.gz`
- `derived/observations/2014-07.csv.gz`
- `derived/observations/2014-08.csv.gz`
- `derived/observations/2014-09.csv.gz`
- `derived/observations/2014-10.csv.gz`
- `derived/observations/2014-11.csv.gz`
- `derived/observations/2014-12.csv.gz`
- `derived/observations/2015-01.csv.gz`
- `derived/observations/2015-02.csv.gz`
- `derived/observations/2015-03.csv.gz`
- `derived/observations/2015-04.csv.gz`
- `derived/observations/2015-05.csv.gz`
- `derived/observations/2015-06.csv.gz`
- `derived/observations/2015-07.csv.gz`
- `derived/observations/2015-08.csv.gz`
- `derived/observations/2015-09.csv.gz`
- `derived/observations/2015-10.csv.gz`
- `derived/observations/2015-11.csv.gz`
- `derived/observations/2015-12.csv.gz`
- `derived/observations/2016-01.csv.gz`
- `derived/observations/2016-02.csv.gz`
- `derived/observations/2016-03.csv.gz`
- `derived/observations/2016-04.csv.gz`
- `derived/observations/2016-05.csv.gz`
- `derived/observations/2016-06.csv.gz`
- `derived/observations/2016-07.csv.gz`
- `derived/observations/2016-08.csv.gz`
- `derived/observations/2016-09.csv.gz`
- `derived/observations/2016-10.csv.gz`
- `derived/observations/2016-11.csv.gz`
- `derived/observations/2016-12.csv.gz`
- `derived/observations/2017-01.csv.gz`
- `derived/observations/2017-02.csv.gz`
- `derived/observations/2017-03.csv.gz`
- `derived/observations/2017-04.csv.gz`
- `derived/observations/2017-05.csv.gz`
- `derived/observations/2017-06.csv.gz`
- `derived/observations/2017-07.csv.gz`
- `derived/observations/2017-08.csv.gz`
- `derived/observations/2017-09.csv.gz`
- `derived/observations/2017-10.csv.gz`
- `derived/observations/2017-11.csv.gz`
- `derived/observations/2017-12.csv.gz`
- `derived/observations/2018-01.csv.gz`
- `derived/observations/2018-02.csv.gz`
- `derived/observations/2018-03.csv.gz`
- `derived/observations/2018-04.csv.gz`
- `derived/observations/2018-05.csv.gz`
- `derived/observations/2018-06.csv.gz`
- `derived/observations/2018-07.csv.gz`
- `derived/observations/2018-08.csv.gz`
- `derived/observations/2018-09.csv.gz`
- `derived/observations/2018-10.csv.gz`
- `derived/observations/2018-11.csv.gz`
- `derived/observations/2018-12.csv.gz`
- `derived/observations/2019-01.csv.gz`
- `derived/observations/2019-02.csv.gz`
- `derived/observations/2019-03.csv.gz`
- `derived/observations/2019-04.csv.gz`
- `derived/observations/2019-05.csv.gz`
- `derived/observations/2019-06.csv.gz`
- `derived/observations/2019-07.csv.gz`
- `derived/observations/2019-08.csv.gz`
- `derived/observations/2019-09.csv.gz`
- `derived/observations/2019-10.csv.gz`
- `derived/observations/2019-11.csv.gz`
- `derived/observations/2019-12.csv.gz`
- `derived/observations/2020-01.csv.gz`
- `derived/observations/2020-02.csv.gz`
- `derived/observations/2020-03.csv.gz`
- `derived/observations/2020-04.csv.gz`
- `derived/observations/2020-05.csv.gz`
- `derived/observations/2020-06.csv.gz`
- `derived/observations/2020-07.csv.gz`
- `derived/observations/2020-08.csv.gz`
- `derived/observations/2020-09.csv.gz`
- `derived/observations/2020-10.csv.gz`
- `derived/observations/2020-11.csv.gz`
- `derived/observations/2020-12.csv.gz`
- `derived/observations/2021-01.csv.gz`
- `derived/observations/2021-02.csv.gz`
- `derived/observations/2021-03.csv.gz`
- `derived/observations/2021-04.csv.gz`
- `derived/observations/2021-05.csv.gz`
- `derived/observations/2021-06.csv.gz`
- `derived/observations/2021-07.csv.gz`
- `derived/observations/2021-08.csv.gz`
- `derived/observations/2021-09.csv.gz`
- `derived/observations/2021-10.csv.gz`
- `derived/observations/2021-11.csv.gz`
- `derived/observations/2021-12.csv.gz`
- `derived/observations/2022-01.csv.gz`
- `derived/observations/2022-02.csv.gz`
- `derived/observations/2022-03.csv.gz`
- `derived/observations/2022-04.csv.gz`
- `derived/observations/2022-05.csv.gz`
- `derived/observations/2022-06.csv.gz`
- `derived/observations/2022-07.csv.gz`
- `derived/observations/2022-08.csv.gz`
- `derived/observations/2022-09.csv.gz`
- `derived/observations/2022-10.csv.gz`
- `derived/observations/2022-11.csv.gz`
- `derived/observations/2022-12.csv.gz`
- `derived/observations/2023-01.csv.gz`
- `derived/observations/2023-02.csv.gz`
- `derived/observations/2023-03.csv.gz`
- `derived/observations/2023-04.csv.gz`
- `derived/observations/2023-05.csv.gz`
- `derived/observations/2023-06.csv.gz`
- `derived/observations/2023-07.csv.gz`
- `derived/observations/2023-08.csv.gz`
- `derived/observations/2023-09.csv.gz`
- `derived/observations/2023-10.csv.gz`
- `derived/observations/2023-11.csv.gz`
- `derived/observations/2023-12.csv.gz`
- `derived/observations/2024-01.csv.gz`
- `derived/observations/2024-02.csv.gz`
- `derived/observations/2024-03.csv.gz`
- `derived/observations/2024-04.csv.gz`
- `derived/observations/2024-05.csv.gz`
- `derived/observations/2024-06.csv.gz`
- `derived/observations/2024-07.csv.gz`
- `derived/observations/2024-08.csv.gz`
- `derived/observations/2024-09.csv.gz`
- `derived/observations/2024-10.csv.gz`
- `derived/observations/2024-11.csv.gz`
- `derived/observations/2024-12.csv.gz`
- `derived/observations/2025-01.csv.gz`
- `derived/observations/2025-02.csv.gz`
- `derived/observations/2025-03.csv.gz`
- `derived/observations/2025-04.csv.gz`
- `derived/observations/2025-05.csv.gz`
- `derived/observations/2025-06.csv.gz`
- `derived/observations/2025-07.csv.gz`
- `derived/observations/2025-08.csv.gz`
- `derived/observations/2025-09.csv.gz`
- `derived/observations/2025-10.csv.gz`
- `derived/observations/2025-11.csv.gz`
- `derived/observations/2025-12.csv.gz`
- `derived/observations/2026-01.csv.gz`
- `derived/observations/2026-02.csv.gz`
- `derived/observations/2026-03.csv.gz`
- `derived/observations/2026-04.csv.gz`
- `derived/observations/2026-05.csv.gz`
- `derived/observations/2026-06.csv.gz`
- `derived/observations/2026-07.csv.gz`
- `derived/observations/2026-08.csv.gz`
- `derived/observations/2026-09.csv.gz`
