#!/usr/bin/env python3
"""Seed research_notes from documented case research. Idempotent (INSERT OR REPLACE)."""
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(__file__).parent / "isds.db"

# enforcement_status values:
#   paid             — Spain actually paid the award
#   enforced         — court(s) entered enforcement judgment; Spain has not paid
#   not_paid         — award for investor; no enforcement judgment obtained yet
#   blocked          — courts refused enforcement, award set aside, or EC state aid decision
#   state_won        — Spain prevailed on merits; no enforcement issue
#   discontinued     — case discontinued before decision
#   pending          — arbitration still pending (no award)

ROWS = [
    # (case_no, enforcement_status, enforcement_detail, context, claim_basis, significance)
    (1318, "paid",
     "Believed settled and paid in the early 2000s. Predates Spain's systematic non-compliance posture. No record of outstanding enforcement proceedings.",
     "Argentine national Emilio Maffezini invested in a chemical products company in Galicia. He alleged Spain's regional development agency SODIGA improperly interfered in his investment, forcing him to make unapproved expenditures and causing significant losses. ICSID Case ARB/97/7.",
     "Fair and equitable treatment and related BIT claims under the Argentina–Spain BIT (1991). Award issued 13 November 2000.",
     "Landmark MFN ruling: the tribunal's broad interpretation of the MFN clause as extending to dispute-settlement provisions became the 'Maffezini doctrine' — the most-cited and contested MFN position in ISDS history."),

    (916, "not_paid",
     "Spain has not paid. US DC Circuit confirmed jurisdiction to enforce ICSID awards (Aug 2024, NextEra precedent). Amsterdam District Court (Feb 2025) held enforcement of this award constitutes illegal state aid under EU law. Colombia Supreme Court refused recognition. Enforcement ongoing in multiple non-EU jurisdictions.",
     "Consortium of European solar PV investors (AES Solar, Ontario Power and others) challenged Spain's post-2012 cuts to photovoltaic feed-in tariffs and the 7% generation tax. UNCITRAL/PCA arbitration. Final Award 28 February 2020. EUR ~91.1M awarded on EUR 1.9B claimed — less than 5% recovery.",
     "Fair and equitable treatment, ECT Article 10(1). UNCITRAL rules — not ICSID; subject to court set-aside proceedings.",
     "Largest claim in the Spain ECT wave (EUR 1.9B). The steep haircut (5% of claimed) illustrates that tribunals accepted FET breach but limited damages. EC state aid concerns apply; Amsterdam court blocked EU enforcement Feb 2025."),

    (821, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Dutch (Charanne BV) and Luxembourg (Construction Investments) investors in Spanish solar PV plants challenged Spain's early regulatory changes to the FIT framework (2010-2012 modifications). First major Spain ECT case decided. SCC Case V(062/2012), seat Madrid.",
     "Fair and equitable treatment and indirect expropriation under ECT Article 10(1). Award 21 January 2016.",
     "First Spain ECT award and the only early one Spain won on the merits. Set an initially narrow interpretation of legitimate expectations — Spain repeatedly invoked it in later cases with diminishing success as later tribunals found the 2012-2014 reforms far more drastic."),

    (836, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Spanish real estate company invested EUR 25M+ in land in Las Rozas, Madrid for residential development. After allegedly receiving municipal encouragement, planning approval was withheld. ICSID Case ARB/12/17. Non-energy case.",
     "Claims under a BIT (specific treaty unclear). Real estate / urban planning sector.",
     "One of the few non-energy investment disputes against Spain in the UNCTAD dataset. Real estate/urban planning context rather than renewable energy."),

    (759, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Luxembourg SPV held equity in concentrated solar power (CSP) plants in Spain. Challenged Spain's sweeping 2013-2014 reforms abolishing the CSP guaranteed tariff regime. SCC Case 2013/094.",
     "Fair and equitable treatment and expropriation, ECT Article 10(1).",
     "One of the largest Spain ECT claims (EUR 840M) where Spain won. Demonstrates that even very large claims failed on merits in some SCC cases."),

    (763, "not_paid",
     "Complex procedural history. Original award (EUR 128M, 2017) ANNULLED by ICSID June 2020 — arbitrator Stanimir Alexandrov had undisclosed relationship with claimants' expert firm Brattle Group (improper constitution + severe departure from fundamental procedure). Resubmission tribunal constituted 2022. New award EUR 262M issued October 2025 — more than double the original, reflecting accrued interest. Spain immediately filed for annulment of the resubmission award. Not paid.",
     "UK (Eiser Infrastructure) and Luxembourg (Energía Solar Luxembourg) investors held stakes in three CSP plants in Spain (Torresol Energy JV, also involving Masdar). Investment made in reliance on Spain's 2007-2008 CSP support framework, systematically dismantled 2012-2014. ICSID Case ARB/13/36.",
     "Fair and equitable treatment, ECT Article 10(1). Tribunal found Spain 'radically' transformed the regulatory environment.",
     "Most procedurally complex case in the Spain ECT wave: annulled for arbitrator misconduct, resubmitted, EUR 262M new award (2025), now being challenged again. The Alexandrov scandal affected multiple arbitrations globally. Each annulment attempt adds years and interest to the mounting liability."),

    (774, "blocked",
     "European Commission declared payment of this award ILLEGAL STATE AID (formal Decision 24 March 2025, SA.54155). Spain ordered not to pay and to prevent any enforcement domestically or abroad — first time EC has formally declared an investment award to constitute state aid. US DC District Court lifted enforcement stay Jan 2025; US Supreme Court order Oct 2025 (likely denying Spain cert). UK Court of Appeal dismissed Spain's appeal Oct 2024; UK Supreme Court granted Spain permission to appeal Jan 2025. Australia enforcement active. Luxembourg: Spain filed proceedings against claimant. Not paid.",
     "Antin Infrastructure Services (Luxembourg and Netherlands SPVs) held equity stakes in Spanish CSP plants. Invested in reliance on Spain's 2007-2008 CSP support framework. ICSID Case ARB/13/31. Award EUR 101M issued October 2018.",
     "Fair and equitable treatment, ECT Article 10(1). Tribunal applied Eiser standard, found Spain radically changed regulatory framework.",
     "Landmark for EU state aid vs. investment arbitration. The EC's March 2025 state aid decision is the first formal declaration that paying an investment award constitutes illegal state aid — now used by Spain as a shield in all enforcement jurisdictions. The most watched enforcement case alongside NextEra."),

    (775, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Dutch holding company (affiliated with Spanish construction group Isolux Corsán) held renewable energy assets in Spain. Claim raises treaty-shopping concerns: nominally Dutch company with Spanish beneficial owners. SCC arbitration.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Raises the 'mailbox company' / nationality-planning issue. Beneficial Spanish ownership may have been relevant to the merits outcome."),

    (794, "enforced",
     "Award (EUR 59.6M) assigned to Blasket Renewable Investments LLC. Australian Federal Court enforced in Blasket Renewable Investments v Kingdom of Spain [2025] FCA 1028 (29 Aug 2025) — combined judgment on 4 ICSID awards worth ~EUR 470M, rejecting Spain's sovereign immunity arguments. Spain intends to appeal. English High Court ruled ICSID/ECT awards NOT assignable to third parties (Nov 2025), blocking UK enforcement — creates UK/Australia split. Spain has not paid.",
     "RREEF Infrastructure (Deutsche Asset Management / DWS) invested in wind and solar energy assets in Spain through UK GP and Luxembourg LP. ICSID Case ARB/13/30. Award EUR 59.6M issued 11 December 2019.",
     "Fair and equitable treatment and expropriation, ECT Article 10(1).",
     "First of the 'Blasket wave' — RREEF assigned its award to Blasket Renewable Investments LLC to pursue enforcement in non-EU courts. The Australian enforcement (Aug 2025) is a landmark; the English High Court's non-assignability ruling (Nov 2025) creates a major split with Australia affecting the entire Blasket enforcement strategy."),

    (713, "not_paid",
     "Spain has not paid. Post-Brexit UK investors (InfraRed is UK-based) have stronger enforcement position — Achmea/Komstroy does not apply to UK-Spain after Jan 2020. Active enforcement proceedings not prominently reported.",
     "InfraRed Capital Partners (UK infrastructure manager) held solar PV assets in Spain through various holding structures. ICSID Case ARB/14/12. Award EUR 28.2M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "UK fund manager claim. Post-Brexit, InfraRed's UK status gives it a cleaner enforcement path in non-EU jurisdictions than EU-domiciled investors."),

    (720, "not_paid",
     "Spain applied for annulment March 2019; enforcement stayed. US DC enforcement proceedings stayed pending annulment. UAE sovereign backing (Mubadala Investment Company) gives Masdar enforcement options in Gulf states and Asia beyond typical EU/US/Australia theaters. Not paid.",
     "Masdar Solar & Wind Cooperatief UA (Dutch cooperative vehicle of Abu Dhabi's Masdar / Mubadala Investment Company) invested in three CSP plants in Spain (Torresol Energy JV, also involving Eiser). ICSID Case ARB/14/1. Award EUR 64.5M issued May 2019.",
     "Fair and equitable treatment, ECT Article 10(1). Tribunal found Spain radically altered the regulatory framework.",
     "UAE sovereign-backed investor creates unusual enforcement dynamics — Masdar can seek enforcement in Gulf, UAE-treaty partners, and Asian jurisdictions where Spain has sovereign assets, beyond the EU/US/Australia theaters."),

    (722, "enforced",
     "Most litigated enforcement case in the wave. ICSID revision request rejected Jan 2024. US DC Circuit confirmed jurisdiction in landmark ruling (Aug 2024) — leading US precedent for ICSID enforcement. Spain filed SCOTUS cert petition Oct 2025. Australian Federal Court enforced as part of Blasket [2025] FCA 1028 (Aug 2025). Singapore: registration granted Jan 2024; Spain applied to set aside May 2025. Not paid — EUR 290.6M outstanding.",
     "NextEra Energy (Florida-based US company, world's largest wind/solar generator) held Spanish renewable energy assets through Dutch subsidiaries. ICSID Case ARB/14/11. Award EUR 290.6M issued 31 May 2019 — largest decided award in the Spain ECT wave.",
     "Fair and equitable treatment, ECT Article 10(1). Tribunal found Spain fundamentally and radically transformed the renewable energy support framework.",
     "Largest award in the Spain ECT wave and most consequential enforcement case. DC Circuit NextEra ruling (Aug 2024) is the leading US precedent on enforcing ICSID awards against EU Member States. Spain's SCOTUS cert petition is the next major legal test for the entire class of cases."),

    (727, "not_paid",
     "Spain has not paid. Luxembourg investor = intra-EU; EU court enforcement blocked under Achmea/Komstroy. No prominent non-EU enforcement proceedings reported.",
     "RENERGY Sàrl (Luxembourg SPV) held solar energy assets in Spain. ICSID. Award EUR 32.9M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Mid-range Luxembourg award. Intra-EU domicile limits enforcement to non-EU jurisdictions."),

    (729, "not_paid",
     "Spain has not paid. Germany = intra-EU; German courts uniformly refuse enforcement of intra-EU ECT awards. RWE has complex incentives given its ongoing European energy market presence.",
     "RWE Innogy GmbH and RWE Innogy Cogen GmbH (renewable energy subsidiaries of German utility RWE, now RWE Renewables) invested in Spanish wind energy assets. ICSID Case ARB/14/30. Award EUR 28.1M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Low recovery rate (~10% of EUR 273M claimed). RWE is one of Europe's largest utilities; the unpaid award is a rounding error on its balance sheet but a matter of principle."),

    (597, "enforced",
     "Award assigned to Blasket Renewable Investments LLC. Australian Federal Court enforced as part of Blasket [2025] FCA 1028 (Aug 2025). UK enforcement blocked on assignability grounds (English High Court Nov 2025). Spain has not paid.",
     "9REN Holding Sàrl (Luxembourg SPV) held solar PV assets in Spain. ICSID Case ARB/15/15. Award EUR 40M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Part of the Blasket enforcement wave in Australia. Luxembourg domicile means EU enforcement blocked; Australian court is the primary enforcement forum."),

    (603, "discontinued",
     "Discontinued for unknown reasons before a decision. Possible settlement, withdrawal, or strategic decision.",
     "Alten (renewable energy developer) initiated an ECT claim related to Spanish solar PV investments. Discontinued before decision. EUR 59.4M claimed.",
     "Energy Charter Treaty, Article 10(1).",
     "One of four Spain ECT cases discontinued without a decision."),

    (610, "not_paid",
     "Spain has not paid. Germany = intra-EU; German courts refuse enforcement.",
     "BayWa r.e. (renewable energy subsidiary of German agricultural cooperative BayWa AG) held solar and wind energy assets in Spain. ICSID Case ARB/15/16. Award EUR 22M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "BayWa r.e. has since become a major global renewable energy developer. The unpaid award remains an outstanding liability on Spain's books."),

    (616, "not_paid",
     "Spain has not paid. Portugal = EU member; EU court enforcement blocked under Achmea/Komstroy.",
     "Cavalum SGPS SA (Portuguese energy company) invested in solar energy in Spain. ICSID Case ARB/15/34. Award EUR 7.4M — low recovery (12% of EUR 60M claimed).",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Portugal-Spain dimension adds diplomatic complexity. Both EU members; both constrained by Achmea/Komstroy in enforcing awards against each other."),

    (620, "not_paid",
     "Spain has not paid. Luxembourg investor = intra-EU; EU court enforcement blocked. Non-EU enforcement (Australia, US) available.",
     "Cube Infrastructure Fund SICAV (Luxembourg infrastructure fund) held renewable energy assets in Spain. ICSID Case ARB/15/20. Award EUR 33.7M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Mid-range Luxembourg fund claim. May pursue Blasket-style enforcement in Australia or US."),

    (622, "pending",
     "Pending — no award yet. German investor = intra-EU. One of the highest-value pending claims.",
     "E.ON SE (Germany's largest integrated electric utility) and subsidiaries invested in Spanish renewable energy. ICSID Case ARB/15/25. EUR 377M claimed.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "A ruling against Spain from E.ON — one of Europe's largest utilities — would be politically significant regardless of enforceability. If awarded, EU enforcement would be blocked; ICSID path enables non-EU enforcement."),

    (628, "not_paid",
     "Spain has not paid. Luxembourg investor = intra-EU; EU court enforcement blocked. Foresight Group (UK-listed asset manager) may pursue non-EU enforcement.",
     "Foresight Luxembourg Solar (Luxembourg vehicle of UK-based Foresight Group infrastructure manager) held solar PV assets in Spain. ICSID Case ARB/15/46. Award EUR 39M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "UK-listed fund manager using Luxembourg SPV. Post-Brexit UK management may pursue non-EU enforcement despite EU-domiciled holding company."),

    (636, "not_paid",
     "Spain has not paid. Luxembourg and Swedish investors = intra-EU; EU court enforcement blocked. ICSID path enables non-EU enforcement attempts.",
     "Hydro Energy 1 Sàrl (Luxembourg) and Hydroxana Sweden AB invested in hydroelectric power assets in Spain. ICSID Case ARB/15/42. Award EUR 30.9M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "One of the few Spain ECT cases involving hydroelectric power, showing Spain's regulatory reforms affected multiple renewable technologies beyond solar."),

    (639, "enforced",
     "Annulment rejected 6 February 2024 (all grounds dismissed). US DC District Court GRANTED enforcement 26 September 2024 — entered judgment for EUR 23.51M, rejecting Spain's EU comity, forum non conveniens, and act of state arguments. As a Japanese investor, Achmea/Komstroy does not apply. Brussels Court of Appeal proceedings (June 2024). Spain has not paid.",
     "JGC Holdings Corporation (formerly JGC Corporation, major Japanese engineering company) invested in solar energy projects in Spain. ICSID arbitration. Award EUR 23.5M. Tribunal found Spain 'radically abolished' the renewable energy support regime, frustrating legitimate expectations. Japanese investor — NOT intra-EU.",
     "Fair and equitable treatment, ECT Article 10(1). Non-intra-EU: Japanese investor. ICSID arbitration.",
     "Strongest enforcement position of any decided case (with Eurus Holdings). US court enforced without hesitation given Japan's non-EU status. The 2024 annulment rejection made the award unassailable on merits. Template for other Japanese investors (Itochu, Mitsui, Eurus) in the wave."),

    (642, "not_paid",
     "Spain has not paid. German individual investors = intra-EU; EU court enforcement blocked.",
     "Individual German investors in Spanish solar PV plants — the retail investor dimension of the wave. People who put personal savings into Spanish solar funds and lost money when subsidies were cut retroactively. ICSID Case ARB/15/36. Award EUR 15M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Represents the many European retail investors who suffered losses when Spain cut solar subsidies. The award is real but practical enforcement is very difficult for individuals without deep pockets."),

    (643, "pending",
     "Pending — no award yet. German investors = intra-EU.",
     "KS Invest GmbH and TLS Invest GmbH (German solar investment companies) holding solar energy assets in Spain. EUR 92.2M claimed.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Two German investment companies; intra-EU; pending arbitration."),

    (644, "pending",
     "Pending — no award yet. Germany/Luxembourg investors = intra-EU. One of the largest pending claims in the entire wave.",
     "Landesbank Baden-Württemberg (LBBW, German state-owned bank) and associated entities invested in or financed Spanish solar energy assets. ICSID Case ARB/15/45. EUR 560.5M claimed.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "German state-owned bank as claimant adds diplomatic and political weight. If awarded, EU enforcement would be blocked, but LBBW has access to Spanish sovereign assets in global capital markets."),

    (656, "blocked",
     "Award SET ASIDE at the seat. Swedish Svea Court of Appeal (December 2022) annulled the EUR 53.3M award applying Achmea and Komstroy — one of the first judicial set-asides of an ECT award on intra-EU grounds. Swedish Supreme Court confirmed (July 2023). Award definitively nullified at the seat (Stockholm). Enforcement in other jurisdictions theoretically possible but severely undermined by seat-state set-aside.",
     "Novenergia II Energy & Environment SCA (Luxembourg, SICAR structure) purchased eight solar parks in Spain 2007-2008. SCC Case 2015/063, Stockholm. Award EUR 53.3M issued February 2018. SCC (non-ICSID) arbitration — subject to judicial set-aside at the seat, unlike ICSID awards.",
     "Fair and equitable treatment, ECT Article 10(1). SCC arbitration — crucially different from ICSID: national courts CAN set aside SCC awards.",
     "Definitive test case for Achmea/Komstroy applied to ECT awards in the seat state. The Swedish set-aside is the key reference point in EU enforcement debates. SCC procedural route (vs ICSID) was fatally vulnerable to this: ICSID awards cannot be annulled by national courts, only by ICSID committees."),

    (657, "not_paid",
     "Award assigned to Blasket. English High Court ruled ICSID/ECT awards NOT assignable to third parties (November 2025) — blocking Blasket's UK enforcement and creating a direct split with the Australian Federal Court ruling in the same Blasket proceedings. Swiss investor Schwab Holding is NOT subject to intra-EU restrictions and may pursue direct enforcement. Spain has not paid.",
     "OperaFund Eco-Invest SICAV PLC (Malta) and Schwab Holding AG (Switzerland) invested in Spanish solar PV plants. ICSID. Award USD 29.3M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "The Blasket assignability ruling from the English High Court (Nov 2025) is highly significant — it creates a major split between UK and Australian courts on whether ICSID awards can be assigned to third-party enforcement vehicles, affecting the entire Blasket enforcement strategy across all assigned cases."),

    (669, "discontinued",
     "Discontinued. Very small claim (EUR 6.1M). Likely withdrawn due to cost-benefit calculation.",
     "Solarpark Engineering SA initiated an ECT claim against Spain regarding solar PV investments. Discontinued before decision.",
     "Energy Charter Treaty.",
     "Very small claim; one of four discontinued Spain ECT cases."),

    (670, "not_paid",
     "Spain has not paid. Germany = intra-EU; German courts refuse enforcement.",
     "SolEs Badajoz GmbH (German SPV) held solar plants in Badajoz, Extremadura. ICSID Case ARB/15/38. Award EUR 40.5M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Badajoz is in Extremadura — one of the sunniest regions in Europe. The solar resource was never in doubt; the issue was the retroactive removal of the subsidies that made the investment viable."),

    (672, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Stadtwerke München GmbH (Munich's municipal utility) and other German investors held renewable energy (including CSP) assets in Spain. ICSID Case ARB/15/1. EUR 423M claimed — largest Spain ECT claim Spain won by amount.",
     "Fair and equitable treatment and expropriation, ECT Article 10(1).",
     "Spain's largest victory by claimed amount in the ECT wave. A publicly owned German utility (city of Munich) claimed against Spain — Spain prevailing shows that institutional ownership does not guarantee success."),

    (673, "not_paid",
     "Spain has not paid. Germany = intra-EU; German courts refuse enforcement.",
     "STEAG GmbH (major German energy company with coal and CSP assets) invested in concentrated solar power plants in Spain. ICSID Case ARB/15/4. Award EUR 27.7M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "STEAG had diversified into Spanish CSP as part of its renewables transition. The unpaid award represents one of many unresolved Germany-Spain ECT tensions."),

    (678, "enforced",
     "Annulment application rejected 21 February 2023. Spain filed revision application May 2023 (triggering provisional enforcement stay). Award assigned to Blasket. Australian Federal Court enforced in Blasket [2025] FCA 1028 (Aug 2025). UK enforcement blocked on assignability grounds (English High Court Nov 2025). Revision proceedings still pending. Spain has not paid.",
     "Watkins Holdings Sàrl and others (Luxembourg-based) invested in solar PV in Spain. ICSID Case ARB/15/44. Award EUR 77M issued 21 January 2020.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "After losing on annulment in 2023, Spain filed a revision application — the revision route is increasingly Spain's fallback delaying tactic. Enforcement succeeding in Australia via Blasket despite revision proceedings underway."),

    (528, "not_paid",
     "Spain has not paid. High recovery rate (~68% of claimed amount). Enforcement proceedings not prominently reported.",
     "Biram and associated investors held solar energy assets in Spain. ICSID. Award EUR 47.3M on EUR 69M claimed — one of the highest recovery rates in the wave.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Unusually high recovery rate (~68%) contrasts with many Spain ECT cases where claimants received only 10-30% of claimed amounts."),

    (536, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Corcoesto SA claimed regarding a gold mine project in Galicia. The regional government of Galicia blocked open-pit mining permits on environmental grounds despite earlier exploration authorization. UNCITRAL Case 2016-26. Non-energy, mining/environmental.",
     "Investment treaty claims (specific treaty unclear — possibly Canada-Spain BIT given Canadian beneficial ownership of the project). UNCITRAL arbitration.",
     "Rare non-energy, non-ECT case in the Spain wave. Spain's refusal to grant a mining permit for environmental reasons was upheld — significant for environmental defence in ISDS."),

    (537, "not_paid",
     "Spain has not paid. Dutch investor = intra-EU; EU court enforcement blocked. Notable for near-full recovery (99% of claimed amount).",
     "Cordoba Beheer BV (Dutch investment vehicle) held solar energy assets in Spain. ICSID. Award EUR 6.8M on EUR 6.9M claimed — essentially full recovery.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "One of the highest recovery rates in the entire wave (99%). The very small absolute amount and EU-only enforcement options make practical recovery very difficult."),

    (545, "not_paid",
     "Spain has not paid. France = EU member; EU court enforcement blocked. EDF (French state-controlled) adds diplomatic complexity — France is an EU partner with its own political incentives regarding the EC state aid doctrine.",
     "EDF Energies Nouvelles SA (100% subsidiary of French state utility EDF SA) acquired twelve solar installations in Spain 2007-2008. Spain abrogated the support framework 2013-2014. ICSID. Award EUR 29.6M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "French state-controlled utility claiming against Spain. The EC's state aid doctrine (developed to block Antin) creates an irony: EDF's parent is partially state-owned, so the French government simultaneously supports and benefits from both the EC's anti-enforcement campaign and potential enforcement of the award."),

    (550, "not_paid",
     "Award EUR 106.2M issued November 2022. Spain applied for annulment September 2023. ICSID committee refused unconditional stay — required Spain to post security; Spain refused and the stay was lifted June 2024 enabling enforcement. Annulment decision issued 31 July 2025 (outcome not fully confirmed). Japanese ultimate parent (Toyota Tsusho/Toyota group) = NOT intra-EU; no Achmea/Komstroy obstacle for Japanese entity claims. Spain has not paid.",
     "Eurus Energy Holdings Corporation (Japan, majority-owned by Toyota Tsusho — Toyota's trading arm) and Eurus Energy Europe BV (Netherlands) invested heavily in Spanish wind energy. ICSID Case ARB/16/4. Award EUR 106.2M issued November 2022. Tribunal selected June 2021 valuation date for full reparation.",
     "Fair and equitable treatment, ECT Article 10(1). Non-intra-EU for the Japanese parent entity.",
     "Toyota Tsusho backing makes this one of the most economically significant non-EU claims. Stay lifted in 2024 after Spain refused to post security — showing growing ICSID committee frustration with Spain's non-compliance. Japanese parent has enforcement options beyond EU/US/Australia."),

    (562, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "Green Power K/S and SCE Solar Don Benito APS (both Danish entities) held solar PV assets in Don Benito, Extremadura. SCC arbitration. EUR 74.3M claimed.",
     "Fair and equitable treatment, ECT Article 10(1). SCC arbitration.",
     "Denmark = EU member. Spain prevailed in this SCC proceeding. Contrasts with similar SCC cases (e.g. Novenergia where Spain lost on merits but won on set-aside)."),

    (567, "not_paid",
     "Spain has not paid. Luxembourg/Dutch investors = intra-EU; EU court enforcement blocked. M&G (UK asset manager, formerly part of Prudential) may pursue non-EU enforcement.",
     "Infracapital F1 Sàrl (Luxembourg) and Infracapital Solar BV (Netherlands), vehicles of UK fund manager M&G Investments, held solar energy assets in Spain. ICSID. Award EUR 24.9M.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "UK-managed fund using EU-domiciled holding vehicles. Post-Brexit UK management may pursue non-EU enforcement despite EU SPVs."),

    (461, "pending",
     "Pending — no award yet.",
     "DCM Energy and others filed an ECT claim against Spain regarding renewable energy investments. Limited public information. Filed 2017.",
     "Energy Charter Treaty, Article 10(1).",
     "Late-stage pending case with limited public disclosure."),

    (469, "state_won",
     "Spain prevailed on the merits. No enforcement issue.",
     "FREIF Eurowind Holdings filed an ECT claim regarding wind energy investments in Spain. EUR 99.4M claimed. ICSID.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Wind energy case — Spain prevailed. One of the few wind-specific (non-solar) cases in the wave."),

    (499, "pending",
     "Pending — no award yet. German state bank in wind-down = intra-EU.",
     "Portigon AG (formerly WestLB AG, a German state bank in managed wind-down since 2012) invested in or financed Spanish solar energy projects. ICSID Case ARB/17/15. Filed 2017.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "A bank in managed run-off pursuing a large arbitration suggests litigation funding involvement. German state ownership adds political dimension."),

    (513, "pending",
     "Pending — no award yet. Dutch investor = intra-EU.",
     "Triodos SICAV II (investment vehicle of Dutch ethical bank Triodos Bank) invested in renewable energy in Spain. Filed 2017.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Triodos Bank is Europe's leading ethical/sustainable bank — the irony of an ESG-focused institution pursuing investor-state arbitration over renewable energy subsidies captures the complexity of the Spain ECT wave."),

    (366, "pending",
     "Pending — no award yet. Swiss investor = NOT intra-EU — no Achmea/Komstroy obstacle if awarded. Strong enforcement potential.",
     "EBL (Genossenschaft Elektra Baselland), a Swiss regional electricity cooperative from Basel-Land canton, and Tubo Sol PE2 SL invested in solar energy in Spain. ICSID. Filed 2018.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Swiss cooperative as claimant — Switzerland is not an EU member, so intra-EU restrictions do not apply. Enforcement outlook significantly better than EU-based claimants if awarded."),

    (372, "pending",
     "Pending — no award yet.",
     "European Solar Farms SA and others filed an ECT claim against Spain regarding solar PV investments. Filed 2018.",
     "Energy Charter Treaty, Article 10(1).",
     "Late-stage pending case with limited public information."),

    (380, "discontinued",
     "Discontinued for unknown reasons. The 2018 Achmea decision (same year as filing) may have contributed — investors re-evaluated enforcement prospects after that ruling. Very large claim (EUR 470M).",
     "GBM Global Energy BV and others (Dutch entities) filed one of the largest claims in the Spain ECT wave — EUR 470M. Discontinued before any decision.",
     "Energy Charter Treaty.",
     "Largest discontinued claim in the Spain ECT wave. Timing of discontinuation (same year as Achmea) is potentially significant — enforcement prospects for EU investors deteriorated sharply in 2018."),

    (388, "pending",
     "Pending — no award yet. Japanese investor = NOT intra-EU — no Achmea/Komstroy obstacle if awarded. Itochu has significant litigation resources.",
     "Itochu Corporation (one of Japan's largest general trading companies / sogo shosha) invested in Spanish solar energy projects. ICSID. Filed 2018.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Japanese sogo shosha as claimant — like JGC, Itochu's non-EU status gives it a clean enforcement path. Could become another JGC-style success story if the merits go its way."),

    (427, "state_won",
     "Spain prevailed on the merits. No enforcement issue. Largest claim Spain has won by amount (EUR 647M).",
     "Valle Ruiz and others filed one of the largest claims in the Spain ECT wave (EUR 647.1M claimed). Tribunal found for Spain. ICSID. Filed 2018.",
     "Fair and equitable treatment and other ECT claims.",
     "Spain's victory in the single largest claim of the wave by amount. Details of merits reasoning not fully public."),

    (284, "pending",
     "Pending — no award yet. Luxembourg investor = intra-EU.",
     "Canepa Green Energy Opportunities I and II Sàrl (Luxembourg SPVs, likely backed by Swiss-based Canepa Asset Management) held renewable energy assets in Spain. ICSID. Filed 2019.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Late-filed claim; Luxembourg domicile limits future enforcement options despite likely Swiss beneficial ownership."),

    (325, "pending",
     "Pending — no award yet. Belgian investor = intra-EU.",
     "Sapec SA (Belgian agri-chemicals and renewable energy group) filed an ECT or BIT claim against Spain. Filed 2019.",
     "Energy Charter Treaty or BIT.",
     "Belgian diversified company. Intra-EU if ECT-based."),

    (336, "pending",
     "Pending — no award yet.",
     "VM Solar Jerez SL and others filed an ECT claim against Spain regarding solar PV investments. ICSID. Filed 2019.",
     "Energy Charter Treaty, Article 10(1).",
     "Late-stage pending case."),

    (243, "pending",
     "Pending — no award yet. Japanese ultimate parent (Mitsui & Co.) provides non-EU enforcement options if awarded.",
     "Mitsui & Co. Energy Europe and Africa BV (Dutch holding company; ultimate parent: Mitsui & Co. Japan, one of Japan's largest sogo shosha) invested in renewable energy in Spain. ICSID. Filed 2020.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Like JGC, Itochu, and Eurus, Mitsui's Japanese parentage provides enforcement options outside the EU if Achmea/Komstroy arguments are raised against the Dutch subsidiary."),

    (180, "pending",
     "Pending — no award yet. Very late filing (2021).",
     "Spanish Solar Energy filed an ECT or other treaty claim against Spain. Very limited public information. Filed 2021.",
     "Energy Charter Treaty or other.",
     "Very late-filed claim; post-dates most of the regulatory measures at issue."),

    (187, "discontinued",
     "Discontinued for unknown reasons. Filed 2021 and discontinued.",
     "TS Villalba and others filed an ECT claim against Spain regarding solar PV investments. Discontinued before decision.",
     "Energy Charter Treaty.",
     "One of four discontinued Spain ECT cases; one of the latest-filed to be discontinued."),

    (118, "pending",
     "Pending — no award yet. German investor = intra-EU. Very late filing (2022) — after Spain's ECT withdrawal process began. ECT sunset clause theoretically protects existing investments for 20 years.",
     "WOC Photovoltaik-Projekt GmbH and others (German solar investment vehicle) filed an ECT claim against Spain. ICSID. Filed 2022.",
     "Fair and equitable treatment, ECT Article 10(1).",
     "Latest filing in the UNCTAD dataset. Filed after Spain notified ECT withdrawal — the sunset clause question will be central to jurisdiction."),
]

NOW = datetime.utcnow().isoformat(timespec="seconds")

if __name__ == "__main__":
    con = sqlite3.connect(DB)
    con.executemany(
        """INSERT OR REPLACE INTO research_notes
           (case_no, enforcement_status, enforcement_detail, context, claim_basis, significance, updated_at)
           VALUES (?,?,?,?,?,?,?)""",
        [(r[0], r[1], r[2], r[3], r[4], r[5], NOW) for r in ROWS],
    )
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM research_notes").fetchone()[0]
    con.close()
    print(f"Seeded {count} research notes.")
