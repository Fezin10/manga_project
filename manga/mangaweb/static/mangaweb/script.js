document.addEventListener('DOMContentLoaded', () => {
    // Function to create a preview for the image files sended in some pages
        let preview = document.querySelector('#image_preview');
        if (preview) {
            function preview_image(event) {
            let input = event.target;
            preview.innerHTML = '';
            if (input.files && input.files.length > 0) {
                let promises = [];
                // Loop to get each image and put then inside a bootstrap grid structure
                for (let i = 0; i < input.files.length; i++) {
                    let promise = new Promise((resolve) => {
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
                            image.alt = `${i} image preview`;
                            image.className = "figure-img img-fluid rounded";
                            figure.appendChild(image);
                            figure.appendChild(figcaption);
                            col.appendChild(figure);
                            resolve(col);
                        };
                        reader.readAsDataURL(input.files[i]);
                    });
                
                    promises.push(promise);
                }
                
                // Make the images show in the order the user selected
                Promise.all(promises).then((columns) => {
                    let row;
                    columns.forEach((col, index) => {
                        if (index % 3 === 0) {
                            if (row) {
                                preview.appendChild(row);
                            }
                            row = document.createElement('div');
                            row.className = 'row';
                        }
                        row.appendChild(col);
                    });
                    if (row) {
                        preview.appendChild(row);
                    }
                });
            }
        }
        let image_input = document.querySelector('#image_input');
        image_input.addEventListener('change', preview_image);
        }


    // Like button to the mangapage
    like_button = document.querySelector("#like_button");
    if (like_button) {
        fetch(like_button.value)
        .then(response => response.json())
        .then(data => {
            if (data['status'] == 'success') {
                if (data['liked'] == true) {
                    like_button.innerText = 'Unlike';
                } else {
                    like_button.innerText = 'Like';
                }
            } else {
                console.log(data['status'])
                alert('Something went wrong when retrieving like data')
            }
        })
        like_button.addEventListener('click', () => {
            fetch(like_button.value, {
                method: "PUT",
                headers: {
                    'X-CSRFTOKEN': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data['status'] == 'success') {
                    if (data['liked'] == true) {
                        like_button.innerText = 'Unlike';
                    } else {
                        like_button.innerText = 'Like';
                    }
                    document.querySelector('#likes').innerText = `Likes: ${data['likes']}`;
                }
            })
        })
    }

    template_render_mobile()
})

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}