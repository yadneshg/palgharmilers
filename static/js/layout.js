function submitForm() {
  var frm = document.getElementsByName('searchform')[0];
  frm.submit(); // Submit the form
  frm.reset(); // Reset all form data
  return false; // Prevent page refresh
}
