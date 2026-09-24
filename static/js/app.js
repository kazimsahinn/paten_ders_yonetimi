document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('input[type="date"]').forEach((input) => {
    if (!input.value) input.value = new Date().toISOString().slice(0, 10);
  });
});
