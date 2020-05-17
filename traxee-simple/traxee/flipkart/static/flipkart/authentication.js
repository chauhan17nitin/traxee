const authModals = document.querySelectorAll('.auth .modal');
const authSwitchLinks = document.querySelectorAll('.switch');

// toggling between modals
authSwitchLinks.forEach((link) => {
  link.addEventListener('click', ()=>{
      authModals.forEach((modal) => modal.classList.toggle('active'));
  });
});

