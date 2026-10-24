const API = "";
const STORY_UNIT_ID = "A999926004821";
const BLOOD_GROUPS = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"];
const TEST_ACTOR = "tech.brian";

const copy = {
  en: {
    apiConnected: "API connected", apiOffline: "API unavailable", record: "Record",
    morning: "Good morning", afternoon: "Good afternoon", evening: "Good evening",
    peopleTitle: "Who are you today?", peopleIntro: "Pick a person. Everyone sees the same blood through their own eyes.",
    demoTitle: "Synthetic story", demoDescription: "Load the demo through the API to explore the full HemoSync journey. Existing ledger history is kept.",
    loadDemo: "Load synthetic demo", demoLoaded: "Synthetic demo loaded through the HemoSync API.",
    demoAlreadyLoaded: "The synthetic story is already in the ledger. No history was reset.",
    demoOnly: "Synthetic data only · Not a medical device", tryFlow: "Try Brian first to release Wanjiru's donation, then Achieng.",
    home: "Home", labTitle: "Lab release inventory", labIntro: "Review the API-recorded tests and use the required two-person release.",
    signRelease: "Release with Brian + Dr. Amina", sameSigner: "Demo: submit the same signer twice",
    recordLabResult: "Record this result", result: "Result", recordTyping: "Record blood typing",
    typingActor: "Technologist", typingGroup: "Typed group",
    quarantine: "Quarantined", released: "Released", releaseSuccess: "Two-person release recorded by the API.",
    queueClear: "The quarantine queue is clear.", samples: "ABO/Rh determinations", infectiousPanel: "Required infectious-disease panel",
    urgent: "Urgent request", urgentDescription: "Choose an encounter. The synthetic chart fills the recorded group; confirm it against two independent samples before matching.",
    patientQueue: "Patient queue", syntheticQueue: "Five synthetic maternity encounters · no real patient details",
    selectEncounter: "Encounter", chooseEncounter: "Choose an encounter",
    chartGroup: "Group on synthetic chart", chartGroupNote: "Pre-filled from this demo encounter only. Confirm the group using two independent samples before matching.",
    waitingForSamples: "Waiting for independent sample confirmation", samplesVerified: "Two samples confirmed · ready to match", unitReserved: "Unit reserved",
    atBedside: "At bedside", transfused: "Transfusion started", returnToQueue: "Return to patient queue",
    selectPatientFirst: "Choose an encounter before matching a unit.",
    choosePatientGroup: "Patient group", chooseGroup: "Choose a group", confirmSamples: "Both independently collected samples match this recorded group",
    labNextStep: "Next verification step",
    panelProgress: "Required panel tests recorded as NEG",
    secondTypingNeeded: "A second technologist must independently confirm the ABO/Rh group.",
    typingMismatch: "The independent ABO/Rh results disagree. Stop and resolve the discrepancy; do not release.",
    releaseReady: "Required tests and two matching independent typings are recorded. Two-person release is next.",
    releaseBlocked: "Release stays blocked until every required result is NEG and two independent typings match.",
    noTypingNeeded: "Two independent ABO/Rh determinations are already recorded.",
    inventory: "On the shelf", inventoryIntro: "Select a unit. Compatibility is checked by the API.",
    bestMatch: "API FEFO suggestion", daysLeft: "days left", reserve: "Check and reserve", noStock: "No released units are available from the API.",
    hardStop: "INCOMPATIBLE — HARD STOP", apiBlocked: "The API rejected this action.",
    suggestedUnit: "Compatible alternative suggested by the API", useAlternative: "Use suggested unit", returnInventory: "Back to inventory",
    patient: "Patient", bedsideTitle: "Bedside check", bedsideIntro: "Scan the patient wristband and unit label, then confirm with the second nurse.",
    patientScan: "Scanned patient ID", unitScan: "Scanned unit ID", secondNurse: "Second nurse",
    startTransfusion: "Start transfusion", issue: "Issue unit", issuedAt: "Issued at", elapsed: "Elapsed since issue",
    transfusionStarted: "Transfusion started. The event was recorded by the API.",
    donorTitle: "Your gift, step by step", donorMessageTitle: "A message for you",
    donorMessage: "Tonight, a mother in Homa Bay held her newborn, and her family will wake together tomorrow because your gift was there when they needed help. Your kindness travelled from your arm to someone else's arms. Asante sana, Wanjiru.",
    donorThanks: "Asante sana, Wanjiru.", donorPrivate: "No test result is shown or sent to the donor in this demo.",
    donorProgress: "Donation journey", nextEligible: "Next eligible date", bookDrive: "Book my next drive",
    comingSoon: "Donation-drive booking is coming soon.",
    lightsTitle: "Stock lights", lightsIntro: "The API calculates stock lights using the figures you enter. Use facility-observed demand and lead time.",
    component: "Component", meanDailyUse: "Mean daily use (units/day)", leadDays: "Delivery lead time (days)", serviceFactor: "Service factor (z)",
    meanDailyHelp: "Average number of units issued per day for this group and component.",
    leadDaysHelp: "Observed time from placing an order until stock is available at this facility.",
    serviceFactorHelp: "Buffer multiplier (z); use an agreed planning value, not a clinical rule.",
    calculateLight: "Calculate with API", onHand: "On hand", reorderPoint: "Reorder point",
    coverage: "Expected use during protection period", enterInputs: "Enter the facility figures to request a stock light.",
    lightHowTitle: "How to read this light", lightHow: "Coverage = daily use × (lead time + 1 review day). Reorder point adds a variability buffer. Red: stock is below expected use; amber: above expected use but below reorder point; green: at or above reorder point.",
    custodyTitle: "Cold chain & custody", custodyIntro: "Follow API-recorded dispatch and receipt. This demo has no live GPS or automatic temperature feed.",
    selectUnit: "Unit", excursionDetail: "Observed excursion details", flagExcursion: "Flag excursion",
    dispatch: "Dispatch to Homa Bay", custodyRecorded: "The API recorded the custody action.",
    temperature: "Observed temperature (°C)", reportTemperature: "Report suspected excursion",
    arrival: "Scan and receive at Homa Bay", inTransit: "In transit · custody is locked",
    transitDestination: "Recorded destination", transitNoTelemetry: "No live location or sensor data is available; this is a custody state, not a vehicle tracker.",
    custodyHold: "HOLD · quality review required", delivered: "Received by Homa Bay County Hospital",
    countyTitle: "County overview", countyIntro: "Inventory counts below come from the API. Calculate a stock light with local observed figures.",
    site: "Facility", group: "Blood group", count: "Available units", lookbackTitle: "Adverse-event look-back",
    lookbackIntro: "Report an event to the API; related unit history is shown from its event ledger.",
    unitForReview: "Unit for review", eventSeverity: "Event severity", eventDetail: "Event description",
    reportEvent: "Record adverse event", eventRecorded: "Adverse event recorded by the API.",
    noFacilities: "No facility inventory is available from the API.",
    transferTitle: "Responsible AI suggestion · stock transfer",
    transferDisclosure: "Explainable rule-based decision aid; this demo has no trained ML model. It uses current API inventory and figures you enter. Nothing moves automatically.",
    transferDataNote: "Use verified facility observations in a pilot. Synthetic demo inputs must not be treated as hospital demand.",
    transferSource: "Source facility", transferTarget: "Destination facility",
    transferGroup: "Exact blood group", transferComponent: "Component",
    sourceUse: "Source mean daily use (units/day)", sourceLead: "Source delivery lead time (days)",
    targetUse: "Destination mean daily use (units/day)", targetLead: "Destination delivery lead time (days)",
    buildSuggestion: "Check stock and suggest", noRecommendation: "No safe transfer suggestion from these inputs.",
    suggestionReason: "Why this suggestion", sourceReserves: "Source stays at or above its calculated reorder point.",
    destinationNeed: "Destination is below its calculated reorder point.",
    sourceProtected: "No suggestion: transferring a unit would put the source below its reorder point.",
    noExactUnit: "No released, unexpired unit of this exact group and component is available.",
    destinationCovered: "No suggestion: the destination is at or above its calculated reorder point.",
    candidate: "Suggested unit", approveTransfer: "Approve and dispatch one unit",
    overrideTransfer: "Override this suggestion", overrideReason: "Why are you overriding? (required)",
    recordOverride: "Record override", transferApproved: "Approved. One unit is now in transit.",
    transferOverridden: "Override recorded. No unit was moved.",
    sourceLight: "Source stock light", destinationLight: "Destination stock light",
    reorderGap: "Calculated destination gap", safeSurplus: "Source surplus above reorder point",
    auditTitle: "Human decisions · tamper-evident audit",
    auditValid: "Decision audit hash chain is valid.", auditInvalid: "Decision audit hash chain is invalid.",
    noDecisionAudit: "No AI suggestions or human decisions have been recorded.",
    suggested: "Suggestion shown", approved: "Approved", overridden: "Overridden", approval_failed: "Approval failed",
    recommended: "Suggestion ready", no_recommendation: "No safe suggestion",
    unitNotMoved: "No unit is moved by an override. An approval only dispatches; destination staff must still receive and check custody.",
    resetDemo: "Load synthetic demo · keep ledger",
    close: "Close", ledgerValid: "Server ledger hash chain is valid.", ledgerInvalid: "Server ledger hash chain has a broken link.",
    noEvents: "No events have been recorded yet.", event: "Event", actor: "Actor", details: "Details",
    emptyUnits: "No units returned by the API.", networkError: "The HemoSync API is offline. Start it from the project folder with `python -m uvicorn api:app --host 127.0.0.1 --port 8000`, then refresh this page.",
    retryConnection: "Retry connection",
    manual: "Demo scenario",
  },
  sw: {
    apiConnected: "API imeunganishwa", apiOffline: "API haipatikani", record: "Rekodi",
    morning: "Habari za asubuhi", afternoon: "Habari za mchana", evening: "Habari za jioni",
    peopleTitle: "Wewe ni nani leo?", peopleIntro: "Chagua mtu. Kila mtu anaona damu ile ile kwa macho yake.",
    demoTitle: "Hadithi ya majaribio", demoDescription: "Pakia hadithi ya majaribio kupitia API uone safari ya HemoSync. Matukio yaliyopo kwenye daftari yatahifadhiwa.",
    loadDemo: "Pakia hadithi ya majaribio", demoLoaded: "Hadithi ya majaribio imepakiwa kupitia API ya HemoSync.",
    demoAlreadyLoaded: "Hadithi ya majaribio ipo kwenye daftari tayari. Hakuna historia iliyofutwa.",
    demoOnly: "Data za majaribio tu · Si kifaa cha matibabu", tryFlow: "Anza na Brian aachilie mchango wa Wanjiru, kisha Achieng.",
    home: "Nyumbani", labTitle: "Maabara: utoaji na orodha", labIntro: "Kagua vipimo vilivyorekodiwa na API na utumie uthibitisho wa watu wawili.",
    signRelease: "Achilia: Brian + Dkt. Amina", sameSigner: "Onyesho: tuma sahihi ya mtu mmoja mara mbili",
    recordLabResult: "Rekodi matokeo haya", result: "Matokeo", recordTyping: "Rekodi kundi la damu",
    typingActor: "Mtaalamu wa maabara", typingGroup: "Kundi lililopimwa",
    quarantine: "Karantini", released: "Imeachiliwa", releaseSuccess: "Utoaji wa watu wawili umerekodiwa na API.",
    queueClear: "Hakuna damu inayosubiri maabara.", samples: "Vipimo vya ABO/Rh", infectiousPanel: "Vipimo vinavyohitajika vya maambukizi",
    urgent: "Ombi la dharura", urgentDescription: "Chagua rekodi. Kundi lililorekodiwa kwenye chati ya majaribio litaonekana; lihakikishe kwa sampuli mbili huru kabla ya kulinganisha damu.",
    patientQueue: "Orodha ya wagonjwa", syntheticQueue: "Wagonjwa watano wa majaribio · hakuna taarifa za wagonjwa halisi",
    selectEncounter: "Rekodi", chooseEncounter: "Chagua rekodi",
    chartGroup: "Kundi kwenye chati ya majaribio", chartGroupNote: "Limejazwa kutoka rekodi hii ya onyesho tu. Thibitisha kundi kwa sampuli mbili huru kabla ya kulinganisha.",
    waitingForSamples: "Inasubiri uthibitisho wa sampuli huru", samplesVerified: "Sampuli mbili zimethibitishwa · tayari kulinganisha", unitReserved: "Damu imehifadhiwa",
    atBedside: "Kando ya kitanda", transfused: "Utiaji damu umeanza", returnToQueue: "Rudi kwenye orodha ya wagonjwa",
    selectPatientFirst: "Chagua rekodi kabla ya kulinganisha damu.",
    choosePatientGroup: "Kundi la mgonjwa", chooseGroup: "Chagua kundi", confirmSamples: "Sampuli zote mbili zilizochukuliwa kwa kujitegemea zinaonyesha kundi hili",
    labNextStep: "Hatua inayofuata ya uthibitisho",
    panelProgress: "Vipimo vinavyohitajika vilivyorekodiwa kuwa NEG",
    secondTypingNeeded: "Mtaalamu wa pili wa maabara lazima athibitishe kundi la ABO/Rh kwa kujitegemea.",
    typingMismatch: "Vipimo huru vya ABO/Rh havilingani. Simama na chunguza tofauti; usiachilie.",
    releaseReady: "Vipimo vinavyohitajika na vipimo viwili huru vinavyolingana vimerekodiwa. Hatua inayofuata ni idhini ya watu wawili.",
    releaseBlocked: "Utoaji utazuiwa hadi matokeo yote yanayohitajika yawe NEG na vipimo viwili huru vilingane.",
    noTypingNeeded: "Vipimo viwili huru vya ABO/Rh tayari vimerekodiwa.",
    inventory: "Damu iliyo tayari", inventoryIntro: "Chagua damu. API hukagua ulinganifu.",
    bestMatch: "Pendekezo la FEFO kutoka API", daysLeft: "siku zimebaki", reserve: "Kagua na hifadhi",
    noStock: "Hakuna damu iliyoachiliwa iliyopatikana kwenye API.", hardStop: "HAIENDANI — IMEZUIWA",
    apiBlocked: "API imekataa hatua hii.", suggestedUnit: "Damu mbadala inayofaa iliyopendekezwa na API",
    useAlternative: "Tumia damu iliyopendekezwa", returnInventory: "Rudi kwenye orodha", patient: "Mgonjwa",
    bedsideTitle: "Ukaguzi wa kando ya kitanda", bedsideIntro: "Changanua bangili ya mgonjwa na lebo ya mfuko, kisha muuguzi wa pili athibitishe.",
    patientScan: "Namba ya mgonjwa iliyochanganuliwa", unitScan: "Namba ya mfuko iliyochanganuliwa", secondNurse: "Muuguzi wa pili",
    startTransfusion: "Anza utiaji damu", issue: "Toa damu", issuedAt: "Ilitolewa saa", elapsed: "Muda tangu kutolewa",
    transfusionStarted: "Utiaji damu umeanza. Tukio limerekodiwa na API.",
    donorTitle: "Mchango wako, hatua kwa hatua", donorMessageTitle: "Ujumbe kwako",
    donorMessage: "Usiku huu, mama mmoja wa Homa Bay alimshika mtoto wake mchanga, na kesho familia yake itaamka pamoja kwa sababu mchango wako ulikuwa hapo walipohitaji msaada. Wema wako ulisafiri kutoka kwako hadi kwenye mikono yake. Asante sana, Wanjiru.",
    donorThanks: "Asante sana, Wanjiru.", donorPrivate: "Matokeo ya vipimo hayaonyeshwi wala kutumwa kwa mchangiaji kwenye onyesho hili.",
    donorProgress: "Safari ya mchango", nextEligible: "Tarehe inayofuata ya kustahili", bookDrive: "Weka nafasi ya zoezi lijalo",
    comingSoon: "Uwekaji nafasi wa zoezi la uchangiaji unakuja.",
    lightsTitle: "Taa za akiba", lightsIntro: "API hukokotoa hali ya akiba kwa takwimu unazoingiza. Tumia matumizi na muda halisi wa kituo.",
    component: "Sehemu ya damu", meanDailyUse: "Matumizi ya wastani kwa siku (mifuko)", leadDays: "Muda wa kuwasili (siku)",
    serviceFactor: "Kiwango cha huduma (z)", calculateLight: "Kokotoa kupitia API", onHand: "Iliyopo",
    meanDailyHelp: "Wastani wa mifuko ya kundi na sehemu hii inayotolewa kwa siku.",
    leadDaysHelp: "Muda unaoonekana kutoka kuweka oda hadi akiba ipatikane kwenye kituo hiki.",
    serviceFactorHelp: "Kizidishi cha akiba ya tofauti (z); tumia thamani ya mpango iliyokubaliwa, si kanuni ya kitabibu.",
    reorderPoint: "Kiwango cha kuagiza", coverage: "Matumizi yanayotarajiwa katika kipindi cha ulinzi",
    enterInputs: "Ingiza takwimu za kituo ili kuomba taa ya akiba.",
    lightHowTitle: "Jinsi ya kusoma hali hii", lightHow: "Ufunikaji = matumizi ya kila siku × (muda wa kuwasili + siku 1 ya ukaguzi). Kiwango cha kuagiza huongeza akiba ya tofauti. Nyekundu: chini ya matumizi yanayotarajiwa; njano: juu ya matumizi yanayotarajiwa lakini chini ya kiwango cha kuagiza; kijani: kwenye au juu ya kiwango cha kuagiza.",
    custodyTitle: "Mnyororo wa baridi na uangalizi", custodyIntro: "Fuatilia utumaji na upokeaji uliorekodiwa na API. Onyesho hili halina GPS ya moja kwa moja wala data ya joto ya kiotomatiki.",
    selectUnit: "Damu", excursionDetail: "Maelezo ya tatizo lililoonekana", flagExcursion: "Weka alama ya tatizo",
    dispatch: "Tuma Homa Bay", custodyRecorded: "API imerekodi hatua ya uangalizi.",
    temperature: "Joto lililoonekana (°C)", reportTemperature: "Ripoti tatizo linaloshukiwa",
    arrival: "Changanua na pokea Homa Bay", inTransit: "Njiani · uangalizi umefungwa",
    transitDestination: "Mahali pa kupelekwa paliporekodiwa", transitNoTelemetry: "Hakuna eneo la moja kwa moja wala data ya kihisi; hii ni hali ya uangalizi, si kifuatiliaji cha gari.",
    custodyHold: "HOLD · ukaguzi wa ubora unahitajika", delivered: "Imepokelewa na Hospitali ya Kaunti ya Homa Bay",
    countyTitle: "Muhtasari wa kaunti", countyIntro: "Idadi hapa imetoka kwa API. Kokotoa taa ya akiba kwa takwimu za kituo.",
    site: "Kituo", group: "Kundi la damu", count: "Mifuko inayopatikana", lookbackTitle: "Ufuatiliaji wa tukio",
    lookbackIntro: "Ripoti tukio kwa API; historia ya mfuko inaonyeshwa kutoka kwenye daftari lake.",
    unitForReview: "Mfuko wa kukaguliwa", eventSeverity: "Ukali wa tukio", eventDetail: "Maelezo ya tukio",
    reportEvent: "Rekodi tukio lisilotarajiwa", eventRecorded: "Tukio lisilotarajiwa limerekodiwa na API.",
    noFacilities: "Hakuna orodha ya vituo kutoka API.",
    transferTitle: "Pendekezo la AI inayowajibika · uhamisho wa damu",
    transferDisclosure: "Msaada wa maamuzi unaoelezeka kwa kanuni; onyesho hili halina modeli ya ML iliyofunzwa. Hutumia akiba ya sasa ya API na takwimu unazoingiza. Hakuna kinachosafirishwa chenyewe.",
    transferDataNote: "Tumia takwimu zilizothibitishwa za kituo kwenye majaribio halisi. Takwimu za onyesho ni za kubuni, si matumizi halisi ya hospitali.",
    transferSource: "Kituo cha chanzo", transferTarget: "Kituo kinachopokea",
    transferGroup: "Kundi halisi la damu", transferComponent: "Sehemu ya damu",
    sourceUse: "Matumizi ya wastani ya chanzo kwa siku (mifuko)", sourceLead: "Muda wa kuwasili wa chanzo (siku)",
    targetUse: "Matumizi ya wastani ya mpokeaji kwa siku (mifuko)", targetLead: "Muda wa kuwasili wa mpokeaji (siku)",
    buildSuggestion: "Kagua akiba na pendekeza", noRecommendation: "Hakuna pendekezo salama la uhamisho kwa takwimu hizi.",
    suggestionReason: "Sababu ya pendekezo", sourceReserves: "Chanzo kitabaki kwenye au juu ya kiwango chake cha kuagiza.",
    destinationNeed: "Kituo kinachopokea kiko chini ya kiwango chake cha kuagiza.",
    sourceProtected: "Hakuna pendekezo: kuhamisha mfuko kutashusha chanzo chini ya kiwango chake cha kuagiza.",
    noExactUnit: "Hakuna mfuko ulioachiliwa, muda wake haujaisha, wa kundi na sehemu hii haswa.",
    destinationCovered: "Hakuna pendekezo: kituo kinachopokea kiko kwenye au juu ya kiwango chake cha kuagiza.",
    candidate: "Mfuko unaopendekezwa", approveTransfer: "Idhinisha na tuma mfuko mmoja",
    overrideTransfer: "Kataa pendekezo hili", overrideReason: "Kwa nini unakataa pendekezo? (inahitajika)",
    recordOverride: "Rekodi kukataa", transferApproved: "Imeidhinishwa. Mfuko mmoja uko safarini.",
    transferOverridden: "Kukataa kumerekodiwa. Hakuna mfuko uliohamishwa.",
    sourceLight: "Hali ya akiba ya chanzo", destinationLight: "Hali ya akiba ya mpokeaji",
    reorderGap: "Pengo hadi kiwango cha kuagiza", safeSurplus: "Ziada ya chanzo juu ya kiwango cha kuagiza",
    auditTitle: "Maamuzi ya watu · rekodi inayotambua mabadiliko",
    auditValid: "Mnyororo wa rekodi ya maamuzi ni sahihi.", auditInvalid: "Mnyororo wa rekodi ya maamuzi una hitilafu.",
    noDecisionAudit: "Hakuna mapendekezo ya AI au maamuzi ya watu yaliyorekodiwa.",
    suggested: "Pendekezo limeonyeshwa", approved: "Imeidhinishwa", overridden: "Imekataliwa", approval_failed: "Idhini imeshindwa",
    recommended: "Pendekezo liko tayari", no_recommendation: "Hakuna pendekezo salama",
    reasonOther: "Sababu", unitNotMoved: "Kukataa hakuhamishi damu. Idhini hutuma tu; wafanyakazi wa kituo kinachopokea bado wanapaswa kupokea na kukagua uangalizi.",
    resetDemo: "Pakia onyesho · hifadhi daftari",
    close: "Funga", ledgerValid: "Mnyororo wa hash wa daftari la seva ni sahihi.", ledgerInvalid: "Mnyororo wa hash wa daftari la seva una hitilafu.",
    noEvents: "Hakuna matukio yaliyorekodiwa bado.", event: "Tukio", actor: "Aliyetenda", details: "Maelezo",
    emptyUnits: "API haijarejesha damu yoyote.", networkError: "HemoSync API haipatikani. Iwashe kwenye folda ya mradi kwa `python -m uvicorn api:app --host 127.0.0.1 --port 8000`, kisha onyesha upya ukurasa huu.",
    retryConnection: "Jaribu kuunganisha tena",
    manual: "Hadithi ya majaribio",
  },
};

