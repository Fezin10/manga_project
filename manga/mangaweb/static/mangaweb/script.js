document.addEventListener('DOMContentLoaded', () => {
    try {
        let preview = document.querySelector('#image_preview');
        function preview_image(event) {
            let input = event.target;
            preview.innerHTML = '';
            if (input.files && input.files.length > 0) {
                let row;
                for (let i = 0; i < input.files.length; i++) {
                    if (i % 3 === 0) {
                        if (row) {
                            preview.appendChild(row);
                        }
                        row = document.createElement('div');
                        row.className = 'row';
                    }
                    let col = document.createElement('div');
                    col.className = 'col-3';
                    let figure = document.createElement('figure');
                    figure.className = "figure";
                    let figcaption = document.createElement('figcaption');
                    figcaption.className = "figure-caption";
                    figcaption.innerText = `${String(i+1).padStart(3, '0')} image.`
                    let reader = new FileReader();
                    reader.onload = function(e) {
                        let image = document.createElement('img');
                        image.src = e.target.result;
                        image.alt = `${i} image preview`
                        image.alt = "%i image preview";
                        image.className = "figure-img img-fluid rounded";
                        figure.appendChild(image);
                        figure.appendChild(figcaption);
                        col.appendChild(figure);
                        row.appendChild(col);
                    };
                    reader.readAsDataURL(input.files[i]);
                }
                if (input.files.length % 3 !== 0) {
                        preview.appendChild(row);
                }
            }
        }
        let image_input = document.querySelector('#image_input');
        image_input.addEventListener('change', preview_image);
    } catch(error) {
        console.log(error);
    }
})