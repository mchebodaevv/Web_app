function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const isOpen = sidebar.classList.contains('open');
    
    if (isOpen) {
        sidebar.classList.remove('open');
        document.querySelector('.main-content').style.marginLeft = '0';
    } else {
        sidebar.classList.add('open');
        document.querySelector('.main-content').style.marginLeft = '250px';
    }
}
// Открытие карточки