const people = [
  { id: "wanjiru", initials: "WK", name: "Wanjiru", title: { en: "Donor, 19", sw: "Mchangiaji, miaka 19" }, quote: { en: "“I gave in March. Nobody told me where it went.”", sw: "“Nilitoa damu Machi. Hakuna aliyeniambia ilienda wapi.”" }, color: "#C8102E" },
  { id: "achieng", initials: "AO", name: "Achieng", title: { en: "Maternity nurse · night shift", sw: "Muuguzi wa uzazi · zamu ya usiku" }, quote: { en: "“At 2 a.m. I am the nurse, the courier and the blood bank.”", sw: "“Saa nane usiku mimi ni muuguzi, msafirishaji na benki ya damu.”" }, color: "#6B0F2A" },
  { id: "brian", initials: "BM", name: "Brian", title: { en: "Lab technologist", sw: "Mtaalamu wa maabara" }, quote: { en: "“I trust the register. I cannot always trust my tired eyes.”", sw: "“Naamini rejista. Siwezi kila mara kuamini macho yangu yaliyochoka.”" }, color: "#0B7A6B" },
  { id: "mercy", initials: "SM", name: "Sister Mercy", title: { en: "Blood bank manager", sw: "Meneja wa benki ya damu" }, quote: { en: "“I order when I am afraid, not when the numbers say so.”", sw: "“Naagiza ninapoogopa, si pale takwimu zinaposema.”" }, color: "#2F6FB7" },
  { id: "hassan", initials: "HA", name: "Hassan", title: { en: "Rider", sw: "Msafirishaji" }, quote: { en: "“If the box warms up, the blame is mine, with no proof.”", sw: "“Kisanduku kikipata joto, lawama ni zangu, bila ushahidi.”" }, color: "#B8790A" },
  { id: "njeri", initials: "NK", name: "Dr. Njeri", title: { en: "County health director", sw: "Mkurugenzi wa afya wa kaunti" }, quote: { en: "“I find out about shortages from social media.”", sw: "“Nasikia kuhusu uhaba kwenye mitandao ya kijamii.”" }, color: "#6A4FB3" },
];

