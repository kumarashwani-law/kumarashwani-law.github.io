// Bar Council of India Rule 36 entry disclaimer: shown once per browser until the visitor agrees.
(function () {
  var KEY = 'ak-disclaimer-agreed';
  var agreed = false;
  try { agreed = localStorage.getItem(KEY) === 'yes'; } catch (e) { agreed = false; }
  if (agreed) return;

  function show() {
    var gate = document.createElement('div');
    gate.className = 'gate';
    gate.setAttribute('role', 'dialog');
    gate.setAttribute('aria-modal', 'true');
    gate.setAttribute('aria-labelledby', 'gate-title');
    gate.innerHTML =
      '<div class="gate-box">' +
      '<b class="serif" style="font-size:20px">Ashwani Kumar</b>' +
      '<h2 id="gate-title">Disclaimer</h2>' +
      '<p>The Bar Council of India does not permit advocates to solicit work or advertise. By clicking “I agree”, you acknowledge that:</p>' +
      '<ul>' +
      '<li>there has been no advertisement, personal communication, solicitation, invitation or inducement of any kind from me to seek work through this website;</li>' +
      '<li>you are visiting this website of your own accord, to find out more about me and my writing for your own information;</li>' +
      '<li>the information here is general and is not legal advice, and reading or using this website does not create an advocate–client relationship;</li>' +
      '<li>the information about me on this website is true and genuine to the best of my knowledge;</li>' +
      '<li>I am not liable for any action taken on the basis of material on this website. Please seek independent legal advice for your situation.</li>' +
      '</ul>' +
      '<div class="row" style="padding-top:8px">' +
      '<button type="button" class="btn btn-primary" id="gate-agree">I agree — enter site</button>' +
      '<a class="btn btn-ghost" href="https://www.google.com">Leave</a>' +
      '</div></div>';
    document.body.appendChild(gate);
    document.body.style.overflow = 'hidden';
    var agree = document.getElementById('gate-agree');
    agree.focus();
    agree.addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'yes'); } catch (e) {}
      gate.remove();
      document.body.style.overflow = '';
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show);
  else show();
})();
