<!-- 
  updated_final_owners.md
  =======================
  PURPOSE:
    Lookup table mapping Spain ECT ISDS case numbers to the ultimate economic
    owner/beneficial controller behind each claimant entity, cutting through
    shell/holding company structures to identify the real national interest.

  PROVENANCE:
    Research conducted by Gemini (Google AI) during a conversation session in
    June 2025, using publicly available corporate registry data, press reports,
    fund prospectuses, and ICSID case records. Results reviewed by the project
    owner but not independently audited against primary legal filings.

  HOW IT IS USED:
    The `ULT_OWNER` JavaScript object in `index.html` is populated from this
    table. It maps case_no -> country string, overriding the nominal home_state
    for the inner ring of the origin doughnut chart in the Visualizations tab
    (renderOriginRings). Only cases with a definitively known single-country
    owner are added to ULT_OWNER; diversified/unknown cases are left out.

  RELATED FILES:
    - ECT_Spain_Claims_Ultimate_Ownership.md — earlier, more detailed write-up
      of 15 landmark cases with citations
    - unknown_final_owner.md — cases where ultimate ownership remains unresolved
    - CLAUDE.md — project-level notes and architecture overview
-->

Case No.	Case Name	Nominal Home State	Ultimate Economic Owner / Parent Entity
1318	Maffezini v. Spain	Argentina	Emilio Agustín Maffezini (Individual Argentine investor)
836	Inversión y Gestión de Bienes IGB and IGB18 Las Rozas v. Spain	Spain	still unknown, 2nd attempt
759	CSP Equity Investment v. Spain	Luxembourg	Abengoa S.A. (Spain)
775	Isolux Infrastructure Netherlands v. Spain	Netherlands	Grupo Isolux Corsán S.A. (Spain) & PSP Investments (Public Sector Pension Investment Board of Canada — a federal Crown corporation)
794	RREEF Infrastructure and RREEF Pan-European Infrastructure v. Spain	UK / Luxembourg	Deutsche Bank AG (Germany) via DWS Group / diversified institutional fund capital
713	InfraRed Environmental Infrastructure and others v. Spain	United Kingdom	Sun Life Financial Inc. (Canada) / diversified institutional fund investors
727	RENERGY v. Spain	Luxembourg	The Marguerite Fund (A consortium of European public/state-backed banks: EIB, CDC, CDP, ICO, KfW, and PKO Bank Polski)
603	Alten Renewable Energy Developments v. Spain	Netherlands	Alten Energías Renovables (Spain — owned by its original founders and management)
616	Cavalum SGPS v. Spain	Portugal	Mirova / Groupe BPCE (France)
628	Foresight Luxembourg Solar 1 and others v. Spain	Luxembourg	diversified (Foresight Solar Fund, publicly listed on the London Stock Exchange with highly fragmented retail and institutional shareholders)
636	Hydro Energy 1 and Hydroxana Sweden v. Spain	Luxembourg / Sweden	Alpiq Holding AG (Switzerland)
642	Kruck and others v. Spain	Germany	German individual investors (Christian Kruck and a group of private retail investors)
669	Solarpark Engineering v. Spain	Luxembourg	still unknown, 2nd attempt
670	SolEs Badajoz v. Spain	Germany	German individual/private investors
673	STEAG v. Spain	Germany	Asterion Industrial Partners (Spain — acquired corporate control in late 2023; previously owned by a consortium of 6 German municipal utilities)
528	Biram and others v. Spain	Germany	German individual/private investors
536	Corcoesto v. Spain	Panama	Edgewater Exploration Ltd. (Canada)
537	Cordoba Beheer and others v. Spain	Netherlands	still unknown, 2nd attempt
545	EDF Energies Nouvelles v. Spain	France	Électricité de France (EDF) SA (Wholly owned by the French State)
550	Eurus Energy Holdings and Eurus Energy Europe v. Spain	Japan / Netherlands	Joint venture between Toyota Tsusho Corporation (60%) and Tokyo Electric Power Company (TEPCO) (40%) (Japan)
562	Green Power and SCE Solar Don Benito v. Spain	Denmark	diversified (Green Power Partners K/S, backed by Danish pension funds and retail clean energy investors)
567	Infracapital F1 and Infracapital Solar v. Spain	Luxembourg / Netherlands	M&G plc (UK — publicly traded savings and investment group)
461	DCM Energy and others v. Spain	Cyprus	diversified (Closed-end solar funds marketed to thousands of German retail investors)
469	FREIF Eurowind Holdings v. Spain	United Kingdom	First Reserve Corporation (USA) / diversified institutional fund investors
499	Portigon v. Spain	Germany	State of North Rhine-Westphalia and German regional savings bank associations (As the legal successor to WestLB)
513	Triodos SICAV II v. Spain	Luxembourg	diversified (Triodos Bank N.V., Netherlands — corporate ownership is distributed via depository receipts held by over 40,000 individual investors)
366	EBL (Genossenschaft Elektra Baselland) and Tubo Sol PE2 v. Spain	Switzerland / Spain	Genossenschaft Elektra Baselland (EBL) (Swiss consumer-owned utility cooperative)
372	European Solar Farms and others v. Spain	Denmark	Danish individual/private investors
380	GBM Global Energy and others v. Spain	Netherlands	SunEdison, Inc. (USA)
388	Itochu Corporation v. Spain	Japan	diversified (Publicly listed sogo shosha trading giant on the Tokyo Stock Exchange)
427	Valle Ruiz and others v. Spain	Netherlands	The del Valle family (Mexican billionaire family)
284	Canepa Green Energy Opportunities v. Spain	Luxembourg	Azora Capital (Spain) & associated private family offices
325	Sapec v. Spain	Belgium	The Eduardo de San José family (Prominent Portuguese/Belgian industrial family)
336	VM Solar Jerez and others v. Spain	(Not Confirmed)	still unknown, 2nd attempt
243	Mitsui & Co. Energy Europe and Africa v. Spain	Netherlands	Mitsui & Co., Ltd. (Japan) / diversified
180	Spanish Solar Energy v. Spain	(Not Confirmed)	still unknown, 2nd attempt
187	TS Villalba and others v. Spain	(Not Confirmed)	still unknown, 2nd attempt
118	WOC Photovoltaik-Projekt and others v. Spain	Germany	White Owl Capital AG (Germany) / diversified