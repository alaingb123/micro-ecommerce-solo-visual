



const rows = document.querySelectorAll('tr.cursor-pointer');


  rows.forEach(row => {
    row.addEventListener('click', function(event) {
      window.location.href = this.dataset.href;
    });
  });