const state = {
  lang: "en", theme: "auto", screen: "people", role: null, units: [], policy: null,
  online: false, selectedDin: null, patientId: "", patientGroup: "", twoSamplesConfirmed: false,
  error: "", stop: null, alternative: null, fefoSuggestion: null, stockLight: null, ledger: null, sites: [], targetUnits: [], encounters: [],
  transferSuggestion: null, transferDecision: null, transferDecisionAudit: null,
  installPrompt: null, canInstall: false, isInstalled: false,
};

const t = (key) => copy[state.lang][key] ?? copy.en[key] ?? key;
const greeting = () => {
  const hour = new Date().getHours();
  return t(hour < 12 ? "morning" : hour < 17 ? "afternoon" : "evening");
};
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;",
}[char]));
const person = () => people.find((item) => item.id === state.role);
const storyUnit = () => state.units.find((unit) => unit.din === STORY_UNIT_ID);
const selectedUnit = () => state.units.find((unit) => unit.din === state.selectedDin);
const activeUnit = () => {
  const selected = selectedUnit();
  if (selected && ["ISSUED", "RESERVED"].includes(selected.state)) return selected;
  return state.units.find((unit) => unit.state === "ISSUED")
    ?? state.units.find((unit) => unit.state === "RESERVED");
};
const formatDate = (value) => value ? new Date(value).toLocaleString(state.lang === "sw" ? "sw-KE" : "en-KE") : "—";
const formatDay = (value) => value ? new Date(value).toLocaleDateString(state.lang === "sw" ? "sw-KE" : "en-KE") : "—";

class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch (error) {
    state.online = false;
    renderHeader();
    throw new ApiError(t("networkError"), 0);
  }
  const data = (response.headers.get("content-type") ?? "").includes("application/json")
    ? await response.json() : null;
  if (!response.ok) throw new ApiError(data?.detail ?? `HTTP ${response.status}`, response.status);
  state.online = true;
  return data;
}

async function refresh() {
  const [, units, policy, sites, encounters] = await Promise.all([
    request("/health"), request("/units"), request("/policy"), request("/sites/inventory"), request("/demo/encounters"),
  ]);
  state.units = units.units;
  state.policy = policy;
  state.sites = sites.sites;
  state.encounters = encounters.encounters;
  renderHeader();
}

async function refreshTransferAudit() {
  state.transferDecisionAudit = await request("/decision-support/audit");
}

function renderHeader() {
  const header = document.querySelector("#topbar");
  const installButton = state.canInstall && !state.isInstalled
    ? `<button class="button secondary small" data-action="install-pwa">Install</button>`
    : "";
  header.innerHTML = `<button class="brand-mark" data-action="people" aria-label="HemoSync · choose person"><svg class="drop-icon" width="28" height="34" viewBox="0 0 32 40" aria-hidden="true"><path d="M16 2C16 2 4 17 4 25a12 12 0 0 0 24 0C28 17 16 2 16 2Z" fill="currentColor"/></svg><span>HemoSync</span></button>
    <span class="api-state ${state.online ? "online" : "offline"}">${escapeHtml(t(state.online ? "apiConnected" : "apiOffline"))}</span>
    <div class="header-actions">
      ${installButton}
      <button class="icon-button" data-action="ledger" aria-label="${escapeHtml(t("record"))}" title="${escapeHtml(t("record"))}">≡</button>
      <button class="language-button" data-action="language" aria-label="Change language">${state.lang === "en" ? "SW" : "EN"}</button>
      <button class="icon-button" data-action="theme" aria-label="Toggle color theme" title="Theme">${state.theme === "dark" ? "☀" : "☾"}</button>
    </div>`;
}

function renderFooter() {
  document.querySelector("#footer").innerHTML = `<div class="footer">${escapeHtml(t("demoOnly"))}${state.isInstalled ? " · PWA installed" : " · Installable demo shell"}</div>`;
}

function showToast(message) {
  const root = document.querySelector("#toast-root");
  root.innerHTML = `<div class="toast">${escapeHtml(message)}</div>`;
  window.setTimeout(() => { root.innerHTML = ""; }, 4000);
}

function errorBanner() {
  return state.error ? `<div class="message error" role="alert">${escapeHtml(state.error)}
    ${!state.online ? `<button class="button secondary small" data-action="retry-api">${escapeHtml(t("retryConnection"))}</button>` : ""}</div>` : "";
}

function pickerScreen() {
  return `<section class="screen-enter">
    <p class="eyebrow">${escapeHtml(greeting())}</p><h1>${escapeHtml(t("peopleTitle"))}</h1>
    <p class="sub">${escapeHtml(t("peopleIntro"))}</p>
    ${state.units.length === 0 ? `<article class="card"><div class="card-title"><h2>${escapeHtml(t("demoTitle"))}</h2><span class="chip violet">API</span></div>
      <p class="muted">${escapeHtml(t("demoDescription"))}</p><button class="button" data-action="demo-reset">${escapeHtml(t("loadDemo"))}</button></article>`
      : `<div class="message">${escapeHtml(t("tryFlow"))}</div><button class="button secondary" data-action="demo-reset">${escapeHtml(t("resetDemo"))}</button>`}
    ${errorBanner()}
    <div class="role-list">${people.map((item) => `<button class="card role-card" data-action="select-role" data-role="${item.id}">
      <span class="avatar" style="background:${item.color}">${item.initials}</span><span><strong>${escapeHtml(item.name)}</strong>
      <small>${escapeHtml(item.title[state.lang])}</small><span class="quote">${escapeHtml(item.quote[state.lang])}</span></span></button>`).join("")}</div>
  </section>`;
}

