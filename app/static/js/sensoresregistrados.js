const btnDelete = document.querySelectorAll('.btn-danger')

if (btnDelete){
    const btnArray = Array.from(btnDelete);
    btnArray.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if(!confirm('¿Estás seguro de que quieres eliminar este sensor?')) {
                e.preventDefault();
            }
        });
    });
}