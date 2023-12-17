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
                            image.alt = `${i+1} image preview`;
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

        let analysis = document.querySelector('#analysis_button');
        if (analysis) {
            analysis.addEventListener('click', () => {
                let check = window.prompt("Report the problem: ");
                if (check !== null) {
                    fetch(`${analysis.getAttribute('data-url')}?reason=${check}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data['status'] === 'success') {
                            location.reload();
                        } else {
                            alert('Fail');
                        }
                    })
                }
            })
        }


        let free = document.querySelector('#free_button');
        if (free) {
            function call(button) {
                let url = button.getAttribute('data-url');
                let check = document.querySelector('#fault');
                let ban_author = document.querySelector('#ban_author');
                if (check.checked) {
                    url += '?fault=True';
                    if (ban_author.checked) {
                        url += '&ban=True';
                    }
                } else if (ban_author.checked) {
                    url += '?ban=True';
                }
                console.log(url);
                return fetch(url)
                .then(response => response.json())
                .then(data => {
                    console.log(data['status']);
                    if (data['status'] === 'success') {
                        return true;
                    } else {
                        alert('Operation failed!');
                        return false;
                    }
                })
            }
            ban = document.querySelector('#block_button');
            ban.addEventListener('click', () => {
                if (call(ban)) {
                    document.querySelector('#fault').parentElement.remove();
                    ban.parentElement.innerHTML = 'Banned';
                }
            });
            free.addEventListener('click', () => {
                call(free).then((success) =>  {
                    if (success) {
                        location.reload();
                    }
                })
            });
        }

        // Like button to the mangapage
        let like_button = document.querySelector("#like_button");
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
                        console.log(data['status'])
                        alert('Can not complete the like process')
                    } else {
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


        let follow_button = document.querySelector('#follow_button');
        if (follow_button) {
            fetch(follow_button.value)
            .then(response => response.json())
            .then(data => {
                if (data['status'] !== 'success') {
                    console.log(data['status']);
                    alert('Can not retrieve the following data from the server');
                } else {
                    console.log(data['following'])
                    if (data['following'] == true) {
                        follow_button.innerText = 'Unfollow';
                    } else {
                        follow_button.innerText = 'Follow';
                    }
                }
            })
            follow_button.addEventListener('click', () => {
                fetch(follow_button.value, {
                    method: "PUT",
                    headers: {
                        'X-CSRFTOKEN': csrftoken
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data['status'] !== 'success') {
                        console.log(data['status']);
                        alert('Fail when trying to un/follow the user');
                    } else {
                        console.log(data['following'])
                        if (data['following'] == true) {
                            follow_button.innerText = 'Unfollow';
                        } else {
                            follow_button.innerText = 'Follow';
                        }
                        document.querySelector('#followers').innerText = `Followers: ${data['following_count']}`
                    }
                })
            })
        }


        let counter = document.querySelector('#counter');
        if (counter) {
            let sinopse = document.querySelector('#sinopse');
            counter.innerText = 300 - sinopse.value.length + ' characters left.';
            sinopse.addEventListener('input', () => {
                counter.innerText = 300 - sinopse.value.length + ' characters left.';
            })
        }


        let author_button = document.querySelector('#author_button');
        if (author_button) {
            author_button.addEventListener('click', () => {
                fetch(author_button.value)
                .then(response => response.json())
                .then(data => {
                    if (data['status'] == 'success') {
                        document.querySelector('#user_author_div').innerHTML = 'Author: True'
                    }
                })
            })
        }


        let pageview = document.querySelector('#page_view');
        if (pageview) {
            let visualization = document.querySelector('#view').innerHTML;
            document.querySelector('#view').remove();
            index = 0; // keeps track of which image to show
            pages = document.querySelectorAll('.page_read');

            // all images besides the first are being hidden
            for (let i = 1; i < pages.length; i++) {
                pages[i].style.display = 'none';
            }

            next = document.querySelector('#next');
            next.style.display = 'none';
            previous = document.querySelector('#previous');
            previous.style.display = 'none';
            
            // handle the clicks to change the image
            document.querySelector('#next_button').addEventListener('click', left)
            document.querySelector('#previous_button').addEventListener('click', right)
           // handles when the navbar is being used 
            document.querySelector('#navbar-toggler').addEventListener('click', () => {
                setTimeout(changetop, 320);
            })

            document.addEventListener('keydown', handleArrowKey);

            // Go to next image
            function left() {
                if (previous.style.display == 'inline') {
                    pages[index].style.display = 'inline';
                    previous.style.display = 'none';
                } else {
                    pages[index].style.display = 'none';
                    if (index+1 >= pages.length) {
                        next.style.display = 'inline';
                        fetch(visualization)
                        changetop()
                    } else {
                        index++;
                        pages[index].style.display = 'inline';
                    }
                }
            }

            // Go to previous image
            function right() {
                if (next.style.display == 'inline') {
                    next.style.display = 'none';
                    pages[index].style.display = 'inline';
                } else {
                    pages[index].style.display = 'none';
                    if (index-1 < 0) {
                        previous.style.display = 'inline';
                        changetop()
                    } else {
                        index--;
                        pages[index].style.display = 'inline';
                    }
                }
            }

            // update the size of the buttons to change the page so they dont get in the way of other things
            function changetop() {
                let n = document.querySelector('#next_button');
                let p = document.querySelector('#previous_button');
                let value;
                if (previous.style.display !== 'none') {
                    // get where the especial text happens, and get bellow it by 2 em to let the user click the content inside the text if needed
                    value = previous.offsetTop + (parseFloat(window.getComputedStyle(previous).fontSize)*2) + 'px';
                } else if (next.style.display !== 'none') {
                    value = next.offsetTop + (parseFloat(window.getComputedStyle(next).fontSize)*2) + 'px';
                } else {
                    value = pages[index].offsetTop + 'px';
                }

                n.style.top = value;
                p.style.top = value;
                
            }

            // go to next or previous page if the user presses right or left key
            function handleArrowKey(event) {
                if (event.key == 'ArrowLeft') {
                    left();
                } else if (event.key == 'ArrowRight') {
                    right();
                }
            }

            changetop()
        }


        if (!isMobileDevice()) {
            try {
                document.getElementById('page_image').className = 'col';
                document.getElementById('page_content').className = 'col';
            } catch {
                null
            }
        }
})

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}