function unitStatus(unit) {
  const labels = {
    QUARANTINE: t("quarantine"), RELEASED: t("released"),
    RESERVED: state.lang === "sw" ? "Imehifadhiwa" : "Reserved",
    ISSUED: state.lang === "sw" ? "Imetolewa" : "Issued",
    TRANSFUSED: state.lang === "sw" ? "Imetiwa mgonjwa" : "Transfused",
    HOLD: state.lang === "sw" ? "Imesimamishwa" : "On hold",
    IN_TRANSIT: state.lang === "sw" ? "Njiani" : "In transit",
    DISCARDED: state.lang === "sw" ? "Imetupwa" : "Discarded",
    EXPIRED: state.lang === "sw" ? "Muda umeisha" : "Expired",
  };
  return labels[unit.state] ?? unit.state;
}

function unitRows(units, interactive = false, suggestedDin = null, canReserve = true) {
  if (!units.length) return `<div class="empty">${escapeHtml(t("emptyUnits"))}</div>`;
  return units.map((unit) => {
    const expires = Math.max(0, Math.ceil((new Date(unit.expires) - Date.now()) / 86400000));
    return `<button class="card unit-card" ${interactive ? `data-action="reserve" data-din="${escapeHtml(unit.din)}" ${canReserve ? "" : "disabled"}` : "disabled"}>
      <span class="blood-group">${escapeHtml(unit.abo_rh)}</span>
      <span class="unit-detail"><strong>…${escapeHtml(unit.din.slice(-4))} · ${escapeHtml(unit.component)}</strong>
        <small>${escapeHtml(unitStatus(unit))} · ${escapeHtml(formatDay(unit.collected))} → ${escapeHtml(formatDay(unit.expires))} · ${escapeHtml(t("daysLeft"))}: ${expires}</small></span>
      <span class="chip ${unit.din === suggestedDin ? "good" : unit.state === "RELEASED" ? "good" : ""}">${escapeHtml(unit.din === suggestedDin ? t("bestMatch") : unitStatus(unit))}</span></button>`;
  }).join("");
}

function releaseScreen() {
  const unit = storyUnit();
  if (!unit) return `<section class="screen-enter"><h1>${escapeHtml(t("labTitle"))}</h1><p class="sub">${escapeHtml(t("labIntro"))}</p>${errorBanner()}<div class="empty">${escapeHtml(t("emptyUnits"))}</div></section>`;
  const markers = state.policy?.required_markers ?? [];
  const rows = markers.map((marker) => {
    const result = unit.tests?.[marker] ?? (state.lang === "sw" ? "Inasubiri" : "Pending");
    return `<form class="row lab-result" data-form="record-test" data-marker="${escapeHtml(marker)}">
      <span class="status-dot ${result === "NEG" ? "good" : result === "REACTIVE" ? "bad" : ""}">${result === "NEG" ? "✓" : result === "REACTIVE" ? "!" : "…"}</span>
      <span class="row-label"><strong>${escapeHtml(marker)}</strong><small>${escapeHtml(t("infectiousPanel"))} · ${escapeHtml(result)}</small></span>
      <select name="result" aria-label="${escapeHtml(t("result"))} for ${escapeHtml(marker)}" required>
        <option value="" disabled ${unit.tests?.[marker] ? "" : "selected"}>${state.lang === "sw" ? "Chagua matokeo" : "Choose a result"}</option>
        ${["NEG", "REACTIVE", "INDETERMINATE"].map((value) => `<option value="${value}" ${value === unit.tests?.[marker] ? "selected" : ""}>${value}</option>`).join("")}
      </select><button class="button small" type="submit">${escapeHtml(t("recordLabResult"))}</button></form>`;
  }).join("");
  const typings = unit.typings ?? [];
  const typingActors = unit.typing_actors ?? [];
  const passedMarkers = markers.filter((marker) => unit.tests?.[marker] === "NEG").length;
  const testsComplete = markers.every((marker) => unit.tests?.[marker] === "NEG");
  const typingsMatch = typings.length >= 2 && new Set(typings).size === 1 && typings[0] === unit.abo_rh;
  const labStep = !testsComplete ? "releaseBlocked"
    : typings.length < 2 ? "secondTypingNeeded"
      : !typingsMatch ? "typingMismatch" : "releaseReady";
  const availableTypists = [
    { id: "tech.brian", name: "Brian" },
    { id: "tech.amina", name: "Dr. Amina" },
  ].filter((technologist) => !typingActors.includes(technologist.id));
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("labTitle"))}</h1>
    <p class="sub">${escapeHtml(t("labIntro"))}</p>${errorBanner()}
    ${unit.state === "QUARANTINE" ? `<article class="card"><div class="card-title"><h2>Unit …${escapeHtml(unit.din.slice(-4))} · RBC · ${escapeHtml(unit.abo_rh)}</h2><span class="chip">${escapeHtml(t("quarantine"))}</span></div>
      <p class="muted">Synthetic donor · ${escapeHtml(formatDate(unit.collected))}</p>
      <div class="message ${labStep === "typingMismatch" ? "error" : ""}"><strong>${escapeHtml(t("labNextStep"))}</strong><br>${escapeHtml(t(labStep))}
        <br><small>${escapeHtml(t("panelProgress"))}: ${passedMarkers}/${markers.length}</small></div>
      <h3>${escapeHtml(t("infectiousPanel"))}</h3>${rows}
      <h3>${escapeHtml(t("samples"))}</h3>${typings.map((typing, index) => `<div class="row"><span class="status-dot ${typing === unit.abo_rh ? "good" : "bad"}">${typing === unit.abo_rh ? "✓" : "!"}</span><span class="row-label"><strong>${escapeHtml(t("typingGroup"))} ${index + 1}</strong><small>${escapeHtml(typing)} · ${escapeHtml(unit.typing_actors?.[index] ?? "")}</small></span></div>`).join("")}
      ${availableTypists.length ? `<form class="typing-form" data-form="record-typing">
        <div class="field"><label>${escapeHtml(t("typingGroup"))}</label><select name="abo_rh">${BLOOD_GROUPS.map((group) => `<option value="${group}" ${group === unit.abo_rh ? "selected" : ""}>${group}</option>`).join("")}</select></div>
        <div class="field"><label>${escapeHtml(t("typingActor"))}</label><select name="actor">${availableTypists.map((technologist) => `<option value="${technologist.id}">${escapeHtml(technologist.name)}</option>`).join("")}</select></div>
        <button class="button secondary" type="submit">${escapeHtml(t("recordTyping"))}</button>
      </form>` : `<p class="muted">${escapeHtml(t("noTypingNeeded"))}</p>`}</article>
      <article class="card"><h3>${escapeHtml(t("signRelease"))}</h3><p class="muted">${state.lang === "sw" ? "Watu wawili tofauti lazima waidhinishe. API itakataa mtu mmoja mara mbili." : "Two different people must authorize release. The API will reject one person signing twice."}</p>
      <button class="button success" data-action="release" ${testsComplete && typingsMatch ? "" : "disabled"}>${escapeHtml(t("signRelease"))}</button>
      ${testsComplete && typingsMatch ? `<button class="button secondary" data-action="same-signer">${escapeHtml(t("sameSigner"))}</button>` : ""}</article>`
      : `<div class="message">${escapeHtml(t("queueClear"))} ${escapeHtml(unitStatus(unit))} · …${escapeHtml(unit.din.slice(-4))}</div>`}
    <h2>${escapeHtml(t("inventory"))}</h2>${unitRows(state.units)}</section>`;
}

function urgentScreen() {
  const released = state.units.filter((unit) => unit.state === "RELEASED");
  const encounters = state.encounters.map((encounter) => {
    const linkedUnit = state.units.find((unit) => unit.reserved_for === encounter.id
      && ["RESERVED", "ISSUED", "TRANSFUSED"].includes(unit.state));
    const status = linkedUnit?.state === "RESERVED" ? t("unitReserved")
      : linkedUnit?.state === "ISSUED" ? t("atBedside")
        : linkedUnit?.state === "TRANSFUSED" ? t("transfused")
          : encounter.id === state.patientId && state.twoSamplesConfirmed ? t("samplesVerified") : t("waitingForSamples");
    return `<button class="card queue-row" aria-pressed="${encounter.id === state.patientId}" data-action="select-encounter" data-patient-id="${encounter.id}">
      <span class="queue-bed">${state.lang === "sw" ? "Kitanda" : "Bed"} ${encounter.bed}</span>
      <span class="unit-detail"><strong>${escapeHtml(encounter.id)} · ${escapeHtml(encounter.blood_group)}</strong><small>${escapeHtml(status)}${linkedUnit ? ` · …${escapeHtml(linkedUnit.din.slice(-4))}` : ""}</small></span>
    </button>`;
  }).join("");
  const selectedEncounter = state.encounters.find((encounter) => encounter.id === state.patientId);
  const patientAlreadyMatched = state.units.some((unit) => unit.reserved_for === state.patientId
    && ["RESERVED", "ISSUED", "TRANSFUSED"].includes(unit.state));
  const canReserve = Boolean(selectedEncounter && state.patientGroup && state.twoSamplesConfirmed && !patientAlreadyMatched);
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("urgent"))}</h1>
    <p class="sub">${escapeHtml(t("urgentDescription"))}</p>${errorBanner()}<article class="card">
      <div class="card-title"><h2>${escapeHtml(t("patientQueue"))}</h2><span class="chip violet">5</span></div>
      <p class="muted">${escapeHtml(t("syntheticQueue"))}</p>${encounters}
    </article><article class="card">
      <div class="field"><label for="encounter-select">${escapeHtml(t("selectEncounter"))}</label>
      <select id="encounter-select" aria-label="${escapeHtml(t("selectEncounter"))}">
        <option value="">${escapeHtml(t("chooseEncounter"))}</option>
        ${state.encounters.map((encounter) => `<option value="${encounter.id}" ${encounter.id === state.patientId ? "selected" : ""}>${state.lang === "sw" ? "Kitanda" : "Bed"} ${encounter.bed} · ${encounter.id}</option>`).join("")}
      </select></div>
      ${selectedEncounter ? `<div class="message"><strong>${escapeHtml(t("chartGroup"))}: ${escapeHtml(selectedEncounter.blood_group)}</strong><br><small>${escapeHtml(t("chartGroupNote"))}</small></div>
      <label class="check-row"><input type="checkbox" id="samples-confirmed" ${state.twoSamplesConfirmed ? "checked" : ""}><span>${escapeHtml(t("confirmSamples"))}</span></label>` : ""}
      ${patientAlreadyMatched ? `<p class="message">${escapeHtml(t("unitReserved"))}</p>` : !canReserve ? `<p class="message">${escapeHtml(t("waitingForSamples"))}</p>` : ""}
      <h2>${escapeHtml(t("inventory"))}</h2><p class="muted">${escapeHtml(t("inventoryIntro"))}</p></article>
    ${unitRows(released, true, state.fefoSuggestion?.din, canReserve)}</section>`;
}

