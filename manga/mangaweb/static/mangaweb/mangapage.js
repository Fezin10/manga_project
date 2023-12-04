function template_render_mobile() {
    if (!isMobileDevice()) {
        document.getElementById('mangapage_thumb').className = 'col-5';
        document.getElementById('mangapage_content').className = 'col-7';
    }
}