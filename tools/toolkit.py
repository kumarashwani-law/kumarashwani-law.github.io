"""Interactive tools: the toolkit index, a DPDP readiness checker and a cyber-fraud first-response guide.
Everything runs in the reader's browser. Nothing they choose is sent anywhere."""

PRIVACY_LINE = ('<p class="small" style="margin:0">Your answers stay in your browser. Nothing is sent to me or to anyone else. '
                'This is general information, not legal advice.</p>')

# ------------------------------------------------------------------ index
INDEX = '''
<main class="wrap">
<section class="page-head">
<h1>Tools</h1>
<p>Free, plain-language tools for common technology-law problems in India. They run in your browser and don't collect anything you enter.</p>
</section>
<section class="grid" style="padding-bottom:96px">
<a class="card guide-card" href="cyber-fraud.html"><span class="kicker">Tool · Cyber fraud</span><h3>Cyber fraud: what to do right now</h3><p>Pick what happened (a scam call, money lost, a hacked account, sextortion) and get the steps in order, with the helplines and portals to use.</p></a>
<a class="card guide-card" href="dpdp-checker.html"><span class="kicker">Tool · Data protection</span><h3>DPDP readiness checker</h3><p>Answer a few questions about your business and get a printable checklist of what the DPDP Act and Rules expect from you by 13 May 2027.</p></a>
<a class="card guide-card" href="../glossary.html"><span class="kicker">Reference</span><h3>Glossary</h3><p>Short definitions of the legal terms used across this site, from "data fiduciary" to "safe harbour".</p></a>
<a class="card guide-card" href="../cases.html"><span class="kicker">Case alerts</span><h3>Follow a case</h3><p>Every case in the tracker has its own feed. Follow one by RSS or email and get an update when its status changes.</p></a>
</section>
</main>
'''