function bedsideScreen() {
  const unit = activeUnit();
  if (!unit) return `<section class="screen-enter"><h1>${escapeHtml(t("bedsideTitle"))}</h1><p class="sub">${escapeHtml(t("bedsideIntro"))}</p>${errorBanner()}<div class="empty">${escapeHtml(t("emptyUnits"))}</div></section>`;
  const activeMatches = state.units.filter((item) => ["RESERVED", "ISSUED"].includes(item.state));
  const issued = unit.state === "ISSUED";
  const form = `<form data-form="transfuse"><div class="field"><label for="scanned-patient">${escapeHtml(t("patientScan"))}</label>
    <input id="scanned-patient" name="scanned_patient" value="${escapeHtml(unit.reserved_for ?? "")}" required></div>
    <div class="field"><label for="scanned-unit">${escapeHtml(t("unitScan"))}</label><input id="scanned-unit" name="scanned_unit" value="${escapeHtml(unit.din)}" required></div>
    <div class="field"><label for="nurse-two">${escapeHtml(t("secondNurse"))}</label><select id="nurse-two" name="nurse2">
      <option value="nurse.mercy">Sister Mercy</option><option value="nurse.other">Another nurse</option></select></div>
    <button class="button success" type="submit">${escapeHtml(t("startTransfusion"))}</button></form>`;
  const seconds = unit.issued_at ? Math.max(0, Math.floor((Date.now() - new Date(unit.issued_at).getTime()) / 1000)) : 0;
  const elapsed = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("bedsideTitle"))}</h1>
    <p class="sub">${escapeHtml(t("bedsideIntro"))}</p>${errorBanner()}
    ${activeMatches.length > 1 ? `<article class="card"><h2>${escapeHtml(t("patientQueue"))}</h2>${activeMatches.map((item) => `<button class="card queue-row" data-action="select-bedside-unit" data-din="${escapeHtml(item.din)}">
      <span class="queue-bed">${escapeHtml(item.reserved_for ?? "")}</span><span class="unit-detail"><strong>…${escapeHtml(item.din.slice(-4))}</strong><small>${escapeHtml(unitStatus(item))}</small></span></button>`).join("")}</article>` : ""}
    <article class="card">
    <div class="card-title"><h2>Unit …${escapeHtml(unit.din.slice(-4))} · ${escapeHtml(unit.abo_rh)}</h2><span class="chip">${escapeHtml(unitStatus(unit))}</span></div>
    <div class="row"><span class="status-dot good">✓</span><span class="row-label"><strong>${escapeHtml(t("patient"))}: ${escapeHtml(unit.reserved_for ?? "—")}</strong><small>${escapeHtml(t("issuedAt"))}: ${escapeHtml(formatDate(unit.issued_at))}</small></span></div>
    ${issued ? `<p class="muted">${escapeHtml(t("elapsed"))}: <span id="elapsed-timer">${elapsed}</span></p>${form}` : `<button class="button" data-action="issue" data-din="${escapeHtml(unit.din)}">${escapeHtml(t("issue"))}</button>`}
    </article></section>`;
}

function donorScreen() {
  const unit = storyUnit();
  const events = state.ledger?.events?.filter((event) => event.unit_id === STORY_UNIT_ID) ?? [];
  const transferred = unit?.state === "TRANSFUSED";
  const journey = [
    { key: "UnitCollected", en: "Collected", sw: "Imekusanywa" },
    { key: "TestResultRecorded", en: "Tests recorded", sw: "Vipimo vimerekodiwa" },
    { key: "UnitReleased", en: "Released", sw: "Imeachiliwa" },
    { key: "TransfusionStarted", en: "Transfusion started", sw: "Utiaji damu umeanza" },
  ];
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("donorTitle"))}</h1>
    <p class="sub">${escapeHtml(t("donorProgress"))}</p>${errorBanner()}
    ${transferred ? `<article class="card" style="background:linear-gradient(155deg,var(--brand),var(--crimson));color:white">
      <p class="eyebrow" style="color:white">${escapeHtml(t("donorMessageTitle"))}</p><h2>${escapeHtml(t("donorMessage"))}</h2>
      <p><strong>${escapeHtml(t("donorThanks"))}</strong></p></article>`
      : `<div class="message">${state.lang === "sw" ? "Mchango wako unaendelea kufuatiliwa. Ujumbe utaonekana baada ya API kurekodi utiaji damu." : "Your donation is being tracked. The message appears after the API records transfusion."}</div>`}
    <article class="card">${journey.map((step) => {
      const complete = events.some((event) => event.etype === step.key);
      return `<div class="row"><span class="status-dot ${complete ? "good" : ""}">${complete ? "✓" : "…"}</span><span class="row-label"><strong>${escapeHtml(step[state.lang])}</strong></span></div>`;
    }).join("")}</article>
    <article class="card"><strong>${escapeHtml(t("nextEligible"))}: 12 Jan</strong><p class="muted">${escapeHtml(t("donorPrivate"))}</p>
    <button class="button" data-action="booking">${escapeHtml(t("bookDrive"))}</button></article></section>`;
}

function lightsForm() {
  return `<form data-form="stock-light" class="card">
    <div class="field"><label for="light-group">${escapeHtml(t("choosePatientGroup"))}</label><select id="light-group" name="group">${BLOOD_GROUPS.map((group) => `<option value="${group}">${group}</option>`).join("")}</select></div>
    <div class="field"><label for="light-component">${escapeHtml(t("component"))}</label><select id="light-component" name="component"><option>RBC</option><option>PLT</option><option>FFP</option></select></div>
    <div class="field"><label for="daily-use">${escapeHtml(t("meanDailyUse"))}</label><input id="daily-use" name="mean_daily_use" type="number" min="0" step="0.1" required><small class="field-help">${escapeHtml(t("meanDailyHelp"))}</small></div>
    <div class="field"><label for="lead-days">${escapeHtml(t("leadDays"))}</label><input id="lead-days" name="lead_days" type="number" min="0" step="0.1" required><small class="field-help">${escapeHtml(t("leadDaysHelp"))}</small></div>
    <div class="field"><label for="service-factor">${escapeHtml(t("serviceFactor"))}</label><input id="service-factor" name="z" type="number" min="0" step="0.01" value="1.96" required><small class="field-help">${escapeHtml(t("serviceFactorHelp"))}</small></div>
    <button class="button violet" type="submit">${escapeHtml(t("calculateLight"))}</button></form>`;
}

function stockLightCard() {
  const result = state.stockLight;
  if (!result) return `<article class="card muted">${escapeHtml(t("enterInputs"))}</article>`;
  const color = result.colour === "GREEN" ? "good" : result.colour === "RED" ? "bad" : "";
  return `<article class="card"><div class="card-title"><h2>${escapeHtml(result.group)} · ${escapeHtml(result.component)}</h2><span class="chip ${color}">${escapeHtml(result.colour)}</span></div>
    <div class="row"><span class="row-label"><strong>${escapeHtml(t("onHand"))}</strong></span><strong>${escapeHtml(result.on_hand)}</strong></div>
    <div class="row"><span class="row-label"><strong>${escapeHtml(t("coverage"))}</strong></span><strong>${Number(result.cover).toFixed(2)}</strong></div>
    <div class="row"><span class="row-label"><strong>${escapeHtml(t("reorderPoint"))}</strong></span><strong>${Number(result.reorder_point).toFixed(2)}</strong></div>
    <details><summary>${escapeHtml(t("lightHowTitle"))}</summary><p class="field-help">${escapeHtml(t("lightHow"))}</p></details></article>`;
}

function transferSuggestionForm() {
  const sites = state.sites ?? [];
  const source = sites.find((site) => Object.keys(site.on_hand).length > 0)?.site ?? sites[0]?.site ?? "";
  const target = sites.find((site) => site.site !== source)?.site ?? "";
  return `<form data-form="transfer-suggestion" class="card">
    <div class="field"><label for="transfer-source">${escapeHtml(t("transferSource"))}</label>
      <select id="transfer-source" name="from_site" required>${sites.map((site) => `<option value="${escapeHtml(site.site)}" ${site.site === source ? "selected" : ""}>${escapeHtml(site.site)}</option>`).join("")}</select></div>
    <div class="field"><label for="transfer-target">${escapeHtml(t("transferTarget"))}</label>
      <select id="transfer-target" name="to_site" required>${sites.filter((site) => site.site !== source).map((site) => `<option value="${escapeHtml(site.site)}" ${site.site === target ? "selected" : ""}>${escapeHtml(site.site)}</option>`).join("")}</select></div>
    <div class="field"><label for="transfer-component">${escapeHtml(t("transferComponent"))}</label>
      <select id="transfer-component" name="component"><option>RBC</option><option>PLT</option><option>FFP</option></select></div>
    <div class="field"><label for="transfer-group">${escapeHtml(t("transferGroup"))}</label>
      <select id="transfer-group" name="group" required><option value="">${escapeHtml(t("chooseGroup"))}</option>${BLOOD_GROUPS.map((group) => `<option value="${group}">${group}</option>`).join("")}</select></div>
    <div class="field"><label for="source-use">${escapeHtml(t("sourceUse"))}</label><input id="source-use" name="source_mean_daily_use" type="number" min="0" step="0.1" required></div>
    <div class="field"><label for="source-lead">${escapeHtml(t("sourceLead"))}</label><input id="source-lead" name="source_lead_days" type="number" min="0" step="0.1" required></div>
    <div class="field"><label for="target-use">${escapeHtml(t("targetUse"))}</label><input id="target-use" name="target_mean_daily_use" type="number" min="0" step="0.1" required></div>
    <div class="field"><label for="target-lead">${escapeHtml(t("targetLead"))}</label><input id="target-lead" name="target_lead_days" type="number" min="0" step="0.1" required></div>
    <div class="field"><label for="transfer-z">${escapeHtml(t("serviceFactor"))}</label><input id="transfer-z" name="z" type="number" min="0.01" step="0.01" value="1.96" required></div>
    <small class="field-help">${escapeHtml(t("transferDataNote"))}</small>
    <button class="button violet" type="submit">${escapeHtml(t("buildSuggestion"))}</button>
  </form>`;
}

function transferReason(suggestion) {
  const reasons = {
    destination_below_reorder_point: "destinationNeed",
    source_below_reserve: "sourceProtected",
    no_released_matching_unit: "noExactUnit",
    destination_stock_adequate: "destinationCovered",
  };
  return t(reasons[suggestion.reason] ?? "noRecommendation");
}

