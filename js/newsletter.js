// Client-side validation + UX for the newsletter signup forms.
// The actual subscription is handled by the email provider named in each
// form's "action" URL (see form markup) — this script does not send email
// itself, it just validates input and gives the person clear feedback
// before handing off to the provider.
(function () {
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function onSubmit(form) {
    form.addEventListener('submit', function (e) {
      var emailInput = form.querySelector('input[type="email"]');
      var consentInput = form.querySelector('input[type="checkbox"]');
      var msg = form.querySelector('.nf-msg');
      var email = (emailInput.value || '').trim();

      emailInput.classList.remove('nf-invalid');
      if (msg) { msg.className = 'nf-msg'; msg.textContent = ''; }

      if (!email || !EMAIL_RE.test(email)) {
        e.preventDefault();
        emailInput.classList.add('nf-invalid');
        emailInput.setAttribute('aria-invalid', 'true');
        if (msg) {
          msg.className = 'nf-msg nf-error';
          msg.textContent = 'Please enter a valid email address.';
        }
        emailInput.focus();
        return;
      }
      emailInput.removeAttribute('aria-invalid');

      if (consentInput && !consentInput.checked) {
        e.preventDefault();
        if (msg) {
          msg.className = 'nf-msg nf-error';
          msg.textContent = 'Please tick the box to confirm you want to receive emails.';
        }
        consentInput.focus();
        return;
      }

      // Valid: let the form submit to the provider (opens in a new tab),
      // and show an optimistic success message here.
      if (msg) {
        msg.className = 'nf-msg nf-success';
        msg.textContent = 'Thanks — check the new tab to confirm your subscription.';
      }
    });
  }

  document.querySelectorAll('.newsletter-form').forEach(onSubmit);
})();