# ------------------------------------------------------------------ DPDP readiness checker
DPDP = '''
<main>
<div class="tool" id="dpdp">
<a href="index.html" style="font-size:14px;font-weight:500;text-decoration:none" class="no-print">← All tools</a>
<span class="kicker">Tool · Data protection</span>
<h1>DPDP readiness checker</h1>
<p class="dek">Answer up to eleven quick questions about how your business handles personal data. You'll get a checklist of what the Digital Personal Data Protection Act, 2023 and the DPDP Rules, 2025 expect from you, most of it by <b>13 May 2027</b>.</p>
''' + PRIVACY_LINE + '''
<div class="tool-card" id="dpdp-card" aria-live="polite"></div>
<p class="small no-print">For the reasoning behind each item, read the full guide: <a href="../guides/dpdp-business-checklist.html">DPDP Act: what your business must do by 13 May 2027</a>.</p>
</div>
</main>
<script>
(function () {
  var Q = [
    {id: 'digital', q: 'Do you collect or hold personal data about people in digital form?',
     help: 'Personal data is anything that identifies a person: names, phone numbers, emails, addresses, photos, ID numbers, health or payment details. "Digital" includes apps, websites, spreadsheets, CRM, email lists, cloud storage and WhatsApp, and paper records you later scan or type in.',
     stopOn: 'no', stop: 'If you hold no personal data in digital form (and don\\'t digitise paper records), the DPDP Act is unlikely to apply. Check again if that changes, for example when you start a website form, an app or a customer spreadsheet.'},
    {id: 'domestic', q: 'Is the data held only for personal or household purposes?',
     help: 'For example, a family\\'s own phone contacts or home CCTV. A business, school, clinic, NGO or freelancer using data for work is not personal or domestic use.',
     stopOn: 'yes', stop: 'Processing for purely personal or domestic purposes is outside the Act (section 3(c)(i)). Other laws, such as the IT Act and privacy rights under Article 21, can still apply.'},
    {id: 'india', q: 'Do you process the data in India, or offer goods or services to people in India?',
     help: 'The Act covers data processed in India, and data processed abroad in connection with offering goods or services to people in India.',
     stopOn: 'no', stop: 'If you neither process data in India nor offer goods or services to people in India, the Act is unlikely to apply to you. Data protection laws of the countries you work in may.'},
    {id: 'children', q: 'Could any of the people whose data you hold be under 18?',
     help: 'Students, young customers, gamers, app users or patients. If you don\\'t check ages, answer "Not sure".'},
    {id: 'disability', q: 'Do you deal with persons with disability who act through a lawful guardian?',
     help: 'For example, a special school, a care home, a hospital or an insurer.'},
    {id: 'vendors', q: 'Do other companies handle personal data for you?',
     help: 'Cloud hosting, payroll, email marketing, CRM, payment gateways, call centres, IT support, analytics. In the Act\\'s terms they are your data processors, and you stay responsible for them.'},
    {id: 'employees', q: 'Do you have employees, interns or contractors whose data you keep?',
     help: 'HR files, payroll, attendance, ID copies, bank details for salary.'},
    {id: 'platform', q: 'Are you a large e-commerce, online gaming or social media platform?',
     help: 'The Rules set user thresholds in the Third Schedule (2 crore registered users for e-commerce and social media, 50 lakh for online gaming). Answer "Not sure" if you are close.'},
    {id: 'sdf', q: 'Has the government notified you as a Significant Data Fiduciary, or might it?',
     help: 'The government can notify businesses as Significant Data Fiduciaries based on the volume and sensitivity of data they process, risk to people\\'s rights, and other factors.'},
    {id: 'abroad', q: 'Does any personal data leave India?',
     help: 'For example, foreign cloud servers, overseas group companies, or tools like email and CRM hosted abroad.'},
    {id: 'breach', q: 'Do you already have a written plan for what to do if personal data is leaked or hacked?',
     help: 'A plan that says who leads, who approves notices, and how you will tell users and the Data Protection Board.'}
  ];
  var ANS = {yes: 'Yes', no: 'No', unsure: 'Not sure'};
  var card = document.getElementById('dpdp-card');
  var answers = {}, i = 0, started = false;

  function el(html) {
    card.innerHTML = html;
    var f = card.querySelector('h2, .tool-q');
    if (f && started) { f.setAttribute('tabindex', '-1'); f.focus(); }
    started = true;
  }

  function ask() {
    var item = Q[i];
    var pct = Math.round(i / Q.length * 100);
    var opts = Object.keys(ANS).map(function (k) {
      var on = answers[item.id] === k ? ' btn-primary' : ' btn-ghost';
      return '<button type="button" class="btn' + on + '" data-a="' + k + '">' + ANS[k] + '</button>';
    }).join('');
    el('<div class="tool-progress" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + pct + '" aria-label="Progress"><span style="width:' + pct + '%"></span></div>' +
       '<span class="label">Question ' + (i + 1) + ' of ' + Q.length + '</span>' +
       '<p class="tool-q">' + item.q + '</p><p class="tool-help">' + item.help + '</p>' +
       '<div class="tool-options">' + opts + '</div>' +
       '<div class="tool-nav">' + (i > 0 ? '<button type="button" class="btn btn-ghost btn-sm" data-nav="back">← Back</button>' : '<span></span>') + '</div>');
    card.querySelectorAll('[data-a]').forEach(function (b) {
      b.addEventListener('click', function () {
        var a = b.getAttribute('data-a');
        answers[item.id] = a;
        if (item.stopOn && a === item.stopOn) return stop(item);
        i++;
        if (i < Q.length) ask(); else result();
      });
    });
    var back = card.querySelector('[data-nav=back]');
    if (back) back.addEventListener('click', function () { i--; ask(); });
  }

  function stop(item) {
    el('<h2 style="margin:0;font-size:22px">The Act may not apply to you</h2><p style="margin:0">' + item.stop + '</p>' +
       '<div class="tool-nav"><button type="button" class="btn btn-ghost btn-sm" data-nav="back">← Change my answer</button>' +
       '<button type="button" class="btn btn-ghost btn-sm" data-nav="restart">Start again</button></div>');
    card.querySelector('[data-nav=back]').addEventListener('click', ask);
    card.querySelector('[data-nav=restart]').addEventListener('click', restart);
  }

  function restart() { answers = {}; i = 0; ask(); }
  function on(id) { return answers[id] === 'yes' || answers[id] === 'unsure'; }

  function result() {
    var items = [
      ['Map your data', 'List every place you collect or hold personal data (forms, apps, CRM, HR, CCTV, email lists, WhatsApp groups, spreadsheets, vendors). For each: what data, why, who can see it, where it is stored, how long you keep it.'],
      ['Rewrite your privacy notice', 'Itemise the personal data you collect and the purpose for each; explain how to withdraw consent, exercise rights and complain to the Data Protection Board. It must be available in English or any Eighth Schedule language.'],
      ['Fix consent, and make withdrawal as easy as giving it', 'Consent must be free, specific, informed, unconditional and unambiguous, by a clear action. No pre-ticked boxes. Where you rely on a "legitimate use" instead, write down why.'],
      ['Put security safeguards in place', 'Encryption or masking, access controls, logs of who accessed what, backups. Keep access logs for at least one year.'],
      [on('breach') && answers.breach === 'yes' ? 'Test your breach plan against the Rules' : 'Write a breach plan', 'On becoming aware of a personal data breach, tell each affected person and the Data Protection Board without delay, and send the Board a detailed report within 72 hours (Rule 7). Decide in advance who leads, who approves, and how you will reach users. Run a mock drill.'],
      ['Delete data you no longer need', 'Erase personal data once the purpose is served or consent is withdrawn, unless a law requires you to keep it.'],
      ['Set up a way to answer users\\' requests', 'People can ask to access a summary of their data, correct, complete or erase it, and nominate someone. Publish a contact person and a grievance process with a response timeline.']
    ];
    var extra = [];
    if (on('children')) extra.push(['Children\\'s data', 'Get verifiable consent from a parent or lawful guardian before processing data of anyone under 18. Do not track, monitor the behaviour of, or target ads at children. Choose age checks that collect as little data as possible. Penalty for breach of these duties: up to Rs 200 crore.']);
    if (on('disability')) extra.push(['Persons with disability', 'Where a person with disability has a lawful guardian, get verifiable consent from the guardian, and check the guardian\\'s appointment.']);
    if (on('vendors')) extra.push(['Vendor contracts', 'Add data-processing clauses to every vendor contract: process only on your instructions, keep it secure, report breaches to you at once, delete or return data at the end. You remain responsible for what they do.']);
    if (on('employees')) extra.push(['Employee data', 'Employment purposes can be a "legitimate use" without consent, but only for what employment actually needs. Cover HR data in your data map, retention rules and security.']);
    if (on('platform')) extra.push(['Three-year inactivity erasure', 'Platforms above the Third Schedule thresholds must erase a user\\'s data after three years of inactivity, telling them at least 48 hours before.']);
    if (on('sdf')) extra.push(['Significant Data Fiduciary duties', 'If notified: appoint a Data Protection Officer based in India, an independent data auditor, and carry out periodic Data Protection Impact Assessments and audits. Penalty for breach: up to Rs 150 crore.']);
    if (on('abroad')) extra.push(['Data leaving India', 'Record which countries your data goes to and why. Transfers are allowed unless the government restricts a country (section 16 and Rule 15), so check for any notification before relying on a destination.']);

    var unsure = Object.keys(answers).filter(function (k) { return answers[k] === 'unsure'; }).length;
    function li(it, n) {
      return '<li><input type="checkbox" id="dc' + n + '" aria-label="Mark done: ' + it[0] + '"><label for="dc' + n + '"><b>' + it[0] + '.</b> ' + it[1] + '</label></li>';
    }
    var n = 0;
    el('<h2 style="margin:0;font-size:24px">Your DPDP checklist</h2>' +
       '<div class="tool-result">' +
       '<p class="must" style="margin:0"><b>The Act applies to you.</b> Most duties take effect on <b>13 May 2027</b>, whether or not the Data Protection Board is fully staffed by then. Penalties go up to <b>Rs 250 crore</b> per instance for failing to keep reasonable security safeguards.</p>' +
       (unsure ? '<p style="margin:0">You answered "Not sure" ' + unsure + (unsure > 1 ? ' times' : ' time') + '. Those items are included below, to be safe. Find out the answer before deciding they don\\'t apply.</p>' : '') +
       '<h2>Everyone</h2><ul class="checklist">' + items.map(function (it) { return li(it, n++); }).join('') + '</ul>' +
       (extra.length ? '<h2>Because of your answers</h2><ul class="checklist">' + extra.map(function (it) { return li(it, n++); }).join('') + '</ul>' : '') +
       '<h2>A six-month plan</h2><ul><li><b>Now to February 2027:</b> data map; vendor clauses; draft notice and consent text.</li><li><b>March to May 2027:</b> one-click withdrawal; security and logging; 72-hour breach drill; publish a contact person and grievance process.</li></ul>' +
       '<p class="small" style="margin:0">Based on the DPDP Act, 2023 and the DPDP Rules, 2025 as of November 2026. General information, not legal advice; for your business\\'s position, speak to a lawyer.</p>' +
       '</div>' +
       '<div class="tool-nav"><button type="button" class="btn btn-ghost btn-sm" data-nav="back">← Change answers</button>' +
       '<span class="row" style="gap:8px"><button type="button" class="btn btn-primary btn-sm" data-nav="print">Print / save PDF</button><button type="button" class="btn btn-ghost btn-sm" data-nav="restart">Start again</button></span></div>');
    card.querySelector('[data-nav=back]').addEventListener('click', function () { i = Q.length - 1; ask(); });
    card.querySelector('[data-nav=restart]').addEventListener('click', restart);
    card.querySelector('[data-nav=print]').addEventListener('click', function () { window.print(); });
  }

  ask();
})();
</script>
'''