function transferSuggestionCard() {
  const suggestion = state.transferSuggestion;
  if (!suggestion) return "";
  const actionable = suggestion.status === "recommended";
  const decision = state.transferDecision;
  return `<article class="card">
    <div class="card-title"><h3>${escapeHtml(t(actionable ? "transferTitle" : "noRecommendation"))}</h3><span class="chip ${actionable ? "violet" : ""}">${escapeHtml(t(suggestion.status))}</span></div>
    <p><strong>${escapeHtml(t("suggestionReason"))}:</strong> ${escapeHtml(transferReason(suggestion))}</p>
    <div class="row"><span class="row-label"><strong>${escapeHtml(t("sourceLight"))} · ${escapeHtml(suggestion.from_site)}</strong></span><span class="chip">${escapeHtml(suggestion.source.colour)}</span></div>
    <div class="row"><span class="row-label"><strong>${escapeHtml(t("destinationLight"))} · ${escapeHtml(suggestion.to_site)}</strong></span><span class="chip">${escapeHtml(suggestion.destination.colour)}</span></div>
    <p class="muted">${escapeHtml(t("onHand"))}: ${suggestion.source.on_hand} → ${suggestion.to_site}: ${suggestion.destination.on_hand} · ${escapeHtml(t("reorderGap"))}: ${suggestion.destination.gap_to_reorder_point} · ${escapeHtml(t("safeSurplus"))}: ${suggestion.source.safe_surplus}</p>
    ${actionable ? `<p><strong>${escapeHtml(t("candidate"))}:</strong> …${escapeHtml(suggestion.candidate_unit.din.slice(-4))} · ${escapeHtml(suggestion.candidate_unit.abo_rh)} · ${escapeHtml(suggestion.candidate_unit.days_left)} ${escapeHtml(t("daysLeft"))}</p>
      <p class="muted">${suggestion.basis.map(escapeHtml).join("<br>")}</p>
      ${decision ? `<div class="message">${escapeHtml(decision.decision === "approved" ? t("transferApproved") : t("transferOverridden"))}</div>` : `<button class="button violet" data-action="approve-transfer">${escapeHtml(t("approveTransfer"))}</button>
        <form data-form="transfer-decision" class="field">
          <label for="transfer-override-reason">${escapeHtml(t("overrideReason"))}</label>
          <input id="transfer-override-reason" name="reason" maxlength="300" required>
          <button class="button secondary" type="submit">${escapeHtml(t("recordOverride"))}</button>
        </form>
        <small class="field-help">${escapeHtml(t("unitNotMoved"))}</small>`}`
      : `<p class="muted">${escapeHtml(suggestion.basis[0])}</p>`}
  </article>`;
}

function transferAuditCard() {
  const audit = state.transferDecisionAudit;
  if (!audit) return "";
  const events = [...audit.events].reverse().slice(0, 5);
  return `<article class="card"><div class="card-title"><h3>${escapeHtml(t("auditTitle"))}</h3><span class="chip ${audit.valid ? "good" : "bad"}">${audit.valid ? "✓" : "!"}</span></div>
    <p class="muted">${escapeHtml(t(audit.valid ? "auditValid" : "auditInvalid"))} · ${audit.count}</p>
    ${events.length ? events.map((event) => `<div class="row"><span class="row-label"><strong>${escapeHtml(t(event.event_type))} · ${escapeHtml(event.actor)}</strong>
      <small>…${escapeHtml(event.recommendation_id.slice(-8))}${event.details.reason ? ` · ${escapeHtml(event.details.reason)}` : ""}</small></span></div>`).join("") : `<p class="muted">${escapeHtml(t("noDecisionAudit"))}</p>`}
  </article>`;
}

function lightsScreen() {
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("lightsTitle"))}</h1>
    <p class="sub">${escapeHtml(t("lightsIntro"))}</p>${errorBanner()}${lightsForm()}${stockLightCard()}
    ${state.role === "mercy" ? `<article class="card"><h2>${escapeHtml(t("transferTitle"))}</h2><p class="muted">${escapeHtml(t("transferDisclosure"))}</p></article>${transferSuggestionForm()}${transferSuggestionCard()}${transferAuditCard()}` : ""}
    <h2>${escapeHtml(t("inventory"))}</h2>${unitRows(state.units)}</section>`;
}

function custodyScreen() {
  const moving = state.units.find((unit) => unit.state === "IN_TRANSIT");
  const released = state.units.filter((unit) => unit.state === "RELEASED");
  const deliveredUnits = state.targetUnits ?? [];
  const hasDelivery = deliveredUnits.length > 0;
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("custodyTitle"))}</h1>
    <p class="sub">${escapeHtml(t("custodyIntro"))}</p>${errorBanner()}
    ${moving ? `<article class="card"><div class="card-title"><h2>${escapeHtml(t("inTransit"))}</h2><span class="chip violet">…${escapeHtml(moving.din.slice(-4))}</span></div>
      <p>${escapeHtml(state.lang === "sw" ? "Hakuna mabadiliko ya hali wakati mfuko uko safarini." : "No unit state changes are accepted while this unit is in transit.")}</p>
      <div class="row"><span class="row-label"><strong>${escapeHtml(t("transitDestination"))}</strong><small>${escapeHtml(moving.dispatched_to ?? "—")}</small></span></div>
      <p class="field-help">${escapeHtml(t("transitNoTelemetry"))}</p>
      <label class="check-row"><input type="checkbox" id="quality-confirmed"><span>${escapeHtml(state.lang === "sw" ? "Afisa wa ubora amethibitisha kuwa hali ya usafirishaji inakubalika" : "Quality officer confirms transport conditions are acceptable")}</span></label>
      <button class="button success" data-action="receive" data-din="${escapeHtml(moving.din)}">${escapeHtml(t("arrival"))}</button></article>`
      : `<article class="card"><div class="field"><label for="custody-unit">${escapeHtml(t("selectUnit"))}</label>
      <select id="custody-unit">${released.map((unit) => `<option value="${escapeHtml(unit.din)}">…${escapeHtml(unit.din.slice(-4))} · ${escapeHtml(unit.abo_rh)}</option>`).join("")}</select></div>
      <div class="field"><label for="temperature-reading">${escapeHtml(t("temperature"))}</label><input id="temperature-reading" type="number" step="0.1" placeholder="e.g. 7.8"></div>
      <div class="field"><label for="excursion-detail">${escapeHtml(t("excursionDetail"))}</label><input id="excursion-detail" placeholder="${escapeHtml(state.lang === "sw" ? "Eleza kilichoonekana" : "Describe what you observed")}"></div>
      <div class="button-row"><button class="button secondary" data-action="excursion">${escapeHtml(t("reportTemperature"))}</button>
      <button class="button" data-action="dispatch">${escapeHtml(t("dispatch"))}</button></div>
      <small class="field-help">${escapeHtml(state.lang === "sw" ? "HemoSync haitabuni kiwango cha joto. Ukiripoti tatizo linaloshukiwa, API huiweka HOLD." : "HemoSync does not invent a temperature threshold. Reporting a suspected excursion asks the API to place the unit on HOLD.")}</small></article>`
    }
    ${released.length === 0 && !moving ? `<div class="empty">${escapeHtml(hasDelivery ? t("delivered") : t("noStock"))}</div>` : ""}
    ${state.units.some((unit) => unit.state === "HOLD") ? `<div class="message error">${escapeHtml(t("custodyHold"))}</div>` : ""}
    ${hasDelivery ? `<div class="message">${escapeHtml(t("delivered"))}</div>${unitRows(deliveredUnits)}` : ""}
    <h2>${escapeHtml(t("inventory"))}</h2>${unitRows(state.units)}</section>`;
}

function countyScreen() {
  const sites = state.sites ?? [];
  const groups = [...new Set(sites.flatMap((item) => Object.keys(item.on_hand)))].sort();
  const reportedEvents = state.ledger?.events?.filter((event) => event.etype === "AdverseEventReported") ?? [];
  return `<section class="screen-enter"><p class="eyebrow">${escapeHtml(greeting())}, ${escapeHtml(person()?.name ?? "")}</p><h1>${escapeHtml(t("countyTitle"))}</h1>
    <p class="sub">${escapeHtml(t("countyIntro"))}</p>${errorBanner()}
    <article class="card"><div class="card-title"><h2>${escapeHtml(t("inventory"))}</h2><span class="chip violet">API</span></div>
      ${sites.length ? `<div class="inventory-grid"><div class="inventory-header">${escapeHtml(t("site"))}</div>${groups.map((group) => `<div class="inventory-header">${escapeHtml(group)}</div>`).join("")}
        ${sites.map((site) => `<strong>${escapeHtml(site.site)}</strong>${groups.map((group) => `<span class="inventory-count">${escapeHtml(site.on_hand[group] ?? 0)}</span>`).join("")}`).join("")}
      </div>` : `<div class="empty">${escapeHtml(t("noFacilities"))}</div>`}
      <p class="field-help">${escapeHtml(state.lang === "sw" ? "Jumla za vituo hutoka kwenye API; hakuna majina ya wafadhili." : "Facility aggregates come from the API; no donor names are shown.")}</p>
    </article>
    <h2>${escapeHtml(t("lookbackTitle"))}</h2><p class="sub">${escapeHtml(t("lookbackIntro"))}</p>
    <form class="card" data-form="adverse-event">
      <div class="field"><label for="event-unit">${escapeHtml(t("unitForReview"))}</label><select id="event-unit" name="din">${state.units.map((unit) => `<option value="${escapeHtml(unit.din)}">…${escapeHtml(unit.din.slice(-4))} · ${escapeHtml(unit.abo_rh)} · ${escapeHtml(unitStatus(unit))}</option>`).join("")}</select></div>
      <div class="field"><label for="event-severity">${escapeHtml(t("eventSeverity"))}</label><select id="event-severity" name="severity"><option value="reported">Reported · synthetic</option><option value="review-required">Review required · synthetic</option></select></div>
      <div class="field"><label for="event-detail">${escapeHtml(t("eventDetail"))}</label><input id="event-detail" name="detail" placeholder="${escapeHtml(state.lang === "sw" ? "Maelezo ya mfano tu" : "Synthetic scenario detail only")}"></div>
      <button class="button violet" type="submit">${escapeHtml(t("reportEvent"))}</button>
    </form>
    ${reportedEvents.length ? `<article class="card"><h3>${escapeHtml(t("lookbackTitle"))}</h3>${reportedEvents.map((event) => `<div class="row">
      <span class="status-dot">${escapeHtml(event.seq)}</span><span class="row-label"><strong>…${escapeHtml((event.unit_id ?? "").slice(-4))} · ${escapeHtml(event.payload.severity ?? "")}</strong>
      <small>${escapeHtml(event.payload.detail ?? "")} · ${escapeHtml(event.actor)}</small></span></div>`).join("")}</article>` : ""}
    ${lightsForm()}${stockLightCard()}</section>`;
}