# ------------------------------------------------------------------ Cyber fraud first response
FRAUD = '''
<main>
<div class="tool" id="fraud">
<a href="index.html" style="font-size:14px;font-weight:500;text-decoration:none" class="no-print">← All tools</a>
<span class="kicker">Tool · Cyber fraud</span>
<h1>Cyber fraud: what to do right now</h1>
<p class="dek">Pick what happened. You'll get the steps in the order that matters, with the numbers and portals to use.</p>
<div class="emergency" role="note">
<b>Lost money? Call <a href="tel:1930">1930</a> now.</b>
<span>It's the national cyber fraud helpline. The sooner you report, the better the chance of freezing the money. In danger or being threatened? Call <a href="tel:112">112</a>.</span>
</div>
''' + PRIVACY_LINE + '''
<div class="tool-card" id="fraud-card" aria-live="polite"></div>
<p class="small no-print">More detail: <a href="../guides/digital-arrest.html">the digital arrest guide</a> and <a href="../guides/account-blocked.html">the blocked account guide</a>.</p>
</div>
</main>
<script>
(function () {
  var card = document.getElementById('fraud-card');
  var SAVE = 'Save everything: call logs, chat screenshots, SMS, bank statements, transaction IDs, any "documents" they sent. Don\\'t delete chats, even embarrassing ones.';
  var PORTAL = 'File a complaint at <a href="https://cybercrime.gov.in" rel="noopener" target="_blank">cybercrime.gov.in</a>. Upload your screenshots and note the complaint number.';
  var CHAKSHU = 'Report the number, WhatsApp account or message on <b>Chakshu</b> at <a href="https://sancharsaathi.gov.in" rel="noopener" target="_blank">sancharsaathi.gov.in</a> (or the Sanchar Saathi app), so it can be blocked for others.';
  var S = {
    call: {label: 'A scam call is happening now', sub: '"Digital arrest", fake police, CBI, customs or courier', steps: [
      ['Hang up.', 'You have no legal duty to stay on a call. No police officer, CBI, ED, customs, RBI or court arrests anyone on a video call or asks for money to "verify" your name.'],
      ['Send nothing.', 'No money, OTPs, Aadhaar, PAN or bank details. Don\\'t install any app they ask for: screen-sharing apps let them see everything.'],
      ['Tell someone you trust, now.', 'Secrecy is part of the scam. A family member or friend breaks the spell.'],
      ['If you\\'re worried it\\'s real,', 'call your local police station yourself, on a number you look up. Never use a number the caller gives you.'],
      ['Report the number.', CHAKSHU]
    ]},
    money: {label: 'I\\'ve lost money', sub: 'Sent it to a scammer, or it was taken from my account', ask: true},
    attempt: {label: 'Someone tried, but I didn\\'t lose money', sub: 'A suspicious call, SMS, link or WhatsApp message', steps: [
      ['Don\\'t reply or click.', 'If you clicked a link or entered details, change those passwords now and tell your bank if card or bank details were involved.'],
      ['Report it.', CHAKSHU],
      ['Block the sender', 'and report the message as spam in WhatsApp or your SMS app.'],
      ['Warn your family,', 'especially older relatives. The same scammers often try several people.']
    ]},
    hacked: {label: 'My account was hacked or someone is impersonating me', sub: 'Email, WhatsApp, Instagram, Facebook, bank', steps: [
      ['Recover the account.', 'Use the platform\\'s official hacked-account process (search its Help Centre). If you still have access, change the password and log out of all other sessions.'],
      ['Turn on two-step verification', 'for the account and for your email, which is usually the way in.'],
      ['Tell your contacts', 'not to send money or OTPs to anyone using your name.'],
      ['Report the fake or hacked account', 'to the platform using its impersonation or hacked-account form.'],
      ['Report it as a crime.', PORTAL + ' Identity theft and cheating by impersonation are offences under sections 66C and 66D of the IT Act.'],
      ['If money is involved,', 'call <a href="tel:1930">1930</a> and your bank straight away.']
    ]},
    images: {label: 'Someone is threatening to share intimate images or a deepfake', sub: 'Sextortion, morphed photos, fake videos', steps: [
      ['Don\\'t pay and don\\'t negotiate.', 'Paying almost never ends it; it usually leads to more demands.'],
      ['Don\\'t delete anything.', 'Screenshot the threats, the profile and the payment requests. ' + SAVE],
      ['Report to the platform.', 'Under Rule 3(2)(b) of the IT Rules, 2021, platforms must remove intimate or morphed images of a person within 24 hours of a complaint by that person or someone on their behalf.'],
      ['Stop the image spreading.', 'If you\\'re 18 or over, <a href="https://stopncii.org" rel="noopener" target="_blank">StopNCII.org</a> creates a digital fingerprint of the image on your own device (the image itself is not uploaded) so participating platforms can block it.'],
      ['Report it as a crime.', PORTAL + ' The portal has a separate category for crimes against women and children, which can be reported anonymously.'],
      ['Talk to someone.', 'This is not your fault. If you feel unsafe, call <a href="tel:112">112</a>.']
    ]}
  };
  var WHEN = {
    now: {label: 'In the last few hours', note: 'You are in the window where money can most often be frozen. Do step 1 before anything else.'},
    days: {label: '1 to 3 days ago', note: 'Report now. Money moves fast, but banks can still put holds on accounts that haven\\'t been emptied.'},
    older: {label: 'More than 3 days ago', note: 'Report anyway. Recovery is harder, but a complaint is needed for the investigation and for any claim against your bank.'}
  };
  function moneySteps(when) {
    return [
      ['Call 1930.', 'Give your phone number, the amount, your bank, the time of each transfer, and the account or UPI ID that received the money.'],
      ['Complain online.', PORTAL + ' Choose "Financial Fraud".'],
      ['Tell your bank in writing,', 'by email and at the branch: ask it to block further debits and to request holds on the receiving accounts. Keep the acknowledgement.'],
      ['Was the transaction unauthorised?', 'If you didn\\'t make or approve it (a skimmed card, a SIM swap), RBI\\'s 2017 rules on customer liability say you have zero liability where the breach was by a third party and you report it to your bank within 3 working days; delays of 4 to 7 working days bring limited liability. If you were tricked into sending it yourself, banks usually treat it as authorised, so in your complaint point out any warning signs the bank ignored (a first-ever large transfer to a new payee, many transfers in a short time).'],
      ['File an FIR', 'at your local or cyber police station, quoting your cybercrime.gov.in complaint number.'],
      ['Escalate if the bank doesn\\'t help.', 'Complain to the bank\\'s grievance officer, then, after 30 days or an unsatisfactory reply, to the RBI Ombudsman at <a href="https://cms.rbi.org.in" rel="noopener" target="_blank">cms.rbi.org.in</a>.'],
      ['Beware of "recovery agents".', 'People who contact you offering to get the money back for a fee are often part of the same fraud.']
    ];
  }
  function focus() { var h = card.querySelector('h2'); if (h) { h.setAttribute('tabindex', '-1'); h.focus(); } }
  function menu() {
    card.innerHTML = '<h2 style="margin:0;font-size:22px">What happened?</h2><div class="tool-options" style="flex-direction:column">' +
      Object.keys(S).map(function (k) {
        return '<button type="button" class="btn btn-ghost" style="justify-content:flex-start;text-align:left;flex-direction:column;align-items:flex-start;gap:2px;padding:14px 18px;height:auto" data-s="' + k + '"><b>' + S[k].label + '</b><span class="small">' + S[k].sub + '</span></button>';
      }).join('') + '</div>';
    card.querySelectorAll('[data-s]').forEach(function (b) {
      b.addEventListener('click', function () { var k = b.getAttribute('data-s'); if (S[k].ask) askWhen(); else show(S[k].label, S[k].steps); });
    });
  }
  function askWhen() {
    card.innerHTML = '<h2 style="margin:0;font-size:22px">When did the money go?</h2><div class="tool-options">' +
      Object.keys(WHEN).map(function (k) { return '<button type="button" class="btn btn-ghost" data-w="' + k + '">' + WHEN[k].label + '</button>'; }).join('') +
      '</div><div class="tool-nav"><button type="button" class="btn btn-ghost btn-sm" data-nav="menu">← Back</button></div>';
    card.querySelectorAll('[data-w]').forEach(function (b) {
      b.addEventListener('click', function () { var w = WHEN[b.getAttribute('data-w')]; show('I\\'ve lost money', moneySteps(), w.note); });
    });
    card.querySelector('[data-nav=menu]').addEventListener('click', menu);
    focus();
  }
  function show(title, steps, note) {
    card.innerHTML = '<h2 style="margin:0;font-size:24px">' + title + '</h2>' +
      '<div class="tool-result">' + (note ? '<p class="must" style="margin:0">' + note + '</p>' : '') +
      '<ol>' + steps.map(function (s) { return '<li><b>' + s[0] + '</b> ' + s[1] + '</li>'; }).join('') + '</ol>' +
      '<p style="margin:0"><b>Keep records.</b> ' + SAVE + '</p>' +
      '<p class="small" style="margin:0">General information as of November 2026, not legal advice.</p></div>' +
      '<div class="tool-nav"><button type="button" class="btn btn-ghost btn-sm" data-nav="menu">← Something else happened</button>' +
      '<button type="button" class="btn btn-primary btn-sm" data-nav="print">Print / save PDF</button></div>';
    card.querySelector('[data-nav=menu]').addEventListener('click', function () { menu(); focus(); });
    card.querySelector('[data-nav=print]').addEventListener('click', function () { window.print(); });
    focus();
  }
  menu();
})();
</script>
'''

PAGES = {
    "index": ("Tools", "Free tools for Indian technology-law problems: a cyber fraud first-response guide and a DPDP Act readiness checker.", INDEX),
    "dpdp-checker": ("DPDP readiness checker", "Answer a few questions and get a printable checklist of what the DPDP Act, 2023 and DPDP Rules, 2025 expect from your business by 13 May 2027.", DPDP),
    "cyber-fraud": ("Cyber fraud: what to do right now", "Scam call, money lost, hacked account or sextortion? Get the first steps in order, with 1930, cybercrime.gov.in, Chakshu and your rights against your bank.", FRAUD),
}