function homeScreen() {
  const screens = {
    brian: releaseScreen,
    achieng: state.screen === "bedside" ? bedsideScreen : urgentScreen,
    wanjiru: donorScreen,
    mercy: lightsScreen,
    hassan: custodyScreen,
    njeri: countyScreen,
  };
  return (screens[state.role] ?? pickerScreen)();
}

function stopScreen() {
  if (!state.stop) return "";
  return `<section class="stop-screen" role="alertdialog" aria-modal="true" aria-labelledby="stop-title">
    <div class="stop-content"><p class="eyebrow" style="color:white">${state.lang === "sw" ? "SIMAMISHA" : "STOP"}</p>
      <h1 id="stop-title">${state.lang === "sw" ? "HAIENDANI — IMEZUIWA" : "INCOMPATIBLE — HARD STOP"}</h1>
      <p>${state.lang === "sw" ? "API imekataa hatua hii." : "The API rejected this action."}</p>
      <article class="card"><strong>${escapeHtml(state.stop.message)}</strong>
        ${state.alternative ? `<p class="muted">${state.lang === "sw" ? "Damu mbadala inayofaa iliyopendekezwa na API" : "Compatible alternative suggested by the API"}: …${escapeHtml(state.alternative.din.slice(-4))} · ${escapeHtml(state.alternative.abo_rh)}</p>` : ""}
      </article>${state.alternative ? `<button class="button" data-action="use-alternative">${state.lang === "sw" ? "Tumia damu iliyopendekezwa" : "Use suggested unit"}</button>` : ""}
      <button class="button secondary" data-action="close-stop">${state.lang === "sw" ? "Rudi kwenye orodha" : "Back to inventory"}</button>
    </div></section>`;
}

async function openLedger() {
  const [ledger, integrity] = await Promise.all([request("/ledger"), request("/ledger/verify")]);
  state.ledger = ledger;
  const events = [...ledger.events].reverse();
  document.querySelector("#overlay-root").innerHTML = `<section class="ledger-panel" role="dialog" aria-modal="true" aria-labelledby="ledger-title">
    <div class="ledger-panel-inner"><div class="card-title"><h2 id="ledger-title">${escapeHtml(t("record"))}</h2>
      <button class="icon-button" data-action="close-ledger" aria-label="${escapeHtml(t("close"))}">×</button></div>
      <p class="message ${integrity.valid ? "" : "error"}">${escapeHtml(integrity.valid ? (state.lang === "sw" ? "Mnyororo wa hash wa daftari la seva ni sahihi." : "Server ledger hash chain is valid.") : (state.lang === "sw" ? "Mnyororo wa hash wa daftari la seva una hitilafu." : "Server ledger hash chain has a broken link."))}</p>
      <p class="muted">${ledger.count} ${escapeHtml(state.lang === "sw" ? "matukio" : "events")}</p>
      ${events.length ? events.map((event) => `<article class="ledger-event"><strong>#${escapeHtml(event.seq)} · ${escapeHtml(event.etype)}${event.unit_id ? ` · …${escapeHtml(event.unit_id.slice(-4))}` : ""}</strong>
        <div class="muted">${escapeHtml(formatDate(event.ts))} · ${escapeHtml(state.lang === "sw" ? "Aliyetenda" : "Actor")}: ${escapeHtml(event.actor)}</div>
        <details><summary>${escapeHtml(state.lang === "sw" ? "Maelezo" : "Details")}</summary><pre class="hash">${escapeHtml(JSON.stringify({ payload: event.payload, prev_hash: event.prev_hash, hash: event.hash }, null, 2))}</pre></details></article>`).join("")
        : `<div class="empty">${escapeHtml(state.lang === "sw" ? "Hakuna matukio yaliyorekodiwa bado." : "No events have been recorded yet.")}</div>`}
    </div></section>`;
}

function render() {
  renderHeader();
  renderFooter();
  const app = document.querySelector("#app");
  if (state.screen === "people") app.innerHTML = pickerScreen();
  else if (state.screen === "donor") app.innerHTML = `<button class="button secondary small" data-action="people">← ${escapeHtml(t("home"))}</button>${donorScreen()}`;
  else app.innerHTML = `<button class="button secondary small" data-action="back-home">← ${escapeHtml(state.role === "achieng" && state.screen === "bedside" ? t("returnToQueue") : t("home"))}</button>${homeScreen()}`;
  if (!state.stop) document.querySelector("#overlay-root").innerHTML = "";
  else document.querySelector("#overlay-root").innerHTML = stopScreen();
}

async function refreshAndRender() {
  await refresh();
  render();
}

async function refreshFefoSuggestion() {
  if (!state.patientGroup) {
    state.fefoSuggestion = null;
    render();
    return;
  }
  const suggestion = await request(`/suggest_fefo?component=RBC&patient_group=${encodeURIComponent(state.patientGroup)}`);
  state.fefoSuggestion = suggestion.unit;
  render();
}

async function resetDemo() {
  const result = await request("/demo/reset", { method: "POST" });
  state.targetUnits = [];
  state.ledger = null;
  state.selectedDin = null;
  await refreshAndRender();
  showToast(result.already_loaded ? t("demoAlreadyLoaded") : t("demoLoaded"));
}

async function reserveUnit(din) {
  try {
    const encounter = state.encounters.find((item) => item.id === state.patientId);
    if (!encounter) {
      throw new Error(t("selectPatientFirst"));
    }
    state.patientGroup = encounter.blood_group;
    state.twoSamplesConfirmed = document.querySelector("#samples-confirmed")?.checked ?? state.twoSamplesConfirmed;
    await request(`/units/${encodeURIComponent(din)}/reserve`, {
      method: "POST",
      body: JSON.stringify({ patient_id: state.patientId, patient_group: state.patientGroup, two_sample_confirmed: state.twoSamplesConfirmed, actor: "nurse.achieng" }),
    });
    state.selectedDin = din;
    state.stop = null;
    state.alternative = null;
    state.screen = "bedside";
    await refreshAndRender();
    showToast(`${t("patient")} ${state.patientId} · …${din.slice(-4)}`);
  } catch (error) {
    if (error instanceof ApiError && error.status === 400) {
      const detail = error.message.toLowerCase();
      if (!detail.includes("hard stop") && !detail.includes("incompatible")) {
        state.error = error.message;
        render();
        return;
      }
      let alternative = null;
      try {
        const component = state.units.find((unit) => unit.din === din)?.component ?? "RBC";
        const suggestion = await request(`/suggest_fefo?component=${encodeURIComponent(component)}&patient_group=${encodeURIComponent(state.patientGroup)}`);
        alternative = suggestion.unit;
      } catch (suggestionError) {
        state.error = suggestionError.message;
      }
      state.stop = { message: error.message };
      state.alternative = alternative?.din === din ? null : alternative;
      render();
      return;
    }
    showError(error);
  }
}

function showError(error) {
  state.error = error instanceof Error ? error.message : String(error);
  if (error instanceof ApiError && error.status === 400) {
    const detail = error.message.toLowerCase();
    if (detail.includes("hard stop") || detail.includes("incompatible") || detail.includes("wristband") || detail.includes("gate 7")) {
      state.stop = { message: error.message };
    }
  }
  render();
}

async function action(name, button) {
  try {
    if (name === "select-role") {
      state.role = button.dataset.role; state.screen = "home"; state.stop = null; state.error = ""; render();
      if (state.role === "achieng") {
        await refreshFefoSuggestion();
      } else if (state.role === "njeri") {
        const [inventory, ledger] = await Promise.all([request("/sites/inventory"), request("/ledger")]);
        state.sites = inventory.sites;
        state.ledger = ledger;
        render();
      } else if (state.role === "mercy") {
        await refreshTransferAudit();
        render();
      } else if (state.role === "wanjiru") {
        state.ledger = await request("/ledger");
        render();
      } else if (state.role === "hassan") {
        const target = await request("/sites/HOMA-BAY/units");
        state.targetUnits = target.units;
        render();
      }
    } else if (name === "people") {
      state.role = null; state.screen = "people"; state.selectedDin = null; state.stop = null; render();
    } else if (name === "demo-reset") {
      await resetDemo();
    } else if (name === "retry-api") {
      await refresh();
      state.error = "";
      render();
    } else if (name === "language") {
      state.lang = state.lang === "en" ? "sw" : "en"; render();
    } else if (name === "theme") {
      state.theme = state.theme === "dark" ? "light" : state.theme === "light" ? "auto" : "dark";
      if (state.theme === "auto") document.documentElement.removeAttribute("data-theme");
      else document.documentElement.dataset.theme = state.theme;
      renderHeader();
    } else if (name === "install-pwa") {
      if (!state.installPrompt) {
        showToast(state.lang === "sw" ? "Tafadhali ufungue tena kwenye kivinjari cha wavuti kilichotumika." : "Open this page in a browser that supports install prompts.");
        return;
      }
      state.installPrompt.prompt();
      const result = await state.installPrompt.userChoice;
      if (result.outcome === "accepted") {
        state.isInstalled = true;
        state.canInstall = false;
      }
      state.installPrompt = null;
      renderHeader();
      renderFooter();
    } else if (name === "ledger") {
      await openLedger();
    } else if (name === "close-ledger") {
      document.querySelector("#overlay-root").innerHTML = "";
    } else if (name === "back-home") {
      state.screen = state.role === "achieng" ? "queue" : state.role ? "home" : "people";
      state.selectedDin = null; state.stop = null; render();
    } else if (name === "select-encounter") {
      const patientId = button.dataset.patientId;
      const encounter = state.encounters.find((item) => item.id === patientId);
      if (!encounter) return;
      const linkedUnit = state.units.find((unit) => unit.reserved_for === patientId
        && ["RESERVED", "ISSUED"].includes(unit.state));
      state.patientId = patientId;
      state.patientGroup = encounter.blood_group;
      if (linkedUnit) {
        state.selectedDin = linkedUnit.din;
        state.screen = "bedside";
      } else {
        state.twoSamplesConfirmed = false;
        state.fefoSuggestion = null;
      }
      render();
      if (!linkedUnit) await refreshFefoSuggestion();
    } else if (name === "select-bedside-unit") {
      state.selectedDin = button.dataset.din;
      render();
    } else if (name === "release" || name === "same-signer") {
      await request(`/units/${encodeURIComponent(STORY_UNIT_ID)}/release`, {
        method: "POST",
        body: JSON.stringify({ tech: "tech.brian", supervisor: name === "same-signer" ? "tech.brian" : "supervisor.amina" }),
      });
      await refreshAndRender(); showToast(t("releaseSuccess"));
    } else if (name === "reserve") {
      await reserveUnit(button.dataset.din);
    } else if (name === "close-stop") {
      state.stop = null; state.alternative = null; state.error = ""; render();
    } else if (name === "use-alternative" && state.alternative) {
      const din = state.alternative.din; state.stop = null; state.alternative = null; await reserveUnit(din);
    } else if (name === "issue") {
      const din = button.dataset.din;
      await request(`/units/${encodeURIComponent(din)}/issue`, { method: "POST", body: JSON.stringify({ actor: "store.mercy" }) });
      state.selectedDin = din; state.screen = "bedside"; await refreshAndRender();
    } else if (name === "approve-transfer") {
      const suggestion = state.transferSuggestion;
      if (!suggestion) throw new Error(t("noRecommendation"));
      const result = await request(`/decision-support/transfer-suggestions/${encodeURIComponent(suggestion.recommendation_id)}/decision`, {
        method: "POST",
        body: JSON.stringify({ decision: "approve", actor: "manager.mercy" }),
      });
      state.transferDecision = result;
      await Promise.all([refresh(), refreshTransferAudit()]);
      render();
      showToast(t("transferApproved"));
    } else if (name === "booking") {
      showToast(state.lang === "sw" ? "Uwekaji nafasi wa zoezi la uchangiaji unakuja." : "Donation-drive booking is coming soon.");
    } else if (name === "excursion") {
      const din = document.querySelector("#custody-unit")?.value;
      if (!din) throw new Error(t("emptyUnits"));
      const temperature = document.querySelector("#temperature-reading")?.value;
      if (!temperature) throw new Error(state.lang === "sw" ? "Ingiza joto lililoonekana." : "Enter the observed temperature.");
      const note = document.querySelector("#excursion-detail")?.value ?? "";
      const detail = `Observed temperature ${temperature} °C. ${note}`.trim();
      await request("/units/flag_excursion", { method: "POST", body: JSON.stringify({ dins: [din], actor: "courier.hassan", detail }) });
      await refreshAndRender(); showToast(state.lang === "sw" ? "API imerekodi hatua ya uangalizi." : "The API recorded the custody action.");
    } else if (name === "dispatch") {
      const din = document.querySelector("#custody-unit")?.value;
      if (!din) throw new Error(t("emptyUnits"));
      await request(`/units/${encodeURIComponent(din)}/dispatch`, { method: "POST", body: JSON.stringify({ to_site: "HOMA-BAY", actor: "courier.hassan" }) });
      await refreshAndRender(); showToast(state.lang === "sw" ? "API imerekodi hatua ya uangalizi." : "The API recorded the custody action.");
    } else if (name === "receive") {
      const din = button.dataset.din;
      const tempOk = document.querySelector("#quality-confirmed")?.checked ?? false;
      const received = await request(`/units/${encodeURIComponent(din)}/receive`, {
        method: "POST",
        body: JSON.stringify({
          from_site: "API-SITE",
          to_site: "HOMA-BAY",
          actor: tempOk ? "quality.homa-bay" : "courier.hassan",
          temp_ok: tempOk,
        }),
      });
      await refreshAndRender();
      state.targetUnits = (await request(`/sites/${encodeURIComponent(received.site)}/units`)).units;
      render();
      showToast(`${t("delivered")} · ${received.site}`);
    }
  } catch (error) {
    showError(error);
  }
}

async function submitForm(form) {
  const data = new FormData(form);
  if (form.dataset.form === "transfer-suggestion") {
    try {
      const suggestion = await request("/decision-support/transfer-suggestions", {
        method: "POST",
        body: JSON.stringify({
          from_site: String(data.get("from_site")),
          to_site: String(data.get("to_site")),
          component: String(data.get("component")),
          group: String(data.get("group")),
          source_mean_daily_use: Number(data.get("source_mean_daily_use")),
          source_lead_days: Number(data.get("source_lead_days")),
          target_mean_daily_use: Number(data.get("target_mean_daily_use")),
          target_lead_days: Number(data.get("target_lead_days")),
          z: Number(data.get("z")),
        }),
      });
      state.transferSuggestion = suggestion;
      state.transferDecision = null;
      state.error = "";
      await refreshTransferAudit();
      render();
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "transfer-decision") {
    const suggestion = state.transferSuggestion;
    if (!suggestion) return;
    try {
      const result = await request(`/decision-support/transfer-suggestions/${encodeURIComponent(suggestion.recommendation_id)}/decision`, {
        method: "POST",
        body: JSON.stringify({
          decision: "override",
          actor: "manager.mercy",
          reason: String(data.get("reason")).trim(),
        }),
      });
      state.transferDecision = result;
      state.error = "";
      await refreshTransferAudit();
      render();
      showToast(t("transferOverridden"));
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "record-test") {
    try {
      await request(`/units/${encodeURIComponent(STORY_UNIT_ID)}/record_test`, {
        method: "POST",
        body: JSON.stringify({
          marker: form.dataset.marker,
          result: String(data.get("result")),
          actor: TEST_ACTOR,
        }),
      });
      await refreshAndRender();
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "record-typing") {
    try {
      await request(`/units/${encodeURIComponent(STORY_UNIT_ID)}/record_typing`, {
        method: "POST",
        body: JSON.stringify({ abo_rh: String(data.get("abo_rh")), actor: String(data.get("actor")) }),
      });
      await refreshAndRender();
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "transfuse") {
    const unit = activeUnit();
    if (!unit) return;
    try {
      await request(`/units/${encodeURIComponent(unit.din)}/transfuse`, {
        method: "POST",
        body: JSON.stringify({ scanned_patient: String(data.get("scanned_patient")), scanned_unit: String(data.get("scanned_unit")), nurse1: "nurse.achieng", nurse2: String(data.get("nurse2")) }),
      });
      if (unit.din === STORY_UNIT_ID) {
        state.role = "wanjiru";
        state.screen = "donor";
        await request("/ledger").then((ledger) => { state.ledger = ledger; });
      } else {
        state.role = "achieng";
        state.screen = "queue";
        state.selectedDin = null;
      }
      await refreshAndRender();
      showToast(state.lang === "sw" ? "Utiaji damu umeanza. Tukio limerekodiwa na API." : "Transfusion started. The event was recorded by the API.");
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "stock-light") {
    try {
      const group = String(data.get("group"));
      const component = String(data.get("component"));
      const amount = await request(`/on_hand?component=${encodeURIComponent(component)}&group=${encodeURIComponent(group)}`);
      const result = await request("/stock_light", {
        method: "POST",
        body: JSON.stringify({ on_hand: amount.count, mean_daily_use: Number(data.get("mean_daily_use")), lead_days: Number(data.get("lead_days")), z: Number(data.get("z")) }),
      });
      state.stockLight = { ...result, group, component, on_hand: amount.count };
      state.error = "";
      render();
    } catch (error) {
      showError(error);
    }
  } else if (form.dataset.form === "adverse-event") {
    const din = String(data.get("din"));
    try {
      await request(`/units/${encodeURIComponent(din)}/report_adverse_event`, {
        method: "POST",
        body: JSON.stringify({ severity: String(data.get("severity")), actor: "director.njeri", detail: String(data.get("detail") ?? "") }),
      });
      const ledger = await request("/ledger");
      state.ledger = ledger;
      state.error = "";
      await refresh();
      render();
      showToast(state.lang === "sw" ? "Tukio lisilotarajiwa limerekodiwa na API." : "Adverse event recorded by the API.");
    } catch (error) {
      showError(error);
    }
  }
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-action]");
  if (!button) return;
  event.preventDefault();
  void action(button.dataset.action, button);
});
document.addEventListener("submit", (event) => {
  const form = event.target.closest("form[data-form]");
  if (!form) return;
  event.preventDefault();
  void submitForm(form);
});
document.addEventListener("change", (event) => {
  if (event.target.id === "transfer-source") {
    const target = document.querySelector("#transfer-target");
    const candidates = state.sites.filter((site) => site.site !== event.target.value);
    const selected = candidates.some((site) => site.site === target.value) ? target.value : candidates[0]?.site;
    target.replaceChildren(...candidates.map((site) => new Option(site.site, site.site, false, site.site === selected)));
  }
  if (event.target.id === "encounter-select") {
    const patientId = event.target.value;
    const encounter = state.encounters.find((item) => item.id === patientId);
    const linkedUnit = state.units.find((unit) => unit.reserved_for === patientId
      && ["RESERVED", "ISSUED"].includes(unit.state));
    state.patientId = patientId;
    state.patientGroup = encounter?.blood_group ?? "";
    state.twoSamplesConfirmed = false;
    state.fefoSuggestion = null;
    if (linkedUnit) {
      state.selectedDin = linkedUnit.din;
      state.screen = "bedside";
    }
    render();
    void refreshFefoSuggestion().catch(showError);
  }
  if (event.target.id === "samples-confirmed") {
    state.twoSamplesConfirmed = event.target.checked;
    render();
  }
});

async function initialize() {
  state.isInstalled = window.matchMedia("(display-mode: standalone)").matches || Boolean(window.navigator.standalone);
  state.canInstall = Boolean(state.installPrompt);
  render();
  try {
    await refresh();
    render();
  } catch (error) {
    state.error = error.message;
    render();
  }
}

window.addEventListener("beforeinstallprompt", (event) => {
  event.preventDefault();
  state.installPrompt = event;
  state.canInstall = true;
  state.isInstalled = false;
  renderHeader();
});

window.addEventListener("appinstalled", () => {
  state.installPrompt = null;
  state.canInstall = false;
  state.isInstalled = true;
  renderHeader();
  renderFooter();
});

void initialize();
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js", { scope: "/" }).catch((error) => {
    console.error("HemoSync offline shell could not be registered.", error);
  });
}

window.setInterval(() => {
  const elapsed = document.querySelector("#elapsed-timer");
  const unit = activeUnit();
  if (!elapsed || !unit?.issued_at) return;
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(unit.issued_at).getTime()) / 1000));
  elapsed.textContent = `${String(Math.floor(seconds / 60)).padStart(2, "0")}:${String(seconds % 60).padStart(2, "0")}`;
}, 1000);